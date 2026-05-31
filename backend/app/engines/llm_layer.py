import json
import logging
import re
import hashlib
from typing import Dict, Any, List, Optional
import os

from sqlalchemy.orm import Session
from sqlalchemy import func
import google.generativeai as genai
import redis

from app.models.mistake import Mistake

logger = logging.getLogger(__name__)

# Basic Redis setup (optional bypass if redis is not reachable)
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
redis_client = None
try:
    redis_client = redis.from_url(redis_url, decode_responses=True)
    redis_client.ping()
except Exception as e:
    logger.warning("Redis not available: %s. Cache will be disabled.", e)
    redis_client = None

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
# Initialize the model once
gemini_model = genai.GenerativeModel('gemini-1.5-flash') if GEMINI_API_KEY else None

SYSTEM_PROMPT = """You are an expert DSA tutor helping a student debug interview-style code.
Your goal is to be clear, encouraging, and specific without spoiling the answer too early.
You must ground every hint in the evidence provided: the student's code, AST findings, failing test cases, runtime errors, and mistake history.

Style rules:
- Sound like a real mentor, not a linter or compiler log.
- Use plain language a student can act on immediately.
- Focus on the most important bug first.
- Do not say generic things like "review your logic" unless you also point to what to inspect.
- Do not reveal the final algorithm in `hint_1` or `hint_2`.
- If there is a visible failing testcase, use it to anchor the explanation.

You must reply strictly in valid JSON format with EXACTLY the following four keys:
- `explanation`: 2-3 sentences explaining the main issue in student-friendly language.
- `hint_1`: One short directional nudge. No code.
- `hint_2`: 1-2 sentences with more concrete guidance. Still no full solution.
- `hint_3`: The corrected code snippet with a short explanation.

Do not include markdown fences, preamble text, or extra keys."""


def _first_sentence(text: str) -> str:
    if not text:
        return ""
    cleaned = " ".join(str(text).strip().split())
    if not cleaned:
        return ""
    parts = re.split(r'(?<=[.!?])\s+', cleaned, maxsplit=1)
    return parts[0].strip()


def _clean_runtime_error(error_message: str) -> str:
    if not error_message:
        return "runtime error"
    lines = [line.strip() for line in str(error_message).splitlines() if line.strip()]
    if not lines:
        return "runtime error"
    for line in reversed(lines):
        if ":" in line or "Error" in line or "Exception" in line:
            return line
    return lines[-1]


def _summarize_ast_issue(issue: Dict[str, Any]) -> str:
    if not issue:
        return "There is a static issue in the code."
    issue_type = str(issue.get("type", "")).lower()
    message = issue.get("message", "") or ""
    line = issue.get("line")

    if issue_type == "syntax_error":
        return f"There is a syntax problem{f' near line {line}' if line else ''}, so the code cannot run yet."
    if issue_type == "infinite_loop":
        return "One of your loops may not be moving toward a stopping condition."
    if issue_type == "unused_variable":
        return "Part of the logic is being stored in a variable that never affects the final answer."
    if issue_type == "missing_base_case":
        return "Your recursive function is missing a stopping condition for a small input."
    if issue_type == "mutable_default":
        return "A mutable default value is being reused across calls, which can create hidden bugs."
    if message:
        return _first_sentence(message)
    return "Static analysis found a code issue worth fixing first."


def _normalise_problem_name(problem_title: Optional[str]) -> str:
    return problem_title or "this problem"


def _build_test_anchor(failing_test: Optional[Dict[str, Any]]) -> str:
    if not failing_test:
        return ""
    test_input = failing_test.get("input", "")
    expected = failing_test.get("expected_output", "?")
    actual = failing_test.get("actual_output") or "(no output)"
    return f"For the visible case input {test_input}, the expected result is {expected}, but your code produces {actual}."


def _runtime_hint_for_language(language: str) -> str:
    lang = (language or "").lower()
    if lang == "python":
        return "Make sure your function returns the answer instead of only printing it, and keep the function signature exactly as the starter code expects."
    if lang == "java":
        return "Check that your method signature matches the starter code exactly and that you return the computed value instead of only printing."
    if lang in {"cpp", "c++"}:
        return "Check the function signature, return type, and whether you are returning the final answer instead of writing only to stdout."
    if lang in {"javascript", "js"}:
        return "Make sure the exported function returns the final value and that parameter names still match the starter function."
    return "Check that your function signature matches the starter code and that you return the final answer."

def get_top_mistakes(user_id: int, db: Session) -> str:
    if not user_id or not db:
        return ""
    
    # Query top 2 mistakes by frequency
    mistakes = (
        db.query(Mistake.mistake_type, func.count(Mistake.id).label("count"))
        .filter(Mistake.user_id == user_id)
        .group_by(Mistake.mistake_type)
        .order_by(func.count(Mistake.id).desc())
        .limit(2)
        .all()
    )
    
    if not mistakes:
        return ""
        
    history_str = ", ".join([f"{m.mistake_type} ({m.count} times)" for m in mistakes])
    return f"This student has previously struggled with: {history_str}."

def compute_cache_key(code: str, language: str, failure_type: str, problem_id: Optional[str] = None) -> str:
    raw = f"{code}:{language}:{failure_type}:{problem_id or 'none'}".encode('utf-8')
    return "llm_cache:" + hashlib.md5(raw).hexdigest()

def extract_json_with_fallback(text: str) -> Dict[str, Any]:
    # Layer 1: Direct Parse
    try:
        return json.loads(text)
    except Exception:
        pass
        
    # Layer 2: Strip markdown fences
    stripped = re.sub(r'```(?:json)?', '', text).strip()
    try:
        return json.loads(stripped)
    except Exception:
        pass
        
    # Layer 3: Regex extraction
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
            
    # Layer 4: Standard fallback
    return {
        "explanation": "We detected an issue in your logic but couldn't parse the specific AI explanation.",
        "hint_1": "Review the basic structure of your inputs and outputs.",
        "hint_2": "Look closely at error stack traces or execution details.",
        "hint_3": "Check for common logical misteps or syntax edge cases."
    }


def build_contextual_fallback(
    language: str,
    failure_report: Dict[str, Any],
    ast_issues: List[Dict[str, Any]],
    problem_title: Optional[str] = None,
) -> Dict[str, Any]:
    title = _normalise_problem_name(problem_title)
    dominant_failure = failure_report.get("dominant_failure_type", "UNKNOWN")
    test_results = failure_report.get("test_results", [])
    failing_test = next((t for t in test_results if t.get("status") != "PASSED"), None)

    if ast_issues:
        first_issue = ast_issues[0]
        issue_summary = _summarize_ast_issue(first_issue)
        line = first_issue.get("line")
        return {
            "explanation": (
                f"Before we even judge the answer for {title}, there is a code issue to fix first. "
                f"{issue_summary}"
            ),
            "hint_1": "Get the code into a runnable state first, then test again on the first visible example.",
            "hint_2": (
                f"Focus on{f' line {line}' if line else ' the location flagged by the analyzer'} and make sure that block does exactly what you intended before moving on."
            ),
            "hint_3": "Use the Show Solution button to compare your final approach with the reference solution.",
        }

    if dominant_failure == "WRONG_OUTPUT" and failing_test:
        expected = failing_test.get("expected_output", "?")
        actual = failing_test.get("actual_output") or "(no output)"
        return {
            "explanation": (
                f"Your code runs to completion, but the logic is off for {title}. "
                f"{_build_test_anchor(failing_test)}"
            ),
            "hint_1": "Walk through that visible testcase step by step and note the moment your state stops matching the answer you expect.",
            "hint_2": (
                f"Pay special attention to how you build the final result: it needs to match {expected} exactly, not just be close in spirit to {actual}."
            ),
            "hint_3": "Use the Show Solution button to compare your algorithm with the reference solution.",
        }

    if dominant_failure == "RUNTIME_ERROR" and failing_test:
        runtime_error = _clean_runtime_error(failing_test.get("error_message", ""))
        return {
            "explanation": (
                f"Your code is crashing before it can finish {title}. "
                f"The key error is: {runtime_error}."
            ),
            "hint_1": "Start by checking the function signature and the type or number of values your code expects to receive.",
            "hint_2": _runtime_hint_for_language(language),
            "hint_3": "Use the Show Solution button to compare your function structure with the reference solution.",
        }

    if dominant_failure == "TIMEOUT":
        return {
            "explanation": (
                f"Your code is not finishing within the allowed time for {title}. "
                "That usually means either one loop never converges or the approach is too slow for larger inputs."
            ),
            "hint_1": "Check whether every loop or recursion step clearly moves toward a stopping condition.",
            "hint_2": "If the control flow looks correct, step back and ask whether this needs the intended DSA pattern instead of checking too many combinations.",
            "hint_3": "Use the Show Solution button to compare the expected time complexity with your approach.",
        }

    if dominant_failure == "EMPTY_OUTPUT" and failing_test:
        return {
            "explanation": (
                f"Your code ran, but it did not produce the answer the evaluator is looking for in {title}. "
                f"{_build_test_anchor(failing_test)}"
            ),
            "hint_1": "Make sure your function actually returns a value for the visible testcase.",
            "hint_2": _runtime_hint_for_language(language),
            "hint_3": "Use the Show Solution button to compare your return path with the reference solution.",
        }

    return {
        "explanation": (
            f"Your submission for {title} still needs another pass. "
            "Use the visible examples to verify both the exact return value and the overall approach."
        ),
        "hint_1": "Start with the first visible example and write down what the function should return before you run it.",
        "hint_2": "Then compare that expected result with what your code is actually building step by step.",
        "hint_3": "Use the Show Solution button to compare against the reference implementation.",
    }

def generate_hints(code: str, language: str, failure_report: Dict[str, Any], ast_issues: List[Dict[str, Any]], user_id: Optional[int] = None, db: Optional[Session] = None, problem_desc: Optional[str] = None, problem_id: Optional[str] = None, hint_intent: Optional[str] = None, pattern_name: Optional[str] = None, problem_title: Optional[str] = None, constraints_text: Optional[str] = None) -> Dict[str, Any]:
    # ── 1. Check Cache ──────────────────────────────────────────
    dominant_failure = failure_report.get("dominant_failure_type", "UNKNOWN")
    cache_key = compute_cache_key(code, language, dominant_failure, problem_id)
    
    if redis_client:
        try:
            cached_val = redis_client.get(cache_key)
            if cached_val:
                return {**json.loads(cached_val), "cached": True, "model": "cache"}
        except Exception as e:
            logger.warning("Redis cache error: %s", e)
            
    # ── 2. Construct Prompt ──────────────────────────────────────
    ast_findings_str = "No static issues detected."
    if ast_issues:
        ast_findings_str = "\n".join([f"- {issue.get('message', 'Issue')}" for issue in ast_issues])
        
    failure_summary = failure_report.get("failure_summary", "")
    test_results = failure_report.get("test_results", [])
    
    # Try to find exactly one failing test case to ground the LLM
    failing_test = next((t for t in test_results if t.get("status") != "PASSED"), None)
    if failing_test:
        test_ctx = (
            f"Failing Test Case:\n"
            f"  Input: {failing_test.get('input', '')}\n"
            f"  Expected Output: {failing_test.get('expected_output', '?')}\n"
            f"  Actual Output: {failing_test.get('actual_output') or failing_test.get('error_message', '(no output)')}"
        )
    else:
        test_ctx = "No specific failing tests to report."
        
    runtime_error_ctx = "No runtime errors."
    if dominant_failure in ["RUNTIME_ERROR", "TIMEOUT", "SYNTAX_ERROR"]:
        runtime_err_msg = failing_test.get('error_message', '') if failing_test else ""
        if dominant_failure == "TIMEOUT":
            runtime_error_ctx = "Code execution timed out."
        else:
            runtime_error_ctx = f"Execution Error: {runtime_err_msg}"
            
    mistakes_ctx = get_top_mistakes(user_id, db) if user_id and db else ""
    
    problem_ctx = ""
    if any([problem_desc, problem_title, pattern_name, constraints_text]):
        problem_ctx = "\n[PROBLEM CONTEXT]\n"
        if problem_title:
            problem_ctx += f"Title: {problem_title}\n"
        if pattern_name:
            problem_ctx += f"Pattern: {pattern_name}\n"
        if constraints_text:
            problem_ctx += f"Constraints: {constraints_text}\n"
        if problem_desc:
            problem_ctx += f"Brief: {problem_desc}\n"

    intent_ctx = ""
    if hint_intent:
        intent_ctx = f"\nHint intent: {hint_intent}\n"
    
    user_prompt = f"""
Student Code:
```{language}
{code}
```
{problem_ctx}
{intent_ctx}
AST Findings:
{ast_findings_str}

Failure Summary:
{failure_summary}
{test_ctx}

Execution Error:
{runtime_error_ctx}

Mistake History:
{mistakes_ctx}

Output Instructions:
1. `explanation`: 2-3 sentences. Identify the root cause in plain student-friendly language.
2. `hint_1`: 1 sentence. A gentle directional nudge tied to the failing testcase or error.
3. `hint_2`: 1-2 sentences. More concrete guidance about what to inspect next, but still no full solution.
4. `hint_3`: Corrected code snippet and a 2-line explanation.
"""

    # ── 3. Call LLM ───────────────────────────────────────────────
    if not gemini_model:
        logger.error("Gemini API key not configured.")
        result_json = build_contextual_fallback(language, failure_report, ast_issues, problem_title)
        return {**result_json, "cached": False, "model": "fallback"}
        
    try:
        # We prepend the system prompt to the user prompt since Gemini handles it fine in text.
        # Alternatively we could use system_instruction if using latest SDK, 
        # but prepending is safe for older versions.
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        response = gemini_model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1000,
                temperature=0.2,
            )
        )
        response_text = response.text
    except Exception as e:
        logger.error("Gemini API call failed: %s", e)
        response_text = ""
        
    # ── 4. Parse & Validate JSON ──────────────────────────────────
    result_json = extract_json_with_fallback(response_text)
    generic_fallback = result_json.get("explanation", "").startswith("We detected an issue")
    if generic_fallback:
        result_json = build_contextual_fallback(language, failure_report, ast_issues, problem_title)
    
    # Ensure keys exist
    for k in ["explanation", "hint_1", "hint_2", "hint_3"]:
        if k not in result_json:
            result_json[k] = ""
            
    # ── 5. Cache Result ───────────────────────────────────────────
    if redis_client and response_text:
        try:
            redis_client.setex(cache_key, 86400, json.dumps(result_json)) # TTL 24h
        except Exception as e:
            logger.warning("Failed to write to redis: %s", e)
            
    return {**result_json, "cached": False, "model": "gemini-1.5-flash"}

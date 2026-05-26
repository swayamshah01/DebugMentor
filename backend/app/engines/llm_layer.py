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

SYSTEM_PROMPT = """You are an expert programming tutor helping a student debug their code.
Your goal is to guide the student to the correct solution without giving them the direct answer immediately.
You must analyze the factual evidence provided: the student's code, AST static analysis findings, execution failure reports, and mistake history.

You must reply strictly in valid JSON format with EXACTLY the following four keys:
- `explanation`: 2-3 sentences explaining what is wrong without giving the solution.
- `hint_1`: A directional nudge (one sentence, no code).
- `hint_2`: A stronger nudge that references specific lines but still no full solution.
- `hint_3`: The corrected code snippet with a 2-line explanation of what changed and why.

Do not include any preamble, markdown formatting around the JSON, or extra keys."""

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
1. `explanation`: 2-3 sentences. Identify the root cause without explicitly showing how to fix it.
2. `hint_1`: 1 sentence. A gentle directional nudge.
3. `hint_2`: 1-2 sentences. Specific guidance mentioning the exact problem line, but no code.
4. `hint_3`: Corrected code snippet and a 2-line explanation.
"""

    # ── 3. Call LLM ───────────────────────────────────────────────
    if not gemini_model:
        logger.error("Gemini API key not configured.")
        result_json = extract_json_with_fallback("")
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

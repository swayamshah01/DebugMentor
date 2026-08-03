"""On-demand, code-specific progressive hint generation."""

from __future__ import annotations

import json

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.config import settings
from app.models.problem import Problem
from app.models.submission import Submission


class HintGenerationError(RuntimeError):
    pass


class GeneratedHint(BaseModel):
    level: int
    title: str = Field(min_length=3, max_length=90)
    content: str = Field(min_length=20, max_length=900)
    focus: str = Field(min_length=2, max_length=40)


class GeneratedSolution(BaseModel):
    title: str = Field(min_length=3, max_length=90)
    explanation: str = Field(min_length=20, max_length=1200)
    code: str = Field(min_length=20)


class HintBundle(BaseModel):
    diagnosis: str = Field(min_length=20, max_length=1200)
    hints: list[GeneratedHint] = Field(min_length=2, max_length=2)
    solution: GeneratedSolution


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "diagnosis": {"type": "string"},
        "hints": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer"},
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "focus": {"type": "string"},
                },
                "required": ["level", "title", "content", "focus"],
            },
        },
        "solution": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "explanation": {"type": "string"},
                "code": {"type": "string"},
            },
            "required": ["title", "explanation", "code"],
        },
    },
    "required": ["diagnosis", "hints", "solution"],
}


SYSTEM_PROMPT = """You are DebugMentor, a senior DSA coach reviewing one student's exact submission.
Return only the requested JSON. Diagnose the student's code, not a generic version of the problem.
Mention concrete identifiers, conditions, or control-flow choices from their code when useful.
Hint 1 must be a Socratic nudge without an algorithm or solution. Hint 2 may name the missing
invariant or corrective direction but must still make the student write the fix. The final solution
must be a complete console program in the requested language: read stdin exactly as specified,
define and call the language's normal main entry point, and print only the expected answer.
Never reveal hidden inputs or hidden expected outputs. Do not invent test results."""


def _visible_failure_context(report: dict) -> str:
    lines: list[str] = []
    hidden_failures = 0
    for result in report.get("test_results", []):
        if result.get("status") == "PASSED":
            continue
        if result.get("is_hidden"):
            hidden_failures += 1
            continue
        lines.append(
            " | ".join(
                [
                    str(result.get("label") or "Visible test"),
                    f"input={result.get('input')}",
                    f"expected={result.get('expected_output')}",
                    f"actual={result.get('actual_output') or '(no output)'}",
                    f"status={result.get('status')}",
                    f"error={result.get('error_summary') or 'none'}",
                ]
            )
        )
    if hidden_failures:
        lines.append(f"{hidden_failures} hidden test(s) failed; their values are intentionally unavailable.")
    return "\n".join(lines) or "No visible failing value is available; reason from the code and summary."


def _build_prompt(submission: Submission, problem: Problem) -> str:
    report = submission.test_results if isinstance(submission.test_results, dict) else {}
    examples = json.dumps(problem.examples_json or [], ensure_ascii=True)
    return f"""Problem title: {problem.title}
Pattern: {problem.pattern.name if problem.pattern else 'Uncategorized'}
Difficulty: {problem.difficulty}

Problem statement:
{problem.statement}

Input and constraints:
{problem.constraints_text or 'No extra constraints provided.'}

Visible examples:
{examples}

Submission language: {submission.language}
Official result: {report.get('summary') or report.get('failure_summary') or submission.status}
Dominant failure: {report.get('dominant_failure_type') or 'unknown'}

Available failing-test evidence:
{_visible_failure_context(report)}

Student code:
```{submission.language}
{submission.code}
```

Generate a diagnosis, two progressively more specific hints, and a complete corrected console program."""


def generate_hint_bundle(submission: Submission, problem: Problem) -> dict:
    if not settings.GEMINI_API_KEY:
        raise HintGenerationError(
            "AI hints are not configured. Add GEMINI_API_KEY to backend/.env and restart the backend."
        )

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": _build_prompt(submission, problem)}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 3000,
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
        },
    }

    try:
        with httpx.Client(timeout=settings.HINT_TIMEOUT_SECONDS) as client:
            response = client.post(
                endpoint,
                headers={"x-goog-api-key": settings.GEMINI_API_KEY},
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
        response_text = body["candidates"][0]["content"]["parts"][0]["text"]
        generated = HintBundle.model_validate_json(response_text)
    except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, ValidationError) as exc:
        raise HintGenerationError(
            "The hint service could not produce valid personalized guidance. Please try again."
        ) from exc

    ordered_hints = sorted(generated.hints, key=lambda item: item.level)
    ordered_hints[0].level = 1
    ordered_hints[1].level = 2
    normalized = generated.model_copy(update={"hints": ordered_hints})
    return normalized.model_dump()

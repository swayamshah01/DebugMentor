"""
failure_detector.py — Failure Classification Engine (Phase 2)

Processes raw execution results from the executor and classifies each
test run into one of 6 states:
  TIMEOUT, COMPILE_ERROR, RUNTIME_ERROR, EMPTY_OUTPUT, WRONG_OUTPUT, PASSED

Produces a structured FailureReport JSON for the /submit response.
"""

import ast
import json
import re
from typing import List, Dict, Any, Optional


# ── Known runtime error patterns ─────────────────────────────────────────────
RUNTIME_ERROR_PATTERNS = [
    r"(TypeError|NameError|ValueError|IndexError|KeyError|ZeroDivisionError"
    r"|AttributeError|RecursionError|OverflowError|FileNotFoundError"
    r"|StopIteration|RuntimeError|UnboundLocalError)",
]


def _classify_single(result: Dict[str, Any]) -> str:
    """
    Classify a single executor result into one of:
    TIMEOUT, COMPILE_ERROR, RUNTIME_ERROR, EMPTY_OUTPUT, PASSED.
    (WRONG_OUTPUT requires expected output, reserved for Phase 3.)
    """
    # 1. Timeout
    if result.get("timed_out", False):
        return "TIMEOUT"

    stderr = result.get("error_message", "") or ""
    stdout = result.get("actual_output", "") or ""
    exit_code = result.get("exit_code", -1)
    stage = result.get("stage", "run")

    if stage == "compile" and exit_code != 0:
        return "COMPILE_ERROR"

    # 2. Runtime error (non-zero exit code or known error in stderr)
    if exit_code != 0:
        return "RUNTIME_ERROR"

    # Also catch error patterns printed to stderr even with exit_code 0
    if stderr.strip():
        for pattern in RUNTIME_ERROR_PATTERNS:
            if re.search(pattern, stderr):
                return "RUNTIME_ERROR"

    # 3. Empty output
    if not stdout.strip():
        return "EMPTY_OUTPUT"

    # 4. If we have an expected output, perform normalized comparison
    expected = result.get("expected_output")
    if expected and expected != "?":
        def _norm(s: str) -> str:
            if s is None:
                return ""
            # Normalize line endings and surrounding whitespace
            s2 = s.replace('\r\n', '\n').replace('\r', '\n').strip()
            return s2

        exp_norm = _norm(str(expected))
        act_norm = _norm(str(stdout))

        def _parse_structured(value: str):
            if not value:
                return None

            candidates = [
                value,
                value.replace("true", "True").replace("false", "False").replace("null", "None"),
                value.replace("True", "true").replace("False", "false").replace("None", "null"),
            ]

            for candidate in candidates:
                try:
                    return ast.literal_eval(candidate)
                except Exception:
                    pass
                try:
                    return json.loads(candidate)
                except Exception:
                    pass
            return None

        # Handle boolean-like comparisons case-insensitively
        if exp_norm.lower() in ("true", "false"):
            if act_norm.lower() != exp_norm.lower():
                return "WRONG_OUTPUT"
            return "PASSED"

        # Numeric compare when both look like ints
        try:
            if exp_norm.isdigit() and act_norm.lstrip('-').isdigit():
                if int(exp_norm) != int(act_norm):
                    return "WRONG_OUTPUT"
                return "PASSED"
        except Exception:
            pass

        exp_structured = _parse_structured(exp_norm)
        act_structured = _parse_structured(act_norm)
        if exp_structured is not None and act_structured is not None:
            if exp_structured != act_structured:
                return "WRONG_OUTPUT"
            return "PASSED"

        # Fallback string compare
        if act_norm != exp_norm:
            return "WRONG_OUTPUT"

        return "PASSED"

    # 5. Default: PASSED (no expected to compare against)
    return "PASSED"


def _extract_error_type(stderr: str) -> Optional[str]:
    """
    Extract the specific Python error type from stderr output.
    e.g. 'IndexError', 'RecursionError', etc.
    """
    if not stderr:
        return None
    for pattern in RUNTIME_ERROR_PATTERNS:
        match = re.search(pattern, stderr)
        if match:
            return match.group(1)
    return None


def detect_failures(
    test_results: List[Dict[str, Any]],
    ast_issues: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Classify failure states for a batch of test execution results.

    Parameters
    ----------
    test_results : list[dict]
        Each dict has keys from test_generator + executor output:
        input, label, expected_output, actual_output, error_message,
        exit_code, timed_out, execution_time_ms.
    ast_issues : list[dict] | None
        Optional AST issues to include in the report metadata.

    Returns
    -------
    dict – a FailureReport with keys:
        total, passed, failed, has_failures, dominant_failure_type,
        error_category, failure_summary, test_results (enriched).
    """
    enriched = []
    state_counts: Dict[str, int] = {}

    for result in test_results:
        state = _classify_single(result)
        state_counts[state] = state_counts.get(state, 0) + 1

        enriched_result = {**result, "status": state}

        # Enrich with error type if applicable
        if state == "RUNTIME_ERROR":
            error_type = _extract_error_type(
                result.get("error_message", "")
            )
            enriched_result["error_type"] = error_type

        enriched.append(enriched_result)

    total = len(enriched)
    passed = state_counts.get("PASSED", 0)
    failed = total - passed

    # Determine dominant failure type (most common non-PASSED state)
    failure_states = {k: v for k, v in state_counts.items() if k != "PASSED"}
    dominant = max(failure_states, key=failure_states.get) if failure_states else None

    # Error category (from AST or dominant failure)
    error_category = None
    if ast_issues:
        # Prioritize AST errors
        severities = [i["severity"] for i in ast_issues]
        if "error" in severities:
            error_category = "static_analysis_error"
        elif "warning" in severities:
            error_category = "static_analysis_warning"
    if not error_category and dominant:
        error_category = dominant.lower()

    # Human-readable failure summary
    if failed == 0:
        failure_summary = f"All {total} test cases passed successfully."
    else:
        parts = []
        for state, count in sorted(failure_states.items()):
            parts.append(f"{count} {state.replace('_', ' ').lower()}")
        failure_summary = (
            f"{failed} of {total} test cases failed: {', '.join(parts)}."
        )

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "has_failures": failed > 0,
        "dominant_failure_type": dominant,
        "error_category": error_category,
        "failure_summary": failure_summary,
        "test_results": enriched,
    }

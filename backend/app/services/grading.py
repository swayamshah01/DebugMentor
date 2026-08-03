"""Problem grading built around complete stdin/stdout programs."""

from __future__ import annotations

import ast
import json
import math
from collections import Counter
from typing import Any

from sqlalchemy.orm import Session

from app.engines.executor import run_code_batch
from app.models.problem import Problem
from app.models.testcase import TestCase


_UNPARSED = object()
_FAILURE_LABELS = {
    "COMPILE_ERROR": ("compile error", "compile errors"),
    "RUNTIME_ERROR": ("runtime error", "runtime errors"),
    "TIMEOUT": ("timeout", "timeouts"),
    "EMPTY_OUTPUT": ("empty output", "empty outputs"),
    "WRONG_OUTPUT": ("wrong output", "wrong outputs"),
}


def _parse_structured(value: str) -> Any:
    for candidate in (
        value,
        value.replace("true", "True").replace("false", "False").replace("null", "None"),
    ):
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, TypeError):
            pass
        try:
            return ast.literal_eval(candidate)
        except (ValueError, SyntaxError):
            pass
    return _UNPARSED


def outputs_match(expected: str, actual: str) -> bool:
    expected_text = str(expected).replace("\r\n", "\n").replace("\r", "\n").strip()
    actual_text = str(actual).replace("\r\n", "\n").replace("\r", "\n").strip()

    expected_value = _parse_structured(expected_text)
    actual_value = _parse_structured(actual_text)

    if expected_value is not _UNPARSED and actual_value is not _UNPARSED:
        if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
            return math.isclose(float(expected_value), float(actual_value), rel_tol=1e-6, abs_tol=1e-6)
        return expected_value == actual_value

    expected_lines = [line.rstrip() for line in expected_text.splitlines()]
    actual_lines = [line.rstrip() for line in actual_text.splitlines()]
    return expected_lines == actual_lines


def _classify(execution: dict, expected_output: str) -> str:
    if execution.get("stage") == "compile" and execution.get("exit_code") != 0:
        return "COMPILE_ERROR"
    if execution.get("timed_out"):
        return "TIMEOUT"
    if execution.get("exit_code") != 0:
        return "RUNTIME_ERROR"
    actual_output = execution.get("actual_output", "")
    if outputs_match(expected_output, actual_output):
        return "PASSED"
    if not str(actual_output).strip():
        return "EMPTY_OUTPUT"
    return "WRONG_OUTPUT"


def _load_cases(
    db: Session,
    problem_id: int,
    *,
    include_hidden: bool,
    test_case_id: int | None,
) -> list[TestCase]:
    query = db.query(TestCase).filter(TestCase.problem_id == problem_id)
    if not include_hidden:
        query = query.filter(TestCase.is_hidden.is_(False))
    if test_case_id is not None:
        query = query.filter(TestCase.id == test_case_id)
    return query.order_by(TestCase.order_index).all()


def grade_problem(
    db: Session,
    problem: Problem,
    code: str,
    language: str,
    *,
    include_hidden: bool,
    test_case_id: int | None = None,
) -> dict:
    cases = _load_cases(
        db,
        problem.id,
        include_hidden=include_hidden,
        test_case_id=test_case_id,
    )
    if not cases:
        raise ValueError("No eligible test case was found for this problem.")

    executions = run_code_batch(code, language, [case.input for case in cases])
    test_results: list[dict] = []

    for case, execution in zip(cases, executions, strict=True):
        status = _classify(execution, case.expected_output)
        test_results.append(
            {
                "test_case_id": case.id,
                "label": case.label,
                "input": case.input,
                "expected_output": case.expected_output,
                "actual_output": execution.get("actual_output", ""),
                "error_message": execution.get("error_message", ""),
                "error_summary": execution.get("error_summary", ""),
                "execution_time_ms": execution.get("execution_time_ms", 0),
                "stage": execution.get("stage", "run"),
                "is_hidden": case.is_hidden,
                "status": status,
            }
        )

    counts = Counter(result["status"] for result in test_results)
    passed = counts.get("PASSED", 0)
    failed = len(test_results) - passed
    failures = {status: count for status, count in counts.items() if status != "PASSED"}
    dominant = max(failures, key=failures.get) if failures else None

    if failed:
        detail = ", ".join(
            f"{count} {_FAILURE_LABELS.get(status, (status.lower(), status.lower()))[count != 1]}"
            for status, count in sorted(failures.items())
        )
        test_label = "test" if len(test_results) == 1 else "tests"
        summary = f"{failed} of {len(test_results)} {test_label} failed: {detail}."
    else:
        summary = "The test passed." if len(test_results) == 1 else f"All {len(test_results)} tests passed."

    return {
        "total": len(test_results),
        "passed": passed,
        "failed": failed,
        "success": failed == 0,
        "has_failures": failed > 0,
        "dominant_failure_type": dominant,
        "summary": summary,
        "failure_summary": summary,
        "test_results": test_results,
    }


def public_report(report: dict) -> dict:
    """Hide official hidden-test values while preserving useful feedback."""
    visible_results: list[dict] = []
    hidden_index = 0

    for result in report.get("test_results", []):
        item = dict(result)
        if item.get("is_hidden"):
            hidden_index += 1
            item.update(
                {
                    "label": f"Hidden test {hidden_index}",
                    "input": None,
                    "expected_output": None,
                    "actual_output": None,
                    "error_message": "",
                    "error_summary": (
                        "Your program did not handle this hidden case."
                        if item.get("status") != "PASSED"
                        else ""
                    ),
                }
            )
        visible_results.append(item)

    return {**report, "test_results": visible_results}

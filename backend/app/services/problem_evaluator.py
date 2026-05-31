"""Utilities for evaluating submissions against stored curated problems."""

from __future__ import annotations

import ast
import logging
from ast import literal_eval
from typing import Any, Dict, List, Optional, Tuple

from app.engines.executor import run_code
from app.engines.failure_detector import detect_failures
from app.models.problem import Problem
from app.models.testcase import TestCase

logger = logging.getLogger(__name__)


def extract_python_function_name(code: str) -> Optional[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            return node.name
    return None


def _parse_value(text: str) -> Any:
    try:
        return literal_eval(text)
    except Exception:
        return text.strip().strip('"').strip("'")


def parse_problem_input(raw_input: str) -> List[Any]:
    if raw_input is None:
        return []

    lines = [line.strip() for line in str(raw_input).splitlines() if line.strip()]
    if not lines:
        return []

    return [_parse_value(line) for line in lines]


def build_python_runner(code: str, function_name: Optional[str], raw_input: str) -> str:
    if not function_name:
        return code

    helper = f"""
import ast

{code}

def __dm_parse_value(text):
    try:
        return ast.literal_eval(text)
    except Exception:
        return text.strip().strip('"').strip("'")

__dm_raw_input = {raw_input!r}
__dm_lines = [line for line in __dm_raw_input.splitlines() if line.strip()]
__dm_args = [__dm_parse_value(line) for line in __dm_lines]
__dm_result = {function_name}(*__dm_args)
print(__dm_result)
"""
    return helper.strip()


def load_problem_test_cases(db, problem_id: int) -> List[TestCase]:
    return (
        db.query(TestCase)
        .filter(TestCase.problem_id == problem_id)
        .order_by(TestCase.order_index)
        .all()
    )


def evaluate_problem_submission(
    problem: Problem,
    code: str,
    language: str,
    db,
    include_hidden: bool = True,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], List[TestCase]]:
    all_test_cases = load_problem_test_cases(db, problem.id)
    test_cases = all_test_cases if include_hidden else [case for case in all_test_cases if not case.is_hidden]
    raw_results: List[Dict[str, Any]] = []
    function_name = extract_python_function_name(code) if language.lower() == "python" else None

    for test_case in test_cases:
        if language.lower() == "python" and function_name:
            exec_code = build_python_runner(code, function_name, test_case.input)
            exec_result = run_code(user_code=exec_code, language=language, test_input="")
        else:
            exec_result = run_code(user_code=code, language=language, test_input=test_case.input or "")

        raw_results.append({
            "input": test_case.input,
            "label": test_case.label,
            "expected_output": test_case.expected_output,
            "actual_output": exec_result.get("actual_output", "").strip(),
            "error_message": exec_result.get("error_message", ""),
            "exit_code": exec_result.get("exit_code", -1),
            "timed_out": exec_result.get("timed_out", False),
            "execution_time_ms": exec_result.get("execution_time_ms", 0),
            "is_hidden": test_case.is_hidden,
            "order_index": test_case.order_index,
        })

    failure_report = detect_failures(raw_results)
    return raw_results, failure_report, test_cases


def build_problem_context(problem: Problem, visible_results: List[Dict[str, Any]]) -> str:
    parts = [
        f"Problem: {problem.title}",
        f"Pattern: {problem.pattern.name if problem.pattern else 'Unknown'}",
        f"Difficulty: {problem.difficulty}",
        f"Statement: {problem.statement}",
    ]
    if problem.constraints_text:
        parts.append(f"Constraints: {problem.constraints_text}")
    if visible_results:
        visible_lines = []
        for item in visible_results:
            if not item.get("is_hidden"):
                visible_lines.append(
                    f"- {item.get('label')}: input={item.get('input')} expected={item.get('expected_output')} actual={item.get('actual_output') or item.get('error_message') or ''}"
                )
        if visible_lines:
            parts.append("Visible failures/tests:\n" + "\n".join(visible_lines))
    return "\n".join(parts)


def classify_hint_intent(failure_report: Dict[str, Any], ast_issues: List[Dict[str, Any]]) -> str:
    if any(issue.get("type") == "syntax_error" for issue in ast_issues):
        return "bug_fix"

    dom = (failure_report or {}).get("dominant_failure_type")
    if dom == "WRONG_OUTPUT":
        return "conceptual"
    if dom in {"RUNTIME_ERROR", "TIMEOUT", "EMPTY_OUTPUT"}:
        return "bug_fix"
    return "edge_case"

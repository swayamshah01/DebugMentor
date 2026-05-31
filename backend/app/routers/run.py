"""Lightweight execution endpoint for practice runs.

`POST /api/run` executes code without creating a submission record or
touching learning-profile state.

Behavior:
- For curated problems, Run checks only visible tests.
- For free-form execution, Run still behaves like a direct execution tool.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.engines.executor import run_code as engine_run_code
from app.models.problem import Problem
from app.models.testcase import TestCase
from app.models.user import User
from app.services.problem_evaluator import (
    build_python_runner,
    evaluate_problem_submission,
    extract_python_function_name,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class RunRequest(BaseModel):
    code: str
    language: str
    problem_id: int | None = None
    test_case_id: int | None = None
    test_input: str | None = None


class RunResponse(BaseModel):
    success: bool
    output: str
    exec_time: str
    language: str
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    dominant_failure_type: str | None = None
    test_results: list[dict] = Field(default_factory=list)


@router.post(
    "/run",
    response_model=RunResponse,
    summary="Execute code and return practice feedback",
    description=(
        "Runs the submitted code. Curated problems are checked against visible "
        "tests only, while Submit performs the official visible + hidden grading."
    ),
)
def run_code(
    payload: RunRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RunResponse:
    """POST /api/run"""
    del current_user  # authenticated access still matters; the value is unused below

    lang = payload.language.lower()
    logger.info("Running code (%d chars) for language: %s", len(payload.code), lang)

    if not payload.code or not payload.code.strip():
        raise HTTPException(status_code=400, detail="Write some code before running it.")

    if payload.problem_id is not None:
        problem = db.query(Problem).filter(
            Problem.id == payload.problem_id,
            Problem.is_active.is_(True),
        ).first()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        if payload.test_case_id is not None:
            selected_visible = db.query(TestCase).filter(
                TestCase.id == payload.test_case_id,
                TestCase.problem_id == problem.id,
                TestCase.is_hidden.is_(False),
            ).first()
            if not selected_visible:
                raise HTTPException(status_code=404, detail="Visible test case not found")

        raw_results, failure_report, _ = evaluate_problem_submission(
            problem=problem,
            code=payload.code,
            language=lang,
            db=db,
            include_hidden=False,
        )

        total = failure_report.get("total", len(raw_results))
        passed = failure_report.get("passed", 0)
        failed = failure_report.get("failed", max(total - passed, 0))
        success = not failure_report.get("has_failures", False)
        first_failure = next(
            (item for item in failure_report.get("test_results", []) if item.get("status") != "PASSED"),
            None,
        )

        average_ms = 0
        if raw_results:
            average_ms = int(sum(item.get("execution_time_ms", 0) for item in raw_results) / len(raw_results))

        if success:
            output = f"Passed all visible tests ({passed}/{total})."
        elif first_failure:
            expected = first_failure.get("expected_output", "?")
            actual = first_failure.get("actual_output") or first_failure.get("error_message") or "(no output)"
            label = first_failure.get("label") or "Visible test"
            output = (
                f"{label} failed. Expected {expected}, got {actual}. "
                f"{failure_report.get('failure_summary', '')}"
            ).strip()
        else:
            output = failure_report.get("failure_summary") or "Visible tests failed."

        return RunResponse(
            success=success,
            output=output,
            exec_time=f"{average_ms / 1000:.3f}s",
            language=lang,
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            dominant_failure_type=failure_report.get("dominant_failure_type"),
            test_results=failure_report.get("test_results", []),
        )

    run_input = payload.test_input or ""

    try:
        exec_code = payload.code
        exec_input = run_input

        if lang == "python":
            function_name = extract_python_function_name(payload.code)
            if function_name and run_input:
                exec_code = build_python_runner(payload.code, function_name, run_input)
                exec_input = ""

        result = engine_run_code(user_code=exec_code, language=lang, test_input=exec_input)

        success = result.get("exit_code") == 0 and not result.get("timed_out")

        if result.get("timed_out"):
            output = result.get("error_message") or "Execution timed out."
        elif not success:
            output = result.get("error_message") or "Process exited with a non-zero status."
        else:
            output = result.get("actual_output") or "(program produced no output)"

        elapsed = f"{result.get('execution_time_ms', 0) / 1000:.3f}s"

        return RunResponse(
            success=success,
            output=output,
            exec_time=elapsed,
            language=lang,
            total_tests=1,
            passed_tests=1 if success else 0,
            failed_tests=0 if success else 1,
            dominant_failure_type=None if success else "RUNTIME_ERROR",
            test_results=[],
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("run_code error: %s", exc, exc_info=True)
        return RunResponse(
            success=False,
            output=f"Internal execution error: {exc}",
            exec_time="-",
            language=lang,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            dominant_failure_type="INTERNAL_ERROR",
            test_results=[],
        )

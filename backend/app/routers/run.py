"""Lightweight execution endpoint for curated practice problems.

`POST /api/run` executes code without creating a submission record or
touching profile state. It is intended for quick checks against sample,
visible, or custom input while the user is practicing a curated problem.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.engines.executor import run_code as engine_run_code
from app.models.problem import Problem
from app.models.testcase import TestCase
from app.models.user import User
from app.services.problem_evaluator import build_python_runner, extract_python_function_name

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


@router.post(
    "/run",
    response_model=RunResponse,
    summary="Execute code and return output",
    description=(
        "Runs the submitted code directly. "
        "Python is executed via subprocess. "
        "Other languages require a compiler — coming in Phase 2."
    ),
)
def run_code(
    payload: RunRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RunResponse:
    """POST /api/run"""
    lang = payload.language.lower()
    logger.info("Running code (%d chars) for language: %s", len(payload.code), lang)

    run_input = payload.test_input or ""

    if payload.problem_id is not None:
        problem = db.query(Problem).filter(
            Problem.id == payload.problem_id,
            Problem.is_active.is_(True),
        ).first()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        if payload.test_case_id is not None:
            test_case = db.query(TestCase).filter(
                TestCase.id == payload.test_case_id,
                TestCase.problem_id == problem.id,
                TestCase.is_hidden.is_(False),
            ).first()
            if not test_case:
                raise HTTPException(status_code=404, detail="Visible test case not found")
            run_input = test_case.input or ""
        elif not run_input:
            first_visible = db.query(TestCase).filter(
                TestCase.problem_id == problem.id,
                TestCase.is_hidden.is_(False),
            ).order_by(TestCase.order_index).first()
            if first_visible:
                run_input = first_visible.input or ""

    try:
        exec_code = payload.code
        exec_input = run_input

        # Curated Python practice problems usually use function-style starter code.
        # Wrap the function call during Run so users get a meaningful quick check.
        if payload.problem_id is not None and lang == "python":
            function_name = extract_python_function_name(payload.code)
            if function_name:
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
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("run_code error: %s", exc, exc_info=True)
        return RunResponse(
            success=False,
            output=f"Internal execution error: {exc}",
            exec_time="—",
            language=lang,
        )

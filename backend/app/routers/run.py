"""Practice execution: run one selected visible test case."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.problem import Problem
from app.models.user import User
from app.schemas.grading import GradeResponse, RunRequest
from app.services.grading import grade_problem, public_report


router = APIRouter()


@router.post(
    "/run",
    response_model=GradeResponse,
    summary="Run one visible test case",
)
def run_visible_test(
    payload: RunRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> GradeResponse:
    problem = db.query(Problem).filter(
        Problem.id == payload.problem_id,
        Problem.is_active.is_(True),
    ).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")

    try:
        report = grade_problem(
            db,
            problem,
            payload.code,
            payload.language,
            include_hidden=False,
            test_case_id=payload.test_case_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    safe_report = public_report(report)
    return GradeResponse(
        success=safe_report["success"],
        mode="run",
        summary=safe_report["summary"],
        total_tests=safe_report["total"],
        passed_tests=safe_report["passed"],
        failed_tests=safe_report["failed"],
        dominant_failure_type=safe_report["dominant_failure_type"],
        test_results=safe_report["test_results"],
    )

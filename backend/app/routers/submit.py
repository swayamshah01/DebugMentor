"""Official submission grading against visible and hidden test cases."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models.mistake import Mistake
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.schemas.grading import SubmissionResponse, SubmitRequest
from app.services.grading import grade_problem, public_report


logger = logging.getLogger(__name__)
router = APIRouter()


MISTAKE_TYPES = {
    "COMPILE_ERROR": "compile_error",
    "RUNTIME_ERROR": "runtime_error",
    "TIMEOUT": "timeout",
    "EMPTY_OUTPUT": "empty_output",
    "WRONG_OUTPUT": "wrong_output",
}


@router.post(
    "/submit",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Grade an official submission",
)
def submit_solution(
    payload: SubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
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
            include_hidden=True,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    submission = Submission(
        user_id=current_user.id,
        problem_id=problem.id,
        code=payload.code,
        language=payload.language,
        status="passed" if report["success"] else "failed",
        hint_level=0,
        feedback=None,
        ast_findings=None,
        test_results=report,
        hints=None,
    )
    db.add(submission)

    try:
        db.flush()
        mistake_type = MISTAKE_TYPES.get(report.get("dominant_failure_type"))
        if mistake_type:
            db.add(
                Mistake(
                    user_id=current_user.id,
                    submission_id=submission.id,
                    mistake_type=mistake_type,
                    description=report["summary"],
                )
            )
        db.commit()
        db.refresh(submission)
    except Exception as exc:
        db.rollback()
        logger.exception("Could not save submission")
        raise HTTPException(status_code=500, detail="Could not save the submission.") from exc

    safe_report = public_report(report)
    return SubmissionResponse(
        submission_id=submission.id,
        problem_id=problem.id,
        status=submission.status,
        submitted_at=submission.submitted_at,
        hints_available=bool(not report["success"] and settings.GEMINI_API_KEY),
        success=safe_report["success"],
        mode="submit",
        summary=safe_report["summary"],
        total_tests=safe_report["total"],
        passed_tests=safe_report["passed"],
        failed_tests=safe_report["failed"],
        dominant_failure_type=safe_report["dominant_failure_type"],
        test_results=safe_report["test_results"],
    )

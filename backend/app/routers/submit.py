import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.engines.executor import run_code
from app.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/submit",
    response_model=SubmissionResponse,
    status_code=201,
    summary="Submit code for analysis",
    description=(
        "Accepts a code submission, runs real analysis (Python: ast + subprocess; "
        "other languages: pattern detection), persists to the database, "
        "and returns a structured response including progressive hints and test case results."
    ),
)
def submit_code(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    """
    POST /api/submit

    Flow
    ----
    1. Validate incoming payload (Pydantic)
    2. Run analyze_code() — real Python execution or pattern detection
    3. Persist submission to DB (code, language, status, first-hint as feedback)
    4. Return SubmissionResponse with the full analysis_result attached
    """
    logger.info(
        "Submission: user_id=%s lang=%s code_len=%d",
        current_user.id, payload.language, len(payload.code),
    )

    try:
        # Run execution engine
        result = run_code(
            user_code=payload.code,
            language=payload.language,
            test_input=payload.test_input or ""
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Execution error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Execution service error.")

    # ── Step 2: Persist to DB ─────────────────────────────────────────────────
    # ── Step 2: Persist to DB ─────────────────────────────────────────────────
    db_status = "passed" if result.get("exit_code") == 0 else "failed"

    try:
        submission = Submission(
            user_id    = current_user.id,
            code       = payload.code,
            language   = payload.language,
            status     = db_status,
            hint_level = 0,
            feedback   = result.get("error_message") or "",
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        logger.info("Submission saved: id=%s status=%s", submission.id, submission.status)

    except Exception as exc:
        db.rollback()
        logger.error("DB write failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save submission: {exc}",
        )

    # ── Step 3: Build response — attach analysis_result ───────────────────────
    # Pydantic can't read analysis_result from the ORM object (it's not a column),
    # so we build the response dict manually.
    response_data = {
        "id":              submission.id,
        "user_id":         submission.user_id,
        "code":            submission.code,
        "language":        submission.language,
        "submitted_at":    submission.submitted_at,
        "hint_level":      submission.hint_level,
        "status":          submission.status,
        "feedback":        submission.feedback,
        "exit_code":       result.get("exit_code"),
        "actual_output":   result.get("actual_output"),
        "error_message":   result.get("error_message"),
        "execution_time_ms": result.get("execution_time_ms"),
        "timed_out":       result.get("timed_out"),
        "analysis_result": None, # Kept null as we replaced analyzer
    }

    return SubmissionResponse(**response_data)

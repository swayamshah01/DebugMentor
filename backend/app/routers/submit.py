import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.analyzer import analyze_code   # ← real analyzer

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
        payload.user_id, payload.language, len(payload.code),
    )

    # ── Step 1: Analyse ───────────────────────────────────────────────────────
    try:
        analysis = analyze_code(code=payload.code, language=payload.language)
    except Exception as exc:
        logger.error("Analyzer error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis service error.")

    # ── Step 2: Persist to DB ─────────────────────────────────────────────────
    first_hint_text = (
        analysis["hints"][0]["text"] if analysis.get("hints") else ""
    )

    try:
        submission = Submission(
            user_id    = payload.user_id,
            code       = payload.code,
            language   = payload.language,
            status     = analysis["status"],
            hint_level = 0,
            feedback   = first_hint_text,
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
        "analysis_result": analysis,   # full structured data for frontend
    }

    return SubmissionResponse(**response_data)

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.dummy_analyzer import analyze_code

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/submit",
    response_model=SubmissionResponse,
    status_code=201,
    summary="Submit code for analysis",
    description=(
        "Accepts a code submission, runs analysis (Phase 1: dummy), "
        "persists the result to the database, and returns a structured response "
        "containing the hint and status."
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
    1. Validate the incoming payload (handled by Pydantic automatically)
    2. Call analyze_code() from the analyzer service
    3. Persist the submission + analysis result to the DB
    4. Return a SubmissionResponse

    Error handling
    --------------
    - DB failures → HTTP 500 with descriptive message
    - Pydantic validation failures → HTTP 422 (handled by FastAPI automatically)
    """
    logger.info(
        "New submission: user_id=%s language=%s code_length=%d",
        payload.user_id, payload.language, len(payload.code)
    )

    # ── Step 1: Run analysis ───────────────────────────────────────────────────
    try:
        analysis = analyze_code(code=payload.code, language=payload.language)
    except Exception as exc:
        logger.error("Analyzer failed: %s", exc)
        raise HTTPException(status_code=500, detail="Analysis service unavailable.")

    # ── Step 2: Persist to DB ─────────────────────────────────────────────────
    try:
        submission = Submission(
            user_id    = payload.user_id,
            code       = payload.code,
            language   = payload.language,
            status     = analysis["status"],
            hint_level = analysis["hint_level"],
            feedback   = analysis["feedback"],
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        logger.info("Submission saved: id=%s", submission.id)
        return submission

    except Exception as exc:
        db.rollback()
        logger.error("DB write failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save submission: {str(exc)}",
        )

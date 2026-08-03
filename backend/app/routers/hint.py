"""Reveal generated hints progressively for a failed submission."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.submission import Submission
from app.models.user import User
from app.schemas.grading import HintRequest, HintResponse
from app.services.hints import HintGenerationError, generate_hint_bundle


router = APIRouter()


@router.post("/hint", response_model=HintResponse, summary="Reveal the next personalized hint")
def reveal_hint(
    payload: HintRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HintResponse:
    submission = db.query(Submission).filter(Submission.id == payload.submission_id).with_for_update().first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only request hints for your own submission.")
    if submission.status == "passed":
        raise HTTPException(status_code=409, detail="This submission already passes every test.")
    if not submission.problem:
        raise HTTPException(status_code=409, detail="This submission is not linked to a practice problem.")

    if not isinstance(submission.hints, dict) or not submission.hints.get("hints"):
        try:
            submission.hints = generate_hint_bundle(submission, submission.problem)
            submission.feedback = submission.hints.get("diagnosis")
        except HintGenerationError as exc:
            db.rollback()
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    next_level = min((submission.hint_level or 0) + 1, 3)
    submission.hint_level = next_level

    if next_level < 3:
        generated_hint = submission.hints["hints"][next_level - 1]
        title = generated_hint["title"]
        content = generated_hint["content"]
        focus = generated_hint["focus"]
        solution_code = None
    else:
        solution = submission.hints["solution"]
        title = solution["title"]
        content = solution["explanation"]
        focus = "solution"
        solution_code = solution["code"]

    db.commit()
    return HintResponse(
        submission_id=submission.id,
        level=next_level,
        title=title,
        content=content,
        focus=focus,
        is_solution=next_level == 3,
        solution_code=solution_code,
        levels_remaining=3 - next_level,
    )

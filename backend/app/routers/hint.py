from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.submission import Submission
from app.models.mistake import Mistake
from app.engines.llm_layer import redis_client

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/hint", summary="Reveal next progressive hint")
def reveal_hint(
    submission_id: int = Body(...),
    user_id: int = Body(None),
    db: Session = Depends(get_db)
):
    """
    POST /api/hint
    Increments the hint level in Redis and returns the specific hint payload.
    Logs usage into the Phase 4 Mistake table.
    """
    # 1. Look up submission
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    hints_data = submission.hints or {}
        
    # 2. Get current hint level from Redis
    raw_user_id = user_id if user_id else "anon"
    redis_key = f"hint_level:{raw_user_id}:{submission_id}"
    
    current_level = 0
    if redis_client:
        try:
            val = redis_client.get(redis_key)
            if val is not None:
                current_level = int(val)
        except Exception as e:
            logger.warning("Redis read error on /hint: %s", e)
            
    # 3. Increment level
    new_level = current_level + 1
    if new_level > 3:
        new_level = 3
        
    # 4. Write back to Redis
    if redis_client:
        try:
            redis_client.setex(redis_key, 604800, str(new_level)) # 7 days TTL
        except Exception as e:
            logger.warning("Redis write error on /hint: %s", e)
            
    # 5. Extract hint payload
    hint_text = hints_data.get(f"hint_{new_level}", "No hint available.")
    
    # 6. Database updates
    if new_level == 3 and submission.hint_level < 3:
        submission.hint_level = 3
        db.commit()
        
    # Log to Mistakes table for Phase 4
    if new_level > current_level and user_id:
        error_category = "unknown_error"
        if submission.test_results and isinstance(submission.test_results, dict):
            error_category = submission.test_results.get("error_category", "unknown_error")
            
        mistake = Mistake(
            user_id=user_id,
            submission_id=submission_id,
            mistake_type=error_category,
            description=hint_text
        )
        db.add(mistake)
        db.commit()
        
    return {
        "level": new_level,
        "hint": hint_text,
        "is_solution": new_level == 3,
        "levels_remaining": 3 - new_level
    }

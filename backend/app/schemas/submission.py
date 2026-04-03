from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class SubmissionCreate(BaseModel):
    """
    Payload the client sends when submitting code for analysis.
    """
    code: str
    language: str
    user_id: int


class SubmissionResponse(BaseModel):
    """
    Data returned to the client after a submission is processed.
    """
    model_config = ConfigDict(from_attributes=True)

    id:           int
    user_id:      int
    code:         str
    language:     str
    submitted_at: datetime
    hint_level:   int
    status:       str
    feedback:     Optional[str] = None

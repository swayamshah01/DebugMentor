from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any


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

    analysis_result contains the full structured analysis:
      - status, bug_summary, error_line, execution_output
      - hints:      list of {level, title, icon, text}
      - test_cases: list of {id, input, expected, actual, passed}
    """
    model_config = ConfigDict(from_attributes=True)

    id:              int
    user_id:         int
    code:            str
    language:        str
    submitted_at:    datetime
    hint_level:      int
    status:          str
    feedback:        Optional[str] = None
    analysis_result: Optional[Any] = None   # full structured result for the frontend

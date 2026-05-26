from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any, List, Dict


class SubmissionCreate(BaseModel):
    """
    Payload the client sends when submitting code for analysis.
    """
    code: str
    language: str
    user_id: Optional[int] = None
    test_input: Optional[str] = ""
    problem_id: Optional[int] = None
    problem_desc: Optional[str] = None


class SubmissionResponse(BaseModel):
    """
    Data returned to the client after a submission is processed (Phase 2).

    Includes:
      - Core submission fields
      - ast_issues: list of AST analysis findings
      - failure_report: structured FailureReport from the failure detector
      - hints: null (reserved for Phase 3)
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

    # Phase 2 structured results
    ast_issues:      Optional[List[Dict[str, Any]]] = None
    failure_report:  Optional[Dict[str, Any]] = None
    hints:           Optional[Any] = None
    problem_id:      Optional[int] = None

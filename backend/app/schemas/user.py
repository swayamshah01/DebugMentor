from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """
    Payload the client sends when registering a new user.
    """
    username: str
    email: EmailStr


class UserResponse(BaseModel):
    """
    Data returned to the client after user creation or lookup.
    """
    model_config = ConfigDict(from_attributes=True)

    id:           int
    username:     str
    email:        str
    created_at:   datetime
    error_pattern: Optional[str] = None   # Phase 2: populated by learning-profile service

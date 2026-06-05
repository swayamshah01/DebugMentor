import re
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserCreate(BaseModel):
    """
    Payload the client sends when registering a new user.
    """
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 3 or len(cleaned) > 24:
            raise ValueError("Username must be between 3 and 24 characters.")
        if not re.fullmatch(r"[A-Za-z0-9_]+", cleaned):
            raise ValueError("Username can contain only letters, numbers, and underscores.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        checks = [
            re.search(r"[A-Z]", value),
            re.search(r"[a-z]", value),
            re.search(r"\d", value),
            re.search(r"[^A-Za-z0-9]", value),
        ]
        if not all(checks):
            raise ValueError(
                "Password must include at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character."
            )
        return value


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

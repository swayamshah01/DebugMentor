from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    Represents a student using DebugMentor.

    Columns
    -------
    id              : auto-increment primary key
    username        : unique display name (max 50 chars)
    email           : unique email address (max 120 chars)
    created_at      : UTC timestamp of account creation
    error_pattern   : JSON stored as Text — recurring mistake history
                      (populated in Phase 2 by the learning-profile service)
    """

    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(50),  unique=True, nullable=False, index=True)
    email         = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    error_pattern = Column(Text, nullable=True)   # JSON blob — Phase 2

    # ── Relationships ──────────────────────────────────────────────────────────
    submissions = relationship("Submission", back_populates="user",
                               cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"

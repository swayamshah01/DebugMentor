from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class Mistake(Base):
    """
    Records every hint revealed by a student for the learning profile (Phase 4).

    Columns
    -------
    id            : auto-increment primary key
    user_id       : FK → users.id
    submission_id : FK → submissions.id
    mistake_type  : mapped from error_category
    description   : the text of the revealed hint
    created_at    : UTC timestamp
    """

    __tablename__ = "mistakes"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=True, index=True)
    mistake_type  = Column(String(100), nullable=False, index=True)
    description   = Column(Text, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # ── Relationships ──────────────────────────────────────────────────────────
    user = relationship("User")
    submission = relationship("Submission")

    def __repr__(self) -> str:
        return f"<Mistake id={self.id} type={self.mistake_type} user_id={self.user_id}>"

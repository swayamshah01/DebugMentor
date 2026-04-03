from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Submission(Base):
    """
    Records every code submission made by a student.

    Columns
    -------
    id           : auto-increment primary key
    user_id      : FK → users.id
    code         : the raw submitted source code
    language     : e.g. "python", "cpp", "java", "javascript"
    submitted_at : UTC timestamp of submission
    hint_level   : 0 = first hint, 1 = more specific, 2 = full solution
    status       : "pending" | "analyzed" | "error"
    feedback     : the AI-generated hint text (Phase 1: dummy value)
    """

    __tablename__ = "submissions"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    code         = Column(Text,        nullable=False)
    language     = Column(String(30),  nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    hint_level   = Column(Integer,     default=0,         nullable=False)
    status       = Column(String(20),  default="pending", nullable=False)
    feedback     = Column(Text,        nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────────
    user = relationship("User", back_populates="submissions")

    def __repr__(self) -> str:
        return (
            f"<Submission id={self.id} user_id={self.user_id} "
            f"language={self.language!r} status={self.status!r}>"
        )

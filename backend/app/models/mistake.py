from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Mistake(Base):
    """A classified failure associated with a graded submission."""

    __tablename__ = "mistakes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    submission_id = Column(
        Integer,
        ForeignKey("submissions.id"),
        nullable=True,
        index=True,
    )
    mistake_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    submission = relationship("Submission")

    def __repr__(self) -> str:
        return f"<Mistake id={self.id} type={self.mistake_type} user_id={self.user_id}>"

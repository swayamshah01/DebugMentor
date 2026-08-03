from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Submission(Base):
    """A final submission graded against visible and hidden test cases."""

    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=True, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(30), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    hint_level = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    test_results = Column(JSON, nullable=True)
    hints = Column(JSON, nullable=True)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem")

    def __repr__(self) -> str:
        return (
            f"<Submission id={self.id} user_id={self.user_id} "
            f"language={self.language!r} status={self.status!r}>"
        )

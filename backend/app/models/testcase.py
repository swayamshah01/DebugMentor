from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TestCase(Base):
    """A visible or hidden stdin/stdout test case for a problem."""

    __tablename__ = "test_cases"
    __test__ = False

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    label = Column(String(200), nullable=False)
    input = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    problem = relationship("Problem", back_populates="test_cases")

    def __repr__(self) -> str:
        return f"<TestCase id={self.id} problem_id={self.problem_id} label={self.label!r}>"

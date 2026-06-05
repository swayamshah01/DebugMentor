from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TestCase(Base):
    """
    Represents a single test case for a DSA problem.

    Columns
    -------
    id              : auto-increment primary key
    problem_id      : FK → problems.id
    label           : human-readable label (e.g., "Example 1", "Edge Case: Empty Array")
    input           : serialized input (e.g., JSON string, array string, etc.)
    expected_output : expected output as string
    is_hidden       : whether this test case is visible to student before submission
    order_index     : display order
    created_at      : UTC timestamp
    """

    __tablename__ = "test_cases"
    __test__ = False

    id              = Column(Integer, primary_key=True, index=True)
    problem_id      = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    label           = Column(String(200), nullable=False)
    input           = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden       = Column(Boolean, default=False, nullable=False)
    order_index     = Column(Integer, default=0, nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    # ── Relationships ──────────────────────────────────────────────────────────
    problem = relationship("Problem", back_populates="test_cases")

    def __repr__(self) -> str:
        return f"<TestCase id={self.id} problem_id={self.problem_id} label={self.label!r}>"

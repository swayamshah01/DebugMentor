from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Problem(Base):
    """A database-backed practice problem and its language templates."""

    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    pattern_id = Column(Integer, ForeignKey("patterns.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    difficulty = Column(String(20), nullable=False)
    short_description = Column(Text, nullable=True)
    statement = Column(Text, nullable=False)
    input_format = Column(Text, nullable=True)
    output_format = Column(Text, nullable=True)
    constraints_text = Column(Text, nullable=True)
    examples_json = Column(JSON, nullable=True)
    starter_code_json = Column(JSON, nullable=True)
    reference_solution_json = Column(JSON, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    pattern = relationship("Pattern", back_populates="problems")
    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Problem id={self.id} title={self.title!r}>"

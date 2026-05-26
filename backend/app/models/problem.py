from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Problem(Base):
    """
    Represents a curated DSA interview question.

    Columns
    -------
    id                      : auto-increment primary key
    pattern_id              : FK → patterns.id
    title                   : human-readable problem title (e.g., "Two Sum")
    slug                    : URL-friendly identifier
    difficulty              : "easy" | "medium" | "hard"
    short_description       : one-liner summary
    statement               : full problem statement (HTML or Markdown)
    constraints_text        : constraints section (e.g., "1 <= n <= 10^5")
    examples_json           : JSON list of {input, output, explanation} examples
    starter_code_json       : JSON mapping {language: code} for starter templates
    reference_solution_json : JSON mapping {language: code} — optional, internal use
    order_index             : display order within pattern
    is_active               : whether problem is currently available
    created_at              : UTC timestamp
    """

    __tablename__ = "problems"

    id                      = Column(Integer, primary_key=True, index=True)
    pattern_id              = Column(Integer, ForeignKey("patterns.id"), nullable=False, index=True)
    title                   = Column(String(200), nullable=False)
    slug                    = Column(String(200), unique=True, nullable=False, index=True)
    difficulty              = Column(String(20), nullable=False)  # "easy", "medium", "hard"
    short_description       = Column(Text, nullable=True)
    statement               = Column(Text, nullable=False)
    constraints_text        = Column(Text, nullable=True)
    examples_json           = Column(JSON, nullable=True)  # [{input, output, explanation}, ...]
    starter_code_json       = Column(JSON, nullable=True)  # {python: "...", javascript: "...", ...}
    reference_solution_json = Column(JSON, nullable=True)  # {python: "...", ...}
    order_index             = Column(Integer, default=0, nullable=False)
    is_active               = Column(Boolean, default=True, nullable=False)
    created_at              = Column(DateTime(timezone=True), server_default=func.now())

    # ── Relationships ──────────────────────────────────────────────────────────
    pattern = relationship("Pattern", back_populates="problems")
    test_cases = relationship("TestCase", back_populates="problem",
                             cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Problem id={self.id} title={self.title!r}>"

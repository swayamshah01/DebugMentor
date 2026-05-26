from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Pattern(Base):
    """
    Represents a DSA pattern category (e.g., Arrays, Sliding Window, Binary Search).

    Columns
    -------
    id              : auto-increment primary key
    name            : human-readable pattern name (e.g., "Two Pointers")
    slug            : URL-friendly identifier (e.g., "two-pointers")
    description     : brief explanation of the pattern
    icon_name       : optional icon identifier for UI rendering
    order_index     : display order in UI (ascending)
    created_at      : UTC timestamp
    """

    __tablename__ = "patterns"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(100), unique=True, nullable=False, index=True)
    slug            = Column(String(100), unique=True, nullable=False, index=True)
    description     = Column(Text, nullable=True)
    icon_name       = Column(String(50), nullable=True)
    order_index     = Column(Integer, default=0, nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    # ── Relationships ──────────────────────────────────────────────────────────
    problems = relationship("Problem", back_populates="pattern",
                           cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Pattern id={self.id} name={self.name!r}>"

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Pattern(Base):
    """A DSA pattern used to organize practice problems."""

    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon_name = Column(String(50), nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    problems = relationship(
        "Problem",
        back_populates="pattern",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Pattern id={self.id} name={self.name!r}>"

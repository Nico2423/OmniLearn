from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base, TimestampMixin


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    subsection_id = Column(Integer, ForeignKey("subsections.id"), unique=True)
    content = Column(Text)
    multimedia_urls = Column(ARRAY(String), nullable=True)

    subsection = relationship("Subsection", back_populates="lesson")
    reasoning_traces = relationship("ReasoningTrace", back_populates="lesson", cascade="all, delete-orphan")


class ReasoningTrace(Base, TimestampMixin):
    __tablename__ = "reasoning_traces"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="reasoning_traces")

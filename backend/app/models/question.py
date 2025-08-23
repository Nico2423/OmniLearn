from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    text = Column(Text)
    difficulty = Column(String)  # "easy", "medium", "hard"
    correct_answer = Column(Text)

    section = relationship("Section", back_populates="questions")

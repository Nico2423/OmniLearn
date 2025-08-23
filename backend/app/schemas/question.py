from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class HATEOASLink(BaseModel):
    href: str
    rel: str
    method: str


class QuestionBase(BaseModel):
    text: str
    difficulty: str  # "easy", "medium", "hard"
    correct_answer: str


class QuestionCreate(BaseModel):
    section_id: int
    section_title: str
    difficulty: Optional[str] = "medium"  # Default to medium difficulty


class QuestionResponse(QuestionBase):
    id: int
    section_id: int
    links: Optional[List[HATEOASLink]] = None


class AnswerSubmit(BaseModel):
    question_id: int
    answer: str


class AnswerFeedback(BaseModel):
    is_correct: bool
    feedback: str
    correct_answer: Optional[str] = None  # Only provided if is_correct is False

from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List

from app.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    AnswerSubmit,
    AnswerFeedback,
)
from app.services.question import QuestionService

router = APIRouter()


@router.post("/", response_model=List[QuestionResponse])
async def create_questions(
    data: QuestionCreate,
    service: QuestionService = Depends(),
) -> Any:
    """
    Generate practice questions for a section.
    """
    try:
        return await service.generate_questions(
            data.section_id, data.section_title, data.difficulty
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/section/{section_id}", response_model=List[QuestionResponse])
async def get_questions_by_section(
    section_id: int,
    difficulty: str = None,
    service: QuestionService = Depends(),
) -> Any:
    """
    Get questions for a section, optionally filtered by difficulty.
    """
    questions = await service.get_questions_by_section(section_id, difficulty)
    return questions


@router.post("/evaluate", response_model=AnswerFeedback)
async def evaluate_answer(
    data: AnswerSubmit,
    service: QuestionService = Depends(),
) -> Any:
    """
    Evaluate a student's answer to a question.
    """
    try:
        return await service.evaluate_answer(data.question_id, data.answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

from app.schemas.knowledge_tree import KnowledgeTreeResponse


class CourseVisibility(str, Enum):
    PRIVATE = "PRIVATE"
    ORGANIZATION = "ORGANIZATION"
    PUBLIC = "PUBLIC"


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    topic: str
    visibility: CourseVisibility = CourseVisibility.PRIVATE


class CourseCreate(CourseBase):
    organization_id: Optional[int] = None


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[CourseVisibility] = None
    is_active: Optional[bool] = None


class CourseResponse(CourseBase):
    id: int
    is_active: bool
    created_by_id: int
    organization_id: Optional[int] = None
    knowledge_tree_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    knowledge_tree: Optional[KnowledgeTreeResponse] = None
    enrollment_count: int = 0
    is_enrolled: bool = False

    class Config:
        from_attributes = True


class CourseEnrollmentCreate(BaseModel):
    course_id: int


class CourseEnrollmentResponse(BaseModel):
    id: int
    course_id: int
    user_id: int
    is_active: bool
    completed_subsections: List[int] = []
    current_subsection_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserProgressRecordCreate(BaseModel):
    subsection_id: int
    score: Optional[int] = None
    completed: bool = False


class UserProgressRecordResponse(BaseModel):
    id: int
    enrollment_id: int
    subsection_id: int
    score: Optional[int] = None
    attempts: int
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
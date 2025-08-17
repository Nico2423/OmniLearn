from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for OAuth users


class UserOAuthCreate(BaseModel):
    email: EmailStr
    name: str
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserProgressUpdate(BaseModel):
    subsection_id: int
    completed: bool
    score: Optional[float] = None


class UserProgressResponse(BaseModel):
    user_id: int
    completed_subsections: List[int]
    scores: Dict[str, float]  # subsection_id -> score
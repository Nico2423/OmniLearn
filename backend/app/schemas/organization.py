from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationMember(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class OrganizationResponse(OrganizationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    members: List[OrganizationMember] = []

    class Config:
        from_attributes = True


class OrganizationInviteCreate(BaseModel):
    email: EmailStr
    role: str = "member"


class OrganizationInviteResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    organization_id: int
    invited_by_id: int
    token: str
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
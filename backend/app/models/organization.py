from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin


# Association table for organization members
organization_members = Table(
    'organization_members',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role', String, default='member'),  # 'admin' or 'member'
    Column('joined_at', DateTime(timezone=True), server_default=func.now())
)


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    members = relationship(
        "User", 
        secondary=organization_members, 
        back_populates="organizations"
    )
    courses = relationship("Course", back_populates="organization", cascade="all, delete-orphan")


class OrganizationInvite(Base, TimestampMixin):
    __tablename__ = "organization_invites"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    email = Column(String, index=True, nullable=False)
    role = Column(String, default='member')  # 'admin' or 'member'
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    invited_by = relationship("User", foreign_keys=[invited_by_id])
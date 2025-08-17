from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, ARRAY, JSON, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    
    # OAuth fields
    google_id = Column(String, unique=True, nullable=True, index=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    progress = relationship("UserProgress", back_populates="user", uselist=False, cascade="all, delete-orphan")
    organizations = relationship(
        "Organization", 
        secondary="organization_members", 
        back_populates="members"
    )
    created_courses = relationship("Course", back_populates="created_by", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="user", cascade="all, delete-orphan")


class UserProgress(Base, TimestampMixin):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    completed_subsections = Column(ARRAY(Integer), default=[])
    scores = Column(JSON, default={})  # subsection_id -> score

    user = relationship("User", back_populates="progress")
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin


class CourseVisibility(enum.Enum):
    PRIVATE = "PRIVATE"  # Only creator can access
    ORGANIZATION = "ORGANIZATION"  # All organization members can access
    PUBLIC = "PUBLIC"  # Anyone can access (future feature)


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String, index=True, nullable=False)  # The learning topic
    visibility = Column(SQLEnum(CourseVisibility), default=CourseVisibility.PRIVATE)
    is_active = Column(Boolean, default=True)
    
    # Ownership and organization
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Link to knowledge tree (one-to-one relationship)
    knowledge_tree_id = Column(Integer, ForeignKey("knowledge_trees.id"), unique=True, nullable=True)
    
    # Relationships
    created_by = relationship("User", back_populates="created_courses")
    organization = relationship("Organization", back_populates="courses")
    knowledge_tree = relationship("KnowledgeTree", back_populates="course", uselist=False)
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")


class CourseEnrollment(Base, TimestampMixin):
    __tablename__ = "course_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Progress tracking
    completed_subsections = Column(String, default="[]")  # JSON array of subsection IDs
    current_subsection_id = Column(Integer, ForeignKey("subsections.id"), nullable=True)
    
    # Relationships
    course = relationship("Course", back_populates="enrollments")
    user = relationship("User", back_populates="enrollments")
    current_subsection = relationship("Subsection")
    progress_records = relationship("UserProgressRecord", back_populates="enrollment", cascade="all, delete-orphan")


class UserProgressRecord(Base, TimestampMixin):
    __tablename__ = "user_progress_records"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("course_enrollments.id"), nullable=False)
    subsection_id = Column(Integer, ForeignKey("subsections.id"), nullable=False)
    score = Column(Integer, nullable=True)  # Score out of 100
    attempts = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    
    # Relationships
    enrollment = relationship("CourseEnrollment", back_populates="progress_records")
    subsection = relationship("Subsection")
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import json

from app.models.course import Course, CourseEnrollment, UserProgressRecord, CourseVisibility
from app.models.organization import organization_members
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate, CourseEnrollmentCreate, UserProgressRecordCreate


def create_course(db: Session, course_data: CourseCreate, user_id: int) -> Course:
    """Create a new course"""
    course = Course(
        title=course_data.title,
        description=course_data.description,
        topic=course_data.topic,
        visibility=course_data.visibility,
        created_by_id=user_id,
        organization_id=course_data.organization_id
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def get_course_by_id(db: Session, course_id: int, user_id: Optional[int] = None) -> Optional[Course]:
    """Get course by ID with access control"""
    course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
    
    if not course:
        return None
    
    # Check access permissions
    if user_id and not can_access_course(db, course, user_id):
        return None
        
    return course


def can_access_course(db: Session, course: Course, user_id: int) -> bool:
    """Check if user can access the course"""
    # Creator can always access
    if course.created_by_id == user_id:
        return True
    
    # Private courses only accessible by creator
    if course.visibility == CourseVisibility.PRIVATE:
        return False
    
    # Organization courses accessible by organization members
    if course.visibility == CourseVisibility.ORGANIZATION and course.organization_id:
        member_exists = db.query(organization_members).filter(
            and_(
                organization_members.c.organization_id == course.organization_id,
                organization_members.c.user_id == user_id
            )
        ).first()
        return member_exists is not None
    
    # Public courses accessible by anyone (future feature)
    if course.visibility == CourseVisibility.PUBLIC:
        return True
    
    return False


def get_user_courses(db: Session, user_id: int, organization_id: Optional[int] = None) -> List[Course]:
    """Get courses accessible by user"""
    query = db.query(Course).filter(Course.is_active == True)
    
    if organization_id:
        # Get organization courses where user is a member
        query = query.filter(
            and_(
                Course.organization_id == organization_id,
                Course.visibility == CourseVisibility.ORGANIZATION
            )
        ).join(organization_members, Course.organization_id == organization_members.c.organization_id).filter(
            organization_members.c.user_id == user_id
        )
    else:
        # Get all accessible courses
        query = query.filter(
            or_(
                Course.created_by_id == user_id,  # Own courses
                and_(  # Organization courses where user is member
                    Course.visibility == CourseVisibility.ORGANIZATION,
                    Course.organization_id.in_(
                        db.query(organization_members.c.organization_id).filter(
                            organization_members.c.user_id == user_id
                        )
                    )
                )
            )
        )
    
    return query.all()


def update_course(db: Session, course_id: int, course_update: CourseUpdate, user_id: int) -> Optional[Course]:
    """Update course (only by creator or org admin)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course or not can_modify_course(db, course, user_id):
        return None
    
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course


def can_modify_course(db: Session, course: Course, user_id: int) -> bool:
    """Check if user can modify the course"""
    # Creator can always modify
    if course.created_by_id == user_id:
        return True
    
    # Organization admin can modify organization courses
    if course.organization_id:
        admin_exists = db.query(organization_members).filter(
            and_(
                organization_members.c.organization_id == course.organization_id,
                organization_members.c.user_id == user_id,
                organization_members.c.role == 'admin'
            )
        ).first()
        return admin_exists is not None
    
    return False


def enroll_user_in_course(db: Session, course_id: int, user_id: int) -> Optional[CourseEnrollment]:
    """Enroll user in course"""
    # Check if already enrolled
    existing = db.query(CourseEnrollment).filter(
        and_(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id == user_id,
            CourseEnrollment.is_active == True
        )
    ).first()
    
    if existing:
        return existing
    
    # Check course access
    course = get_course_by_id(db, course_id, user_id)
    if not course:
        return None
    
    enrollment = CourseEnrollment(
        course_id=course_id,
        user_id=user_id
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def get_user_enrollment(db: Session, course_id: int, user_id: int) -> Optional[CourseEnrollment]:
    """Get user's enrollment in course"""
    return db.query(CourseEnrollment).filter(
        and_(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id == user_id,
            CourseEnrollment.is_active == True
        )
    ).first()


def update_progress(
    db: Session, 
    enrollment_id: int, 
    progress_data: UserProgressRecordCreate
) -> Optional[UserProgressRecord]:
    """Update user progress for a subsection"""
    # Get or create progress record
    progress = db.query(UserProgressRecord).filter(
        and_(
            UserProgressRecord.enrollment_id == enrollment_id,
            UserProgressRecord.subsection_id == progress_data.subsection_id
        )
    ).first()
    
    if not progress:
        progress = UserProgressRecord(
            enrollment_id=enrollment_id,
            subsection_id=progress_data.subsection_id
        )
        db.add(progress)
    
    # Update progress
    progress.attempts += 1
    if progress_data.score is not None:
        progress.score = max(progress.score or 0, progress_data.score)
    progress.completed = progress_data.completed
    
    # Update enrollment's completed subsections
    if progress_data.completed:
        enrollment = db.query(CourseEnrollment).filter(
            CourseEnrollment.id == enrollment_id
        ).first()
        if enrollment:
            completed = json.loads(enrollment.completed_subsections or "[]")
            if progress_data.subsection_id not in completed:
                completed.append(progress_data.subsection_id)
                enrollment.completed_subsections = json.dumps(completed)
    
    db.commit()
    db.refresh(progress)
    return progress
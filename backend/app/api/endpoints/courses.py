from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.endpoints.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.course import (
    create_course, get_course_by_id, get_user_courses, update_course,
    enroll_user_in_course, get_user_enrollment, update_progress
)
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse, CourseDetailResponse,
    CourseEnrollmentResponse, UserProgressRecordCreate, UserProgressRecordResponse
)

router = APIRouter()


@router.post("/", response_model=CourseResponse)
def create_new_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new course"""
    # Validate organization access if specified
    if course_data.organization_id:
        from app.services.organization import is_organization_member
        if not is_organization_member(db, course_data.organization_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of the specified organization"
            )
    
    course = create_course(db, course_data, current_user.id)
    return course


@router.get("/", response_model=List[CourseResponse])
def get_my_courses(
    organization_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get courses accessible by current user"""
    return get_user_courses(db, current_user.id, organization_id)


@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course(
    course_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get course details"""
    user_id = current_user.id if current_user else None
    course = get_course_by_id(db, course_id, user_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or access denied"
        )
    
    # Check if user is enrolled
    is_enrolled = False
    if current_user:
        enrollment = get_user_enrollment(db, course_id, current_user.id)
        is_enrolled = enrollment is not None
    
    # Get enrollment count
    enrollment_count = len(course.enrollments)
    
    response_data = CourseDetailResponse.from_orm(course)
    response_data.enrollment_count = enrollment_count
    response_data.is_enrolled = is_enrolled
    
    return response_data


@router.put("/{course_id}", response_model=CourseResponse)
def update_course_endpoint(
    course_id: int,
    course_update: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update course (creator or org admin only)"""
    course = update_course(db, course_id, course_update, current_user.id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course"
        )
    return course


@router.post("/{course_id}/enroll", response_model=CourseEnrollmentResponse)
def enroll_in_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll in a course"""
    enrollment = enroll_user_in_course(db, course_id, current_user.id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot enroll in this course"
        )
    
    # Convert completed_subsections from JSON string to list
    import json
    response_data = CourseEnrollmentResponse.from_orm(enrollment)
    response_data.completed_subsections = json.loads(enrollment.completed_subsections or "[]")
    
    return response_data


@router.get("/{course_id}/enrollment", response_model=CourseEnrollmentResponse)
def get_my_enrollment(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's enrollment in course"""
    enrollment = get_user_enrollment(db, course_id, current_user.id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in this course"
        )
    
    # Convert completed_subsections from JSON string to list
    import json
    response_data = CourseEnrollmentResponse.from_orm(enrollment)
    response_data.completed_subsections = json.loads(enrollment.completed_subsections or "[]")
    
    return response_data


@router.post("/{course_id}/progress", response_model=UserProgressRecordResponse)
def update_course_progress(
    course_id: int,
    progress_data: UserProgressRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress for a subsection"""
    # Get user's enrollment
    enrollment = get_user_enrollment(db, course_id, current_user.id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in this course"
        )
    
    progress = update_progress(db, enrollment.id, progress_data)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update progress"
        )
    
    return progress


@router.get("/{course_id}/progress", response_model=List[UserProgressRecordResponse])
def get_course_progress(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress for all subsections in course"""
    enrollment = get_user_enrollment(db, course_id, current_user.id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in this course"
        )
    
    return enrollment.progress_records
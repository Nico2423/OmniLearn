from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.endpoints.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.course import Course
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
    
    # Manually construct response to avoid serialization issues
    response_data = CourseDetailResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        topic=course.topic,
        visibility=course.visibility,
        is_active=course.is_active,
        created_by_id=course.created_by_id,
        organization_id=course.organization_id,
        knowledge_tree_id=course.knowledge_tree_id,
        created_at=course.created_at,
        updated_at=course.updated_at,
        knowledge_tree=None,  # TODO: Serialize knowledge tree if needed
        enrollment_count=enrollment_count,
        is_enrolled=is_enrolled
    )
    
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
    
    # Manually construct response to handle JSON string conversion
    import json
    response_data = CourseEnrollmentResponse(
        id=enrollment.id,
        course_id=enrollment.course_id,
        user_id=enrollment.user_id,
        is_active=enrollment.is_active,
        completed_subsections=json.loads(enrollment.completed_subsections or "[]"),
        current_subsection_id=enrollment.current_subsection_id,
        created_at=enrollment.created_at
    )
    
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
    
    # Manually construct response to handle JSON string conversion
    import json
    response_data = CourseEnrollmentResponse(
        id=enrollment.id,
        course_id=enrollment.course_id,
        user_id=enrollment.user_id,
        is_active=enrollment.is_active,
        completed_subsections=json.loads(enrollment.completed_subsections or "[]"),
        current_subsection_id=enrollment.current_subsection_id,
        created_at=enrollment.created_at
    )
    
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


@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a course (creator only)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Only creator can delete
    if course.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this course"
        )
    
    # Soft delete by setting is_active to False
    course.is_active = False
    db.commit()
    
    return {"message": "Course deleted successfully"}


@router.put("/{course_id}/knowledge-tree")
def link_knowledge_tree_to_course(
    course_id: int,
    knowledge_tree_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Link a knowledge tree to a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Only creator can link knowledge tree
    if course.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this course"
        )
    
    course.knowledge_tree_id = knowledge_tree_id
    db.commit()
    db.refresh(course)
    
    return course
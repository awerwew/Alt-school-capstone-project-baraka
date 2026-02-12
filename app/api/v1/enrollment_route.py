from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.schemas.enrollment_schema import EnrollmentResponse, EnrollmentCreate
from app.api.deps import get_db,get_current_active_admin, get_current_active_student
from app.models.user_model import User
from app.services.enrollment_service import enrollment_service


router = APIRouter()


@router.post(
    "/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED
)
def enroll_in_course(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
):
    return enrollment_service.enroll_student(
        db=db, 
        student=current_user, 
        enrollment_data=enrollment
    )


@router.get("/", response_model=List[EnrollmentResponse])
def view_all_enrollment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return enrollment_service.get_all_enrollments(db=db)


@router.get(
    "/{course_id}/enrollments",
    status_code=status.HTTP_200_OK
)
def get_course_enrollments(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return enrollment_service.get_course_enrollments(db=db, course_id=course_id)



@router.delete("/{course_id}", status_code=status.HTTP_200_OK)
def deregister_student(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
):
    return enrollment_service.deregister_student(
        db=db,
        student=current_user,
        course_id=course_id
    )


@router.delete("/{student_id}/{course_id}", status_code=status.HTTP_200_OK)
def remove_student_from_enrollment(
    student_id: UUID,
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return enrollment_service.remove_student(
        db=db,
        student_id=student_id,
        course_id=course_id
    )
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.schemas.course_schema import CourseCreate, CourseResponse, CourseUpdate
from app.api.deps import get_db,get_current_active_admin
from app.models.user_model import User
from app.services.course_service import course_service


router = APIRouter()


@router.get("/", response_model=List[CourseResponse])
def view_all_courses(db: Session = Depends(get_db)):
    return course_service.get_all_courses(db)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: UUID, db: Session = Depends(get_db)):
    return course_service.get_course_by_id(db, course_id)



@router.post(
    "/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return course_service.create_course(db, course)


@router.patch(
    "/{course_id}",
    response_model=CourseResponse
)
def update_course(
    course_id: UUID,
    course: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return course_service.update_course(db, course_id, course)


@router.patch("/{course_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return course_service.deactivate_course(db, course_id)



@router.patch("/{course_id}/activate", status_code=status.HTTP_200_OK)
def activate_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return course_service.activate_course(db, course_id)




@router.delete("/{course_id}")
def delete_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return course_service.delete_course(db, course_id)
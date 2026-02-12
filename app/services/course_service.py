from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from typing import List
from app.models.course_model import Course 
from app.schemas.course_schema import CourseCreate, CourseUpdate


class CourseService:

    @staticmethod
    def get_course_by_id(db: Session, course_id: UUID):
        course = db.query(Course).filter(Course.id == course_id).first()

        if not course:
            raise HTTPException(
                status_code=404,
                detail="Course not found!"
            )

        return course
    

    @staticmethod
    def get_all_courses(db: Session) -> List[Course]:
        return db.query(Course).all()
    


    @staticmethod
    def create_course(db: Session, course: CourseCreate) -> Course:
        # Check for duplicate course code
        existing = db.query(Course).filter(Course.code == course.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course with this code already exists"
            )

        new_course = Course(
            title=course.title,
            code=course.code,
            capacity=course.capacity
        )

        db.add(new_course)
        db.commit()
        db.refresh(new_course)

        return new_course
    

    @staticmethod
    def update_course(
        db: Session,
        course_id: UUID,
        course_data: CourseUpdate
    ) -> Course:

        db_course = db.query(Course).filter(Course.id == course_id).first()

        if not db_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # If code is being updated, check for duplicates
        if course_data.code and course_data.code != db_course.code:
            existing = db.query(Course).filter(
                Course.code == course_data.code
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course with this code already exists"
                )

        # Update only provided fields (PATCH behavior)
        update_data = course_data.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_course, key, value)

        db.commit()
        db.refresh(db_course)

        return db_course
    

    @staticmethod
    def deactivate_course(db: Session, course_id: UUID) -> dict:
        course = db.query(Course).filter(Course.id == course_id).first()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        if not course.is_active:
            return {
                "message": "Course is already inactive",
                "course_id": course.id
            }

        course.is_active = False
        db.commit()

        return {
            "message": "Course deactivated successfully",
            "course_id": course.id
        }
    

    @staticmethod
    def activate_course(db: Session, course_id: UUID) -> dict:
        course = db.query(Course).filter(Course.id == course_id).first()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        if course.is_active:
            return {
                "message": "Course is already active",
                "course_id": course.id
            }

        course.is_active = True
        db.commit()

        return {
            "message": "Course activated successfully",
            "course_id": course.id
        }
    

    @staticmethod
    def delete_course(db: Session, course_id: UUID) -> dict:
        db_course = db.query(Course).filter(Course.id == course_id).first()

        if not db_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found!"
            )

        db.delete(db_course)
        db.commit()

        return {"message": "Course deleted successfully"}
    


course_service = CourseService()





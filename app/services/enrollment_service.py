from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from typing import List, Dict
from app.models.enrollment_model import Enrollment
from app.schemas.enrollment_schema import EnrollmentCreate
from app.models.user_model import User
from app.models.course_model import Course




class EnrollmentService:


    @staticmethod
    def enroll_student(db: Session, student: User, enrollment_data: EnrollmentCreate) -> Enrollment:
        # 1️⃣ Check if course exists
        course = db.query(Course).filter(Course.id == enrollment_data.course_id).first()
        if not course or not course.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found or inactive"
            )

        # 2️⃣ Check course capacity
        enrolled_count = db.query(Enrollment).filter(Enrollment.course_id == course.id).count()
        if enrolled_count >= course.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course capacity full"
            )

        # 3️⃣ Check if student already enrolled
        existing = db.query(Enrollment).filter(
            Enrollment.course_id == course.id,
            Enrollment.user_id == student.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already enrolled in this course"
            )

        # 4️⃣ Create enrollment
        new_enrollment = Enrollment(
            user_id=student.id,
            course_id=course.id
        )
        db.add(new_enrollment)
        db.commit()
        db.refresh(new_enrollment)

        return new_enrollment
    


    @staticmethod
    def get_all_enrollments(db: Session) -> List[Enrollment]:
        """
        Retrieve all enrollments from the database.
        """
        return db.query(Enrollment).all()
    


    @staticmethod
    def get_course_enrollments(db: Session, course_id: UUID) -> Dict:
        """
        Retrieve all enrollments for a specific course.
        """
        enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()

        if not enrollments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No enrollments found for this course"
            )

        return {
            "course_id": course_id,
            "total_students": len(enrollments),
            "enrollments": enrollments
        }
    


    @staticmethod
    def deregister_student(db: Session, student: User, course_id: UUID) -> dict:
        """
        Deregister a student from a course.
        """
        enrollment = db.query(Enrollment).filter(
            Enrollment.course_id == course_id,
            Enrollment.user_id == student.id
        ).first()

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )

        db.delete(enrollment)
        db.commit()

        return {
            "message": "You deregistered successfully",
            "course_id": course_id
        }
    


    @staticmethod
    def remove_student(db: Session, student_id: UUID, course_id: UUID) -> dict:
        """
        Remove a specific student from a specific course.
        """
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == student_id,
            Enrollment.course_id == course_id
        ).one_or_none()

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )

        db.delete(enrollment)
        db.commit()

        return {
            "message": "Student removed successfully",
            "user_id": student_id,
            "course_id": course_id
        }
    

enrollment_service = EnrollmentService()



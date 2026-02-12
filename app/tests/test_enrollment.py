from fastapi import HTTPException
from app.core.security import verify_pwd, get_pwd_hash
from .conftest import TestingSessionLocal, mock_student_user, mock_admin_user, mock_course
import jwt
import uuid
from app.main import app
from app.api.deps import get_current_active_admin, get_current_active_student
from app.core.config import settings 
from app.models.course_model import Course
from app.models.enrollment_model import Enrollment
from app.models.user_model import User



def test_enroll_in_course_success(client):
    db = TestingSessionLocal()
    
    student = mock_student_user()
    student.hashed_pwd = get_pwd_hash("studentpassword") 
    db.add(student)

    # Create active course with capacity
    course_id = uuid.uuid4()
    course = Course(
        id=course_id,
        title="Math",
        code="Basic Math",
        capacity=2,
        is_active=True
    )
    db.add(course)
    db.commit()

    # Override dependency to return student
    app.dependency_overrides[get_current_active_student] = lambda: student

    payload = {"course_id": str(course_id)}
    response = client.post("/enrollments", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == str(student.id)
    assert data["course_id"] == str(course_id)



def test_enroll_course_not_found(client):
    student = mock_student_user()
    student.hashed_pwd = get_pwd_hash("studentpassword") 
    app.dependency_overrides[get_current_active_student] = lambda: student

    payload = {"course_id": str(uuid.uuid4())}
    response = client.post("/enrollments", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()



def test_enroll_course_capacity_full(client):
    db = TestingSessionLocal()
    student1 = mock_student_user()
    student1.hashed_pwd = get_pwd_hash("studentpassword")
    db.add(student1)
    db.commit()

    # Course with capacity 1
    course_id = uuid.uuid4()
    course = Course(
        id=course_id,
        title="Physics",
        code="Physics 101",
        capacity=1,
        is_active=True
    )
    db.add(course)
    db.commit()

    # Enroll first student
    enrollment = Enrollment(user_id=student1.id, course_id=course.id)
    db.add(enrollment)
    db.commit()

    # New student trying to enroll
    student2 = User(id=uuid.uuid4(), name="Student 2", email="student2@example.com", role="student", is_active=True)
    student2.hashed_pwd = get_pwd_hash("studentpassword")
    db.add(student2)
    db.commit()

    app.dependency_overrides[get_current_active_student] = lambda: student2
    payload = {"course_id": str(course_id)}
    response = client.post("/enrollments", json=payload)

    assert response.status_code == 400
    assert "capacity" in response.json()["detail"].lower()


def test_enroll_course_already_enrolled(client):
    db = TestingSessionLocal()
    student = mock_student_user()
    student.hashed_pwd = get_pwd_hash("studentpassword")    
    db.add(student)

    course_id = uuid.uuid4()
    course = Course(id=course_id, title="Chemistry", code="Chemistry 101", capacity=2, is_active=True)
    db.add(course)
    db.commit()

    # Enroll student first
    enrollment = Enrollment(user_id=student.id, course_id=course.id)
    db.add(enrollment)
    db.commit()

    app.dependency_overrides[get_current_active_student] = lambda: student
    payload = {"course_id": str(course_id)}
    response = client.post("/enrollments", json=payload)

    assert response.status_code == 400
    assert "already enrolled" in response.json()["detail"].lower()


def test_view_all_enrollments_success(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    db.add(admin)

    # Create course
    course = Course(
        id=uuid.uuid4(),
        title="Math",
        code="Basic Math",
        capacity=10,
        is_active=True
    )
    db.add(course)

    # Create student
    student = mock_student_user()
    student.hashed_pwd = get_pwd_hash("studentpassword")      
    db.add(student)

    db.commit()

    # Create enrollment
    enrollment = Enrollment(
        user_id=student.id,
        course_id=course.id
    )
    db.add(enrollment)
    db.commit()

    # Override admin dependency
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.get("/enrollments")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["user_id"] == str(student.id)
    assert data[0]["course_id"] == str(course.id)



def test_view_all_enrollments_empty(client):
    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.get("/enrollments")
    assert response.status_code == 200
    assert response.json() == []



def test_view_all_enrollments_unauthorized(client):
    def non_authorized_user():
        raise HTTPException(status_code=403, detail="Not authorized to access this route")
    app.dependency_overrides[get_current_active_admin] = non_authorized_user

    response = client.get("/enrollments")
    assert response.status_code in [401, 403]



def test_get_course_enrollments_success(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    db.add(admin)

    # Create course
    course_id = uuid.uuid4()
    course = Course(
        id=course_id,
        title="Physics",
        code="Physics 101",
        capacity=10,
        is_active=True
    )
    db.add(course)

    # Create students
    student1 = mock_student_user()
    student1.hashed_pwd = get_pwd_hash("studentpassword") 
    student2 = mock_student_user()
    student2.hashed_pwd = get_pwd_hash("studentpassword") 
    db.add_all([student1, student2])
    db.commit()

    # Create enrollments
    enrollment1 = Enrollment(user_id=student1.id, course_id=course.id)
    enrollment2 = Enrollment(user_id=student2.id, course_id=course.id)
    db.add_all([enrollment1, enrollment2])
    db.commit()

    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.get(f"/enrollments/{course_id}/enrollments")
    assert response.status_code == 200

    data = response.json()
    assert data["course_id"] == str(course_id)
    assert data["total_students"] == 2
    assert len(data["enrollments"]) == 2



def test_get_course_enrollments_not_found(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    db.add(admin)

    # Create course but no enrollments
    course_id = uuid.uuid4()
    course = Course(
        id=course_id,
        title="Chemistry",
        code="Chemistry 101",
        capacity=10,
        is_active=True
    )
    db.add(course)
    db.commit()

    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.get(f"/enrollments/{course_id}/enrollments")
    assert response.status_code == 404
    assert "no enrollments" in response.json()["detail"].lower()


def test_get_course_enrollments_unauthorized(client):
    def unauthorized_user():
        raise HTTPException(status_code=403, detail="Not authorized to access this route")
    
    app.dependency_overrides[get_current_active_admin] = unauthorized_user

    random_id = uuid.uuid4()
    response = client.get(f"/enrollments/{random_id}/enrollments")

    assert response.status_code in [401, 403]



def test_deregister_student_success(client):
    db = TestingSessionLocal()

    # Create student
    student = mock_student_user()
    student.hashed_pwd = get_pwd_hash("studentpassword") 
    db.add(student)

    # Create course
    course = mock_course()
    db.add(course)
    db.commit()

    # Create enrollment
    enrollment = Enrollment(user_id=student.id, course_id=course.id)
    db.add(enrollment)
    db.commit()

    # Override dependency to simulate logged-in student
    app.dependency_overrides[get_current_active_student] = lambda: student

    # Perform deregistration
    response = client.delete(f"/enrollments/{course.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == str(course.id)
    assert "deregistered" in data["message"].lower()

    # Verify enrollment removed
    remaining = db.query(Enrollment).filter(
        Enrollment.user_id == student.id,
        Enrollment.course_id == course.id
    ).first()
    assert remaining is None



def test_deregister_student_not_found(client):
    # Student with no enrollment
    student = mock_student_user()
    student.hashed_pwd = get_pwd_hash("studentpassword") 
    app.dependency_overrides[get_current_active_student] = lambda: student

    # Random course ID
    response = client.delete(f"/enrollments/{uuid.uuid4()}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_remove_student_success(client):
    db = TestingSessionLocal()

    # Create admin
    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    db.add(admin)

    # Create student
    student = mock_student_user()
    student.hashed_pwd = get_pwd_hash("studentpassword") 
    db.add(student)

    # Create course
    course = mock_course()
    db.add(course)
    db.commit()

    # Create enrollment
    enrollment = Enrollment(user_id=student.id, course_id=course.id)
    db.add(enrollment)
    db.commit()

    # Override dependency to simulate logged-in admin
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    # Remove student from enrollment
    response = client.delete(f"/enrollments/{student.id}/{course.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(student.id)
    assert data["course_id"] == str(course.id)
    assert "removed successfully" in data["message"].lower()

    # Verify enrollment removed
    remaining = db.query(Enrollment).filter(
        Enrollment.user_id == student.id,
        Enrollment.course_id == course.id
    ).first()
    assert remaining is None



def test_remove_student_not_found(client):
    db = TestingSessionLocal()

    # Create admin
    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    db.add(admin)
    db.commit()

    # Override dependency
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    # Attempt to remove non-existent enrollment
    response = client.delete(f"/enrollments/{uuid.uuid4()}/{uuid.uuid4()}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
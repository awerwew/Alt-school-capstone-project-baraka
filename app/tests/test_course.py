from fastapi import HTTPException
from app.core.security import  get_pwd_hash
from .conftest import TestingSessionLocal, mock_admin_user
import uuid
from app.main import app
from app.api.deps import get_current_active_admin
from app.models.course_model import Course



def test_view_all_courses(client):
    db = TestingSessionLocal()

    course1 = Course(
        id=uuid.uuid4(),
        title="Math",
        code="Basic Math",
        capacity=30,
        is_active=True
    )

    course2 = Course(
        id=uuid.uuid4(),
        title="Physics",
        code="Basic Physics",
        capacity=25,
        is_active=True
    )

    db.add(course1)
    db.add(course2)
    db.commit()

    response = client.get("/courses")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "Math"
    assert data[1]["title"] == "Physics"


def test_view_all_courses_empty(client):
    response = client.get("/courses")

    assert response.status_code == 200
    assert response.json() == []


def test_get_course_success(client):
    db = TestingSessionLocal()

    course_id = uuid.uuid4()

    course = Course(
        id=course_id,
        title="Math",
        code="Basic Math",
        capacity=30,
        is_active=True
    )

    db.add(course)
    db.commit()

    response = client.get(f"/courses/{course_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(course_id)
    assert data["title"] == "Math"
    assert data["code"] == "Basic Math"


def test_create_course_success(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    db.add(admin)
    db.commit()

    app.dependency_overrides[get_current_active_admin] = lambda: admin

    payload = {
        "title": "Biology",
        "code": "Introduction to Biology",
        "capacity": 40,
        "is_active": True
    }

    response = client.post("/courses", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Biology"
    assert data["code"] == "Introduction to Biology"
    assert data["capacity"] == 40
    assert data["is_active"] is True

   

def test_create_course_unauthorized(client):
    # simulate non-admin    
    def non_admin_override():
        raise HTTPException(status_code=403, detail="You're not authorized to access this route")
    
    app.dependency_overrides[get_current_active_admin] = non_admin_override

    payload = {
        "title": "Chemistry",
        "code": "Basic Chemistry",
        "capacity": 30,
        "is_active": True
    }

    response = client.post("/courses", json=payload)
    # your dependency should raise 403 or 401 if not admin
    assert response.status_code in [403, 401]


def test_update_course_success(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    db.add(admin)

    # Create course to update
    course_id = uuid.uuid4()
    course = Course(
        id=course_id,
        title="Math",
        code="Basic Math",
        capacity=30,
        is_active=True
    )
    db.add(course)
    db.commit()

    app.dependency_overrides[get_current_active_admin] = lambda: admin

    payload = {
        "title": "Advanced Math",
        "code": "Updated Math Description",
        "capacity": 50,
        "is_active": True
    }

    response = client.patch(f"/courses/{course_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Advanced Math"
    assert data["code"] == "Updated Math Description"
    assert data["capacity"] == 50



def test_update_course_not_found(client):
    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    random_id = uuid.uuid4()
    payload = {
        "title": "Physics",
        "code": "Physics Updated",
        "capacity": 20,
        "is_active": True
    }

    response = client.patch(f"/courses/{random_id}", json=payload)
    # Assuming your service raises 404
    assert response.status_code == 404


def test_deactivate_course_success(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    db.add(admin)

    # Create active course
    course_id = uuid.uuid4()
    course = Course(
        id=course_id,
        title="Math",
        code="Basic Math",
        capacity=30,
        is_active=True
    )
    db.add(course)
    db.commit()

    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.patch(f"/courses/{course_id}/deactivate")
    assert response.status_code == 200
    data = response.json()
    assert "deactivated" in data.get("message", "").lower()


def test_deactivate_course_not_found(client):
    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    random_id = uuid.uuid4()
    response = client.patch(f"/courses/{random_id}/deactivate")
    # Assuming service raises 404
    assert response.status_code == 404



def test_activate_course_success(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    db.add(admin)

    # Create inactive course
    course_id = uuid.uuid4()
    course = Course(
        id=course_id,
        title="History",
        code="World History",
        capacity=40,
        is_active=False
    )
    db.add(course)
    db.commit()

    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.patch(f"/courses/{course_id}/activate")
    assert response.status_code == 200
    data = response.json()
    assert "activated" in data.get("message", "").lower()


def test_activate_course_not_found(client):
    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    random_id = uuid.uuid4()
    response = client.patch(f"/courses/{random_id}/activate")
    # Assuming service raises 404
    assert response.status_code == 404


def test_delete_course_success(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    db.add(admin)

    # Create course to delete
    course_id = uuid.uuid4()
    course = Course(
        id=course_id,
        title="Biology",
        code="Intro Biology",
        capacity=40,
        is_active=True
    )
    db.add(course)
    db.commit()

    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.delete(f"/courses/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert "deleted" in data.get("message", "").lower()


def test_delete_course_not_found(client):
    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    app.dependency_overrides['get_current_active_admin'] = lambda: admin

    random_id = uuid.uuid4()
    response = client.delete(f"/courses/{random_id}")
    # Assuming service raises 404
    assert response.status_code == 404




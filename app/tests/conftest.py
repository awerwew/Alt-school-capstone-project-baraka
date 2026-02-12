import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.api.deps import get_db
from app.models.user_model import User
from app.models.course_model import Course
from app.models.enrollment_model import Enrollment


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db():
    # Drop all tables and recreate them before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield



# Override DB dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


def mock_admin_user():
    return User(
        id=uuid.uuid4(),
        email="admin@example.com",
        name="Admin",
        role="admin",        
        is_active=True
    )


def mock_student_user():
    unique_email = f"student_{uuid.uuid4()}@example.com"
    return User(
        id=uuid.uuid4(),
        name="Student User",
        email=unique_email,
        role="student",
        is_active=True
    )

def mock_course(course_id=None):
    return Course(
        id=course_id or uuid.uuid4(),
        title="Math 101",
        code="MATH101",
        capacity=10,
        is_active=True
    )
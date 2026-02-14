from app.core.security import verify_pwd, get_pwd_hash
from .conftest import TestingSessionLocal, mock_admin_user
from app.models.user_model import User
import jwt
import uuid
from app.main import app
from app.api.deps import get_current_active_admin, get_current_user
from app.core.config import settings 




def test_register_success(client):
    response = client.post(
        "/api/v1/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "strongpassword",
            "role": "student"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "john@example.com"
    assert data["name"] == "John Doe"
    assert data["role"] == "student"
    assert "id" in data


def test_register_duplicate_email(client):
    # First registration
    client.post(
        "/api/v1/register",
        json={
            "name": "Jane",
            "email": "jane@example.com",
            "password": "password123",
            "role": "student"
        }
    )

    # Try again with same email
    response = client.post(
        "/api/v1/register",
        json={
            "name": "Jane2",
            "email": "jane@example.com",
            "password": "password456",
            "role": "student"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "User with email already exist"



def test_password_is_hashed(client):
    db = TestingSessionLocal()

    client.post(
        "/api/v1/register",
        json={
            "name": "Hash Test",
            "email": "hash@example.com",
            "password": "mypassword",
            "role": "student"
        }
    )             
        
           
    user = db.query(User).filter(User.email == "hash@example.com").first()

    assert user is not None
    assert user.hashed_pwd != "mypassword"
    assert verify_pwd("mypassword", user.hashed_pwd) is True


def test_register_invalid_email(client):
    response = client.post(
        "/api/v1/register",
        json={
            "name": "Invalid",
            "email": "not-an-email",
            "password": "123456",
            "role": "student"
        }
    )

    assert response.status_code == 422
    

        
def test_login_success(client):
    db = TestingSessionLocal()

    # Create test user
    hashed_password = get_pwd_hash("testpassword")
    user = User(
        name="Test User", 
        email="test@example.com",
        hashed_pwd=hashed_password,
        role="student",
        is_active=True
    )
    db.add(user)
    db.commit()

    # OAuth2PasswordRequestForm requires "username" and "password"
    response = client.post(
        "/api/v1/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"

    # Decode JWT to verify payload
    payload = jwt.decode(
        data["access_token"],
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == "test@example.com"
    assert payload["role"] == "student"

    
def test_login_invalid_password(client):
    db = TestingSessionLocal()

    hashed_password = get_pwd_hash("correctpassword")
    user = User(
        name="Wrong Pass User",
        email="wrongpass@example.com",
        hashed_pwd=hashed_password,
        role="student",
        is_active=True
    )
    db.add(user)
    db.commit()

    response = client.post(
        "/api/v1/token",
        data={"username": "wrongpass@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["detail"].lower() == "invalid credential"


def test_login_user_not_found(client):
    response = client.post(
        "/api/v1/token",
        data={"username": "nouser@example.com", "password": "any"}
    )
    assert response.status_code == 401
    assert response.json()["detail"].lower()  == "invalid credential"



def test_login_inactive_user(client):
    db = TestingSessionLocal()

    hashed_password = get_pwd_hash("password123")
    user = User(
        name ="inactive user",
        email="inactive@example.com",
        hashed_pwd=hashed_password,
        role="student",
        is_active=False
    )
    db.add(user)
    db.commit()

    
    response = client.post(
        "/api/v1/token",
        data={"username": "inactive@example.com", "password": "password123"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Inactive user"






def test_deactivate_user_success(client):
    db = TestingSessionLocal()

    # Create admin and target user
    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword") 
    target_user_id = uuid.uuid4()
    user = User(
        id=target_user_id,
        email="user@example.com",
        name="User",
        role="student",
        hashed_pwd=get_pwd_hash("userpassword"),
        is_active=True
    )
    db.add(admin)
    db.add(user)
    db.commit()

    # Override current_admin dependency
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.patch(f"/api/v1/{target_user_id}/deactivate")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User deactivated successfully"
    assert data["deactivated_user_id"] == str(target_user_id)
    assert data["performed_by_admin_id"] == str(admin.id)

    db.refresh(user)
    assert user.is_active is False


def test_admin_cannot_deactivate_self(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword")
    db.add(admin)
    db.commit()

    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.patch(f"/api/v1/{admin.id}/deactivate")
    assert response.status_code == 403
    assert response.json()["detail"] == "Admins cannot deactivate themselves"


def test_deactivate_user_not_found(client):
    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword")
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    random_id = uuid.uuid4()
    response = client.patch(f"/api/v1/{random_id}/deactivate")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_deactivate_user_already_inactive(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword")
    inactive_user_id = uuid.uuid4()
    user = User(
        id=inactive_user_id,
        email="inactive@example.com",
        name="Inactive User",
        role="student",
        hashed_pwd=get_pwd_hash("somepassword"), 
        is_active=False
    )
    db.add(admin)
    db.add(user)
    db.commit()

    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.patch(f"/api/v1/{inactive_user_id}/deactivate")
    assert response.status_code == 200
    assert response.json()["message"] == "User is already inactive"
    assert response.json()["user_id"] == str(inactive_user_id)


def test_activate_user_success(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword")
    target_user_id = uuid.uuid4()
    user = User(
        id=target_user_id,
        email="inactive@example.com",
        name="Inactive User",
        role="student",
        hashed_pwd=get_pwd_hash("somepassword"),
        is_active=False
    )
    db.add(admin)
    db.add(user)
    db.commit()

    # Override dependency
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.patch(f"/api/v1/{target_user_id}/activate")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User activated successfully"
    assert data["user_id"] == str(target_user_id)

    db.refresh(user)
    assert user.is_active is True



def test_activate_user_already_active(client):
    db = TestingSessionLocal()

    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword")
    active_user_id = uuid.uuid4()
    user = User(
        id=active_user_id,
        email="active@example.com",
        name="Active User",
        role="student",
        hashed_pwd=get_pwd_hash("somepassword"),
        is_active=True
    )
    db.add(admin)
    db.add(user)
    db.commit()

    app.dependency_overrides[get_current_active_admin] = lambda: admin

    response = client.patch(f"/api/v1/{active_user_id}/activate")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User is already active"
    assert data["user_id"] == str(active_user_id)


def test_activate_user_not_found(client):
    admin = mock_admin_user()
    admin.hashed_pwd = get_pwd_hash("adminpassword")
    app.dependency_overrides[get_current_active_admin] = lambda: admin

    random_id = uuid.uuid4()
    response = client.patch(f"/api/v1/{random_id}/activate")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

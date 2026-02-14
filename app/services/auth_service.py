from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.core.security import get_pwd_hash, verify_pwd, create_access_token
from fastapi.security import  OAuth2PasswordRequestForm
from app.core.config import settings
from datetime import timedelta



class AuthService:

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Register a new user.
        """

        # Firstly check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with email already exist"
            )

        # Hash password
        hashed_password = get_pwd_hash(user_data.password)

        # Create user
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            role=user_data.role,
            hashed_pwd=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
    


    @staticmethod
    def login(db: Session, form_data: OAuth2PasswordRequestForm) -> dict:
        """
        Authenticate user and return access token.
        """

        # Find user by email (username field contains email)
        user = db.query(User).filter(User.email == form_data.username).first()

        #  Validate credentials
        if not user or not verify_pwd(form_data.password, user.hashed_pwd):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credential"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.TOKEN_EXPIRES)

        access_token = create_access_token(
            data={
                "sub": user.email,
                "role": user.role
            },
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    
    

    @staticmethod
    def deactivate_user(
        db: Session,
        user_id: UUID,
        current_admin: User
    ) -> dict:
        """
        Deactivate a user account (Admin only).
        Prevents admin from deactivating themselves.
        """

        # Prevent admin from deactivating themselves
        if user_id == current_admin.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot deactivate themselves"
            )

        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # If already inactive
        if not user.is_active:
            return {
                "message": "User is already inactive",
                "user_id": user.id
            }

        # Deactivate user
        user.is_active = False
        db.commit()

        return {
            "message": "User deactivated successfully",
            "deactivated_user_id": user.id,
            "performed_by_admin_id": current_admin.id
        }
    


    @staticmethod
    def activate_user(db: Session, user_id: UUID) -> dict:
        """
        Activate a user account (Admin only).
        """

        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        #  If already active
        if user.is_active:
            return {
                "message": "User is already active",
                "user_id": user.id
            }

        # Activate user
        user.is_active = True
        db.commit()

        return {
            "message": "User activated successfully",
            "user_id": user.id
        }
    

auth_route = AuthService()  
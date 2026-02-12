from fastapi import APIRouter, Depends,  status
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.user_schema import UserResponse, UserCreate
from app.models.user_model import User
from app.api.deps import get_db,get_current_active_admin,get_current_active_student,get_current_user
from app.schemas.auth_schema import Token
from app.services.auth_service import auth_route



router = APIRouter()



@router.post("/register", status_code=201, response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return auth_route.register_user(db=db, user_data=user)

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return auth_route.login(db=db, form_data=form_data)



@router.patch("/{user_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user),
    current_user: User = Depends(get_current_active_admin)
):
    return auth_route.deactivate_user(
        db=db,
        user_id=user_id,
        current_admin=current_admin
    )


@router.patch("/{user_id}/activate", status_code=status.HTTP_200_OK)
def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return auth_route.activate_user(
        db=db,
        user_id=user_id
    )



# i didn't see the need to include the route bellow to the service route since the business logic is not overwhelming  
@router.get("/profile")
def profile(current_user: User = Depends(get_current_user)):
    return {"message": f"Profile of {current_user.name} ({current_user.role})"}


@router.get("/student/dashboard")
def student_dashboard (current_user: User = Depends(get_current_active_student)):
    return {"message": "Welcome Student"}


@router.get("/admin/dashboard")
def admin_dashboard (current_user: User = Depends(get_current_active_admin)):
    return {"message": "Welcome Admin"}
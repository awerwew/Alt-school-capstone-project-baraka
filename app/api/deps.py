from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from app.models.user_model import User, UserRole
from app.db.session import SessionLocal
from app.core.security import verify_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def get_current_user(
        token: str = Depends(oauth2_scheme), db:Session=Depends(get_db)
):
    token_data = verify_token(token)
    user = db.query(User).filter(User.email == token_data.email).first()    
    if user is None:
        raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="User does not exist",
                headers={"WWW-Authenticate": "Bearer"}
                )   
    return user
       
    

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Inactive user"                
                )   
    return current_user



def get_current_active_admin(
        current_user:User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="inactive Admin")
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="You're not authorized to access this route")
    return current_user


def get_current_active_student(
        current_user:User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="inactive Student")
    if current_user.role != UserRole.USER.value:
        raise HTTPException(status_code=403, detail="You're not authorized to access this route")
    return current_user



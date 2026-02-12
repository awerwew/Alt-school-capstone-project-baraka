from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from pydantic import EmailStr
import jwt
from passlib.context import CryptContext
from jwt import PyJWTError
from app.schemas.auth_schema import TokenData
from app.core.config import settings



pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm= settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        email: EmailStr = payload.get('sub')
        if email is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="couldn't verify credentials",
                headers={"WWW-Authenticate": "Bearer"}
                )
        return TokenData(email = email)
    except PyJWTError:
         raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="couldn't verify credentials",
                headers={"WWW-Authenticate": "Bearer"}
                )                    

 
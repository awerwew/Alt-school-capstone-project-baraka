from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from uuid import UUID

class User(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    password: str    
    role: Literal["student", "admin"]
    is_active: bool = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["student", "admin"]
    

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True
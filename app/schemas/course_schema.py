from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class Course(BaseModel):
    id: UUID
    title: str
    code: str
    capacity: int = Field(..., gt=0, le=300)  
    is_active: bool = True

class CourseCreate(BaseModel):
    title: str
    code: str
    capacity: int = Field(..., gt=0, le=300) 
     
    

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0, le=300)

class CourseResponse(BaseModel):
    id: UUID
    title: str
    code: str
    capacity: int
    is_active: bool = True

    class Config:
        from_attributes = True


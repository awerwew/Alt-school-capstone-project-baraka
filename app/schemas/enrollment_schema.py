from datetime import datetime
from pydantic import BaseModel
from uuid import UUID





class Enrollment(BaseModel):
    id: int
    user_id: UUID
    course_id: UUID
    created_at: datetime
    

class EnrollmentCreate(BaseModel):         
    course_id: UUID



class EnrollmentResponse(BaseModel):
    id: int
    user_id: UUID
    course_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
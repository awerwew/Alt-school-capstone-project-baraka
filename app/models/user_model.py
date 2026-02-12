import uuid
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

from enum import Enum

class UserRole(str,Enum):
    ADMIN = "admin"
    USER = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index = True, nullable= False)
    email = Column(String, unique = True, index = True, nullable = False)
    hashed_pwd = Column(String, nullable = False)
    role = Column(String, default=UserRole.USER.value, nullable= False)
    is_active = Column(Boolean, default=True)


   
 
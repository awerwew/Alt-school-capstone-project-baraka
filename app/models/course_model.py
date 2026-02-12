import uuid
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base



class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    code = Column(String, unique=True, nullable=False, index= True)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

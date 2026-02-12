from fastapi import FastAPI
from app.api.v1 import auth_route
from app.api.v1 import course_route
from app.api.v1 import enrollment_route
from app.core.config import settings


app = FastAPI(title="Enrolloment Application")


app.include_router(auth_route.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(course_route.router, prefix="/courses", tags=["Courses"])
app.include_router(enrollment_route.router, prefix="/enrollments", tags=["Enrolloments"])


@app.get("/")
def root_path():
    return {"message": "My Enrollment Application"}
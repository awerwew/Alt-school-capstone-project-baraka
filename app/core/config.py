from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Enrollment_App"
    API_V1_STR: str = "/api/v1"
  
    # DB
    DATABASE_URL: str

    # Security
    TOKEN_EXPIRES: int = 30
    ALGORITHM: str = ""
    SECRET_KEY: str = ""

   
    class Config:
        env_file = ".env"
        env_file_ending = "utf-8"


settings = Settings()
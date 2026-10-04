import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LMS - Leave Management System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "lms_secret_key_super_secure_jwt_token_2026_antigravity"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database: Default to PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/LMS")

    class Config:
        case_sensitive = True

settings = Settings()

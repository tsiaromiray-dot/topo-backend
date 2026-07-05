import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./topo.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "topo-app-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    REMINDER_HOURS: int = 48

    class Config:
        env_file = ".env"

settings = Settings()

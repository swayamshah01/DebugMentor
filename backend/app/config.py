import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Application settings loaded from .env file.
    Phase 2: migrate to pydantic-settings BaseSettings for validation.
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    def __post_init__(self):
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in .env")


settings = Settings()

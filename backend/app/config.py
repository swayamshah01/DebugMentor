import os

from dotenv import load_dotenv


load_dotenv()


def _as_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_list(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    def __init__(self) -> None:
        self.DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
        if not self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL must be configured in backend/.env")

        self.SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
        self.DEBUG = _as_bool("DEBUG", False)
        self.SQL_ECHO = _as_bool("SQL_ECHO", False)
        self.AUTO_SEED_CURATED_CONTENT = _as_bool("AUTO_SEED_CURATED_CONTENT", True)
        self.CORS_ORIGINS = _as_list("CORS_ORIGINS", "*")

        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

        self.EXECUTION_TIMEOUT_SECONDS = int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "5"))
        self.COMPILE_TIMEOUT_SECONDS = int(os.getenv("COMPILE_TIMEOUT_SECONDS", "10"))

        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.HINT_TIMEOUT_SECONDS = int(os.getenv("HINT_TIMEOUT_SECONDS", "30"))


settings = Settings()

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if o.strip()
    ]
    MAX_INTERESTS: int = 3


settings = Settings()


def validate_settings() -> None:
    missing = []
    if not settings.GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not settings.GOOGLE_PLACES_API_KEY:
        missing.append("GOOGLE_PLACES_API_KEY")
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

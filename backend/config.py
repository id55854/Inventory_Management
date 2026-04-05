"""Environment config for RetailPulse backend."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(_BACKEND_DIR / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{_BACKEND_DIR / 'retailpulse.db'}"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"  # env: GEMINI_MODEL (Section 6.2)


settings = Settings()

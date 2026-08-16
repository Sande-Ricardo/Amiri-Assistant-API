from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core App Settings
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    CORS_ALLOWED_ORIGINS: str = "*"

    # Database Settings
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/amiri"
    DB_SSL_CA_PATH: str | None = None

    # LLM Settings
    LLM_PROVIDER: Literal["gemini", "groq"] = "gemini"
    GOOGLE_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GEMINI_MODEL_NAME: str = "gemini-1.5-flash"
    GROQ_MODEL_NAME: str = "llama-3.1-8b-instant"

    # Execution / Timeout Settings
    MAX_LLM_RETRIES: int = 2
    REQUEST_TIMEOUT_SECONDS: int = 120


settings = Settings()

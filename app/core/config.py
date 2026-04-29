from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Groq
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"

    # Research pipeline
    max_papers: int = Field(default=5, ge=1, le=20)
    max_critic_iterations: int = Field(default=3, ge=1, le=5)

    # App
    log_level: str = "INFO"
    environment: str = "development"
    app_name: str = "Autonomous Research Assistant"
    app_version: str = "1.0.0"


settings = Settings()
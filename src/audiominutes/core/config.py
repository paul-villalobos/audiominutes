"""Configuration settings for AudioMinutes."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    app_name: str = "AudioMinutes"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database settings
    database_url: str = Field(default="postgresql://localhost:5432/audiominutes", env="DATABASE_URL")
    
    # External API settings
    assemblyai_api_key: str = Field(default="", env="ASSEMBLYAI_API_KEY")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    resend_api_key: str = Field(default="", env="RESEND_API_KEY")
    
    # File upload settings
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    allowed_audio_formats: list[str] = Field(
        default=["wav", "mp3", "m4a", "flac", "aac", "ogg"],
        env="ALLOWED_AUDIO_FORMATS"
    )
    
    # Email settings
    from_email: str = Field(default="noreply@audiominutes.com", env="FROM_EMAIL")
    from_name: str = Field(default="AudioMinutes", env="FROM_NAME")
    
    # CORS settings
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

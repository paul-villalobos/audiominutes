"""Configuration settings for AudioMinutes."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings - Simplified for MVP."""
    
    # App settings (fixed for MVP)
    app_name: str = "AudioMinutes"
    app_version: str = "0.1.0"
    debug: bool = False  # Fixed for MVP simplicity
    
    # Essential API keys only
    database_url: str = Field(env="DATABASE_URL")
    assemblyai_api_key: str = Field(env="ASSEMBLYAI_API_KEY")
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    resend_api_key: str = Field(env="RESEND_API_KEY")
    
    # Fixed settings for MVP (no env vars needed)
    max_file_size_mb: int = 100
    allowed_audio_formats: str = "wav,mp3,m4a"
    from_email: str = "noreply@audiominutes.com"
    from_name: str = "AudioMinutes"
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def allowed_audio_formats_list(self) -> list[str]:
        """Convert comma-separated string to list."""
        return [fmt.strip() for fmt in self.allowed_audio_formats.split(",")]
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """Convert comma-separated string to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()

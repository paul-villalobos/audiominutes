"""Configuration settings for VoxCliente."""

import logging
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings - Simplified for MVP."""
    
    # App settings (fixed for MVP)
    app_name: str = "VoxCliente"
    app_version: str = "0.1.0"
    debug: bool = False  # Disabled by default for security
    
    # Essential API keys only
    assemblyai_api_key: str = Field(env="ASSEMBLYAI_API_KEY")
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    resend_api_key: str = Field(env="RESEND_API_KEY")
    posthog_api_key: str = Field(env="POSTHOG_API_KEY")
    posthog_host: str = Field(default="https://app.posthog.com", env="POSTHOG_HOST")
    
    
    # Fixed settings for MVP (no env vars needed)
    max_file_size_mb: int = 500
    from_email: str = "actas@actas.voxcliente.com"
    from_name: str = "VoxCliente"
    reply_to_email: str = "hola@voxcliente.com"
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """Convert comma-separated string to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def should_log_apis(self) -> bool:
        """Determinar si debemos loggear respuestas de APIs."""
        return self.debug  # Solo en modo debug
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Ignorar variables de entorno extra
    }


# Global settings instance
try:
    settings = Settings()
    logger.info("Configuración cargada exitosamente")
    logger.info(f"Variables de entorno detectadas:")
    logger.info(f"- ASSEMBLYAI_API_KEY: {'✓' if settings.assemblyai_api_key else '✗'}")
    logger.info(f"- OPENAI_API_KEY: {'✓' if settings.openai_api_key else '✗'}")
    logger.info(f"- RESEND_API_KEY: {'✓' if settings.resend_api_key else '✗'}")
    logger.info(f"- POSTHOG_API_KEY: {'✓' if settings.posthog_api_key else '✗'}")
except Exception as e:
    logger.error(f"Error cargando configuración: {str(e)}", exc_info=True)
    raise

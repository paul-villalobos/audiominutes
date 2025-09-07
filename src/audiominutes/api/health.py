"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from audiominutes.core.config import settings


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    app_name: str
    version: str
    debug: bool


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug
    )


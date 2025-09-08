"""Health check endpoints - Simplified for MVP."""

from fastapi import APIRouter

from audiominutes.config import settings


router = APIRouter()


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }

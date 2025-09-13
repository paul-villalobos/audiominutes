"""Health check endpoints - Simplified for MVP."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from audiominutes.config import settings
from audiominutes.utils import validate_audio_file, validate_email, sanitize_filename


router = APIRouter()


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


@router.post("/validate-file")
async def validate_file(
    file: UploadFile = File(...),
    email: str = Form(...)
):
    """
    Endpoint simple para validar archivo de audio y email.
    Solo para testing - no procesa el archivo.
    """
    # Validar email
    is_email_valid, email_error = validate_email(email)
    if not is_email_valid:
        raise HTTPException(status_code=400, detail=email_error)
    
    # Validar archivo
    is_file_valid, file_error = validate_audio_file(file.filename, file.size)
    if not is_file_valid:
        raise HTTPException(status_code=400, detail=file_error)
    
    # Sanitizar nombre
    sanitized_name = sanitize_filename(file.filename)
    
    return {
        "status": "valid",
        "filename": file.filename,
        "sanitized_filename": sanitized_name,
        "size_bytes": file.size,
        "email": email,
        "message": "Archivo y email válidos"
    }

"""Health check endpoints - Simplified for MVP."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import tempfile
import os

from voxcliente.config import settings
from voxcliente.utils import validate_audio_file, validate_email, sanitize_filename
from voxcliente.services import assemblyai_service, openai_service, resend_email_service


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


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    email: str = Form(...)
):
    """
    Endpoint simple para transcribir audio con AssemblyAI.
    """
    # Validar email
    is_email_valid, email_error = validate_email(email)
    if not is_email_valid:
        raise HTTPException(status_code=400, detail=email_error)
    
    # Validar archivo
    is_file_valid, file_error = validate_audio_file(file.filename, file.size)
    if not is_file_valid:
        raise HTTPException(status_code=400, detail=file_error)
    
    try:
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Transcribir archivo directamente (AssemblyAI maneja el upload internamente)
        transcript = assemblyai_service.transcribe_file(temp_file_path)
        if not transcript:
            raise HTTPException(status_code=500, detail="Error en la transcripción")
        
        # Generar acta profesional usando OpenAI
        acta = openai_service.generate_acta(transcript)
        if not acta:
            raise HTTPException(status_code=500, detail="Error generando acta")
        
        # Enviar acta por email con transcripción adjunta
        email_sent = resend_email_service.send_acta_email(email, acta, file.filename, transcript)
        
        # Limpiar archivo temporal
        os.unlink(temp_file_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "email": email,
            "transcript": transcript,
            "acta": acta,
            "email_sent": email_sent,
            "message": "Transcripción completada y acta enviada por email" if email_sent else "Transcripción completada, pero error enviando email"
        }
        
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error procesando audio: {str(e)}")

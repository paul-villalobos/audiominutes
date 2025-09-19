"""Health check endpoints - Simplified for MVP."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from typing import Optional
import tempfile
import os
from datetime import datetime

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
    request: Request,
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
    
    # Tracking al inicio - form_submit
    posthog = request.app.state.posthog
    posthog.capture(
        distinct_id=email,
        event='form_submit',
        properties={
            'filename': file.filename,
            'file_size_mb': round(file.size / 1024 / 1024, 2),
            'timestamp': datetime.now().isoformat()
        }
    )
    
    try:
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Transcribir archivo directamente (AssemblyAI maneja el upload internamente)
        transcription_result = assemblyai_service.transcribe_file(temp_file_path)
        if not transcription_result:
            raise HTTPException(status_code=500, detail="Error en la transcripción")
        
        transcript = transcription_result['transcript']
        assemblyai_cost = transcription_result['assemblyai_cost']['cost_usd']
        duration_minutes = transcription_result['assemblyai_cost']['duration_minutes']
        
        # Generar acta profesional usando OpenAI
        acta_result = openai_service.generate_acta(transcript)
        if not acta_result:
            raise HTTPException(status_code=500, detail="Error generando acta")
        
        # Extraer acta y costos de OpenAI
        acta = {k: v for k, v in acta_result.items() if k not in ['openai_usage', 'openai_cost']}
        openai_cost = acta_result['openai_cost']['total_cost_usd']
        
        # Enviar acta por email con transcripción adjunta
        email_sent = resend_email_service.send_acta_email(email, acta, file.filename, transcript)
        
        # Calcular costo total real
        # AssemblyAI: costo real de la API
        # OpenAI: costo real de la API
        # Email: $0.0004 por email (Resend)
        email_cost = 0.0004
        total_cost = round(assemblyai_cost + openai_cost + email_cost, 6)
        
        # Tracking al final - acta_generated
        posthog.capture(
            distinct_id=email,
            event='acta_generated',
            properties={
                'filename': file.filename,
                'duration_minutes': duration_minutes,
                'file_size_mb': round(file.size / 1024 / 1024, 2),
                'cost_usd': total_cost,
                'cost_breakdown': {
                    'assemblyai_cost_usd': assemblyai_cost,
                    'openai_cost_usd': openai_cost,
                    'email_cost_usd': email_cost
                },
                'openai_usage': acta_result['openai_usage'],
                'assemblyai_usage': transcription_result['assemblyai_usage'],
                'email_sent': email_sent,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # Limpiar archivo temporal
        os.unlink(temp_file_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "email": email,
            "transcript": transcript,
            "acta": acta,
            "email_sent": email_sent,
            "duration_minutes": duration_minutes,
            "cost_usd": total_cost,
            "cost_breakdown": {
                "assemblyai_cost_usd": assemblyai_cost,
                "openai_cost_usd": openai_cost,
                "email_cost_usd": email_cost
            },
            "openai_usage": acta_result['openai_usage'],
            "assemblyai_usage": transcription_result['assemblyai_usage'],
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

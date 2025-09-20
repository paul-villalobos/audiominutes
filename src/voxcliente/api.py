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


def _validate_inputs(file: UploadFile, email: str) -> None:
    """Validar email y archivo de entrada."""
    # Validar email
    is_email_valid, email_error = validate_email(email)
    if not is_email_valid:
        raise HTTPException(status_code=400, detail=email_error)
    
    # Validar archivo
    is_file_valid, file_error = validate_audio_file(file.filename, file.size)
    if not is_file_valid:
        raise HTTPException(status_code=400, detail=file_error)


def _track_form_submit(posthog, email: str, filename: str, file_size: int) -> None:
    """Tracking inicial del formulario."""
    posthog.capture(
        distinct_id=email,
        event='form_submit',
        properties={
            'filename': filename,
            'file_size_mb': round(file_size / 1024 / 1024, 2),
            'timestamp': datetime.now().isoformat()
        }
    )


def _track_acta_generated(posthog, email: str, filename: str, file_size: int, 
                         duration_minutes: float, total_cost: float, 
                         cost_breakdown: dict, openai_usage: dict, 
                         assemblyai_usage: dict, email_sent: bool) -> None:
    """Tracking final de acta generada."""
    posthog.capture(
        distinct_id=email,
        event='acta_generated',
        properties={
            'filename': filename,
            'duration_minutes': duration_minutes,
            'file_size_mb': round(file_size / 1024 / 1024, 2),
            'cost_usd': total_cost,
            'cost_breakdown': cost_breakdown,
            'openai_usage': openai_usage,
            'assemblyai_usage': assemblyai_usage,
            'email_sent': email_sent,
            'timestamp': datetime.now().isoformat()
        }
    )


async def _save_temp_file(file: UploadFile) -> str:
    """Guardar archivo temporalmente."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
        content = await file.read()
        temp_file.write(content)
        return temp_file.name


def _cleanup_temp_file(file_path: str) -> None:
    """Limpiar archivo temporal."""
    if file_path:
        try:
            os.unlink(file_path)
        except:
            pass


def _process_audio_pipeline(temp_file_path: str, email: str, filename: str) -> dict:
    """Procesar pipeline completo de audio a acta."""
    # Transcribir archivo
    transcription_result = assemblyai_service.transcribe_file(temp_file_path)
    if not transcription_result:
        raise HTTPException(status_code=500, detail="Error en la transcripción")
    
    transcript = transcription_result['transcript']
    assemblyai_cost = transcription_result['assemblyai_cost']['cost_usd']
    duration_minutes = transcription_result['assemblyai_cost']['duration_minutes']
    
    # Generar acta profesional
    acta_result = openai_service.generate_acta(transcript)
    if not acta_result:
        raise HTTPException(status_code=500, detail="Error generando acta")
    
    # Extraer acta y costos
    acta = {k: v for k, v in acta_result.items() if k not in ['openai_usage', 'openai_cost']}
    openai_cost = acta_result['openai_cost']['total_cost_usd']
    
    # Enviar email
    email_sent = resend_email_service.send_acta_email(email, acta, filename, transcript)
    
    # Calcular costos totales
    email_cost = 0.0004  # Resend cost
    total_cost = round(assemblyai_cost + openai_cost + email_cost, 6)
    
    return {
        'transcript': transcript,
        'acta': acta,
        'email_sent': email_sent,
        'duration_minutes': duration_minutes,
        'total_cost': total_cost,
        'cost_breakdown': {
            'assemblyai_cost_usd': assemblyai_cost,
            'openai_cost_usd': openai_cost,
            'email_cost_usd': email_cost
        },
        'openai_usage': acta_result['openai_usage'],
        'assemblyai_usage': transcription_result['assemblyai_usage']
    }


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
    Endpoint simplificado para transcribir audio con AssemblyAI.
    """
    # Validar entradas
    _validate_inputs(file, email)
    
    # Tracking inicial
    posthog = request.app.state.posthog
    _track_form_submit(posthog, email, file.filename, file.size)
    
    temp_file_path = None
    try:
        # Guardar archivo temporalmente
        temp_file_path = await _save_temp_file(file)
        
        # Procesar pipeline completo
        result = _process_audio_pipeline(temp_file_path, email, file.filename)
        
        # Tracking final
        _track_acta_generated(
            posthog, email, file.filename, file.size,
            result['duration_minutes'], result['total_cost'],
            result['cost_breakdown'], result['openai_usage'],
            result['assemblyai_usage'], result['email_sent']
        )
        
        # Respuesta simplificada
        return {
            "status": "success",
            "filename": file.filename,
            "email": email,
            "transcript": result['transcript'],
            "acta": result['acta'],
            "email_sent": result['email_sent'],
            "duration_minutes": result['duration_minutes'],
            "cost_usd": result['total_cost'],
            "cost_breakdown": result['cost_breakdown'],
            "openai_usage": result['openai_usage'],
            "assemblyai_usage": result['assemblyai_usage'],
            "message": "Transcripción completada y acta enviada por email" if result['email_sent'] else "Transcripción completada, pero error enviando email"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando audio: {str(e)}")
    finally:
        # Limpiar archivo temporal
        _cleanup_temp_file(temp_file_path)

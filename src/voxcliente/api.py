"""Health check endpoints - Simplified for MVP."""

import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from typing import Optional
import tempfile
import os
from datetime import datetime
from contextlib import asynccontextmanager

from voxcliente.config import settings
from voxcliente.utils import validate_audio_file, validate_email
from voxcliente.services import assemblyai_service, openai_service, resend_email_service
from voxcliente.services.file_manager import file_manager
from voxcliente.services.analytics_service import analytics_service

logger = logging.getLogger(__name__)


router = APIRouter()


@asynccontextmanager
async def temp_file_context(file: UploadFile):
    """Context manager para manejo automático de archivos temporales."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        yield temp_path
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
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
    
    # Generar archivos para descarga
    try:
        download_files = resend_email_service.generate_download_files(acta, transcript, filename)
        
        # Limpiar archivos antiguos después de generar nuevos
        try:
            removed_count = file_manager.cleanup_old_files()
            if removed_count > 0:
                logger.info(f"Se eliminaron {removed_count} archivos antiguos")
        except Exception as cleanup_error:
            logger.warning(f"Error en limpieza automática: {cleanup_error}")
            
    except Exception as e:
        logger.error(f"Error generando archivos de descarga: {e}")
        download_files = None
    
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
        'assemblyai_usage': transcription_result['assemblyai_usage'],
        'download_files': download_files
    }


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}


@router.get("/download/{file_type}/{file_id}")
async def download_file(file_type: str, file_id: str):
    """
    Descargar archivo Word generado.
    
    Args:
        file_type: Tipo de archivo ('acta' o 'transcript')
        file_id: ID único del archivo
        
    Returns:
        Archivo Word para descarga
    """
    
    try:
        # Validar tipo de archivo
        if file_type not in ["acta", "transcript"]:
            raise HTTPException(status_code=400, detail="Tipo de archivo no válido")
        
        # Obtener ruta del archivo directamente
        file_path = file_manager.get_file_path(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        # Nombre simple de archivo
        download_filename = f"{file_type}.docx"
        
        
        # Retornar archivo para descarga
        return FileResponse(
            path=str(file_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=download_filename,
            headers={
                "Content-Disposition": f"attachment; filename=\"{download_filename}\"",
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sirviendo archivo {file_type}/{file_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")






@router.post("/transcribe")
async def transcribe_audio(
    request: Request,
    file: UploadFile = File(...),
    email: str = Form(...)
):
    """
    Endpoint simplificado para transcribir audio con AssemblyAI.
    """
    
    try:
        # Validación inline de email y archivo
        is_email_valid, email_error = validate_email(email)
        if not is_email_valid:
            raise HTTPException(status_code=400, detail=email_error)
        
        is_file_valid, file_error = validate_audio_file(file.filename, file.size)
        if not is_file_valid:
            raise HTTPException(status_code=400, detail=file_error)
        
        
        # Tracking inicial
        posthog = request.app.state.posthog
        analytics_service.track_form_submit(posthog, email, file.filename, file.size)
    except Exception as e:
        logger.error(f"Error en validación inicial: {str(e)}", exc_info=True)
        raise
    
    # Procesar con context manager para manejo automático de archivos temporales
    async with temp_file_context(file) as temp_file_path:
        
        # Procesar pipeline completo
        result = _process_audio_pipeline(temp_file_path, email, file.filename)
        
        # Tracking final
        analytics_service.track_acta_generated(
            posthog, email, file.filename, file.size,
            result['duration_minutes'], result['total_cost'],
            result['cost_breakdown'], result['openai_usage'],
            result['assemblyai_usage'], result['email_sent']
        )
        
        # Respuesta simplificada
        
        # Preparar URLs de descarga si están disponibles
        download_urls = None
        if result['download_files']:
            download_urls = {
                'acta_url': f"/api/v1/download/acta/{result['download_files']['acta_id']}",
                'transcript_url': f"/api/v1/download/transcript/{result['download_files']['transcript_id']}",
                'acta_filename': f"Acta_Reunion_{file.filename}.docx",
                'transcript_filename': f"Transcripcion_{file.filename}.docx"
            }
        
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
            "download_files": download_urls,
            "message": "Transcripción completada y acta enviada por email" if result['email_sent'] else "Transcripción completada, pero error enviando email"
        }

"""Health check endpoints - Simplified for MVP."""

import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from typing import Optional
import tempfile
import os
from datetime import datetime

from voxcliente.config import settings
from voxcliente.utils import validate_audio_file, validate_email, sanitize_filename
from voxcliente.services import assemblyai_service, openai_service, resend_email_service
from voxcliente.services.file_manager import file_manager

logger = logging.getLogger(__name__)


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
    
    # Generar archivos para descarga
    try:
        download_files = resend_email_service.generate_download_files(acta, transcript, filename)
        logger.info(f"Archivos de descarga generados: {download_files}")
        
        # Limpiar archivos antiguos después de generar nuevos
        try:
            removed_count = file_manager.cleanup_old_files()
            if removed_count > 0:
                logger.info(f"Limpieza automática: {removed_count} archivos antiguos eliminados")
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
    logger.info("Health check solicitado")
    try:
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug,
            "env_vars_loaded": {
                "assemblyai": bool(settings.assemblyai_api_key),
                "openai": bool(settings.openai_api_key),
                "resend": bool(settings.resend_api_key),
                "posthog": bool(settings.posthog_api_key)
            }
        }
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


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
    logger.info(f"Solicitud de descarga: {file_type}/{file_id}")
    
    try:
        # Validar tipo de archivo
        if file_type not in ["acta", "transcript"]:
            raise HTTPException(status_code=400, detail="Tipo de archivo no válido. Use 'acta' o 'transcript'")
        
        # Obtener información del archivo
        file_info = file_manager.get_file_info(file_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="Archivo no encontrado o expirado")
        
        # Verificar que el tipo coincida
        if file_info["file_type"] != file_type:
            raise HTTPException(status_code=400, detail="Tipo de archivo no coincide con el ID")
        
        # Obtener ruta del archivo
        file_path = file_manager.get_file_path(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="Archivo no encontrado en disco")
        
        # Generar nombre de archivo para descarga
        original_filename = file_info["original_filename"]
        clean_filename = original_filename.replace('.', '_')
        
        if file_type == "acta":
            download_filename = f"Acta_Reunion_{clean_filename}.docx"
        else:
            download_filename = f"Transcripcion_{clean_filename}.docx"
        
        logger.info(f"Sirviendo archivo: {file_path} como {download_filename}")
        
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


@router.post("/cleanup-files")
async def cleanup_files():
    """
    Limpiar archivos temporales antiguos.
    Endpoint para mantenimiento del sistema.
    """
    logger.info("Iniciando limpieza de archivos temporales")
    
    try:
        removed_count = file_manager.cleanup_old_files()
        stats = file_manager.get_stats()
        
        logger.info(f"Limpieza completada: {removed_count} archivos eliminados")
        
        return {
            "status": "success",
            "removed_files": removed_count,
            "current_stats": stats,
            "message": f"Limpieza completada. {removed_count} archivos eliminados."
        }
        
    except Exception as e:
        logger.error(f"Error en limpieza de archivos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en limpieza: {str(e)}")


@router.get("/file-stats")
async def get_file_stats():
    """
    Obtener estadísticas del sistema de archivos temporales.
    """
    try:
        stats = file_manager.get_stats()
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


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
    logger.info(f"Iniciando transcripción para {email}, archivo: {file.filename}, tamaño: {file.size} bytes")
    
    try:
        # Validar entradas
        _validate_inputs(file, email)
        logger.info("Validación de entradas exitosa")
        
        # Tracking inicial
        posthog = request.app.state.posthog
        if posthog:
            _track_form_submit(posthog, email, file.filename, file.size)
            logger.info("Tracking inicial enviado a PostHog")
        else:
            logger.warning("PostHog no disponible, saltando tracking")
    except Exception as e:
        logger.error(f"Error en validación inicial: {str(e)}", exc_info=True)
        raise
    
    temp_file_path = None
    try:
        # Guardar archivo temporalmente
        logger.info("Guardando archivo temporalmente...")
        temp_file_path = await _save_temp_file(file)
        logger.info(f"Archivo guardado en: {temp_file_path}")
        
        # Procesar pipeline completo
        logger.info("Iniciando pipeline de procesamiento...")
        result = _process_audio_pipeline(temp_file_path, email, file.filename)
        logger.info("Pipeline completado exitosamente")
        
        # Tracking final
        if posthog:
            _track_acta_generated(
                posthog, email, file.filename, file.size,
                result['duration_minutes'], result['total_cost'],
                result['cost_breakdown'], result['openai_usage'],
                result['assemblyai_usage'], result['email_sent']
            )
            logger.info("Tracking final enviado a PostHog")
        else:
            logger.warning("PostHog no disponible, saltando tracking final")
        
        # Respuesta simplificada
        logger.info("Preparando respuesta exitosa")
        
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
        
    except Exception as e:
        logger.error(f"Error procesando audio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error procesando audio: {str(e)}")
    finally:
        # Limpiar archivo temporal
        logger.info("Limpiando archivo temporal...")
        _cleanup_temp_file(temp_file_path)
        logger.info("Proceso completado")

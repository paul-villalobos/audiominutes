"""Utilidades simples para validación - MVP."""

import re
from typing import Optional
from voxcliente.config import settings


def validate_audio_file(filename: str, file_size_bytes: int) -> tuple[bool, Optional[str]]:
    """
    Valida archivo de audio de forma simple.
    
    Returns:
        (is_valid, error_message)
    """
    if not filename:
        return False, "Nombre de archivo requerido"
    
    # Validar tamaño usando configuración centralizada
    max_size_bytes = settings.max_file_size_mb * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        return False, f"Archivo muy grande. Máximo: {settings.max_file_size_mb}MB"
    
    return True, None


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Valida email de forma simple.
    
    Returns:
        (is_valid, error_message)
    """
    if not email:
        return False, "Email requerido"
    
    # Regex simple pero efectivo
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Formato de email inválido"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nombre de archivo de forma simple.
    """
    if not filename:
        return "audio_file"
    
    # Remover caracteres peligrosos
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Limitar longitud
    if len(sanitized) > 100:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:95] + ('.' + ext if ext else '')
    
    return sanitized

"""Sistema de gestión de archivos temporales para descarga de documentos Word."""

import os
import uuid
import time
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """Gestor de archivos temporales para descarga."""
    
    def __init__(self):
        """Inicializar gestor de archivos."""
        self.temp_dir = Path("uploads/temp")
        self.actas_dir = self.temp_dir / "actas"
        self.transcripts_dir = self.temp_dir / "transcripts"
        
        # Crear directorios si no existen
        self._ensure_directories()
        
        # Registro de archivos: {file_id: {path, created_at, file_type}}
        self.file_registry: Dict[str, Dict] = {}
        
        # Tiempo de vida de archivos (1 hora)
        self.file_lifetime_hours = 1
        
        logger.info(f"FileManager inicializado. Directorio temporal: {self.temp_dir}")
    
    def _ensure_directories(self) -> None:
        """Crear directorios necesarios."""
        try:
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.actas_dir.mkdir(parents=True, exist_ok=True)
            self.transcripts_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Directorios temporales creados/verificados")
        except Exception as e:
            logger.error(f"Error creando directorios temporales: {e}")
            raise
    
    def generate_file_id(self) -> str:
        """Generar ID único para archivo."""
        return str(uuid.uuid4())
    
    def save_file(self, source_file_path: str, file_type: str, original_filename: str) -> str:
        """
        Guardar archivo temporalmente y registrar para descarga.
        
        Args:
            source_file_path: Ruta del archivo fuente
            file_type: Tipo de archivo ('acta' o 'transcript')
            original_filename: Nombre del archivo original
            
        Returns:
            ID único del archivo guardado
        """
        try:
            file_id = self.generate_file_id()
            
            # Determinar directorio destino
            if file_type == "acta":
                dest_dir = self.actas_dir
            elif file_type == "transcript":
                dest_dir = self.transcripts_dir
            else:
                raise ValueError(f"Tipo de archivo no válido: {file_type}")
            
            # Crear archivo destino
            dest_file_path = dest_dir / f"{file_id}.docx"
            
            # Copiar archivo
            shutil.copy2(source_file_path, dest_file_path)
            
            # Registrar archivo
            self.file_registry[file_id] = {
                "path": str(dest_file_path),
                "created_at": datetime.now(),
                "file_type": file_type,
                "original_filename": original_filename
            }
            
            logger.info(f"Archivo guardado: {file_id} -> {dest_file_path}")
            return file_id
            
        except Exception as e:
            logger.error(f"Error guardando archivo {file_type}: {e}")
            raise
    
    def get_file_path(self, file_id: str) -> Optional[Path]:
        """
        Obtener ruta del archivo por ID.
        
        Args:
            file_id: ID único del archivo
            
        Returns:
            Ruta del archivo o None si no existe
        """
        if file_id not in self.file_registry:
            logger.warning(f"Archivo no encontrado en registro: {file_id}")
            return None
        
        file_info = self.file_registry[file_id]
        file_path = Path(file_info["path"])
        
        if not file_path.exists():
            logger.warning(f"Archivo no existe en disco: {file_path}")
            # Limpiar registro
            del self.file_registry[file_id]
            return None
        
        return file_path
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """
        Obtener información del archivo por ID.
        
        Args:
            file_id: ID único del archivo
            
        Returns:
            Información del archivo o None si no existe
        """
        if file_id not in self.file_registry:
            return None
        
        file_info = self.file_registry[file_id].copy()
        file_path = Path(file_info["path"])
        
        if not file_path.exists():
            # Limpiar registro si archivo no existe
            del self.file_registry[file_id]
            return None
        
        # Agregar información adicional
        file_info["size_bytes"] = file_path.stat().st_size
        file_info["exists"] = True
        
        return file_info
    
    def cleanup_old_files(self) -> int:
        """
        Limpiar archivos antiguos basado en tiempo de vida.
        
        Returns:
            Número de archivos eliminados
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.file_lifetime_hours)
            files_to_remove = []
            
            # Identificar archivos antiguos
            for file_id, file_info in self.file_registry.items():
                if file_info["created_at"] < cutoff_time:
                    files_to_remove.append(file_id)
            
            # Eliminar archivos
            removed_count = 0
            for file_id in files_to_remove:
                if self._remove_file(file_id):
                    removed_count += 1
            
            logger.info(f"Limpieza completada: {removed_count} archivos eliminados")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error en limpieza de archivos: {e}")
            return 0
    
    def _remove_file(self, file_id: str) -> bool:
        """
        Eliminar archivo específico.
        
        Args:
            file_id: ID único del archivo
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            if file_id not in self.file_registry:
                return False
            
            file_info = self.file_registry[file_id]
            file_path = Path(file_info["path"])
            
            # Eliminar archivo del disco
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Archivo eliminado del disco: {file_path}")
            
            # Eliminar del registro
            del self.file_registry[file_id]
            logger.debug(f"Archivo eliminado del registro: {file_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando archivo {file_id}: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Obtener estadísticas del gestor de archivos.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            total_files = len(self.file_registry)
            acta_files = sum(1 for info in self.file_registry.values() if info["file_type"] == "acta")
            transcript_files = sum(1 for info in self.file_registry.values() if info["file_type"] == "transcript")
            
            # Calcular tamaño total
            total_size = 0
            for file_info in self.file_registry.values():
                file_path = Path(file_info["path"])
                if file_path.exists():
                    total_size += file_path.stat().st_size
            
            return {
                "total_files": total_files,
                "acta_files": acta_files,
                "transcript_files": transcript_files,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "file_lifetime_hours": self.file_lifetime_hours
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
    
    def cleanup_all(self) -> int:
        """
        Limpiar todos los archivos temporales.
        
        Returns:
            Número de archivos eliminados
        """
        try:
            removed_count = 0
            file_ids = list(self.file_registry.keys())
            
            for file_id in file_ids:
                if self._remove_file(file_id):
                    removed_count += 1
            
            logger.info(f"Limpieza completa: {removed_count} archivos eliminados")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error en limpieza completa: {e}")
            return 0


# Instancia global del gestor de archivos
file_manager = FileManager()

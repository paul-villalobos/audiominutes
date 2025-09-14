"""Servicios externos - Simplificado para MVP."""

import assemblyai as aai
from typing import Optional
from audiominutes.config import settings


class AssemblyAIService:
    """Servicio simple para AssemblyAI."""
    
    def __init__(self):
        """Inicializar cliente de AssemblyAI."""
        aai.settings.api_key = settings.assemblyai_api_key
        config = aai.TranscriptionConfig(
            language_code="es",
            speaker_labels=True,
            )

        config.set_custom_spelling(
            {
                "LAIVE": ["laib"],
            }
        )

        self.transcriber = aai.Transcriber(config=config)
    
    def transcribe_file(self, file_path: str) -> Optional[str]:
        """
        Transcribir archivo local usando AssemblyAI.
        Basado en la documentación oficial de AssemblyAI.
        
        Args:
            file_path: Ruta del archivo local
            
        Returns:
            Transcripción del audio o None si hay error
        """
        try:
            # Transcribir archivo local directamente
            transcript = self.transcriber.transcribe(file_path)
            
            return transcript.text if transcript.text else None
            
        except Exception as e:
            print(f"Error en transcripción: {e}")
            return None


# Instancia global del servicio
assemblyai_service = AssemblyAIService()

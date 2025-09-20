"""Servicio de transcripción con AssemblyAI - Simplificado para MVP."""

import assemblyai as aai
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from voxcliente.config import settings


class AssemblyAIService:
    """Servicio simple para AssemblyAI."""
    
    def __init__(self):
        """Inicializar cliente de AssemblyAI."""
        aai.settings.api_key = settings.assemblyai_api_key
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            format_text=True,
            punctuate=True,
            language_code="es",
            )

        config.set_custom_spelling(
            {
                "LAIVE": ["laib", "Laibe"],
                "HORECA": ["Oreka"],
            }
        )

        self.transcriber = aai.Transcriber(config=config)
    
    def transcribe_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Transcribir archivo local usando AssemblyAI con utterances.
        Basado en la documentación oficial de AssemblyAI.
        
        Args:
            file_path: Ruta del archivo local
            
        Returns:
            Diccionario con transcripción y información de costos o None si hay error
        """
        try:
            # Transcribir archivo local directamente
            transcript = self.transcriber.transcribe(file_path)
            
            # Guardar respuesta de AssemblyAI en archivo local para debugging
            self._save_assemblyai_response(transcript, file_path)
            
            # Verificar si la transcripción fue exitosa
            if transcript.status == aai.TranscriptStatus.error:
                print(f"Error en la transcripción: {transcript.error}")
                return None
            
            # Procesar utterances para obtener texto con información de hablantes
            formatted_text = ""
            if transcript.utterances:
                for utterance in transcript.utterances:
                    formatted_text += f"Hablante {utterance.speaker}: {utterance.text}\n"
                formatted_text = formatted_text.strip()
            else:
                # Fallback al texto completo si no hay utterances
                formatted_text = transcript.text if transcript.text else None
            
            if not formatted_text:
                return None
            
            # Calcular duración y costo de AssemblyAI
            # AssemblyAI cobra $0.27 por hora (Universal) = $0.0045 por minuto
            # Usamos Universal por defecto (incluye speaker labels, punctuation, etc.)
            duration_minutes = transcript.audio_duration / 60 if transcript.audio_duration else 0
            assemblyai_cost = duration_minutes * 0.0045
            
            return {
                'transcript': formatted_text,
                'assemblyai_usage': {
                    'audio_duration_seconds': transcript.audio_duration,
                    'audio_duration_minutes': round(duration_minutes, 2),
                    'confidence': transcript.confidence
                },
                'assemblyai_cost': {
                    'duration_minutes': round(duration_minutes, 2),
                    'cost_usd': round(assemblyai_cost, 6)
                }
            }
            
        except Exception as e:
            print(f"Error en transcripción: {e}")
            return None
    
    def _save_assemblyai_response(self, transcript, file_path: str) -> None:
        """Guardar respuesta de AssemblyAI en archivo local para debugging."""
        # Solo guardar si está habilitado el logging de APIs
        if not settings.should_log_apis:
            return
            
        try:
            # Crear directorio de logs si no existe
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Generar nombre de archivo con timestamp al inicio para ordenamiento cronológico
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_assemblyai_response.txt"
            log_file_path = logs_dir / filename
            
            # Extraer información del transcript
            status = transcript.status
            confidence = getattr(transcript, 'confidence', 'N/A')
            audio_duration = getattr(transcript, 'audio_duration', 'N/A')
            text = getattr(transcript, 'text', 'N/A')
            utterances_count = len(transcript.utterances) if transcript.utterances else 0
            
            # Crear contenido del archivo
            content = f"""
=== RESPUESTA DE ASSEMBLYAI ===
Timestamp: {datetime.now().isoformat()}
Archivo procesado: {Path(file_path).name}
Status: {status}
Confidence: {confidence}
Duración audio (segundos): {audio_duration}
Número de utterances: {utterances_count}

=== TEXTO COMPLETO ===
{text}

=== UTTERANCES (HABLANTES) ===
"""
            
            # Agregar utterances si existen
            if transcript.utterances:
                for i, utterance in enumerate(transcript.utterances):
                    content += f"Utterance {i+1}:\n"
                    content += f"  Speaker: {utterance.speaker}\n"
                    content += f"  Text: {utterance.text}\n"
                    content += f"  Confidence: {getattr(utterance, 'confidence', 'N/A')}\n"
                    content += f"  Start: {getattr(utterance, 'start', 'N/A')}ms\n"
                    content += f"  End: {getattr(utterance, 'end', 'N/A')}ms\n\n"
            else:
                content += "No hay utterances disponibles\n"
            
            content += f"""
=== METADATOS COMPLETOS ===
{transcript}

=== FIN DE RESPUESTA ===
"""
            
            # Guardar archivo
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📁 Respuesta de AssemblyAI guardada en: {log_file_path}")
            
        except Exception as e:
            print(f"⚠️ Error guardando respuesta de AssemblyAI: {e}")


# Instancia global del servicio
assemblyai_service = AssemblyAIService()

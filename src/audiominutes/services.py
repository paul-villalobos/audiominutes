"""Servicios externos - Simplificado para MVP."""

import assemblyai as aai
import openai
from typing import Optional
from audiominutes.config import settings


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
            }
        )

        self.transcriber = aai.Transcriber(config=config)
    
    def transcribe_file(self, file_path: str) -> Optional[str]:
        """
        Transcribir archivo local usando AssemblyAI con utterances.
        Basado en la documentación oficial de AssemblyAI.
        
        Args:
            file_path: Ruta del archivo local
            
        Returns:
            Transcripción del audio con información de hablantes o None si hay error
        """
        try:
            # Transcribir archivo local directamente
            transcript = self.transcriber.transcribe(file_path)
            
            # Verificar si la transcripción fue exitosa
            if transcript.status == aai.TranscriptStatus.error:
                print(f"Error en la transcripción: {transcript.error}")
                return None
            
            # Procesar utterances para obtener texto con información de hablantes
            if transcript.utterances:
                formatted_text = ""
                for utterance in transcript.utterances:
                    formatted_text += f"Hablante {utterance.speaker}: {utterance.text}\n"
                return formatted_text.strip()
            else:
                # Fallback al texto completo si no hay utterances
                return transcript.text if transcript.text else None
            
        except Exception as e:
            print(f"Error en transcripción: {e}")
            return None


class OpenAIService:
    """Servicio simple para OpenAI."""
    
    def __init__(self):
        """Inicializar cliente de OpenAI."""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def generate_acta(self, transcript: str) -> Optional[str]:
        """
        Generar acta profesional a partir de transcripción.
        
        Args:
            transcript: Transcripción del audio
            
        Returns:
            Acta profesional o None si hay error
        """
        try:
            prompt = f"""
Convierte la siguiente transcripción de reunión en un acta profesional y estructurada:

TRANSCRIPCIÓN:
{transcript}

FORMATO DEL ACTA:
1. **Información General**
   - Fecha: [Fecha de la reunión]
   - Participantes: [Lista de participantes identificados]
   - Duración: [Duración estimada]

2. **Agenda/Temas Tratados**
   - [Lista de temas principales discutidos]

3. **Decisiones Tomadas**
   - [Decisiones importantes acordadas]

4. **Acciones Pendientes**
   - [Tareas asignadas con responsables]

5. **Próximos Pasos**
   - [Siguientes reuniones o acciones]

6. **Observaciones**
   - [Notas adicionales relevantes]

IMPORTANTE:
- Mantén un tono profesional y formal
- Organiza la información de manera clara y estructurada
- Identifica participantes, decisiones y acciones cuando sea posible
- Si no hay información específica sobre fechas o participantes, usa "[Por determinar]"
- Mantén la información original pero organízala profesionalmente
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en crear actas de reuniones profesionales."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generando acta: {e}")
            return None


# Instancias globales de los servicios
assemblyai_service = AssemblyAIService()
openai_service = OpenAIService()

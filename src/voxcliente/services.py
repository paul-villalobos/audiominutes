"""Servicios externos - Simplificado para MVP."""

import assemblyai as aai
import openai
import resend
from typing import Optional
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


class ResendEmailService:
    """Servicio simple para Resend."""
    
    def __init__(self):
        """Inicializar cliente de Resend."""
        resend.api_key = settings.resend_api_key
        self.template_path = Path(__file__).parent / "templates" / "email_template.html"
    
    def send_acta_email(self, email: str, acta: str, filename: str) -> bool:
        """
        Enviar acta por email usando Resend.
        
        Args:
            email: Email del destinatario
            acta: Contenido del acta
            filename: Nombre del archivo procesado
            
        Returns:
            True si se envió correctamente, False si hubo error
        """
        try:
            # Cargar template HTML
            template_content = self._load_template()
            if not template_content:
                print("Error: No se pudo cargar el template de email")
                return False
            
            # Personalizar template
            html_content = self._personalize_template(template_content, acta, filename)
            
            # Enviar email
            response = resend.Emails.send({
                "from": f"{settings.from_name} <{settings.from_email}>",
                "to": [email],
                "subject": f"Acta de Reunión - {filename}",
                "html": html_content,
            })
            
            print(f"Email enviado exitosamente: {response}")
            return True
            
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False
    
    def _load_template(self) -> Optional[str]:
        """Cargar template HTML desde archivo."""
        try:
            return self.template_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error cargando template: {e}")
            return None
    
    def _personalize_template(self, template: str, acta: str, filename: str) -> str:
        """Personalizar template con datos específicos."""
        timestamp = datetime.now().strftime("%d/%m/%Y a las %H:%M")
        
        return template.replace("{{ acta_content }}", acta) \
                     .replace("{{ filename }}", filename) \
                     .replace("{{ timestamp }}", timestamp)


# Instancias globales de los servicios
assemblyai_service = AssemblyAIService()
openai_service = OpenAIService()
resend_email_service = ResendEmailService()

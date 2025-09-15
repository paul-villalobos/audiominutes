"""Servicios externos - Simplificado para MVP."""

import assemblyai as aai
import openai
import resend
import json
import re
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
        self.prompt_path = Path(__file__).parent / "prompts" / "acta_generation.txt"
    
    def generate_acta(self, transcript: str) -> Optional[Dict[str, Any]]:
        """
        Generar acta profesional a partir de transcripción.
        
        Args:
            transcript: Transcripción del audio
            
        Returns:
            Diccionario con resumen_ejecutivo y acta completa o None si hay error
        """
        try:
            # Cargar prompt desde archivo
            prompt_template = self._load_prompt()
            if not prompt_template:
                print("Error: No se pudo cargar el prompt")
                return None
            
            # Personalizar prompt con la transcripción
            prompt = prompt_template.replace("{{ transcript }}", transcript)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en crear actas de reuniones profesionales. Responde ÚNICAMENTE con JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            # Parsear respuesta JSON
            raw_response = response.choices[0].message.content
            parsed_data = self._parse_response(raw_response)
            
            return parsed_data
            
        except Exception as e:
            print(f"Error generando acta: {e}")
            return None
    
    def _load_prompt(self) -> Optional[str]:
        """Cargar prompt desde archivo."""
        try:
            return self.prompt_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error cargando prompt: {e}")
            return None
    
    def _parse_response(self, raw_response: str) -> Optional[Dict[str, Any]]:
        """Parsear respuesta JSON de OpenAI."""
        try:
            # Extraer JSON entre las etiquetas <output> y </output>
            pattern = r'<output>(.*?)</output>'
            match = re.search(pattern, raw_response, re.DOTALL)
            
            if not match:
                print("Error: No se encontró JSON entre etiquetas <output>")
                return None
            
            json_str = match.group(1).strip()
            
            # Parsear JSON
            parsed_data = json.loads(json_str)
            
            # Validar estructura requerida
            if not self._validate_structure(parsed_data):
                print("Error: Estructura JSON inválida")
                return None
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"Error parseando JSON: {e}")
            return None
        except Exception as e:
            print(f"Error procesando respuesta: {e}")
            return None
    
    def _validate_structure(self, data: Dict[str, Any]) -> bool:
        """Validar estructura del JSON parseado."""
        try:
            # Verificar que tenga las claves principales
            if "resumen_ejecutivo" not in data or "acta" not in data:
                return False
            
            resumen = data["resumen_ejecutivo"]
            if not isinstance(resumen, dict):
                return False
            
            # Verificar campos del resumen ejecutivo
            required_fields = ["objetivo", "acuerdos", "proximos_pasos"]
            for field in required_fields:
                if field not in resumen:
                    return False
            
            return True
            
        except Exception:
            return False


class ResendEmailService:
    """Servicio simple para Resend."""
    
    def __init__(self):
        """Inicializar cliente de Resend."""
        resend.api_key = settings.resend_api_key
        self.template_path = Path(__file__).parent / "templates" / "email_template.html"
    
    def send_acta_email(self, email: str, acta_data: Dict[str, Any], filename: str) -> bool:
        """
        Enviar acta por email usando Resend.
        
        Args:
            email: Email del destinatario
            acta_data: Diccionario con resumen_ejecutivo y acta completa
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
            
            # Personalizar template con resumen ejecutivo en el cuerpo
            html_content = self._personalize_template(template_content, acta_data, filename)
            
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
    
    def _personalize_template(self, template: str, acta_data: Dict[str, Any], filename: str) -> str:
        """Personalizar template con datos específicos."""
        timestamp = datetime.now().strftime("%d/%m/%Y a las %H:%M")
        
        # Extraer resumen ejecutivo
        resumen = acta_data.get("resumen_ejecutivo", {})
        objetivo = resumen.get("objetivo", "No especificado")
        acuerdos = resumen.get("acuerdos", "No especificados")
        proximos_pasos = resumen.get("proximos_pasos", "No especificados")
        
        # Crear resumen ejecutivo para el cuerpo del email
        resumen_ejecutivo_html = f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #2c3e50; margin-top: 0;">📋 Resumen Ejecutivo</h3>
            <p><strong>🎯 Objetivo:</strong> {objetivo}</p>
            <p><strong>🤝 Acuerdos:</strong> {acuerdos}</p>
            <p><strong>📅 Próximos Pasos:</strong> {proximos_pasos}</p>
        </div>
        <p style="color: #666; font-size: 14px;">
            <em>Para detalles completos, consulta el acta adjunta.</em>
        </p>
        """
        
        # Acta completa para adjunto (si se necesita en el template)
        acta_completa = acta_data.get("acta", "")
        
        return template.replace("{{ resumen_ejecutivo }}", resumen_ejecutivo_html) \
                     .replace("{{ acta_content }}", acta_completa) \
                     .replace("{{ filename }}", filename) \
                     .replace("{{ timestamp }}", timestamp)


# Instancias globales de los servicios
assemblyai_service = AssemblyAIService()
openai_service = OpenAIService()
resend_email_service = ResendEmailService()

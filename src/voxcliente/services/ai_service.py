"""Servicio de IA con OpenAI - Simplificado para MVP."""

import openai
import json
import re
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from voxcliente.config import settings


class OpenAIService:
    """Servicio simple para OpenAI."""
    
    def __init__(self):
        """Inicializar cliente de OpenAI."""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "acta_generation.txt"
    
    def generate_acta(self, transcript: str) -> Optional[Dict[str, Any]]:
        """
        Generar acta profesional a partir de transcripción.
        
        Args:
            transcript: Transcripción del audio
            
        Returns:
            Diccionario con resumen_ejecutivo, acta completa y costos o None si hay error
        """
        try:
            # Cargar prompt desde archivo
            prompt_template = self._load_prompt()
            if not prompt_template:
                print("Error: No se pudo cargar el prompt")
                return None
            
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": transcript}
                ],
                # temperature=0.3 # gpt-5-mini no soporta temperature
            )
            
            # Parsear respuesta JSON
            raw_response = response.choices[0].message.content
            
            # Guardar respuesta de OpenAI en archivo local para debugging
            self._save_openai_response(raw_response, transcript[:50])
            
            parsed_data = self._parse_response(raw_response)
            
            # Agregar información de costos
            if parsed_data:
                parsed_data['openai_usage'] = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
                
                # Calcular costo real (precios de GPT-5-mini)
                # Input: $0.25 per 1M tokens = $0.00025 per 1K tokens
                # Output: $2 per 1M tokens = $0.002 per 1K tokens
                input_cost = (response.usage.prompt_tokens / 1000) * 0.00025
                output_cost = (response.usage.completion_tokens / 1000) * 0.002
                total_openai_cost = input_cost + output_cost
                
                parsed_data['openai_cost'] = {
                    'input_cost_usd': round(input_cost, 6),
                    'output_cost_usd': round(output_cost, 6),
                    'total_cost_usd': round(total_openai_cost, 6)
                }
            
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
    
    def _save_openai_response(self, response: str, transcript_preview: str) -> None:
        """Guardar respuesta de OpenAI en archivo local para debugging."""
        # Solo guardar si está habilitado el logging de APIs
        if not settings.should_log_apis:
            return
            
        try:
            # Crear directorio de logs si no existe
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Generar nombre de archivo con timestamp al inicio para ordenamiento cronológico
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_openai_response.txt"
            file_path = logs_dir / filename
            
            # Crear contenido del archivo
            content = f"""
=== RESPUESTA DE OPENAI ===
Timestamp: {datetime.now().isoformat()}
Modelo: gpt-5-mini
Transcripción (primeros 50 chars): {transcript_preview}

=== RESPUESTA COMPLETA ===
{response}

=== FIN DE RESPUESTA ===
"""
            
            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📁 Respuesta de OpenAI guardada en: {file_path}")
            
        except Exception as e:
            print(f"⚠️ Error guardando respuesta de OpenAI: {e}")
    
    def _parse_response(self, raw_response: str) -> Optional[Dict[str, Any]]:
        """Parsear respuesta JSON de OpenAI."""
        try:
            # Intentar múltiples formatos de parsing
            
            # 1. Buscar JSON entre etiquetas <output> y </output>
            pattern = r'<output>(.*?)</output>'
            match = re.search(pattern, raw_response, re.DOTALL)
            
            if match:
                json_str = match.group(1).strip()
                print(f"✅ JSON encontrado entre etiquetas <output>: {json_str[:100]}...")
            else:
                # 2. Buscar JSON entre ```json y ```
                pattern = r'```json\s*(.*?)\s*```'
                match = re.search(pattern, raw_response, re.DOTALL)
                
                if match:
                    json_str = match.group(1).strip()
                    print(f"✅ JSON encontrado entre ```json: {json_str[:100]}...")
                else:
                    # 3. Buscar JSON directo (sin etiquetas)
                    json_str = raw_response.strip()
                    print(f"⚠️ Intentando parsear respuesta directa: {json_str[:100]}...")
            
            # Parsear JSON
            parsed_data = json.loads(json_str)
            
            # Validar estructura requerida
            if not self._validate_structure(parsed_data):
                print("Error: Estructura JSON inválida")
                return None
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON: {e}")
            print(f"📄 Respuesta completa de OpenAI: {raw_response}")
            return None
        except Exception as e:
            print(f"❌ Error procesando respuesta: {e}")
            print(f"📄 Respuesta completa de OpenAI: {raw_response}")
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


# Instancia global del servicio
openai_service = OpenAIService()

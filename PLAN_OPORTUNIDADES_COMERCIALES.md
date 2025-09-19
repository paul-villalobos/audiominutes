# Plan de Implementación: Detección de Oportunidades Comerciales

## 🎯 Objetivo

Agregar detección automática de oportunidades comerciales en las transcripciones de reuniones, donde el chatbot identifique productos/servicios que el prospecto podría comprar a nosotros.

## 📋 Requerimientos Específicos

### Funcionalidad Principal

- El chatbot debe analizar la transcripción y decidir si hay información comercial relevante
- Solo en caso positivo, agregar un listado resumen de productos que nos podría comprar
- Incluir información de proveedores actuales, precios, cantidades y condiciones comerciales

### Estructura de Datos

- **Condiciones comerciales**: A nivel de empresa prospecto (no por producto)
- **Productos identificados**: Lista de productos/servicios específicos mencionados
- **Detección**: Sin palabras clave específicas, análisis contextual
- **Ubicación**: Las oportunidades aparecen en el acta
- **Precisión**: Solo extraer información mencionada explícitamente, no inventar

## 🏗️ Estructura JSON Actualizada

```json
{
  "resumen_ejecutivo": {
    "objetivo": "Objetivo principal de la reunión en 1-2 líneas",
    "acuerdos": "Principales acuerdos tomados en 2-3 líneas",
    "proximos_pasos": "Próximos pasos concretos en 2-3 líneas"
  },
  "acta": "Acta completa y detallada siguiendo la estructura corporativa",
  "oportunidades_comerciales": {
    "hay_oportunidades": true/false,
    "condiciones_comerciales": "Condiciones comerciales generales de la empresa prospecto mencionadas en la reunión",
    "productos_identificados": [
      {
        "producto": "nombre del producto/servicio mencionado",
        "proveedor_actual": "nombre del proveedor actual mencionado",
        "precio": "precio específico mencionado en la transcripción",
        "cantidad": "cantidad específica mencionada en la transcripción",
        "observaciones": "cualquier detalle adicional mencionado sobre este producto"
      }
    ]
  }
}
```

## 📝 Plan de Implementación

### 1. Variable de Configuración (MVP)

**Archivo**: `src/voxcliente/config.py`

- Agregar variable `PRODUCTOS_DETECTAR` hardcodeada para MVP
- Incluir TODO para hacerla configurable por usuario en el futuro
- Ejemplo: `PRODUCTOS_DETECTAR = ["software", "consultoría", "servicios IT"]`

### 2. Extensión del Prompt

**Archivo**: `src/voxcliente/prompts/acta_generation.txt`

- Agregar nueva sección de instrucciones para detección comercial
- Incluir variable de productos a detectar
- Actualizar formato JSON de salida
- Agregar reglas específicas:
  - Solo extraer información mencionada explícitamente
  - No inventar datos que no estén en la transcripción
  - Analizar contexto para identificar oportunidades comerciales

### 3. Actualización de Servicios

**Archivo**: `src/voxcliente/services.py`

#### OpenAIService

- Modificar `_validate_structure()` para validar nueva estructura JSON
- Agregar validación de campos `oportunidades_comerciales`
- Verificar estructura de `productos_identificados`

#### ResendEmailService

- Actualizar `_personalize_template()` para incluir oportunidades comerciales
- Modificar `_generate_word_document()` para mostrar sección comercial en el acta
- Agregar lógica condicional: solo mostrar si `hay_oportunidades` es true

### 4. Template de Email

**Archivo**: `src/voxcliente/templates/email_template.html`

- Agregar sección de oportunidades comerciales en el HTML
- Formato limpio y profesional
- Solo mostrar si hay oportunidades detectadas
- Incluir tanto condiciones comerciales como lista de productos

### 5. Integración en el Acta Word

- Nueva sección: "OPORTUNIDADES COMERCIALES"
- Estructura jerárquica:
  1. Condiciones comerciales generales
  2. Lista de productos identificados con detalles
- Solo se incluye si hay información comercial relevante

## 🔧 Características Técnicas

### Simplicidad

- Extensión mínima del sistema actual
- Reutilización de componentes existentes
- Mínimos cambios en la arquitectura

### Flexibilidad

- Variable configurable para tipos de productos (futuro)
- Estructura JSON extensible
- Fácil mantenimiento y actualización

### Precisión

- Solo extrae información mencionada explícitamente
- No inventa datos comerciales
- Análisis contextual inteligente

### Integración

- Aparece tanto en email como en acta Word
- Mantiene formato profesional existente
- Condicional: solo se muestra si hay oportunidades

## 📋 TODO para el Futuro

### Configuración de Usuario

- Hacer configurable por usuario los tipos de productos/servicios a detectar
- Interfaz de configuración en el frontend
- Base de datos para almacenar preferencias por usuario

### Mejoras Adicionales

- Análisis de sentimiento en oportunidades comerciales
- Scoring de probabilidad de venta
- Integración con CRM
- Alertas automáticas para oportunidades de alto valor

## 🎯 Criterios de Éxito

1. **Funcionalidad**: El sistema detecta correctamente oportunidades comerciales
2. **Precisión**: Solo extrae información mencionada en la transcripción
3. **Integración**: Las oportunidades aparecen correctamente en email y acta
4. **Simplicidad**: Implementación mínima sin afectar funcionalidad existente
5. **Flexibilidad**: Fácil configuración de tipos de productos a detectar

## 📅 Priorización

### Fase 1 (MVP)

- Variable hardcodeada de productos
- Extensión del prompt
- Estructura JSON básica
- Integración en acta Word

### Fase 2 (Futuro)

- Configuración por usuario
- Interfaz de configuración
- Mejoras en análisis contextual

---

**Nota**: Este plan mantiene la filosofía de simplicidad del proyecto, agregando funcionalidad valiosa con mínimos cambios al sistema existente.



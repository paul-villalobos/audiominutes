# 📋 Plan de Desarrollo VoxCliente MVP

## 🎯 Resumen del Proyecto

**VoxCliente** es un backend que convierte grabaciones de audio en actas de reuniones profesionales mediante IA. El MVP se enfoca en validar tracción de usuarios con funcionalidad mínima viable.

### Objetivo Principal

Automatizar la transcripción de reuniones y generar actas profesionales que se envían automáticamente por email, sin necesidad de registro de usuarios.

## 🛠️ Stack Tecnológico

- **Framework:** FastAPI + SQLAlchemy
- **Base de datos:** PostgreSQL
- **APIs externas:** AssemblyAI, OpenAI, Resend
- **Entorno:** Python 3.13.5 + Poetry 2.1

## 📊 Modelo de Datos

```sql
-- Tabla principal para tracking de uso
CREATE TABLE usage_logs (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    duration_minutes FLOAT NOT NULL,
    assembly_cost DECIMAL(10,4),
    openai_cost DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT NOW(),
    transcript_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'processing'
);

-- Índices para analytics
CREATE INDEX idx_usage_logs_email ON usage_logs(email);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);
```

## 🚀 Plan de Desarrollo Paso a Paso

### **Fase 1: Configuración Base** ⏳

#### 1.1 Configurar Entorno de Desarrollo ✅ **COMPLETADO**

- ✅ Instalar dependencias básicas (FastAPI, SQLAlchemy, PostgreSQL)
- ✅ Configurar Poetry con todas las dependencias necesarias
- ✅ Crear estructura de directorios del proyecto
- ✅ Configurar variables de entorno
- ✅ Crear aplicación FastAPI básica
- ✅ Implementar health check endpoint
- ✅ Verificar funcionamiento correcto

#### 1.2 Configurar Base de Datos ✅ **COMPLETADO**

- ✅ Configurar conexión a PostgreSQL
- ✅ Crear modelo SQLAlchemy para `usage_logs`
- ✅ Crear índices para optimización
- ✅ Endpoint de health check para base de datos

### **Fase 2: API Core** ⏳

#### 2.1 Estructura Básica de FastAPI ✅ **COMPLETADO**

- ✅ Crear aplicación FastAPI principal
- ✅ Configurar CORS y middleware básico
- ✅ Implementar endpoint de health check
- ✅ Estructurar routers y dependencias

#### 2.2 Validación de Archivos ✅ **COMPLETADO**

- ✅ Implementar validación de tipos de archivo (.wav, .mp3, .m4a)
- ✅ Validación de tamaño máximo de archivos
- ✅ Sanitización de inputs de usuario
- ✅ Validación de formato de email

### **Fase 3: Integración con Servicios Externos** ⏳

#### 3.1 AssemblyAI Integration ✅ **COMPLETADO**

- ✅ Configurar cliente de AssemblyAI
- ✅ Implementar upload de archivos de audio
- ✅ Manejar transcripción asíncrona
- ✅ Procesar resultados de transcripción

#### 3.2 OpenAI Integration ✅ **COMPLETADO**

- ✅ Configurar cliente de OpenAI
- ✅ Crear prompt optimizado para actas profesionales
- ✅ Implementar generación de actas
- ✅ Manejar límites de tokens y costos

#### 3.3 Resend Email Service ⏳ **COMPLETADO**

- ✅ Configurar cliente de Resend
- ✅ Crear template HTML profesional
- ✅ Implementar envío automático de actas

### **Fase 4: Flujo Completo y Robustez** ⏳

#### 4.1 Endpoint Principal ⏳ **PENDIENTE**

- ⏳ Crear endpoint `/process-audio` que orqueste todo el flujo
- ⏳ Implementar procesamiento asíncrono
- ⏳ Manejar estados de procesamiento
- ⏳ Logging detallado de cada paso

#### 4.2 Manejo de Errores ⏳ **PENDIENTE**

- ⏳ Implementar manejo robusto de errores
- ⏳ Crear respuestas de error consistentes
- ⏳ Logging de errores para debugging
- ⏳ Rollback de transacciones en caso de fallo

### **Fase 5: Seguridad y Testing** ⏳

#### 5.1 Seguridad ⏳ **PENDIENTE**

- ⏳ Implementar validaciones de seguridad adicionales
- ⏳ Configurar headers de seguridad
- ⏳ Rate limiting básico
- ⏳ Logs de seguridad

#### 5.2 Testing ⏳ **PENDIENTE**

- ⏳ Configurar pytest y testing framework
- ⏳ Tests unitarios para cada servicio
- ⏳ Tests de integración para el flujo completo
- ⏳ Tests de validación de archivos

### **Fase 6: Deployment** ⏳

#### 6.1 Configuración de Producción ⏳ **PENDIENTE**

- ⏳ Configurar variables de entorno para producción
- ⏳ Optimizar configuración de FastAPI
- ⏳ Configurar logging para producción
- ⏳ Documentación de deployment

## 🔧 Dependencias Instaladas

```toml
[tool.poetry.dependencies]
python = "^3.13"
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlalchemy = "^2.0.23"
alembic = "^1.12.1"
psycopg2-binary = "^2.9.9"
python-multipart = "^0.0.6"
python-dotenv = "^1.0.0"
assemblyai = "^0.21.0"
openai = "^1.3.0"
resend = "^0.6.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.0.0"
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
httpx = "^0.25.2"
```

## 📁 Estructura del Proyecto Actual

```
src/audiominutes/
├── __init__.py
├── main.py                 # ✅ Aplicación FastAPI principal
├── api/
│   ├── __init__.py
│   └── health.py          # ✅ Endpoint de health check
├── core/
│   ├── __init__.py
│   └── config.py          # ✅ Configuración centralizada
├── models/                # ⏳ Modelos de base de datos (próximo)
├── services/              # ⏳ Servicios externos (próximo)
└── utils/                 # ⏳ Utilidades (próximo)
```

## 📈 Métricas de Éxito MVP

1. **Funcionalidad:** Procesamiento completo de audio → acta → email
2. **Performance:** Procesamiento en < 5 minutos para archivos de 1 hora
3. **Confiabilidad:** 95% de éxito en procesamiento
4. **Costo:** Tracking preciso de costos por procesamiento

## ⚠️ Consideraciones Importantes

- **Sin autenticación:** MVP sin registro de usuarios
- **Sin historial:** No dashboard de archivos procesados
- **Sin API pública:** Solo endpoint interno
- **Limitaciones de archivo:** Tamaño máximo y formatos específicos

## 🎯 Estado Actual

**Progreso General:** 50% completado

- ✅ **Fase 1.1:** Configurar Entorno de Desarrollo (100%)
- ✅ **Fase 1.2:** Configurar Base de Datos (100%)
- ✅ **Fase 2:** API Core (100% - Completada)
- ⏳ **Fase 3:** Integración con Servicios Externos (67% - AssemblyAI y OpenAI completados)
- ⏳ **Fase 4:** Flujo Completo y Robustez (0%)
- ⏳ **Fase 5:** Seguridad y Testing (0%)
- ⏳ **Fase 6:** Deployment (0%)

## 🚀 Próximo Paso

**Fase 3.3: Resend Email Service**

- Configurar cliente de Resend
- Crear template HTML profesional
- Implementar envío automático de actas
- Manejar tracking de emails

---

**Última actualización:** $(date)
**Estado:** En desarrollo activo

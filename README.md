# VoxCliente MVP

**Backend de una app que convierte grabaciones de audio en actas de reuniones profesionales mediante IA**

VoxCliente automatiza la transcripción de reuniones y genera actas profesionales que se envían automáticamente por email. MVP enfocado en validar tracción de usuarios con funcionalidad mínima viable.

## Ejecutar aplicación:

### 🐳 Con Docker (Recomendado)

```bash
# Construir y ejecutar con docker-compose
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### 🐍 Con Python directamente

```bash
# Opción 1: Usando el módulo Python
poetry run python -m voxcliente.main

# Opción 2: Usando uvicorn directamente
poetry run uvicorn src.voxcliente.main:app --host 127.0.0.1 --port 8000

# Opción 3: Con reload para desarrollo
poetry run uvicorn src.voxcliente.main:app --reload --host 127.0.0.1 --port 8000
```

## 🎯 Funcionalidades

### Core Features

- ✅ Upload de archivos de audio
- ✅ Transcripción automática con AssemblyAI
- ✅ Generación de actas profesionales con OpenAI
- ✅ Envío automático por email con Resend
- ✅ Sin registro: solo email + archivo

### Features Técnicas

- ✅ Validación de archivos antes del procesamiento

## 🛠️ Stack Tecnológico

### Backend

- **Framework:** FastAPI + SQLAlchemy
- **Base de datos:** PostgreSQL
- **APIs externas:** AssemblyAI, OpenAI, Resend

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

## 🚀 Configuración y Desarrollo

### Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd voxcliente-backend

# Instalar dependencias con Poetry
poetry install

# Copiar archivo de configuración
cp .env.example .env
# Editar .env con tus API keys
```

### Variables de Entorno

Crea un archivo `.env` con las siguientes variables:

```env
# App settings
DEBUG=false

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/voxcliente

# External API Keys
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
RESEND_API_KEY=your_resend_api_key_here

# File upload settings
MAX_FILE_SIZE_MB=100
ALLOWED_AUDIO_FORMATS=["wav", "mp3", "m4a", "flac", "aac", "ogg"]

# Email settings
FROM_EMAIL=noreply@voxcliente.com
FROM_NAME=VoxCliente

# CORS settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### Ejecutar en Desarrollo

```bash
# Usando Poetry
poetry run python -m voxcliente.main

# O directamente con uvicorn
poetry run uvicorn voxcliente.main:app --reload --host 0.0.0.0 --port 8000
```

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

## 🔧 APIs y Servicios

### AssemblyAI

- **Modelo:** Universal-1 (mejor precisión)
- **Costo:** $0.12/hora de audio
- **Features:** Transcripción, speaker detection

### OpenAI

- **Modelo:** GPT-4 (actas profesionales)
- **Costo:** Variable por tokens
- **Prompt:** Optimizado para formato de actas

### Resend

- **Plan:** Gratuito (3,000 emails/mes)
- **Templates:** HTML profesional
- **Tracking:** Opens, clicks

## ⚠️ Limitaciones MVP

- **Autenticación:** Sin registro de usuarios
- **Historial:** Sin dashboard de archivos procesados
- **API:** Sin API pública

## 🔐 Seguridad

### Validaciones implementadas

- Formato de email válido
- Tipos de archivo permitidos sólo audio (.wav, .mp3, .m4a, otros relevantes)
- Sanitización de inputs

### Consideraciones de producción

- HTTPS obligatorio
- CORS configurado correctamente
- Headers de seguridad
- Logs de seguridad

### v1.0.0 (MVP)

- ✅ Upload y procesamiento de audio
- ✅ Transcripción con AssemblyAI
- ✅ Generación de actas con OpenAI
- ✅ Envío automático por email

**VoxCliente** - Transforma tus reuniones en actas profesionales automáticamente 🎤→📄

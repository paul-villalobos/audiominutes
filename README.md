# AudioMinutes MVP

**Backend de una app que convierte grabaciones de audio en actas de reuniones profesionales mediante IA**

AudioMinutes automatiza la transcripción de reuniones y genera actas profesionales que se envían automáticamente por email. MVP enfocado en validar tracción de usuarios con funcionalidad mínima viable.

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

**AudioMinutes** - Transforma tus reuniones en actas profesionales automáticamente 🎤→📄

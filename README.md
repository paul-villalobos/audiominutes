# AudioMinutes MVP

**Aplicación web que convierte grabaciones de audio en actas de reuniones profesionales mediante IA**

AudioMinutes automatiza la transcripción de reuniones y genera actas profesionales que se envían automáticamente por email. MVP enfocado en validar tracción de usuarios con funcionalidad mínima viable.

## 🎯 Funcionalidades

### Core Features
- ✅ Upload de archivos de audio (máximo 15 minutos)
- ✅ Transcripción automática con AssemblyAI
- ✅ Generación de actas profesionales con OpenAI
- ✅ Envío automático por email con Resend
- ✅ Sin registro: solo email + archivo

### Features Técnicas
- ✅ Sistema de whitelist para duración ilimitada (equipo interno)
- ✅ Tracking de costos por usuario (AssemblyAI + OpenAI)
- ✅ Analytics básico (Google Analytics + contador interno)
- ✅ Geolocalización por IP
- ✅ Validación de archivos antes del procesamiento

## 🏗️ Arquitectura

```
[Frontend Nginx] ←→ [FastAPI Backend] ←→ [PostgreSQL]
                            ↓
            [AssemblyAI] + [OpenAI] + [Resend]
```

## 🛠️ Stack Tecnológico

### Backend
- **Framework:** FastAPI + SQLAlchemy
- **Base de datos:** PostgreSQL
- **APIs externas:** AssemblyAI, OpenAI, Resend
- **Deployment:** Docker + EasyPanel

### Frontend
- **Tecnología:** HTML + Vanilla JS + CSS
- **Servidor:** Nginx estático
- **UX:** Upload → Loading → Resultado por email

### Infrastructure
- **Hosting:** Vultr VPS con EasyPanel
- **Containers:** FastAPI + Nginx + PostgreSQL
- **Orchestration:** Docker Compose

## 📁 Estructura del Proyecto

```
audioministutes/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # FastAPI app principal
│   ├── models.py               # SQLAlchemy models
│   ├── database.py             # Database configuration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── assembly.py         # AssemblyAI integration
│   │   ├── openai_service.py   # OpenAI integration
│   │   └── email_service.py    # Resend email service
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py       # Email, audio validation
│   │   ├── geolocation.py      # IP geolocation
│   │   └── cost_calculator.py  # API cost tracking
│   └── alembic/               # Database migrations
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Instalación y Setup

### Prerrequisitos
- Docker y Docker Compose
- Cuentas en: AssemblyAI, OpenAI, Resend, Google Analytics
- Vultr VPS con EasyPanel configurado

### 1. Clonar el repositorio
```bash
git clone https://github.com/tuusuario/audioministutes.git
cd audioministutes
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
```

Editar `.env` con tus API keys:
```env
# Database
DATABASE_URL=postgresql://audiominutes:password@db:5432/audiominutes

# API Keys
ASSEMBLYAI_API_KEY=tu_api_key_aqui
OPENAI_API_KEY=tu_api_key_aqui
RESEND_API_KEY=tu_api_key_aqui

# Configuración
WHITELIST_EMAILS=tu@email.com,equipo@empresa.com
MAX_DURATION_MINUTES=15
GA_TRACKING_ID=G-XXXXXXXXXX

# Costos (USD por hora/token)
ASSEMBLYAI_COST_PER_HOUR=0.12
OPENAI_COST_PER_1K_TOKENS=0.002
```

### 3. Desarrollo local
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Aplicar migraciones
docker-compose exec backend alembic upgrade head
```

La aplicación estará disponible en:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- Documentación: http://localhost:8000/docs

### 4. Testing
```bash
# Tests unitarios
docker-compose exec backend pytest

# Test de integración completa
curl -X POST "http://localhost:8000/upload" \
  -F "email=test@example.com" \
  -F "audio=@test_audio.wav"
```

## 🚢 Deployment en EasyPanel

### 1. Preparar para producción
```bash
# Construir imágenes de producción
docker-compose -f docker-compose.prod.yml build

# Push a registry (opcional)
docker tag audioministutes_backend:latest your-registry/audioministutes:backend
docker push your-registry/audioministutes:backend
```

### 2. Configurar en EasyPanel
1. Crear nuevo proyecto "AudioMinutes"
2. Agregar servicios:
   - **PostgreSQL Database**
   - **FastAPI Backend** (puerto 8000)
   - **Nginx Frontend** (puerto 80)
3. Configurar variables de entorno
4. Configurar networking entre servicios
5. Deploy y verificar

### 3. Configurar dominio
```bash
# En EasyPanel, configurar:
# - Dominio personalizado
# - SSL automático
# - Health checks
```

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
    country VARCHAR(2),
    transcript_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'processing'
);

-- Índices para analytics
CREATE INDEX idx_usage_logs_email ON usage_logs(email);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);
CREATE INDEX idx_usage_logs_country ON usage_logs(country);
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

## 📈 Métricas y Analytics

### Google Analytics 4
- Pageviews y sesiones
- Conversión upload → email enviado
- Geolocalización de usuarios
- Tiempo en página

### Métricas internas
```sql
-- Usuarios únicos por día
SELECT DATE(created_at), COUNT(DISTINCT email) 
FROM usage_logs 
GROUP BY DATE(created_at);

-- Costos promedio por usuario
SELECT AVG(assembly_cost + openai_cost) as avg_cost 
FROM usage_logs 
WHERE status = 'completed';

-- Países con más usuarios
SELECT country, COUNT(*) as users 
FROM usage_logs 
GROUP BY country 
ORDER BY users DESC;
```

## ⚠️ Limitaciones MVP

- **Duración:** 15 minutos máximo (usuarios regulares)
- **Formato:** Un solo formato de acta (no personalizable)
- **Autenticación:** Sin registro de usuarios
- **Historial:** Sin dashboard de archivos procesados
- **API:** Sin API pública
- **Idiomas:** Solo español (configurable)

## 🔐 Seguridad

### Validaciones implementadas
- Formato de email válido
- Duración de audio máxima
- Tipos de archivo permitidos (.wav, .mp3, .m4a)
- Rate limiting básico
- Sanitización de inputs

### Consideraciones de producción
- HTTPS obligatorio
- CORS configurado correctamente
- Headers de seguridad
- Logs de seguridad
- Backup de database

## 🚨 Monitoring y Troubleshooting

### Logs importantes
```bash
# Ver logs en tiempo real
docker-compose logs -f backend

# Errores específicos de APIs
grep "ERROR" /var/log/audioministutes/app.log

# Costos por día
docker-compose exec backend python -c "
from models import usage_logs
print(usage_logs.daily_cost_report())
"
```

### Alertas recomendadas
- Costos diarios > $10 USD
- Tasa de error > 5%
- Latencia promedio > 60 segundos
- Espacio en disco < 1GB

## 💰 Costos Estimados

### Por archivo de 10 minutos promedio:
- **AssemblyAI:** $0.02 USD
- **OpenAI:** $0.01 USD
- **Total:** ~$0.03 USD por acta

### Escalabilidad:
- **100 archivos/mes:** $3 USD
- **1,000 archivos/mes:** $30 USD
- **10,000 archivos/mes:** $300 USD

## 🗺️ Roadmap Post-MVP

Si hay tracción positiva:
- [ ] Múltiples formatos de acta
- [ ] Dashboard de usuario con historial
- [ ] Sistema de autenticación
- [ ] API pública con rate limiting
- [ ] Identificación automática de speakers
- [ ] Límites personalizados por usuario
- [ ] Integración con calendarios
- [ ] Webhook notifications
- [ ] Soporte multi-idioma

## 🤝 Contribución

1. Fork el repositorio
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Changelog

### v1.0.0 (MVP)
- ✅ Upload y procesamiento de audio
- ✅ Transcripción con AssemblyAI
- ✅ Generación de actas con OpenAI
- ✅ Envío automático por email
- ✅ Tracking de costos y analytics
- ✅ Deploy en EasyPanel

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Para preguntas o problemas:
- 📧 Email: soporte@audioministutes.com
- 📋 Issues: GitHub Issues
- 📖 Docs: `/docs` endpoint del API

---

**AudioMinutes** - Transforma tus reuniones en actas profesionales automáticamente 🎤→📄
# 📊 Plan de Implementación: Indicadores de Crecimiento y Costos

## 🎯 Objetivo

Implementar un sistema completo de métricas para medir **Activación**, **Retención**, **Referral** y **Costos** que permita definir un modelo de pricing sostenible y optimizar el crecimiento del negocio.

## 📋 Resumen Ejecutivo

### Indicadores a Implementar

- **🔹 Activación**: Número de actas generadas por semana, % de usuarios que llegan al aha moment
- **🔄 Retención**: 2nd Acta Rate, APU/week, Retention Curve
- **📤 Referral**: % de actas compartidas, Invitation Rate
- **💰 Costos**: Costo por acta, costo por usuario/mes, desglose por proveedor

### Modelo de Datos

- **2 tablas principales**: `user_events` (eventos atómicos) y `user_profiles` (perfiles de usuario)
- **BI-friendly**: Estructura compatible con Power BI, Tableau, SQL directo
- **Escalable**: Fácil agregar nuevos eventos y métricas

---

## 🏗️ Arquitectura del Sistema

### 1. Modelo de Datos

#### Tabla: `user_events` (Eventos Atómicos)

```python
class UserEvent(Base):
    __tablename__ = "user_events"

    # Claves
    id = Column(Integer, primary_key=True)
    event_id = Column(String(36), unique=True, nullable=False)  # UUID
    user_email = Column(String(255), nullable=False, index=True)

    # Tiempo
    event_datetime = Column(DateTime, nullable=False, index=True)

    # Dimensiones de negocio
    event_type = Column(String(50), nullable=False, index=True)
    event_category = Column(String(30), nullable=False, index=True)  # 'activation', 'retention', 'referral', 'cost'

    # Métricas numéricas
    duration_minutes = Column(Float, nullable=True)  # Duración del audio
    file_size_mb = Column(Float, nullable=True)  # Tamaño del archivo
    cost_usd = Column(Float, nullable=True)  # Costo del evento

    # Dimensiones adicionales
    user_cohort = Column(String(20), nullable=True, index=True)  # Calculado automáticamente
    referral_source = Column(String(50), nullable=True, index=True)

    # Datos flexibles
    event_metadata = Column(JSON, nullable=True)  # Datos específicos del evento
    cost_breakdown = Column(JSON, nullable=True)  # Desglose de costos

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

#### Tabla: `user_profiles` (Perfiles de Usuario)

```python
class UserProfile(Base):
    __tablename__ = "user_profiles"

    # Clave primaria
    email = Column(String(255), primary_key=True)

    # Fechas importantes
    first_seen_date = Column(Date, nullable=False, index=True)
    first_acta_date = Column(Date, nullable=True, index=True)
    last_activity_date = Column(Date, nullable=True, index=True)

    # Métricas pre-calculadas
    total_actas = Column(Integer, default=0, nullable=False)
    total_downloads = Column(Integer, default=0, nullable=False)
    total_shares = Column(Integer, default=0, nullable=False)
    total_referrals = Column(Integer, default=0, nullable=False)
    total_cost_usd = Column(Float, default=0, nullable=False)

    # Dimensiones de usuario
    user_cohort = Column(String(20), nullable=False, index=True)
    user_segment = Column(String(30), nullable=True, index=True)  # 'new', 'active', 'churned', 'power_user'
    referral_source = Column(String(50), nullable=True, index=True)

    # Flags de estado
    is_activated = Column(Boolean, default=False, nullable=False, index=True)
    is_retained = Column(Boolean, default=False, nullable=False, index=True)
    is_referrer = Column(Boolean, default=False, nullable=False, index=True)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. Servicios de Tracking

#### Servicio: `MetricsService`

```python
class MetricsService:
    """Servicio para tracking de métricas y eventos."""

    def __init__(self, db_session):
        self.db = db_session

    def track_event(self, event_type: str, user_email: str, event_data: dict):
        """Registrar evento en la base de datos."""
        pass

    def calculate_user_cohort(self, date: datetime) -> str:
        """Calcular cohorte basada en la fecha."""
        pass

    def update_user_profile(self, user_email: str, event_data: dict):
        """Actualizar perfil de usuario con nuevos datos."""
        pass

    def get_activation_metrics(self, start_date: date, end_date: date) -> dict:
        """Calcular métricas de activación."""
        pass

    def get_retention_metrics(self, start_date: date, end_date: date) -> dict:
        """Calcular métricas de retención."""
        pass

    def get_referral_metrics(self, start_date: date, end_date: date) -> dict:
        """Calcular métricas de referral."""
        pass

    def get_cost_metrics(self, start_date: date, end_date: date) -> dict:
        """Calcular métricas de costos."""
        pass
```

---

## 📊 Eventos a Capturar

### 🔹 ACTIVACIÓN (Aha Moment)

#### Eventos:

1. **`form_submit`**

   - **Cuándo**: Usuario envía formulario con email y archivo
   - **Dónde**: Al inicio del endpoint `/transcribe`
   - **Datos**: `email`, `filename`, `file_size_mb`
   - **Propósito**: Contar usuarios que intentan usar el servicio

2. **`acta_generated`**

   - **Cuándo**: Acta generada exitosamente y enviada por email
   - **Dónde**: Al final del endpoint `/transcribe` (después de enviar email)
   - **Datos**: `email`, `filename`, `duration_minutes`, `file_size_mb`
   - **Propósito**: Contar usuarios que llegan al "aha moment"

3. **`acta_downloaded`**
   - **Cuándo**: Usuario descarga acta desde el email
   - **Dónde**: Tracking en email (pixel tracking o link tracking)
   - **Datos**: `email`, `filename`, `download_timestamp`
   - **Propósito**: Confirmar que el usuario realmente recibió y usó el acta

#### Indicadores:

- **Actas generadas por semana**: Contar eventos `acta_generated` por semana
- **% Activación**: `(usuarios con acta_generated) ÷ (usuarios con form_submit)`

### 🔄 RETENCIÓN (Repetición del Aha)

#### Eventos:

4. **`second_acta_generated`**

   - **Cuándo**: Usuario genera su segunda acta
   - **Dónde**: Al final del endpoint `/transcribe` (si es segunda acta del usuario)
   - **Datos**: `email`, `filename`, `duration_minutes`, `days_since_first_acta`
   - **Propósito**: Medir 2nd Acta Rate

5. **`weekly_acta_generated`**

   - **Cuándo**: Usuario genera acta en semana diferente a la anterior
   - **Dónde**: Al final del endpoint `/transcribe`
   - **Datos**: `email`, `filename`, `week_number`, `actas_this_week`
   - **Propósito**: Medir APU/week (Actas por Usuario por semana)

6. **`retention_check`**
   - **Cuándo**: Usuario genera acta después de X días
   - **Dónde**: Al final del endpoint `/transcribe`
   - **Datos**: `email`, `filename`, `days_since_first_acta`, `retention_period`
   - **Propósito**: Medir Retention Curve (Día 1, 7, 30)

#### Indicadores:

- **2nd Acta Rate**: % usuarios que generan segunda acta en 7 días
- **APU/week**: Actas por usuario por semana
- **Retention Curve**: Retención en días 1, 7, 30

### 📤 REFERRAL (Viral Loop)

#### Eventos:

7. **`acta_shared`**

   - **Cuándo**: Usuario comparte acta (link o forward)
   - **Dónde**: Tracking en email o en dashboard
   - **Datos**: `email`, `filename`, `share_method`, `share_timestamp`
   - **Propósito**: Medir % de actas compartidas

8. **`referral_sent`**

   - **Cuándo**: Usuario recomienda VoxCliente a un colega
   - **Dónde**: Formulario de referido o botón de compartir
   - **Datos**: `email`, `referral_email`, `referral_method`, `referral_timestamp`
   - **Propósito**: Medir Invitation Rate

9. **`referral_converted`**
   - **Cuándo**: Usuario referido genera su primera acta
   - **Dónde**: Al final del endpoint `/transcribe` (si es usuario referido)
   - **Datos**: `email`, `referrer_email`, `filename`, `conversion_timestamp`
   - **Propósito**: Medir efectividad de referidos

#### Indicadores:

- **% Actas compartidas**: Actas compartidas en primeros 7 días
- **Invitation Rate**: Usuarios que recomiendan VoxCliente después del primer aha

### 💰 COSTOS (Modelo de Pricing)

#### Eventos:

10. **`transcription_cost`**

    - **Cuándo**: Después de transcribir audio con AssemblyAI
    - **Datos**: `duration_minutes`, `cost_usd`, `provider` (AssemblyAI)
    - **Cálculo**: `duration_minutes * $0.006`

11. **`llm_processing_cost`**

    - **Cuándo**: Después de generar acta con OpenAI
    - **Datos**: `input_tokens`, `output_tokens`, `cost_usd`, `model` (GPT-4.1-mini)
    - **Cálculo**: `(input_tokens * $0.00015 + output_tokens * $0.0006) / 1000`

12. **`email_cost`**

    - **Cuándo**: Después de enviar email con Resend
    - **Datos**: `email_count`, `cost_usd`, `provider` (Resend)
    - **Cálculo**: `email_count * $0.0004`

13. **`total_acta_cost`**
    - **Cuándo**: Al final del proceso completo
    - **Datos**: `total_cost_usd`, `cost_breakdown`, `user_email`
    - **Cálculo**: `transcription_cost + llm_processing_cost + email_cost`

#### Indicadores:

- **Costo Promedio por Acta (CPA)**: `total_cost_usd / total_actas_generated`
- **Costo Promedio por Usuario al Mes (CPU/Month)**: `SUM(total_cost_usd) / COUNT(DISTINCT user_email) / months`
- **Costo por Minuto de Audio**: `SUM(transcription_cost) / SUM(duration_minutes)`
- **Costo por Token de LLM**: `SUM(llm_processing_cost) / SUM(input_tokens + output_tokens)`

---

## 🚀 Plan de Implementación

### Fase 1: Fundación (Semana 1)

**Objetivo**: Crear modelo de datos y servicios básicos

#### Tareas:

1. **Crear modelos de datos**

   - Implementar `UserEvent` y `UserProfile` en `models.py`
   - Crear migración de base de datos
   - Configurar índices para rendimiento

2. **Crear `MetricsService`**

   - Implementar funciones básicas de tracking
   - Función para calcular cohortes
   - Función para actualizar perfiles de usuario

3. **Modificar endpoint `/transcribe`**
   - Agregar tracking de eventos básicos
   - Registrar `form_submit` al inicio
   - Registrar `acta_generated` al final
   - Mantener compatibilidad con código existente

#### Entregables:

- ✅ Modelos de datos implementados
- ✅ Migración de base de datos creada
- ✅ `MetricsService` básico funcionando
- ✅ Endpoint `/transcribe` con tracking básico

### Fase 2: Métricas Core (Semana 2)

**Objetivo**: Implementar cálculo de métricas principales

#### Tareas:

1. **Implementar métricas de activación**

   - Función para calcular % de activación
   - Función para contar actas por semana
   - Endpoint `/metrics/activation`

2. **Implementar métricas de retención**

   - Función para calcular 2nd Acta Rate
   - Función para calcular APU/week
   - Función para calcular Retention Curve
   - Endpoint `/metrics/retention`

3. **Implementar métricas de referral**
   - Función para calcular % de actas compartidas
   - Función para calcular Invitation Rate
   - Endpoint `/metrics/referral`

#### Entregables:

- ✅ Endpoints de métricas funcionando
- ✅ Cálculos de activación, retención y referral
- ✅ Testing de métricas

### Fase 3: Tracking de Costos (Semana 3)

**Objetivo**: Implementar tracking detallado de costos

#### Tareas:

1. **Modificar servicios para tracking de costos**

   - `AssemblyAIService`: Calcular costo de transcripción
   - `OpenAIService`: Calcular costo de tokens
   - `ResendEmailService`: Calcular costo de email

2. **Implementar métricas de costos**

   - Función para calcular CPA (Costo por Acta)
   - Función para calcular CPU/Month (Costo por Usuario/Mes)
   - Función para desglose de costos por proveedor
   - Endpoint `/metrics/costs`

3. **Integrar tracking de costos en endpoint `/transcribe`**
   - Registrar eventos de costo
   - Calcular costo total por acta
   - Actualizar perfil de usuario con costos

#### Entregables:

- ✅ Tracking de costos implementado
- ✅ Métricas de costos funcionando
- ✅ Desglose de costos por proveedor

### Fase 4: Dashboard y Referral (Semana 4)

**Objetivo**: Crear dashboard y sistema de referral

#### Tareas:

1. **Crear dashboard HTML**

   - Página estática que consume endpoints de métricas
   - Gráficos básicos con Chart.js
   - Diseño responsive y simple
   - Actualización automática cada 5 minutos

2. **Implementar sistema de referral**

   - Botones de compartir en emails
   - Tracking de clicks en links de compartir
   - Sistema simple de referidos con códigos únicos
   - Formulario de referido

3. **Implementar tracking de descarga**
   - Pixel tracking en emails
   - Link tracking para descargas
   - Endpoint `/track/download`

#### Entregables:

- ✅ Dashboard HTML funcionando
- ✅ Sistema de referral implementado
- ✅ Tracking de descarga funcionando

### Fase 5: Refinamiento y Optimización (Semana 5)

**Objetivo**: Optimizar rendimiento y agregar funcionalidades avanzadas

#### Tareas:

1. **Optimizar consultas**

   - Revisar y optimizar índices
   - Implementar consultas eficientes
   - Agregar caching para métricas frecuentes

2. **Agregar funcionalidades avanzadas**

   - Exportación de datos en CSV/JSON
   - Alertas por email para métricas críticas
   - Comparación de cohortes
   - Análisis de tendencias

3. **Documentación y testing**
   - Documentar endpoints de métricas
   - Crear ejemplos de uso
   - Testing completo del sistema
   - Documentación para herramientas BI

#### Entregables:

- ✅ Sistema optimizado y documentado
- ✅ Exportación de datos implementada
- ✅ Testing completo
- ✅ Documentación para BI

---

## 📊 Endpoints de Métricas

### Endpoints de Growth

```
GET /metrics/activation
GET /metrics/retention
GET /metrics/referral
GET /metrics/summary
```

### Endpoints de Costos

```
GET /metrics/costs/summary
GET /metrics/costs/per-user
GET /metrics/costs/per-acta
GET /metrics/costs/breakdown
```

### Endpoints de Exportación

```
GET /export/events?start_date=2024-01-01&end_date=2024-12-31&format=csv
GET /export/metrics/daily?start_date=2024-01-01&end_date=2024-12-31
GET /export/users?segment=active&format=csv
```

### Endpoints de Tracking

```
GET /track/download?email=user@example.com&filename=meeting.wav
POST /track/share
POST /track/referral
```

---

## 💡 Ejemplos de Respuestas de API

### GET /metrics/activation

```json
{
  "activation": {
    "actas_this_week": 45,
    "activation_rate": 0.78,
    "total_users": 120,
    "activated_users": 94,
    "trend_7_days": 0.15
  }
}
```

### GET /metrics/retention

```json
{
  "retention": {
    "second_acta_rate": 0.35,
    "apu_this_week": 1.8,
    "retention_curve": {
      "day_1": 0.95,
      "day_7": 0.42,
      "day_30": 0.18
    },
    "cohort_analysis": {
      "2024-W01": { "users": 25, "retention_30d": 0.2 },
      "2024-W02": { "users": 30, "retention_30d": 0.25 }
    }
  }
}
```

### GET /metrics/costs/summary

```json
{
  "costs": {
    "total_cost_usd": 125.5,
    "total_actas": 450,
    "total_users": 120,
    "avg_cost_per_acta": 0.28,
    "avg_cost_per_user_month": 1.05,
    "cost_breakdown": {
      "transcription": 67.5,
      "llm_processing": 45.2,
      "email": 12.8
    },
    "pricing_recommendations": {
      "pay_per_use": 2.99,
      "monthly_subscription": 9.99,
      "annual_subscription": 99.99
    }
  }
}
```

---

## 🎯 Modelo de Pricing Recomendado

### Análisis de Costos Base

- **Costo por acta**: ~$0.28 (transcripción + LLM + email)
- **Costo por usuario/mes**: ~$1.05 (4 actas promedio)
- **Margen recomendado**: 3-5x el costo

### Opciones de Pricing

1. **Pay-per-use**: $2.99 por acta (10x margen)
2. **Suscripción Mensual**: $9.99/mes hasta 10 actas (9x margen)
3. **Suscripción Anual**: $99.99/año hasta 120 actas (8x margen)
4. **Enterprise**: $29.99/mes actas ilimitadas (variable)

---

## 🔧 Configuración Técnica

### Variables de Entorno

```bash
# Costos por proveedor
ASSEMBLYAI_COST_PER_MINUTE=0.006
OPENAI_INPUT_COST_PER_1K_TOKENS=0.00015
OPENAI_OUTPUT_COST_PER_1K_TOKENS=0.0006
RESEND_COST_PER_EMAIL=0.0004

# Configuración de métricas
METRICS_RETENTION_DAYS=30
METRICS_COHORT_WEEKS=12
METRICS_UPDATE_INTERVAL=300
```

### Índices de Base de Datos

```sql
-- Índices para rendimiento
CREATE INDEX idx_user_events_email_datetime ON user_events(user_email, event_datetime);
CREATE INDEX idx_user_events_type_category ON user_events(event_type, event_category);
CREATE INDEX idx_user_events_cohort ON user_events(user_cohort);
CREATE INDEX idx_user_profiles_cohort ON user_profiles(user_cohort);
CREATE INDEX idx_user_profiles_segment ON user_profiles(user_segment);
```

---

## 📈 Métricas de Éxito

### KPIs Principales

- **Activación**: >70% de usuarios que envían formulario generan acta
- **Retención**: >30% de usuarios generan segunda acta en 7 días
- **Referral**: >15% de usuarios comparten actas en primeros 7 días
- **Costos**: <$0.30 por acta generada

### Métricas de Rendimiento

- **Tiempo de respuesta**: <2 segundos para endpoints de métricas
- **Disponibilidad**: >99.5% uptime
- **Precisión**: 100% de eventos trackeados correctamente

---

## 🚨 Consideraciones Importantes

### Privacidad y Seguridad

- ✅ No almacenar datos sensibles en eventos
- ✅ Anonimizar datos para exportación
- ✅ Cumplir con GDPR/LOPD
- ✅ Implementar rate limiting en endpoints

### Escalabilidad

- ✅ Índices optimizados para consultas frecuentes
- ✅ Agregación de datos para consultas históricas
- ✅ Caching de métricas calculadas
- ✅ Monitoreo de rendimiento

### Mantenimiento

- ✅ Logging detallado de eventos
- ✅ Alertas automáticas para métricas críticas
- ✅ Backup regular de datos de métricas
- ✅ Documentación actualizada

---

## 📚 Recursos Adicionales

### Documentación

- [Guía de implementación de métricas](docs/metrics-implementation.md)
- [API Reference para métricas](docs/metrics-api.md)
- [Guía de integración con BI](docs/bi-integration.md)

### Herramientas Recomendadas

- **Power BI**: Para dashboards empresariales
- **Tableau**: Para análisis avanzados
- **Grafana**: Para monitoreo en tiempo real
- **PostgreSQL**: Para consultas complejas

### Próximos Pasos

1. Revisar y aprobar este plan
2. Asignar recursos y timeline
3. Comenzar implementación por fases
4. Monitorear métricas desde el día 1
5. Iterar y mejorar basado en datos reales

---

**Fecha de creación**: $(date)
**Versión**: 1.0
**Estado**: Pendiente de implementación

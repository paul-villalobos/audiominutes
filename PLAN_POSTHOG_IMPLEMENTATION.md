# 🚀 Plan de Implementación: Indicadores de Growth con PostHog

## 🎯 Objetivo

Implementar un sistema completo de métricas de **Conversión**, **Retención**, **Referral** y **Costos** usando **solo PostHog**, siguiendo la filosofía de **simplicidad primero**.

## 📋 Resumen Ejecutivo

### Indicadores a Implementar

- **🔹 Conversión**: Número de actas generadas, % de éxito en creación de actas
- **🔄 Retención**: 2nd Acta Rate, APU/week, Retention Curve automática
- **📤 Referral**: % de actas compartidas, Invitation Rate
- **💰 Costos**: Costo por acta, costo por usuario/mes, desglose por proveedor

---

---

## 📊 Eventos a Capturar (Simplificados)

### **Resumen de Eventos Consolidados**

| **Sección**    | **Eventos**                                          | **Total**     |
| -------------- | ---------------------------------------------------- | ------------- |
| **CONVERSIÓN** | `form_submit`, `acta_generated`, `acta_downloaded`   | 3             |
| **RETENCIÓN**  | _(Consolidado en `acta_generated`)_                  | 0             |
| **REFERRAL**   | `acta_shared`, `referral_sent`, `referral_converted` | 3             |
| **COSTOS**     | _(Consolidado en `acta_generated`)_                  | 0             |
| **TOTAL**      |                                                      | **6 eventos** |

### 🔹 CONVERSIÓN (Éxito en Creación de Actas)

#### **Evento: `form_submit`**

```python
# Al inicio del endpoint /transcribe
posthog.capture(email, 'form_submit', {
    'filename': file.filename,
    'file_size_mb': file.size / 1024 / 1024,
    'timestamp': datetime.now().isoformat()
})
```

#### **Evento: `acta_generated` (Consolidado)**

```python
# Al final del endpoint /transcribe (después de enviar email)
# Incluye conversión, retención y costos en un solo evento
posthog.capture(email, 'acta_generated', {
    'filename': file.filename,
    'duration_minutes': duration_minutes,
    'file_size_mb': file.size / 1024 / 1024,
    'cost_usd': total_cost,
    'cost_breakdown': {
        'transcription': duration_minutes * 0.006,
        'llm': (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000,
        'email': 0.0004
    },
    'provider_details': {
        'transcription_provider': 'AssemblyAI',
        'llm_model': 'GPT-4.1-mini',
        'email_provider': 'Resend'
    },
    'timestamp': datetime.now().isoformat()
})
```

#### **Indicadores de Conversión Calculables en PostHog**

- ✅ **Tasa de éxito de creación**: `count(acta_generated) / count(form_submit)`
- ✅ **Funnel de conversión**: `form_submit` → `acta_generated` → `acta_downloaded`
- ✅ **Tiempo promedio de procesamiento**: `average(acta_generated.timestamp - form_submit.timestamp)`

#### **Evento: `acta_downloaded`**

```python
# En email tracking (pixel o link)
posthog.capture(email, 'acta_downloaded', {
    'filename': filename,
    'download_timestamp': datetime.now().isoformat()
})
```

### 🔄 RETENCIÓN (Repetición del Aha)

#### **Indicadores de Retención Calculables Automáticamente en PostHog**

- ✅ **Segunda acta rate**: PostHog identifica usuarios con múltiples eventos automáticamente
- ✅ **Retención por día**: Análisis automático de cohortes por fecha
- ✅ **Retención curve**: Generación automática (día 1, 7, 30)
- ✅ **APU (Actas Por Usuario)**: Cálculo automático de promedio por usuario
- ✅ **Cohort analysis**: Agrupación automática por semana de registro

### 📤 REFERRAL (Viral Loop)

#### **Evento: `acta_shared`**

```python
# En botón de compartir o forward de email
posthog.capture(email, 'acta_shared', {
    'filename': filename,
    'share_method': 'email_forward',  # o 'link_copy', 'social_media'
    'share_timestamp': datetime.now().isoformat()
})
```

#### **Evento: `referral_sent`**

```python
# En formulario de referido
posthog.capture(email, 'referral_sent', {
    'referral_email': referral_email,
    'referral_method': 'email_form',  # o 'link', 'social'
    'referral_timestamp': datetime.now().isoformat()
})
```

#### **Evento: `referral_converted`**

```python
# Al final del endpoint /transcribe (si es usuario referido)
posthog.capture(email, 'referral_converted', {
    'referrer_email': referrer_email,
    'filename': file.filename,
    'conversion_timestamp': datetime.now().isoformat()
})
```

### 💰 COSTOS (Modelo de Pricing)

#### **Indicadores de Costo Calculables en PostHog**

- ✅ **Costo promedio por acta**: `average(acta_generated.cost_usd)`
- ✅ **Tendencia de costos**: `group_by_day(acta_generated.cost_usd)`
- ✅ **Distribución de costos**: `histogram(acta_generated.cost_usd)`
- ✅ **Costo total por período**: `sum(acta_generated.cost_usd, "7d")`
- ✅ **Costo por usuario**: `sum(acta_generated.cost_usd) / unique_users(acta_generated)`
- ✅ **Desglose por proveedor**: Análisis automático de `cost_breakdown`

---

## 🚀 Plan de Implementación

### **Fase 1: Setup Básico (Día 1)**

#### **Objetivo**: Configurar PostHog y tracking básico

#### **Tareas**:

1. **Instalar PostHog**

   ```bash
   pip install posthog
   ```

2. **Configurar PostHog**

   ```python
   # En config.py
   POSTHOG_API_KEY = "your-api-key"
   ```

3. **Modificar endpoint `/transcribe`**

   ```python
   # Agregar tracking básico
   from posthog import Posthog

   posthog = Posthog(POSTHOG_API_KEY)

   @app.post("/transcribe")
   async def transcribe_audio(file: UploadFile, email: str):
       # Tracking al inicio
       posthog.capture(email, 'form_submit', {
           'filename': file.filename,
           'file_size_mb': file.size / 1024 / 1024
       })

       # ... tu código existente ...

       # Tracking al final
       posthog.capture(email, 'acta_generated', {
           'filename': file.filename,
           'duration_minutes': duration_minutes,
           'cost_usd': total_cost
       })
   ```

#### **Entregables**:

- ✅ PostHog instalado y configurado
- ✅ Tracking básico funcionando
- ✅ Dashboard automático visible

### **Fase 2: Métricas de Conversión (Día 2)**

#### **Objetivo**: Implementar tracking completo de conversión

#### **Tareas**:

1. **Agregar tracking de descarga**

   ```python
   # En email template (pixel tracking)
   <img src="https://tu-app.com/track/download?email={{email}}&filename={{filename}}" width="1" height="1">

   # Endpoint de tracking
   @app.get("/track/download")
   async def track_download(email: str, filename: str):
       posthog.capture(email, 'acta_downloaded', {
           'filename': filename,
           'download_timestamp': datetime.now().isoformat()
       })
       return Response(content="", media_type="image/png")
   ```

2. **Configurar funnel de conversión**
   - En PostHog: Events → Funnels
   - Crear funnel: `form_submit` → `acta_generated` → `acta_downloaded`

#### **Entregables**:

- ✅ Tracking de descarga funcionando
- ✅ Funnel de conversión configurado
- ✅ Métricas de conversión visibles

### **Fase 3: Métricas de Retención (Día 3)**

#### **Objetivo**: Configurar análisis automático de retención en PostHog

#### **Tareas**:

1. **Configurar análisis de retención en PostHog**

   **Paso 1: Crear Insight de Retención**

   - Ir a PostHog → Insights → New Insight
   - Seleccionar "Retention" como tipo de insight
   - Configurar:
     - **Event**: `acta_generated`
     - **Period**: 1 day, 7 days, 30 days
     - **Group by**: None (todos los usuarios)

   **Paso 2: Crear Cohort Analysis**

   - Ir a PostHog → Cohorts → New Cohort
   - Crear cohorte "Usuarios con Segunda Acta"
   - Configurar: usuarios que han generado `acta_generated` más de 1 vez

   **Paso 3: Crear Dashboard de Retención**

   - Ir a PostHog → Dashboards → New Dashboard
   - Agregar gráficos:
     - Retention curve (1d, 7d, 30d)
     - Cohort analysis por semana
     - Segunda acta rate

2. **Configurar alertas de retención**
   - En PostHog: Alerts → New Alert
   - Crear alerta: "Retención 7 días < 30%"
   - Configurar notificación por email/Slack

#### **Entregables**:

- ✅ Análisis de retención configurado automáticamente
- ✅ Dashboard de retención funcionando
- ✅ Alertas de retención configuradas

### **Fase 4: Métricas de Referral (Día 4)**

#### **Objetivo**: Implementar sistema de referral y configurar análisis en PostHog

#### **Tareas**:

1. **Agregar botones de compartir**

   ```html
   <!-- En email template -->
   <a href="https://tu-app.com/share?email={{email}}&filename={{filename}}"
     >Compartir Acta</a
   >
   <a href="https://tu-app.com/refer?email={{email}}">Recomendar VoxCliente</a>
   ```

2. **Crear endpoints de tracking**

   ```python
   @app.get("/share")
   async def track_share(email: str, filename: str):
       posthog.capture(email, 'acta_shared', {
           'filename': filename,
           'share_method': 'email_link'
       })
       return RedirectResponse(url="https://tu-app.com")

   @app.get("/refer")
   async def track_referral(email: str):
       # Mostrar formulario de referido
       return templates.TemplateResponse("referral_form.html", {"email": email})
   ```

3. **Configurar análisis de referral en PostHog**

   **Paso 1: Crear Funnel de Referral**

   - Ir a PostHog → Insights → New Insight
   - Seleccionar "Funnel" como tipo de insight
   - Configurar steps:
     - `acta_generated` → `acta_shared` → `referral_sent` → `referral_converted`

   **Paso 2: Crear Cohort de Usuarios Referidores**

   - Ir a PostHog → Cohorts → New Cohort
   - Crear cohorte "Usuarios Referidores"
   - Configurar: usuarios que han ejecutado `acta_shared`

   **Paso 3: Crear Dashboard de Referral**

   - Ir a PostHog → Dashboards → New Dashboard
   - Agregar gráficos:
     - Funnel de referral
     - % de usuarios que comparten actas
     - Tasa de conversión de referidos

#### **Entregables**:

- ✅ Sistema de referral funcionando
- ✅ Tracking de compartir funcionando
- ✅ Análisis de referral configurado en PostHog

### **Fase 5: Métricas de Costos (Día 5)**

#### **Objetivo**: Implementar tracking consolidado de costos

#### **Tareas**:

1. **Modificar endpoint `/transcribe` para incluir costos**

   ```python
   @app.post("/transcribe")
   async def transcribe_audio(file: UploadFile, email: str):
       # ... código existente de transcripción y generación ...

       # Calcular costos
       transcription_cost = duration_minutes * 0.006
       llm_cost = (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000
       email_cost = 0.0004
       total_cost = transcription_cost + llm_cost + email_cost

       # Tracking consolidado con todos los costos
       posthog.capture(email, 'acta_generated', {
           'filename': file.filename,
           'duration_minutes': duration_minutes,
           'file_size_mb': file.size / 1024 / 1024,
           'cost_usd': total_cost,
           'cost_breakdown': {
               'transcription': transcription_cost,
               'llm': llm_cost,
               'email': email_cost
           },
           'provider_details': {
               'transcription_provider': 'AssemblyAI',
               'llm_model': 'GPT-4.1-mini',
               'email_provider': 'Resend'
           },
           'timestamp': datetime.now().isoformat()
       })
   ```

2. **Configurar análisis de costos en PostHog**

   **Paso 1: Crear Insight de Costos**

   - Ir a PostHog → Insights → New Insight
   - Seleccionar "Trends" como tipo de insight
   - Configurar:
     - **Event**: `acta_generated`
     - **Property**: `cost_usd`
     - **Aggregation**: Average, Sum
     - **Breakdown**: Por día/semana

   **Paso 2: Crear Insight de Distribución de Costos**

   - Ir a PostHog → Insights → New Insight
   - Seleccionar "Distribution" como tipo de insight
   - Configurar:
     - **Event**: `acta_generated`
     - **Property**: `cost_usd`
     - **Chart type**: Histogram

   **Paso 3: Crear Insight de Desglose por Proveedor**

   - Ir a PostHog → Insights → New Insight
   - Seleccionar "Breakdown" como tipo de insight
   - Configurar:
     - **Event**: `acta_generated`
     - **Property**: `cost_breakdown.transcription`, `cost_breakdown.llm`, `cost_breakdown.email`

   **Paso 4: Configurar Alertas de Costos**

   - En PostHog: Alerts → New Alert
   - Crear alerta: "Costo promedio por acta > $0.30"
   - Configurar notificación por email/Slack

#### **Entregables**:

- ✅ Tracking consolidado de costos funcionando
- ✅ Análisis automático de costos configurado
- ✅ Métricas de costos visibles con 1 evento

### **Fase 6: Dashboard y Alertas (Día 6)**

#### **Objetivo**: Configurar dashboard completo y alertas

#### **Tareas**:

1. **Configurar dashboard completo en PostHog**

   **Paso 1: Crear Dashboard Principal**

   - Ir a PostHog → Dashboards → New Dashboard
   - Nombre: "VoxCliente Analytics Dashboard"

   **Paso 2: Agregar Gráficos de Conversión**

   - Agregar Insight: Funnel de conversión (form_submit → acta_generated → acta_downloaded)
   - Agregar Insight: Trend de actas generadas por día
   - Agregar Insight: Tasa de éxito de creación por semana

   **Paso 3: Agregar Gráficos de Retención**

   - Agregar Insight: Retention curve (1d, 7d, 30d)
   - Agregar Insight: Cohort analysis por semana
   - Agregar Insight: Segunda acta rate

   **Paso 4: Agregar Gráficos de Costos**

   - Agregar Insight: Costo promedio por acta (trend)
   - Agregar Insight: Distribución de costos (histogram)
   - Agregar Insight: Desglose por proveedor (pie chart)

   **Paso 5: Agregar Gráficos de Referral**

   - Agregar Insight: Funnel de referral
   - Agregar Insight: % de usuarios que comparten actas
   - Agregar Insight: Tasa de conversión de referidos

   **Paso 6: Configurar Actualización Automática**

   - Configurar refresh cada 1 hora
   - Configurar exportación automática a Slack/Email

2. **Configurar alertas críticas**

   **Paso 1: Crear Alerta de Retención**

   - Ir a PostHog → Alerts → New Alert
   - Configurar:
     - **Insight**: Retention (7 días)
     - **Condition**: < 25%
     - **Notification**: Email + Slack
     - **Frequency**: Daily

   **Paso 2: Crear Alerta de Costos**

   - Ir a PostHog → Alerts → New Alert
   - Configurar:
     - **Insight**: Average cost per acta
     - **Condition**: > $0.30
     - **Notification**: Email + Slack
     - **Frequency**: Daily

   **Paso 3: Crear Alerta de Volumen**

   - Ir a PostHog → Alerts → New Alert
   - Configurar:
     - **Insight**: Actas generadas por día
     - **Condition**: < 10
     - **Notification**: Email + Slack
     - **Frequency**: Daily

3. **Crear endpoint de métricas simples**
   ```python
   @app.get("/metrics")
   async def get_metrics():
       """Métricas básicas en JSON."""
       return {
           "actas_this_week": posthog.get_events_count("acta_generated", "7d"),
           "total_users": posthog.get_unique_users("acta_generated", "30d"),
           "conversion_rate": posthog.get_funnel_conversion("form_submit", "acta_generated"),
           "retention_rate": posthog.get_retention("acta_generated", "7d"),
           "avg_cost_per_acta": posthog.get_average("acta_generated", "cost_usd"),
           "total_cost_week": posthog.get_sum("acta_generated", "cost_usd", "7d"),
           "cost_per_user": posthog.get_sum("acta_generated", "cost_usd", "30d") / posthog.get_unique_users("acta_generated", "30d")
       }
   ```

#### **Entregables**:

- ✅ Dashboard completo funcionando
- ✅ Alertas configuradas
- ✅ Endpoint de métricas funcionando

---

## 📊 Dashboard PostHog

### **Vista Principal**

```
📊 VoxCliente Analytics Dashboard
├── 👥 Usuarios
│   ├── Total: 150 usuarios
│   ├── Activos esta semana: 45
│   └── Nuevos esta semana: 12
├── 📄 Actas
│   ├── Generadas esta semana: 45
│   ├── Promedio por usuario: 1.8
│   └── Tasa de éxito de creación: 78%
├── 🔄 Retención
│   ├── Día 1: 95%
│   ├── Día 7: 35%
│   └── Día 30: 18%
├── 💰 Costos
│   ├── Promedio por acta: $0.28
│   ├── Total esta semana: $12.60
│   └── Por usuario: $0.84
└── 📤 Referral
    ├── Actas compartidas: 15%
    ├── Referidos enviados: 8%
    └── Conversiones: 25%
```

### **Gráficos Automáticos**

- ✅ **Trend de actas generadas** (por día/semana)
- ✅ **Cohort analysis** (retención por semana)
- ✅ **Funnel de conversión** (form_submit → acta_generated → acta_downloaded)
- ✅ **Distribución de costos** (histograma automático de cost_usd)
- ✅ **Tendencia de costos** (promedio por día/semana)
- ✅ **Desglose de costos** (análisis automático de cost_breakdown)
- ✅ **Retención curve** (día 1, 7, 30)

---

## 🎯 Métricas de Éxito

### **KPIs Principales**

- **Conversión**: >70% de usuarios que envían formulario generan acta exitosamente
- **Retención**: >30% de usuarios generan segunda acta en 7 días
- **Referral**: >15% de usuarios comparten actas en primeros 7 días
- **Costos**: <$0.30 por acta generada

### **Métricas de Rendimiento**

- **Tiempo de respuesta**: <2 segundos para tracking
- **Disponibilidad**: >99.5% uptime
- **Precisión**: 100% de eventos trackeados correctamente

---

## 🔧 Configuración Técnica

### **Variables de Entorno**

```bash
# PostHog
POSTHOG_API_KEY=your-api-key
POSTHOG_HOST=https://app.posthog.com

# Costos por proveedor
ASSEMBLYAI_COST_PER_MINUTE=0.006
OPENAI_INPUT_COST_PER_1K_TOKENS=0.00015
OPENAI_OUTPUT_COST_PER_1K_TOKENS=0.0006
RESEND_COST_PER_EMAIL=0.0004
```

### **Dependencias**

```bash
# Solo una dependencia adicional
pip install posthog
```

---

## 💡 Ventajas de Solo PostHog

### **Simplicidad**

- ✅ **1 línea de código** para tracking básico
- ✅ **Dashboard automático** sin desarrollo
- ✅ **Métricas automáticas** sin configuración
- ✅ **Cero mantenimiento** del sistema
- ✅ **6 eventos consolidados** en lugar de 12 separados

### **Funcionalidades**

- ✅ **Analytics completos** (retention, cohorts, funnels)
- ✅ **Dashboards profesionales**
- ✅ **Alertas automáticas**
- ✅ **Exportación de datos**

### **Escalabilidad**

- ✅ **PostHog maneja** el crecimiento
- ✅ **Infraestructura automática**
- ✅ **Optimización automática**
- ✅ **Soporte técnico incluido**

---

## 🚨 Consideraciones Importantes

### **Privacidad y Seguridad**

- ✅ **No almacenar datos sensibles** en eventos
- ✅ **Anonimizar datos** para exportación
- ✅ **Cumplir con GDPR/LOPD**
- ✅ **Rate limiting** en endpoints de tracking

### **Limitaciones**

- ❌ **Dependencia externa** (PostHog)
- ❌ **Costo** después de 1M eventos/mes
- ❌ **Personalización limitada** del dashboard
- ❌ **Datos offline** no disponibles

---

## 📚 Recursos Adicionales

### **Documentación PostHog**

- [PostHog Python SDK](https://posthog.com/docs/libraries/python)
- [PostHog Events API](https://posthog.com/docs/api/events)
- [PostHog Dashboard Guide](https://posthog.com/docs/user-guides/dashboards)

### **Herramientas Complementarias**

- **Google Sheets**: Para análisis manual de datos
- **Zapier**: Para automatización de alertas
- **Slack**: Para notificaciones de métricas

### **Próximos Pasos**

1. Revisar y aprobar este plan
2. Crear cuenta en PostHog
3. Comenzar implementación por fases
4. Monitorear métricas desde el día 1
5. Iterar y mejorar basado en datos reales

---

**Fecha de creación**: $(date)
**Versión**: 2.0
**Estado**: Listo para implementación
**Filosofía**: Simplicidad primero - 100% de métricas con 1% del esfuerzo
**Mejoras**: Consolidación de eventos (12 → 6), instrucciones detalladas de PostHog

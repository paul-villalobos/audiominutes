# 🚀 Plan de Implementación: Indicadores de Growth con PostHog

## 🎯 Objetivo

Implementar un sistema completo de métricas de **Activación**, **Retención**, **Referral** y **Costos** usando **solo PostHog**, siguiendo la filosofía de **simplicidad primero**.

## 📋 Resumen Ejecutivo

### Filosofía: Simplicidad Primero

- ✅ **1 línea de código** para tracking básico
- ✅ **Dashboard automático** sin desarrollo
- ✅ **Métricas automáticas** sin configuración
- ✅ **Cero mantenimiento** del sistema de métricas

### Indicadores a Implementar

- **🔹 Activación**: Número de actas generadas, % de usuarios que llegan al aha moment
- **🔄 Retención**: 2nd Acta Rate, APU/week, Retention Curve automática
- **📤 Referral**: % de actas compartidas, Invitation Rate
- **💰 Costos**: Costo por acta, costo por usuario/mes, desglose por proveedor

---

## 🏗️ Arquitectura Simplificada

### **Solo PostHog (Sin Base de Datos de Métricas)**

```python
# Instalación súper simple
pip install posthog

# Configuración mínima
from posthog import Posthog
posthog = Posthog('your-api-key')

# Tracking en 1 línea
posthog.capture(email, 'acta_generated', {'cost_usd': total_cost})
```

### **Ventajas de Solo PostHog**

- ✅ **Setup**: 5 minutos
- ✅ **Mantenimiento**: Cero
- ✅ **Dashboard**: Automático
- ✅ **Métricas**: Automáticas
- ✅ **Costo**: Gratis hasta 1M eventos/mes

---

## 📊 Eventos a Capturar

### 🔹 ACTIVACIÓN (Aha Moment)

#### **Evento: `form_submit`**

```python
# Al inicio del endpoint /transcribe
posthog.capture(email, 'form_submit', {
    'filename': file.filename,
    'file_size_mb': file.size / 1024 / 1024,
    'timestamp': datetime.now().isoformat()
})
```

#### **Evento: `acta_generated`**

```python
# Al final del endpoint /transcribe (después de enviar email)
posthog.capture(email, 'acta_generated', {
    'filename': file.filename,
    'duration_minutes': duration_minutes,
    'file_size_mb': file.size / 1024 / 1024,
    'cost_usd': total_cost,
    'timestamp': datetime.now().isoformat()
})
```

#### **Evento: `acta_downloaded`**

```python
# En email tracking (pixel o link)
posthog.capture(email, 'acta_downloaded', {
    'filename': filename,
    'download_timestamp': datetime.now().isoformat()
})
```

### 🔄 RETENCIÓN (Repetición del Aha)

#### **Evento: `second_acta_generated`**

```python
# Al final del endpoint /transcribe (si es segunda acta)
posthog.capture(email, 'second_acta_generated', {
    'filename': file.filename,
    'duration_minutes': duration_minutes,
    'days_since_first_acta': days_since_first,
    'timestamp': datetime.now().isoformat()
})
```

#### **Evento: `weekly_acta_generated`**

```python
# Al final del endpoint /transcribe
posthog.capture(email, 'weekly_acta_generated', {
    'filename': file.filename,
    'week_number': datetime.now().isocalendar()[1],
    'actas_this_week': actas_this_week,
    'timestamp': datetime.now().isoformat()
})
```

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

#### **Evento: `transcription_cost`**

```python
# Después de transcribir con AssemblyAI
posthog.capture(email, 'transcription_cost', {
    'duration_minutes': duration_minutes,
    'cost_usd': duration_minutes * 0.006,
    'provider': 'AssemblyAI',
    'timestamp': datetime.now().isoformat()
})
```

#### **Evento: `llm_processing_cost`**

```python
# Después de generar acta con OpenAI
posthog.capture(email, 'llm_processing_cost', {
    'input_tokens': input_tokens,
    'output_tokens': output_tokens,
    'cost_usd': (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000,
    'model': 'GPT-4.1-mini',
    'timestamp': datetime.now().isoformat()
})
```

#### **Evento: `email_cost`**

```python
# Después de enviar email con Resend
posthog.capture(email, 'email_cost', {
    'email_count': 1,
    'cost_usd': 0.0004,
    'provider': 'Resend',
    'timestamp': datetime.now().isoformat()
})
```

#### **Evento: `total_acta_cost`**

```python
# Al final del proceso completo
posthog.capture(email, 'total_acta_cost', {
    'total_cost_usd': total_cost,
    'cost_breakdown': {
        'transcription': transcription_cost,
        'llm': llm_cost,
        'email': email_cost
    },
    'timestamp': datetime.now().isoformat()
})
```

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
   POSTHOG_HOST = "https://app.posthog.com"
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

### **Fase 2: Métricas de Activación (Día 2)**

#### **Objetivo**: Implementar tracking completo de activación

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

2. **Configurar funnel de activación**
   - En PostHog: Events → Funnels
   - Crear funnel: `form_submit` → `acta_generated` → `acta_downloaded`

#### **Entregables**:

- ✅ Tracking de descarga funcionando
- ✅ Funnel de activación configurado
- ✅ Métricas de activación visibles

### **Fase 3: Métricas de Retención (Día 3)**

#### **Objetivo**: Implementar tracking de retención

#### **Tareas**:

1. **Agregar tracking de segunda acta**

   ```python
   # En endpoint /transcribe
   # Verificar si es segunda acta del usuario
   user_actas = posthog.get_events(email, 'acta_generated')
   if len(user_actas) == 1:  # Es segunda acta
       posthog.capture(email, 'second_acta_generated', {
           'filename': file.filename,
           'days_since_first_acta': days_since_first
       })
   ```

2. **Configurar análisis de retención**
   - En PostHog: Events → Retention
   - Configurar: Event `acta_generated`, períodos 1d, 7d, 30d

#### **Entregables**:

- ✅ Tracking de segunda acta funcionando
- ✅ Análisis de retención configurado
- ✅ Métricas de retención visibles

### **Fase 4: Métricas de Referral (Día 4)**

#### **Objetivo**: Implementar sistema de referral

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

3. **Configurar análisis de referral**
   - En PostHog: Events → Cohorts
   - Crear cohorte: usuarios que han compartido actas

#### **Entregables**:

- ✅ Sistema de referral funcionando
- ✅ Tracking de compartir funcionando
- ✅ Métricas de referral visibles

### **Fase 5: Métricas de Costos (Día 5)**

#### **Objetivo**: Implementar tracking detallado de costos

#### **Tareas**:

1. **Modificar servicios para tracking de costos**

   ```python
   # En AssemblyAIService
   async def transcribe(self, audio_file):
       # ... transcripción existente ...

       # Tracking de costo
       cost = duration_minutes * 0.006
       posthog.capture(email, 'transcription_cost', {
           'duration_minutes': duration_minutes,
           'cost_usd': cost,
           'provider': 'AssemblyAI'
       })

       return transcription

   # En OpenAIService
   async def generate_acta(self, transcription):
       # ... generación existente ...

       # Tracking de costo
       cost = (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000
       posthog.capture(email, 'llm_processing_cost', {
           'input_tokens': input_tokens,
           'output_tokens': output_tokens,
           'cost_usd': cost,
           'model': 'GPT-4.1-mini'
       })

       return acta
   ```

2. **Configurar análisis de costos**
   - En PostHog: Events → Insights
   - Crear gráficos: costo promedio por acta, tendencias de costos

#### **Entregables**:

- ✅ Tracking de costos funcionando
- ✅ Análisis de costos configurado
- ✅ Métricas de costos visibles

### **Fase 6: Dashboard y Alertas (Día 6)**

#### **Objetivo**: Configurar dashboard completo y alertas

#### **Tareas**:

1. **Configurar dashboard en PostHog**

   - Crear dashboard con métricas principales
   - Agregar gráficos de activación, retención, costos
   - Configurar actualización automática

2. **Configurar alertas**

   ```python
   # En PostHog: Alerts
   # Crear alertas para:
   # - Retención < 25%
   # - Costo por acta > $0.30
   # - Actas generadas < 10 por día
   ```

3. **Crear endpoint de métricas simples**
   ```python
   @app.get("/metrics")
   async def get_metrics():
       """Métricas básicas en JSON."""
       return {
           "actas_this_week": posthog.get_events_count("acta_generated", "7d"),
           "total_users": posthog.get_unique_users("acta_generated", "30d"),
           "activation_rate": posthog.get_funnel_conversion("form_submit", "acta_generated"),
           "retention_rate": posthog.get_retention("acta_generated", "7d"),
           "avg_cost": posthog.get_average("acta_generated", "cost_usd")
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
│   └── Tasa de activación: 78%
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
- ✅ **Funnel de activación** (form_submit → acta_generated → acta_downloaded)
- ✅ **Distribución de costos** (por proveedor)
- ✅ **Retención curve** (día 1, 7, 30)

---

## 🎯 Métricas de Éxito

### **KPIs Principales**

- **Activación**: >70% de usuarios que envían formulario generan acta
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
**Versión**: 1.0
**Estado**: Listo para implementación
**Filosofía**: Simplicidad primero - 100% de métricas con 1% del esfuerzo

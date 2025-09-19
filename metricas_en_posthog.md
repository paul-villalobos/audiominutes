# 📊 Métricas en PostHog - VoxCliente Analytics

## 🎯 Objetivo

Este documento explica todas las métricas que podemos configurar en PostHog utilizando los eventos programados en VoxCliente, siguiendo la filosofía de **simplicidad primero**.

---

## 📋 Eventos Disponibles

### **🔹 Evento: `form_submit`**

**Cuándo se dispara**: Al inicio del endpoint `/transcribe`
**Propósito**: Medir intención del usuario y entrada al funnel

**Propiedades capturadas**:

```json
{
  "filename": "reunion_equipo.mp3",
  "file_size_mb": 12.5,
  "timestamp": "2024-01-15T14:30:00"
}
```

### **🔹 Evento: `acta_generated`**

**Cuándo se dispara**: Al final exitoso del proceso
**Propósito**: Medir éxito del proceso y costos reales

**Propiedades capturadas**:

```json
{
  "filename": "reunion_equipo.mp3",
  "duration_minutes": 3.2,
  "file_size_mb": 12.5,
  "cost_usd": 0.0234,
  "cost_breakdown": {
    "assemblyai_cost_usd": 0.018,
    "openai_cost_usd": 0.005,
    "email_cost_usd": 0.0004
  },
  "openai_usage": {
    "prompt_tokens": 1250,
    "completion_tokens": 800,
    "total_tokens": 2050
  },
  "assemblyai_usage": {
    "audio_duration_seconds": 180,
    "audio_duration_minutes": 3.0,
    "confidence": 0.95
  },
  "email_sent": true,
  "timestamp": "2024-01-15T14:32:15"
}
```

---

## 📊 Métricas de Activación (Aha Moment)

### **🎯 1. Tasa de Conversión del Funnel**

**Fórmula**: `(acta_generated / form_submit) × 100`

**Configuración en PostHog**:

- **Tipo**: Funnel
- **Eventos**: `form_submit` → `acta_generated`
- **Período**: Últimos 30 días
- **Objetivo**: >70% de conversión

**Dashboard**:

```
📊 Funnel de Activación
├── form_submit: 150 usuarios
├── acta_generated: 127 usuarios
└── Tasa de conversión: 84.7% ✅
```

### **🎯 2. Tiempo de Procesamiento**

**Fórmula**: `timestamp_acta_generated - timestamp_form_submit`

**Configuración en PostHog**:

- **Tipo**: Insight
- **Métrica**: Promedio de tiempo entre eventos
- **Filtro**: Solo eventos exitosos (`email_sent: true`)
- **Objetivo**: <3 minutos promedio

**Dashboard**:

```
⏱️ Performance del Sistema
├── Tiempo promedio: 2.8 min ✅
├── Tiempo máximo: 8.1 min
├── Tiempo mínimo: 0.8 min
└── 95% bajo 5 min ✅
```

### **🎯 3. Tasa de Éxito del Email**

**Fórmula**: `(acta_generated con email_sent=true) / (total acta_generated) × 100`

**Configuración en PostHog**:

- **Tipo**: Insight
- **Métrica**: Porcentaje de `email_sent: true`
- **Objetivo**: >95% de emails enviados

**Dashboard**:

```
📧 Calidad del Proceso
├── Actas generadas: 127
├── Emails enviados: 125
└── Tasa de éxito: 98.4% ✅
```

---

## 🔄 Métricas de Retención

### **🎯 4. Usuarios Únicos**

**Fórmula**: `COUNT(DISTINCT distinct_id)`

**Configuración en PostHog**:

- **Tipo**: Insight
- **Métrica**: Usuarios únicos
- **Evento**: `acta_generated`
- **Período**: Últimos 30 días

**Dashboard**:

```
👥 Usuarios Únicos
├── Últimos 30 días: 45 usuarios
├── Últimos 7 días: 12 usuarios
└── Hoy: 3 usuarios
```

### **🎯 5. Frecuencia de Uso**

**Fórmula**: `COUNT(events) / COUNT(DISTINCT distinct_id)`

**Configuración en PostHog**:

- **Tipo**: Insight
- **Métrica**: Eventos por usuario único
- **Evento**: `acta_generated`
- **Objetivo**: >1.5 actas por usuario

**Dashboard**:

```
🔄 Frecuencia de Uso
├── Eventos totales: 127
├── Usuarios únicos: 45
└── Frecuencia promedio: 2.8 actas/usuario ✅
```

### **🎯 6. Análisis de Retención**

**Configuración en PostHog**:

- **Tipo**: Retention
- **Evento**: `acta_generated`
- **Períodos**: 1d, 7d, 30d
- **Objetivo**: >30% retención a 7 días

**Dashboard**:

```
🔄 Análisis de Retención
├── Día 1: 95% ✅
├── Día 7: 35% ✅
└── Día 30: 18%
```

---

## 💰 Métricas de Costos

### **🎯 7. Costo Promedio por Acta**

**Fórmula**: `AVG(cost_usd)`

**Configuración en PostHog**:

- **Tipo**: Insight
- **Métrica**: Promedio de `cost_usd`
- **Evento**: `acta_generated`
- **Objetivo**: <$0.30 por acta

**Dashboard**:

```
💰 Costos por Acta
├── Promedio: $0.125 ✅ (corregido con precios reales)
├── Mínimo: $0.045
├── Máximo: $0.85
└── Mediana: $0.12
```

### **🎯 8. Desglose de Costos por Proveedor**

**Configuración en PostHog**:

- **Tipo**: Insight
- **Métrica**: Promedio por propiedad
- **Propiedades**: `cost_breakdown.*`
- **Objetivo**: Optimizar el proveedor más caro

**Dashboard**:

```
💰 Desglose de Costos
├── AssemblyAI: $0.045 (36%) - $0.0045/min
├── OpenAI: $0.08 (64%) - GPT-5-mini: $0.25/1M input, $2/1M output
└── Email: $0.0004 (0.3%) - $0.0004/email
```

### **🎯 9. Costo Total por Usuario**

**Fórmula**: `SUM(cost_usd) por distinct_id`

**Configuración en PostHog**:

- **Tipo**: Insight
- **Métrica**: Suma de `cost_usd` por usuario
- **Evento**: `acta_generated`
- **Objetivo**: Identificar usuarios de alto valor

**Dashboard**:

```
💰 Costo por Usuario
├── Promedio: $0.84
├── Usuario más caro: $5.20
└── Total procesado: $37.80
```

### **🎯 10. ROI por Usuario**

**Fórmula**: `(valor_usuario) / (costo_total_usuario)`

**Configuración en PostHog**:

- **Tipo**: Insight calculado
- **Métrica**: Ratio de valor/costo
- **Objetivo**: >500% ROI

**Dashboard**:

```
📈 ROI por Usuario
├── Valor promedio: $5.00
├── Costo promedio: $0.84
└── ROI promedio: 595% ✅
```

---

## 📤 Métricas de Referral (Futuras)

### **🎯 11. Tasa de Compartir**

**Evento futuro**: `acta_shared`
**Objetivo**: >15% de usuarios comparten actas

### **🎯 12. Tasa de Referral**

**Evento futuro**: `referral_sent`
**Objetivo**: >10% de usuarios envían referidos

### **🎯 13. Conversión de Referidos**

**Evento futuro**: `referral_converted`
**Objetivo**: >25% de referidos se convierten

---

## 📊 Métricas de Performance

### **🎯 14. Distribución por Tamaño de Archivo**

**Configuración en PostHog**:

- **Tipo**: Insight
- **Métrica**: Distribución de `file_size_mb`
- **Evento**: `form_submit`
- **Objetivo**: Entender preferencias de usuarios

**Dashboard**:

```
📁 Distribución por Tamaño
├── < 5MB: 45% (68 usuarios)
├── 5-20MB: 35% (53 usuarios)
└── > 20MB: 20% (30 usuarios)
```

### **🎯 15. Análisis de Confianza de Transcripción**

**Configuración en PostHog**:

- **Tipo**: Insight
- **Métrica**: Promedio de `confidence`
- **Evento**: `acta_generated`
- **Objetivo**: >90% confianza promedio

**Dashboard**:

```
🎯 Calidad de Transcripción
├── Confianza promedio: 94.2% ✅
├── Confianza mínima: 78.5%
└── Confianza máxima: 98.7%
```

### **🎯 16. Uso de Tokens de OpenAI**

**Configuración en PostHog**:

- **Tipo**: Insight
- **Métrica**: Promedio de `total_tokens`
- **Evento**: `acta_generated`
- **Objetivo**: Optimizar prompts

**Dashboard**:

```
🤖 Uso de OpenAI (GPT-5-mini)
├── Tokens promedio: 2,050
├── Input tokens: 1,250 ($0.00031)
├── Output tokens: 800 ($0.0016)
└── Costo promedio: $0.00191
```

---

## 🚨 Alertas Automáticas

### **🎯 Alertas de Performance**

```python
# Configurar en PostHog Alerts
if conversion_rate < 70%:
    send_alert("Tasa de conversión baja")

if avg_processing_time > 5_minutes:
    send_alert("Tiempo de procesamiento alto")

if email_success_rate < 95%:
    send_alert("Problemas con envío de emails")
```

### **🎯 Alertas de Costos**

```python
if avg_cost_per_acta > 0.30:
    send_alert("Costo promedio alto")

if total_daily_cost > 10.00:
    send_alert("Costo diario alto")

if openai_cost_percentage > 50%:
    send_alert("OpenAI es el mayor costo")
```

### **🎯 Alertas de Usuarios**

```python
if unique_users_today < 5:
    send_alert("Pocos usuarios nuevos")

if retention_7d < 30%:
    send_alert("Retención baja")

if frequency_per_user < 1.5:
    send_alert("Usuarios no activos")
```

---

## 📈 Dashboard Principal

### **🎯 Vista Ejecutiva**

```
📊 VoxCliente Analytics Dashboard
├── 👥 Usuarios
│   ├── Total: 45 usuarios únicos
│   ├── Activos esta semana: 12
│   └── Nuevos esta semana: 8
├── 📄 Actas
│   ├── Generadas esta semana: 35
│   ├── Promedio por usuario: 2.8
│   └── Tasa de activación: 84.7%
├── 🔄 Retención
│   ├── Día 1: 95%
│   ├── Día 7: 35%
│   └── Día 30: 18%
├── 💰 Costos
│   ├── Promedio por acta: $0.125 (GPT-5-mini)
│   ├── Total esta semana: $4.38
│   └── Por usuario: $0.38
└── ⏱️ Performance
    ├── Tiempo promedio: 2.8 min
    ├── Tasa de éxito email: 98.4%
    └── Confianza transcripción: 94.2%
```

---

## 🔧 Configuración en PostHog

### **🎯 1. Crear Dashboard**

1. Ve a **Dashboards** → **New Dashboard**
2. Nombre: "VoxCliente Analytics"
3. Agrega widgets para cada métrica

### **🎯 2. Configurar Funnels**

1. Ve a **Events** → **Funnels**
2. Crea funnel: `form_submit` → `acta_generated`
3. Configura períodos y filtros

### **🎯 3. Configurar Retention**

1. Ve a **Events** → **Retention**
2. Evento: `acta_generated`
3. Períodos: 1d, 7d, 30d

### **🎯 4. Configurar Alertas**

1. Ve a **Alerts** → **New Alert**
2. Configura condiciones y umbrales
3. Configura notificaciones (email, Slack)

---

## 💡 Próximos Pasos

### **🎯 Fase 2: Métricas de Activación**

- ✅ Implementar tracking de descarga
- ✅ Configurar funnel completo
- ✅ Alertas de activación

### **🎯 Fase 3: Métricas de Retención**

- ✅ Tracking de segunda acta
- ✅ Análisis de cohortes
- ✅ Alertas de retención

### **🎯 Fase 4: Métricas de Referral**

- ✅ Sistema de compartir
- ✅ Tracking de referidos
- ✅ Análisis de viralidad

---

## 🎯 Conclusión

Con estos eventos programados, tenemos **16 métricas clave** que nos permiten:

1. **🔹 Medir activación** completa del usuario
2. **🔹 Analizar retención** y comportamiento
3. **🔹 Optimizar costos** por proveedor
4. **🔹 Monitorear performance** del sistema
5. **🔹 Configurar alertas** automáticas
6. **🔹 Crear dashboards** ejecutivos

**Filosofía aplicada**: Simplicidad primero - máximo valor analítico con mínimo esfuerzo de implementación.

---

**Fecha de creación**: $(date)
**Versión**: 1.0
**Estado**: Listo para implementación
**Eventos implementados**: 2/13 (15.4%)
**Métricas disponibles**: 16/16 (100%)

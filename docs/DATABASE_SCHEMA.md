# 🗄️ Esquema de Base de Datos - AudioMinutes

## 📋 Descripción

Este documento describe el esquema de base de datos que la aplicación **AudioMinutes** asume que existe. La aplicación **NO** crea ni administra estas tablas, solo las utiliza.

## 🎯 Tabla Principal

### `usage_logs`

Tabla para tracking de uso y procesamiento de archivos de audio.

```sql
CREATE TABLE usage_logs (
    -- Clave primaria
    id SERIAL PRIMARY KEY,

    -- Campos requeridos
    email VARCHAR(255) NOT NULL,
    duration_minutes FLOAT NOT NULL,

    -- Tracking de costos
    assembly_cost DECIMAL(10,4),
    openai_cost DECIMAL(10,4),

    -- Tracking de procesamiento
    transcript_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'processing' NOT NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);
```

## 📊 Índices para Optimización

```sql
-- Índice por email para búsquedas rápidas
CREATE INDEX idx_usage_logs_email ON usage_logs(email);

-- Índice por fecha de creación para analytics
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);

-- Índice por status para filtros de procesamiento
CREATE INDEX idx_usage_logs_status ON usage_logs(status);

-- Índice compuesto para consultas complejas
CREATE INDEX idx_usage_logs_email_created_at ON usage_logs(email, created_at);
```

## 🔧 Detalles de Campos

### Campos Obligatorios

- **`id`**: Identificador único auto-incremental
- **`email`**: Email del usuario (VARCHAR 255, NOT NULL)
- **`duration_minutes`**: Duración del audio en minutos (FLOAT, NOT NULL)
- **`status`**: Estado del procesamiento (VARCHAR 50, DEFAULT 'processing')
- **`created_at`**: Timestamp de creación (TIMESTAMP, DEFAULT NOW())
- **`updated_at`**: Timestamp de última actualización (TIMESTAMP, DEFAULT NOW())

### Campos Opcionales

- **`assembly_cost`**: Costo de AssemblyAI (DECIMAL 10,4)
- **`openai_cost`**: Costo de OpenAI (DECIMAL 10,4)
- **`transcript_id`**: ID de transcripción de AssemblyAI (VARCHAR 255)

## 📈 Estados de Procesamiento

La aplicación utiliza los siguientes estados en el campo `status`:

- **`processing`**: Procesamiento en curso (estado inicial)
- **`transcribing`**: Transcripción en progreso
- **`generating`**: Generando acta con IA
- **`sending`**: Enviando email
- **`completed`**: Procesamiento completado exitosamente
- **`failed`**: Error en el procesamiento
- **`cancelled`**: Procesamiento cancelado

## 🔍 Consultas Típicas

### Obtener logs por usuario

```sql
SELECT * FROM usage_logs
WHERE email = 'usuario@ejemplo.com'
ORDER BY created_at DESC;
```

### Analytics de uso por fecha

```sql
SELECT
    DATE(created_at) as fecha,
    COUNT(*) as total_procesamientos,
    SUM(duration_minutes) as minutos_totales,
    SUM(assembly_cost + openai_cost) as costo_total
FROM usage_logs
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY fecha DESC;
```

### Logs en procesamiento

```sql
SELECT * FROM usage_logs
WHERE status IN ('processing', 'transcribing', 'generating', 'sending')
ORDER BY created_at ASC;
```

## ⚠️ Consideraciones Importantes

1. **Sin Administración**: La aplicación NO crea, modifica o elimina tablas
2. **Solo Lectura/Escritura**: Solo realiza operaciones CRUD en datos existentes
3. **Índices Requeridos**: Los índices son críticos para el rendimiento
4. **Constraints**: No hay constraints adicionales más allá de los básicos
5. **Backup**: La administración de backups es responsabilidad externa

## 🚀 Configuración de Conexión

La aplicación espera una variable de entorno `DATABASE_URL` con el formato:

```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

Ejemplo:

```
DATABASE_URL=postgresql://audiominutes:password123@localhost:5432/audiominutes_db
```

## 📝 Notas de Implementación

- **PostgreSQL**: La aplicación está optimizada para PostgreSQL
- **Encoding**: UTF-8 recomendado
- **Timezone**: UTC para timestamps
- **Pooling**: La aplicación maneja su propio pool de conexiones
- **Transacciones**: Usa transacciones automáticas para operaciones críticas

---

**Última actualización**: $(date)  
**Versión del esquema**: 1.0  
**Compatible con**: AudioMinutes Backend v0.1.0+

-- =======================================
-- VoxCliente - Esquema Base PostgreSQL
-- Autenticación tercerizada (Opción C)
-- =======================================

-- 1. Usuarios
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referencia al proveedor de autenticación externo
    auth_provider_id TEXT UNIQUE NOT NULL, -- ID del usuario en Auth0/Supabase/etc.
    email VARCHAR(255) UNIQUE NOT NULL,

    -- Fechas importantes
    first_seen_date DATE NOT NULL,
    first_acta_date DATE,
    last_activity_date DATE,

    -- Métricas acumuladas
    total_actas INT DEFAULT 0 NOT NULL,
    total_downloads INT DEFAULT 0 NOT NULL,
    total_shares INT DEFAULT 0 NOT NULL,
    total_referrals INT DEFAULT 0 NOT NULL,
    total_cost_usd NUMERIC(10,2) DEFAULT 0 NOT NULL,

    -- Dimensiones de usuario
    user_cohort VARCHAR(20) NOT NULL,
    user_segment VARCHAR(30), -- 'new', 'active', 'churned', 'power_user'
    referral_source VARCHAR(50),

    -- Flags de estado
    is_activated BOOLEAN DEFAULT FALSE NOT NULL,
    is_retained BOOLEAN DEFAULT FALSE NOT NULL,
    is_referrer BOOLEAN DEFAULT FALSE NOT NULL,

    -- Auditoría
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- 2. Clientes
CREATE TABLE IF NOT EXISTS clients (
    client_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    client_name TEXT NOT NULL,
    industry TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Reuniones
CREATE TABLE IF NOT EXISTS meetings (
    meeting_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- IDs de transcripción
    transcript_id UUID UNIQUE NOT NULL, -- ID interno
    assemblyai_id TEXT UNIQUE NOT NULL, -- ID real de AssemblyAI

    -- Metadata de la reunión
    meeting_date TIMESTAMP NOT NULL,
    duration_minutes NUMERIC(6,2),
    filename TEXT,

    -- Datos enriquecidos por IA
    topics JSONB,
    summary TEXT,
    sentiment VARCHAR(20),
    importance_distribution JSONB,

    -- Métricas de texto
    word_count_total INT,

    -- Costos directos
    transcription_cost NUMERIC(10,4) DEFAULT 0,
    llm_processing_cost NUMERIC(10,4) DEFAULT 0,
    email_cost NUMERIC(10,4) DEFAULT 0,
    total_acta_cost NUMERIC(10,4) DEFAULT 0,

    -- Estado de procesamiento
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

# Plan de Integración PostgreSQL - VoxCliente MVP

## 📋 Resumen Ejecutivo

Integración de FastAPI con PostgreSQL usando SQL directo (asyncpg) para el MVP, manteniendo la filosofía de **simplicidad primero**.

## 🎯 Objetivos

- Conexión básica a PostgreSQL
- Operaciones CRUD mínimas para users, clients, meetings
- Flujo de usuario: procesar acta → login → guardar en BD
- Sin ORMs pesados, sin migraciones complejas

## 🏗️ Estructura de Archivos

```
src/voxcliente/
├── database/
│   ├── __init__.py
│   ├── connection.py (pool asyncpg)
│   ├── queries.py (SQL básico)
│   ├── services.py (user, client, meeting)
│   └── models.py (Pydantic models)
```

## 🔄 Flujo de Usuario

1. **Usuario sube audio + email** → Se procesa acta
2. **Recibe email con acta** → Ve el valor del producto
3. **"¿Guardar acta y acceder a historial?"** → Login con Clerk
4. **Se crea usuario en BD** con datos del acta procesada

## 📦 Dependencias a Agregar

```toml
# pyproject.toml
asyncpg = "^0.29.0"
```

## 🔧 Configuración

### Variables de Entorno

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/voxcliente
```

### config.py

```python
# Agregar a Settings class
database_url: str = Field(env="DATABASE_URL")
```

## 📁 Archivos a Implementar

### 1. database/**init**.py

```python
"""Database module for VoxCliente."""
from .connection import get_db_pool, close_db_pool
from .queries import *
from .services import *
from .models import *

__all__ = ["get_db_pool", "close_db_pool"]
```

### 2. database/connection.py

```python
"""Database connection management."""
import asyncpg
import logging
from typing import Optional
from voxcliente.config import settings

logger = logging.getLogger(__name__)

# Global pool
_db_pool: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    """Get database connection pool."""
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
        logger.info("Database pool created")
    return _db_pool

async def close_db_pool():
    """Close database connection pool."""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None
        logger.info("Database pool closed")
```

### 3. database/models.py

```python
"""Pydantic models for database operations."""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from uuid import UUID

# User Models
class UserCreate(BaseModel):
    auth_provider_id: str
    email: EmailStr
    user_cohort: str = "2024-01"

class UserResponse(BaseModel):
    user_id: UUID
    email: str
    total_cost_usd: Decimal
    total_actas: int
    created_at: datetime

# Client Models
class ClientCreate(BaseModel):
    user_id: UUID
    client_name: str
    industry: Optional[str] = None

class ClientResponse(BaseModel):
    client_id: UUID
    client_name: str
    industry: Optional[str]
    created_at: datetime

# Meeting Models
class MeetingCreate(BaseModel):
    client_id: UUID
    user_id: UUID
    transcript_id: UUID
    assemblyai_id: str
    meeting_date: datetime
    filename: str

class MeetingUpdate(BaseModel):
    duration_minutes: Optional[Decimal] = None
    topics: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    transcription_cost: Optional[Decimal] = None
    llm_processing_cost: Optional[Decimal] = None
    email_cost: Optional[Decimal] = None
    total_acta_cost: Optional[Decimal] = None
    status: Optional[str] = None

class MeetingResponse(BaseModel):
    meeting_id: UUID
    client_id: UUID
    user_id: UUID
    transcript_id: UUID
    assemblyai_id: str
    meeting_date: datetime
    filename: str
    status: str
    total_acta_cost: Decimal
    created_at: datetime
```

### 4. database/queries.py

```python
"""SQL queries for database operations."""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
import asyncpg

# User Queries
async def create_user(conn: asyncpg.Connection, user_data) -> dict:
    """Create new user."""
    query = """
    INSERT INTO users (auth_provider_id, email, user_cohort, first_seen_date)
    VALUES ($1, $2, $3, CURRENT_DATE)
    RETURNING user_id, email, total_cost_usd, total_actas, created_at
    """
    return await conn.fetchrow(query, user_data.auth_provider_id, user_data.email, user_data.user_cohort)

async def get_user_by_auth_id(conn: asyncpg.Connection, auth_provider_id: str) -> Optional[dict]:
    """Get user by auth provider ID."""
    query = "SELECT * FROM users WHERE auth_provider_id = $1"
    return await conn.fetchrow(query, auth_provider_id)

async def update_user_costs(conn: asyncpg.Connection, user_id: UUID, cost: Decimal) -> None:
    """Update user total costs."""
    query = """
    UPDATE users
    SET total_cost_usd = total_cost_usd + $2,
        total_actas = total_actas + 1,
        updated_at = NOW()
    WHERE user_id = $1
    """
    await conn.execute(query, user_id, cost)

# Client Queries
async def create_client(conn: asyncpg.Connection, client_data) -> dict:
    """Create new client."""
    query = """
    INSERT INTO clients (user_id, client_name, industry)
    VALUES ($1, $2, $3)
    RETURNING client_id, client_name, industry, created_at
    """
    return await conn.fetchrow(query, client_data.user_id, client_data.client_name, client_data.industry)

async def get_clients_by_user(conn: asyncpg.Connection, user_id: UUID) -> List[dict]:
    """Get all clients for a user."""
    query = "SELECT * FROM clients WHERE user_id = $1 ORDER BY created_at DESC"
    return await conn.fetch(query, user_id)

# Meeting Queries
async def create_meeting(conn: asyncpg.Connection, meeting_data) -> dict:
    """Create new meeting."""
    query = """
    INSERT INTO meetings (client_id, user_id, transcript_id, assemblyai_id, meeting_date, filename)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING meeting_id, client_id, user_id, transcript_id, assemblyai_id, meeting_date, filename, status, total_acta_cost, created_at
    """
    return await conn.fetchrow(
        query,
        meeting_data.client_id,
        meeting_data.user_id,
        meeting_data.transcript_id,
        meeting_data.assemblyai_id,
        meeting_data.meeting_date,
        meeting_data.filename
    )

async def update_meeting(conn: asyncpg.Connection, meeting_id: UUID, update_data) -> dict:
    """Update meeting with processing results."""
    # Build dynamic query based on provided fields
    fields = []
    values = []
    param_count = 1

    for field, value in update_data.dict(exclude_unset=True).items():
        fields.append(f"{field} = ${param_count}")
        values.append(value)
        param_count += 1

    if not fields:
        return None

    fields.append("updated_at = NOW()")
    values.append(meeting_id)

    query = f"""
    UPDATE meetings
    SET {', '.join(fields)}
    WHERE meeting_id = ${param_count}
    RETURNING *
    """

    return await conn.fetchrow(query, *values)

async def get_meetings_by_client(conn: asyncpg.Connection, client_id: UUID) -> List[dict]:
    """Get all meetings for a client."""
    query = "SELECT * FROM meetings WHERE client_id = $1 ORDER BY meeting_date DESC"
    return await conn.fetch(query, client_id)
```

### 5. database/services.py

```python
"""Database services for business logic."""
import logging
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime
import asyncpg

from .connection import get_db_pool
from .queries import *
from .models import *

logger = logging.getLogger(__name__)

class UserService:
    """User business logic."""

    @staticmethod
    async def create_user(user_data: UserCreate) -> UserResponse:
        """Create new user."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            try:
                result = await create_user(conn, user_data)
                return UserResponse(**result)
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                raise

    @staticmethod
    async def get_user_by_auth_id(auth_provider_id: str) -> Optional[UserResponse]:
        """Get user by auth provider ID."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            try:
                result = await get_user_by_auth_id(conn, auth_provider_id)
                return UserResponse(**result) if result else None
            except Exception as e:
                logger.error(f"Error getting user: {e}")
                raise

    @staticmethod
    async def update_user_costs(user_id: UUID, cost: Decimal) -> None:
        """Update user total costs."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            try:
                await update_user_costs(conn, user_id, cost)
            except Exception as e:
                logger.error(f"Error updating user costs: {e}")
                raise

class ClientService:
    """Client business logic."""

    @staticmethod
    async def create_client(client_data: ClientCreate) -> ClientResponse:
        """Create new client."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            try:
                result = await create_client(conn, client_data)
                return ClientResponse(**result)
            except Exception as e:
                logger.error(f"Error creating client: {e}")
                raise

    @staticmethod
    async def get_clients_by_user(user_id: UUID) -> List[ClientResponse]:
        """Get all clients for a user."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            try:
                results = await get_clients_by_user(conn, user_id)
                return [ClientResponse(**row) for row in results]
            except Exception as e:
                logger.error(f"Error getting clients: {e}")
                raise

class MeetingService:
    """Meeting business logic."""

    @staticmethod
    async def create_meeting(meeting_data: MeetingCreate) -> MeetingResponse:
        """Create new meeting."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            try:
                result = await create_meeting(conn, meeting_data)
                return MeetingResponse(**result)
            except Exception as e:
                logger.error(f"Error creating meeting: {e}")
                raise

    @staticmethod
    async def update_meeting(meeting_id: UUID, update_data: MeetingUpdate) -> Optional[MeetingResponse]:
        """Update meeting with processing results."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            try:
                result = await update_meeting(conn, meeting_id, update_data)
                return MeetingResponse(**result) if result else None
            except Exception as e:
                logger.error(f"Error updating meeting: {e}")
                raise

    @staticmethod
    async def get_meetings_by_client(client_id: UUID) -> List[MeetingResponse]:
        """Get all meetings for a client."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            try:
                results = await get_meetings_by_client(conn, client_id)
                return [MeetingResponse(**row) for row in results]
            except Exception as e:
                logger.error(f"Error getting meetings: {e}")
                raise
```

## 🔌 Integración con FastAPI

### main.py - Agregar startup/shutdown

```python
from voxcliente.database import get_db_pool, close_db_pool

@app.on_event("startup")
async def startup_event():
    """Initialize database connection."""
    await get_db_pool()
    logger.info("Database connection initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection."""
    await close_db_pool()
    logger.info("Database connection closed")
```

### api.py - Modificar endpoint /transcribe

```python
from voxcliente.database.services import UserService, ClientService, MeetingService
from voxcliente.database.models import UserCreate, ClientCreate, MeetingCreate, MeetingUpdate

@router.post("/transcribe")
async def transcribe_audio(
    request: Request,
    file: UploadFile = File(...),
    email: str = Form(...)
):
    """Endpoint para transcribir audio con AssemblyAI."""

    # ... código existente de procesamiento ...

    # Después del procesamiento exitoso, agregar:
    result = _process_audio_pipeline(temp_file_path, email, file.filename)

    # Preparar datos para guardar en BD (cuando el usuario haga login)
    # Por ahora solo retornamos los datos para el frontend
    return {
        "status": "success",
        "filename": file.filename,
        "email": email,
        "transcript": result['transcript'],
        "acta": result['acta'],
        "email_sent": result['email_sent'],
        "duration_minutes": result['duration_minutes'],
        "cost_usd": result['total_cost'],
        "cost_breakdown": result['cost_breakdown'],
        "openai_usage": result['openai_usage'],
        "assemblyai_usage": result['assemblyai_usage'],
        "download_files": download_urls,
        "message": "Transcripción completada y acta enviada por email",
        # Datos para guardar después del login
        "meeting_data": {
            "transcript_id": str(uuid4()),
            "assemblyai_id": result['assemblyai_usage']['transcript_id'],
            "meeting_date": datetime.now(),
            "filename": file.filename,
            "duration_minutes": result['duration_minutes'],
            "topics": result['acta'].get('topics'),
            "summary": result['acta'].get('summary'),
            "transcription_cost": result['cost_breakdown']['assemblyai_cost_usd'],
            "llm_processing_cost": result['cost_breakdown']['openai_cost_usd'],
            "email_cost": result['cost_breakdown']['email_cost_usd'],
            "total_acta_cost": result['total_cost']
        }
    }
```

## 🚀 Orden de Implementación

1. **Agregar dependencia asyncpg** a pyproject.toml
2. **Crear estructura de carpetas** database/
3. **Implementar connection.py** (pool básico)
4. **Implementar models.py** (Pydantic models)
5. **Implementar queries.py** (SQL básico)
6. **Implementar services.py** (lógica de negocio)
7. **Modificar config.py** (DATABASE_URL)
8. **Modificar main.py** (startup/shutdown)
9. **Modificar api.py** (preparar datos para BD)
10. **Testing básico** (conexión y operaciones CRUD)

## ✅ Checklist de Validación

- [ ] Conexión a PostgreSQL funciona
- [ ] Pool de conexiones se crea correctamente
- [ ] Operaciones CRUD básicas funcionan
- [ ] Manejo de errores básico
- [ ] Logging de operaciones
- [ ] Integración con FastAPI
- [ ] Datos se preparan para guardar post-login

## 🎯 Próximos Pasos

1. Implementar login con Clerk
2. Crear endpoints para guardar datos post-login
3. Crear dashboard básico para ver historial
4. Agregar gestión de clientes
5. Implementar métricas y analytics

---

**Filosofía**: Simplicidad primero - Solo lo mínimo necesario para que el MVP funcione.

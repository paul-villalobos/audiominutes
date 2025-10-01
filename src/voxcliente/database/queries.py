"""SQL queries for database operations."""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
import asyncpg

# User Queries
async def create_user(conn: asyncpg.Connection, user_data) -> dict:
    """Create new user."""
    query = """
    INSERT INTO voxcliente.users (auth_provider_id, email, user_cohort, first_seen_date)
    VALUES ($1, $2, $3, CURRENT_DATE)
    RETURNING user_id, email, total_cost_usd, total_actas, created_at
    """
    return await conn.fetchrow(query, user_data.auth_provider_id, user_data.email, user_data.user_cohort)

async def get_user_by_auth_id(conn: asyncpg.Connection, auth_provider_id: str) -> Optional[dict]:
    """Get user by auth provider ID."""
    query = "SELECT * FROM voxcliente.users WHERE auth_provider_id = $1"
    return await conn.fetchrow(query, auth_provider_id)

async def update_user_costs(conn: asyncpg.Connection, user_id: UUID, cost: Decimal) -> None:
    """Update user total costs."""
    query = """
    UPDATE voxcliente.users 
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
    INSERT INTO voxcliente.clients (user_id, client_name, industry)
    VALUES ($1, $2, $3)
    RETURNING client_id, client_name, industry, created_at
    """
    return await conn.fetchrow(query, client_data.user_id, client_data.client_name, client_data.industry)

async def get_clients_by_user(conn: asyncpg.Connection, user_id: UUID) -> List[dict]:
    """Get all clients for a user."""
    query = "SELECT * FROM voxcliente.clients WHERE user_id = $1 ORDER BY created_at DESC"
    return await conn.fetch(query, user_id)

# Meeting Queries
async def create_meeting(conn: asyncpg.Connection, meeting_data) -> dict:
    """Create new meeting."""
    query = """
    INSERT INTO voxcliente.meetings (client_id, user_id, transcript_id, assemblyai_id, meeting_date, filename)
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
    UPDATE voxcliente.meetings 
    SET {', '.join(fields)}
    WHERE meeting_id = ${param_count}
    RETURNING *
    """
    
    return await conn.fetchrow(query, *values)

async def get_meetings_by_client(conn: asyncpg.Connection, client_id: UUID) -> List[dict]:
    """Get all meetings for a client."""
    query = "SELECT * FROM voxcliente.meetings WHERE client_id = $1 ORDER BY meeting_date DESC"
    return await conn.fetch(query, client_id)

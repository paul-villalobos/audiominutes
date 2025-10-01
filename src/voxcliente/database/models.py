"""Pydantic models for database operations."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from uuid import UUID

# User Models
class UserCreate(BaseModel):
    auth_provider_id: str
    email: str
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

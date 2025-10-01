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

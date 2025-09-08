"""Usage logs model for tracking audio processing - Simplified for MVP."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index

from audiominutes.database import Base


class UsageLog(Base):
    """Simplified model for tracking audio processing usage."""
    
    __tablename__ = "usage_logs"
    
    # Essential fields only
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, index=True)
    duration_minutes = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<UsageLog(id={self.id}, email='{self.email}', duration={self.duration_minutes}min)>"

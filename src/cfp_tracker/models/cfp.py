from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CFP(Base):
    """SQLAlchemy model for CFP data"""
    __tablename__ = "cfps"

    id = Column(Integer, primary_key=True, index=True)
    conference_name = Column(String(255), nullable=False)
    submission_deadline = Column(DateTime, nullable=True)
    conference_start_date = Column(DateTime, nullable=True)
    conference_end_date = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True)
    is_virtual = Column(Boolean, default=False)
    topics = Column(Text, nullable=True)
    submission_url = Column(String(512), nullable=False)
    source = Column(String(100), nullable=False)
    source_url = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CFPSchema(BaseModel):
    """Schema for Call for Papers data"""
    conference_name: str
    submission_deadline: Optional[datetime]
    conference_start_date: Optional[datetime]
    conference_end_date: Optional[datetime]
    location: Optional[str]
    is_virtual: bool = False
    topics: List[str] = []
    submission_url: str
    source: str
    source_url: str
    description: Optional[str] = None

    class Config:
        from_attributes = True  # For SQLAlchemy compatibility 
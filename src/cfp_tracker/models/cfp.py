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
    submission_deadline = Column(DateTime, nullable=False)
    conference_start_date = Column(DateTime, nullable=False)
    conference_end_date = Column(DateTime, nullable=False)
    location = Column(String(255))
    is_virtual = Column(Boolean, default=False)
    topics = Column(Text)  # Stored as JSON string
    submission_url = Column(String(512))
    source = Column(String(100), nullable=False)
    source_url = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CFPSchema(BaseModel):
    """Pydantic model for CFP data validation"""
    id: Optional[int] = None
    conference_name: str
    submission_deadline: datetime
    conference_start_date: datetime
    conference_end_date: datetime
    location: Optional[str] = None
    is_virtual: bool = False
    topics: List[str] = Field(default_factory=list)
    submission_url: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 
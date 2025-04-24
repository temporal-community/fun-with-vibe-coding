import os
from typing import Optional

class Config:
    """Application configuration."""
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cfp_tracker")
    
    # Slack settings
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    
    # Ingestion settings
    INGESTION_BATCH_SIZE: int = 100  # Number of CFPs to process in one batch
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_RELOAD: bool = True  # Enable auto-reload in development 
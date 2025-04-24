import logging
from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models.cfp import CFP
from ..config import Config
from .slack_adapter import SlackAdapter

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling CFP notifications."""
    
    def __init__(self, db: Session):
        """Initialize the notification service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.slack_adapter = None
        if Config.SLACK_WEBHOOK_URL:
            self.slack_adapter = SlackAdapter(Config.SLACK_WEBHOOK_URL)
            
    def get_new_cfps(self, hours: int = 24) -> List[CFP]:
        """Get CFPs that were added in the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List[CFP]: List of new CFPs
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(CFP).filter(CFP.created_at >= cutoff_time).all()
        
    def notify_new_cfps(self, hours: int = 24) -> bool:
        """Notify about new CFPs added in the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            bool: True if notifications were sent successfully
        """
        if not self.slack_adapter:
            logger.warning("Slack webhook URL not configured, skipping notifications")
            return False
            
        cfps = self.get_new_cfps(hours)
        if not cfps:
            logger.info(f"No new CFPs found in the last {hours} hours")
            return True
            
        logger.info(f"Found {len(cfps)} new CFPs to notify about")
        return self.slack_adapter.post_cfps(cfps) 
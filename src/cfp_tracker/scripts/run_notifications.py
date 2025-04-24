#!/usr/bin/env python
import logging
import sys
import os
import time
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.cfp_tracker.storage.database import SessionLocal
from src.cfp_tracker.notifications.service import NotificationService
from src.cfp_tracker.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("notifications.log")
    ]
)

logger = logging.getLogger(__name__)

def run_notifications():
    """Run the notification service to check for new CFPs."""
    logger.info("Starting notification service")
    
    if not Config.SLACK_WEBHOOK_URL:
        logger.error("SLACK_WEBHOOK_URL not configured. Please set the environment variable.")
        return False
    
    try:
        db = SessionLocal()
        service = NotificationService(db)
        
        # Check for CFPs added in the last 24 hours
        success = service.notify_new_cfps(hours=24)
        
        if success:
            logger.info("Successfully sent notifications")
        else:
            logger.error("Failed to send notifications")
            
        return success
    except Exception as e:
        logger.error(f"Error running notifications: {str(e)}")
        return False
    finally:
        db.close()

def main():
    """Main function to run the notification service."""
    logger.info(f"Notification service started at {datetime.now()}")
    
    # Run once immediately
    run_notifications()
    
    # Then run every 6 hours
    while True:
        logger.info("Sleeping for 6 hours before next notification check")
        time.sleep(6 * 60 * 60)  # 6 hours in seconds
        run_notifications()

if __name__ == "__main__":
    main() 
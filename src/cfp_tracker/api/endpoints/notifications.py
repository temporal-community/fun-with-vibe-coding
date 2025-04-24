from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...storage.database import get_db
from ...notifications.service import NotificationService

router = APIRouter()

@router.post("/notify")
async def notify_new_cfps(
    hours: Optional[int] = 24,
    db: Session = Depends(get_db)
):
    """Notify about new CFPs added in the last N hours.
    
    Args:
        hours: Number of hours to look back (default: 24)
        db: Database session
        
    Returns:
        dict: Status of the notification operation
    """
    service = NotificationService(db)
    success = service.notify_new_cfps(hours)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to send notifications"
        )
        
    return {
        "status": "success",
        "message": f"Notifications sent for CFPs added in the last {hours} hours"
    } 
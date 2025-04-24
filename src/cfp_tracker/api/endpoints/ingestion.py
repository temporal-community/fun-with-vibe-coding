from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import logging

from ...ingestion.manager import CFPIngestionManager
from ...models.cfp import CFPSchema, CFP
from ...storage.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

# Create a global ingestion manager
ingestion_manager = CFPIngestionManager()

async def fetch_and_store_cfps(db: Session):
    """Fetch CFPs from all sources and store them in the database"""
    try:
        cfps = await ingestion_manager.fetch_all_cfps()
        logger.info(f"Fetched {len(cfps)} CFPs from all sources")
        
        # Store CFPs in the database
        for cfp_schema in cfps:
            # Convert Pydantic model to dict, excluding unset fields
            cfp_data = cfp_schema.model_dump(exclude_unset=True)
            
            # Check if CFP already exists
            existing_cfp = db.query(CFP).filter(
                CFP.conference_name == cfp_data["conference_name"],
                CFP.submission_deadline == cfp_data["submission_deadline"]
            ).first()
            
            if existing_cfp:
                # Update existing CFP
                for key, value in cfp_data.items():
                    setattr(existing_cfp, key, value)
            else:
                # Create new CFP
                db_cfp = CFP(**cfp_data)
                db.add(db_cfp)
        
        db.commit()
        logger.info(f"Stored {len(cfps)} CFPs in the database")
    except Exception as e:
        logger.error(f"Error fetching and storing CFPs: {e}")
        db.rollback()

@router.post("/ingest", response_model=Dict[str, Any])
async def ingest_cfps(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger CFP ingestion process"""
    try:
        # Add the task to background tasks
        background_tasks.add_task(fetch_and_store_cfps, db)
        
        return {
            "status": "success",
            "message": "CFP ingestion process started",
            "adapters": ingestion_manager.get_adapter_names()
        }
    except Exception as e:
        logger.error(f"Error starting CFP ingestion process: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/adapters", response_model=List[str])
async def get_adapters():
    """Get list of available adapters"""
    return ingestion_manager.get_adapter_names()

@router.get("/adapters/{adapter_name}/last-fetch", response_model=Dict[str, Any])
async def get_adapter_last_fetch(adapter_name: str):
    """Get last fetch time for a specific adapter"""
    last_fetch = ingestion_manager.get_adapter_last_fetch_time(adapter_name)
    
    if last_fetch is None:
        raise HTTPException(status_code=404, detail=f"Adapter '{adapter_name}' not found")
    
    return {
        "adapter": adapter_name,
        "last_fetch": last_fetch.isoformat() if last_fetch else None
    } 
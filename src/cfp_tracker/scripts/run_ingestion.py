import asyncio
import logging
from cfp_tracker.ingestion.manager import CFPIngestionManager
from cfp_tracker.models.cfp import CFP
from cfp_tracker.storage.database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run the CFP ingestion process manually."""
    try:
        # Initialize the ingestion manager
        manager = CFPIngestionManager()
        
        # Get database session
        db = next(get_db())
        
        # Fetch CFPs from all adapters
        for adapter_name, adapter in manager.adapters.items():
            logger.info(f"Fetching CFPs from {adapter_name}")
            try:
                cfps = await adapter.fetch_cfps()
                logger.info(f"Found {len(cfps)} CFPs from {adapter_name}")
                
                # Store CFPs in database
                for cfp_data in cfps:
                    # Check if CFP already exists
                    existing_cfp = db.query(CFP).filter(
                        CFP.source_id == cfp_data.source_id,
                        CFP.source == adapter_name
                    ).first()
                    
                    if existing_cfp:
                        # Update existing CFP
                        for key, value in cfp_data.dict().items():
                            setattr(existing_cfp, key, value)
                        logger.info(f"Updated CFP: {cfp_data.title}")
                    else:
                        # Create new CFP
                        new_cfp = CFP(**cfp_data.dict())
                        db.add(new_cfp)
                        logger.info(f"Created new CFP: {cfp_data.title}")
                
                db.commit()
                logger.info(f"Successfully processed CFPs from {adapter_name}")
                
            except Exception as e:
                logger.error(f"Error processing {adapter_name}: {str(e)}")
                continue
        
        logger.info("Ingestion process completed")
        
    except Exception as e:
        logger.error(f"Error during ingestion process: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main()) 
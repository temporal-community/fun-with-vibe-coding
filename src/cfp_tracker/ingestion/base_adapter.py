from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..models.cfp import CFPSchema

logger = logging.getLogger(__name__)

class BaseCFPAdapter(ABC):
    """Base class for CFP data adapters"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.last_fetch_time: Optional[datetime] = None
    
    @abstractmethod
    async def fetch_cfps(self) -> List[Dict[str, Any]]:
        """Fetch CFPs from the source"""
        pass
    
    @abstractmethod
    def parse_cfp(self, raw_data: Dict[str, Any]) -> CFPSchema:
        """Parse raw CFP data into a CFPSchema object"""
        pass
    
    async def get_cfps(self) -> List[CFPSchema]:
        """Get CFPs from the source and parse them"""
        try:
            raw_cfps = await self.fetch_cfps()
            self.last_fetch_time = datetime.utcnow()
            
            parsed_cfps = []
            for raw_cfp in raw_cfps:
                try:
                    parsed_cfp = self.parse_cfp(raw_cfp)
                    parsed_cfps.append(parsed_cfp)
                except Exception as e:
                    logger.error(f"Error parsing CFP from {self.source_name}: {e}")
                    continue
            
            return parsed_cfps
        except Exception as e:
            logger.error(f"Error fetching CFPs from {self.source_name}: {e}")
            return [] 
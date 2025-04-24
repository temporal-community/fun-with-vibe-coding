from typing import List, Dict, Type
import logging
import asyncio
from datetime import datetime

from .base_adapter import BaseCFPAdapter
from .confstech_adapter import ConfsTechAdapter
from .github_events_adapter import GitHubEventsAdapter
from .dev_events_adapter import DevEventsAdapter
from ..models.cfp import CFPSchema

logger = logging.getLogger(__name__)

class CFPIngestionManager:
    """Manager for CFP data ingestion"""
    
    def __init__(self):
        self.adapters: Dict[str, BaseCFPAdapter] = {}
        self._register_adapters()
    
    def _register_adapters(self):
        """Register available adapters"""
        self.adapters["confs.tech"] = ConfsTechAdapter()
        self.adapters["github_events"] = GitHubEventsAdapter()
        self.adapters["dev_events"] = DevEventsAdapter()
        # Add more adapters here as they are implemented
    
    async def fetch_all_cfps(self) -> List[CFPSchema]:
        """Fetch CFPs from all registered adapters"""
        tasks = []
        for adapter_name, adapter in self.adapters.items():
            logger.info(f"Fetching CFPs from {adapter_name}")
            tasks.append(adapter.get_cfps())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_cfps = []
        for i, result in enumerate(results):
            adapter_name = list(self.adapters.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"Error fetching CFPs from {adapter_name}: {result}")
                continue
            
            all_cfps.extend(result)
        
        return all_cfps
    
    def get_adapter(self, adapter_name: str) -> BaseCFPAdapter:
        """Get a specific adapter by name"""
        return self.adapters.get(adapter_name)
    
    def get_adapter_names(self) -> List[str]:
        """Get names of all registered adapters"""
        return list(self.adapters.keys())
    
    def get_adapter_last_fetch_time(self, adapter_name: str) -> datetime:
        """Get the last fetch time for a specific adapter"""
        adapter = self.get_adapter(adapter_name)
        if adapter:
            return adapter.last_fetch_time
        return None 
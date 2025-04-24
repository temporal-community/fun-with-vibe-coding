import aiohttp
from typing import List, Dict, Any
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from .base_adapter import BaseCFPAdapter
from .utils import parse_date, clean_text, extract_urls
from ..models.cfp import CFPSchema

logger = logging.getLogger(__name__)

class Call4PapersAdapter(BaseCFPAdapter):
    """Adapter for the Call4Papers website"""
    
    def __init__(self):
        super().__init__("Call4Papers")
        self.base_url = "https://www.call4papers.com"
        self.api_url = f"{self.base_url}/api/v1/cfp"
    
    async def fetch_cfps(self) -> List[Dict[str, Any]]:
        """Fetch CFPs from Call4Papers API"""
        async with aiohttp.ClientSession() as session:
            try:
                # Get CFPs for the next 3 months
                end_date = datetime.now() + timedelta(days=90)
                params = {
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "status": "open"
                }
                
                async with session.get(self.api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("cfps", [])
                    else:
                        logger.error(f"Error fetching CFPs from Call4Papers: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"Exception fetching CFPs from Call4Papers: {e}")
                return []
    
    def parse_cfp(self, raw_data: Dict[str, Any]) -> CFPSchema:
        """Parse raw CFP data into a CFPSchema object"""
        # Extract conference name
        conference_name = clean_text(raw_data.get("conference_name", ""))
        
        # Parse dates
        submission_deadline = parse_date(raw_data.get("submission_deadline"))
        conference_start_date = parse_date(raw_data.get("conference_start_date"))
        conference_end_date = parse_date(raw_data.get("conference_end_date"))
        
        # If conference_end_date is not provided, use conference_start_date
        if not conference_end_date and conference_start_date:
            conference_end_date = conference_start_date
        
        # Extract location and check if virtual
        location = clean_text(raw_data.get("location", ""))
        is_virtual = raw_data.get("is_virtual", False)
        
        # Extract topics
        topics = raw_data.get("topics", [])
        if isinstance(topics, str):
            topics = [t.strip() for t in topics.split(",")]
        
        # Extract URLs
        submission_url = raw_data.get("submission_url", "")
        source_url = raw_data.get("source_url", "")
        
        # If submission_url is not provided, try to extract it from the description
        if not submission_url:
            description = raw_data.get("description", "")
            urls = extract_urls(description)
            if urls:
                submission_url = urls[0]
        
        return CFPSchema(
            conference_name=conference_name,
            submission_deadline=submission_deadline,
            conference_start_date=conference_start_date,
            conference_end_date=conference_end_date,
            location=location,
            is_virtual=is_virtual,
            topics=topics,
            submission_url=submission_url,
            source=self.source_name,
            source_url=source_url
        ) 
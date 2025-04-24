import aiohttp
from typing import List, Dict, Any
import logging
from datetime import datetime
import json

from .base_adapter import BaseCFPAdapter
from .utils import parse_date, clean_text
from ..models.cfp import CFPSchema

logger = logging.getLogger(__name__)

class ConfsTechAdapter(BaseCFPAdapter):
    """Adapter for tech-conferences GitHub repository"""
    
    def __init__(self):
        super().__init__("tech-conferences")
        self.base_url = "https://raw.githubusercontent.com/tech-conferences/conference-data/main/conferences/2024"
        self.categories = [
            "python", "javascript", "java", "dotnet", "cpp", "rust", 
            "go", "php", "ruby", "scala", "kotlin", "swift", "android", 
            "ios", "data", "devops", "security", "testing", "ux", "accessibility"
        ]
    
    async def fetch_cfps(self) -> List[Dict[str, Any]]:
        """Fetch CFPs from tech-conferences JSON files"""
        headers = {
            "User-Agent": "CFPTracker/1.0 (https://github.com/your-repo/cfp-tracker)",
            "Accept": "application/json",
        }
        
        all_cfps = []
        
        async with aiohttp.ClientSession() as session:
            for category in self.categories:
                try:
                    url = f"{self.base_url}/{category}.json"
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            try:
                                text = await response.text()
                                if not text.strip():
                                    logger.info(f"Empty response for {category}.json")
                                    continue
                                    
                                data = json.loads(text)
                                if not isinstance(data, list):
                                    logger.error(f"Unexpected data format in {category}.json: not a list")
                                    continue
                                    
                                logger.info(f"Successfully fetched {len(data)} CFPs from {category}.json")
                                
                                # Add category to each CFP
                                for cfp in data:
                                    cfp["category"] = category
                                
                                all_cfps.extend(data)
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse JSON from {category}.json: {e}")
                        else:
                            response_text = await response.text()
                            logger.error(f"Error fetching {category}.json: Status {response.status}, Response: {response_text}")
                except Exception as e:
                    logger.error(f"Exception fetching {category}.json: {e}")
                    continue
        
        logger.info(f"Total CFPs fetched: {len(all_cfps)}")
        return all_cfps
    
    def parse_cfp(self, raw_data: Dict[str, Any]) -> CFPSchema:
        """Parse raw CFP data into a CFPSchema object"""
        # Extract conference name
        conference_name = clean_text(raw_data.get("name", ""))
        
        # Parse dates
        submission_deadline = parse_date(raw_data.get("cfpEndDate"))
        conference_start_date = parse_date(raw_data.get("startDate"))
        conference_end_date = parse_date(raw_data.get("endDate"))
        
        # Extract location and check if virtual
        location = clean_text(raw_data.get("city", ""))
        country = clean_text(raw_data.get("country", ""))
        if country:
            location = f"{location}, {country}" if location else country
            
        is_virtual = raw_data.get("online", False)
        
        # Extract topics
        topics = [raw_data.get("category", "")]
        if "topics" in raw_data:
            topics.extend([topic.strip() for topic in raw_data["topics"]])
        
        # Extract URLs
        submission_url = raw_data.get("cfpUrl", "")
        source_url = raw_data.get("url", "")
        
        return CFPSchema(
            conference_name=conference_name,
            submission_deadline=submission_deadline,
            conference_start_date=conference_start_date,
            conference_end_date=conference_end_date or conference_start_date,  # Use start_date if end_date is not available
            location=location,
            is_virtual=is_virtual,
            topics=topics,
            submission_url=submission_url,
            source=self.source_name,
            source_url=source_url,
            description=clean_text(raw_data.get("description", ""))
        ) 
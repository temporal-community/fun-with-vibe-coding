import aiohttp
from typing import List, Dict, Any
import logging
from datetime import datetime
import base64
import json
import re

from .base_adapter import BaseCFPAdapter
from .utils import parse_date, clean_text
from ..models.cfp import CFPSchema

logger = logging.getLogger(__name__)

class GitHubEventsAdapter(BaseCFPAdapter):
    """Adapter for GitHub-based event repositories"""
    
    def __init__(self):
        super().__init__("github_events")
        self.api_url = "https://api.github.com"
        self.repos = [
            {
                "owner": "Everything-Open-Source",
                "repo": "open-source-events",
                "path": "events.json"
            },
            {
                "owner": "scraly",
                "repo": "developers-conferences-agenda",
                "path": "README.md"
            }
        ]
    
    async def fetch_cfps(self) -> List[Dict[str, Any]]:
        """Fetch CFPs from GitHub repositories"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CFPTracker/1.0"
        }
        
        all_events = []
        
        async with aiohttp.ClientSession() as session:
            for repo in self.repos:
                try:
                    # Fetch file content from GitHub
                    url = f"{self.api_url}/repos/{repo['owner']}/{repo['repo']}/contents/{repo['path']}"
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            content = base64.b64decode(data["content"]).decode("utf-8")
                            
                            if repo["path"].endswith(".json"):
                                # Parse JSON content
                                events = json.loads(content)
                                all_events.extend(events)
                            elif repo["path"].endswith(".md"):
                                # Parse markdown content
                                events = self._parse_markdown_events(content)
                                all_events.extend(events)
                        else:
                            logger.error(f"Error fetching from {repo['owner']}/{repo['repo']}: {response.status}")
                except Exception as e:
                    logger.error(f"Exception fetching from {repo['owner']}/{repo['repo']}: {e}")
                    continue
        
        return all_events
    
    def _parse_markdown_events(self, content: str) -> List[Dict[str, Any]]:
        """Parse events from markdown content"""
        events = []
        
        # Example pattern for conference entries in markdown
        # This pattern needs to be adjusted based on the actual format
        pattern = r"### (.+?)\n- Date: (.+?)\n- CFP: (.+?)\n"
        
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            event = {
                "name": match.group(1),
                "date": match.group(2),
                "cfp_url": match.group(3)
            }
            events.append(event)
        
        return events
    
    def parse_cfp(self, raw_data: Dict[str, Any]) -> CFPSchema:
        """Parse raw CFP data into a CFPSchema object"""
        # Extract conference name
        conference_name = clean_text(raw_data.get("name", ""))
        
        # Parse dates
        date_str = raw_data.get("date", "")
        conference_date = parse_date(date_str)
        
        # For CFP deadline, we might need to parse it from description or other fields
        cfp_deadline = None
        if "cfp_deadline" in raw_data:
            cfp_deadline = parse_date(raw_data["cfp_deadline"])
        
        return CFPSchema(
            conference_name=conference_name,
            submission_deadline=cfp_deadline,
            conference_start_date=conference_date,
            conference_end_date=conference_date,  # Using same date if end date not available
            location=clean_text(raw_data.get("location", "")),
            is_virtual=raw_data.get("is_virtual", False),
            topics=raw_data.get("topics", []),
            submission_url=raw_data.get("cfp_url", ""),
            source=self.source_name,
            source_url=raw_data.get("url", ""),
            description=clean_text(raw_data.get("description", ""))
        ) 
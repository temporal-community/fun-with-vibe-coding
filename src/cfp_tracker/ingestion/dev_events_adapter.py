import aiohttp
import logging
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from datetime import datetime
from .base_adapter import BaseCFPAdapter
from ..models.cfp import CFPSchema

logger = logging.getLogger(__name__)

class DevEventsAdapter(BaseCFPAdapter):
    def __init__(self):
        self.base_url = "https://dev.events/conferences"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; CFPTrackerBot/1.0; +https://github.com/yourusername/cfp-tracker)"
        }

    def _parse_date_range(self, date_text: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse a date range string into start and end dates."""
        try:
            if ' - ' in date_text:
                start_str, end_str = date_text.split(' - ')
                start_date = datetime.strptime(start_str.strip(), '%B %d, %Y')
                end_date = datetime.strptime(end_str.strip(), '%B %d, %Y')
                return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
            else:
                date_obj = datetime.strptime(date_text.strip(), '%B %d, %Y')
                date_str = date_obj.strftime('%Y-%m-%d')
                return date_str, date_str
        except ValueError as e:
            logger.warning(f"Could not parse date range: {date_text}. Error: {str(e)}")
            return None, None

    def _is_virtual_event(self, location: str) -> bool:
        """Determine if an event is virtual based on its location."""
        virtual_indicators = ['virtual', 'online', 'remote', 'digital']
        return any(indicator in location.lower() for indicator in virtual_indicators)

    async def fetch_cfps(self) -> List[Dict[Any, Any]]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch CFPs from dev.events. Status code: {response.status}")
                        return []

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    cfps = []

                    conference_table = soup.find('table')
                    if not conference_table:
                        logger.error("Could not find conference table on dev.events")
                        return []

                    for row in conference_table.find_all('tr')[1:]:  # Skip header row
                        try:
                            cells = row.find_all('td')
                            if len(cells) >= 3:  # Name, Date, Location
                                name_cell = cells[0].find('a')
                                if not name_cell:
                                    continue

                                name = name_cell.text.strip()
                                url = name_cell.get('href', '')
                                if not url.startswith('http'):
                                    url = f"https://dev.events{url}"

                                date_text = cells[1].text.strip()
                                location = cells[2].text.strip()

                                start_date, end_date = self._parse_date_range(date_text)
                                is_virtual = self._is_virtual_event(location)

                                cfp_data = {
                                    'name': name,
                                    'url': url,
                                    'location': location,
                                    'conference_start_date': start_date,
                                    'conference_end_date': end_date,
                                    'is_virtual': is_virtual,
                                    'source_url': self.base_url
                                }
                                cfps.append(cfp_data)

                        except Exception as e:
                            logger.error(f"Error parsing conference entry: {str(e)}")
                            continue

                    logger.info(f"Found {len(cfps)} CFPs from dev.events")
                    return cfps

        except Exception as e:
            logger.error(f"Error fetching CFPs from dev.events: {str(e)}")
            return []

    def parse_cfp(self, cfp_data: Dict[Any, Any]) -> CFPSchema:
        return CFPSchema(
            conference_name=cfp_data['name'],
            conference_url=cfp_data['url'],
            location=cfp_data['location'],
            conference_start_date=cfp_data['conference_start_date'],
            conference_end_date=cfp_data['conference_end_date'],
            is_virtual=cfp_data['is_virtual'],
            topics=['technology', 'software development'],  # Default topics for dev.events
            source='dev.events',
            source_url=cfp_data['source_url'],
            submission_url=cfp_data['url']  # Using conference URL as submission URL since dev.events doesn't provide specific CFP URLs
        ) 
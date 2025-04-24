import re
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse a date string into a datetime object"""
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%d %B %Y",
        "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try to extract date using regex
    date_patterns = [
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD or YYYY/MM/DD
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD-MM-YYYY or DD/MM/YYYY
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',  # DD-MM-YY or DD/MM/YY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                try:
                    # Assume YYYY-MM-DD format
                    return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                except ValueError:
                    try:
                        # Assume DD-MM-YYYY format
                        return datetime(int(groups[2]), int(groups[1]), int(groups[0]))
                    except ValueError:
                        continue
    
    logger.warning(f"Could not parse date: {date_str}")
    return None

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and normalizing"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Trim
    return text.strip()

def extract_urls(text: str) -> list:
    """Extract URLs from text"""
    if not text:
        return []
    
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.findall(url_pattern, text) 
import logging
import requests
from typing import List, Optional
from datetime import datetime

from ..models.cfp import CFP

logger = logging.getLogger(__name__)

class SlackAdapter:
    """Adapter for posting CFP notifications to Slack."""
    
    def __init__(self, webhook_url: str):
        """Initialize the Slack adapter.
        
        Args:
            webhook_url: The Slack webhook URL to post messages to
        """
        self.webhook_url = webhook_url
        
    def format_cfp_message(self, cfp: CFP) -> dict:
        """Format a CFP as a Slack message.
        
        Args:
            cfp: The CFP to format
            
        Returns:
            dict: A Slack message block
        """
        # Format deadline
        deadline_str = "No deadline specified"
        if cfp.submission_deadline:
            deadline_str = cfp.submission_deadline.strftime("%B %d, %Y")
            
        # Format conference dates
        dates_str = "Dates not specified"
        if cfp.conference_start_date and cfp.conference_end_date:
            if cfp.conference_start_date == cfp.conference_end_date:
                dates_str = cfp.conference_start_date.strftime("%B %d, %Y")
            else:
                dates_str = f"{cfp.conference_start_date.strftime('%B %d')} - {cfp.conference_end_date.strftime('%B %d, %Y')}"
                
        # Format location
        location_str = cfp.location if cfp.location else "Location not specified"
        if cfp.is_virtual:
            location_str = "Virtual Event"
            
        # Format topics
        topics_str = ", ".join(cfp.topics) if cfp.topics else "No topics specified"
        
        # Create message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎤 New CFP: {cfp.conference_name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Submission Deadline:*\n{deadline_str}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Conference Dates:*\n{dates_str}"
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Location:*\n{location_str}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Topics:*\n{topics_str}"
                    }
                ]
            }
        ]
        
        # Add submission URL if available
        if cfp.submission_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Submission URL:* <{cfp.submission_url}|Submit your proposal>"
                }
            })
            
        # Add source URL if available
        if cfp.source_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Conference Website:* <{cfp.source_url}|Learn more>"
                }
            })
            
        return {
            "blocks": blocks
        }
        
    def post_cfps(self, cfps: List[CFP]) -> bool:
        """Post multiple CFPs to Slack.
        
        Args:
            cfps: List of CFPs to post
            
        Returns:
            bool: True if all messages were posted successfully, False otherwise
        """
        success = True
        for cfp in cfps:
            try:
                message = self.format_cfp_message(cfp)
                response = requests.post(
                    self.webhook_url,
                    json=message
                )
                response.raise_for_status()
                logger.info(f"Posted CFP {cfp.conference_name} to Slack")
            except Exception as e:
                logger.error(f"Error posting CFP {cfp.conference_name} to Slack: {str(e)}")
                success = False
                
        return success 
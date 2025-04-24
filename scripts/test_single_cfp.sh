#!/bin/bash

# Check if webhook URL is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <slack_webhook_url>"
  echo "Example: $0 https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
  exit 1
fi

# Export the webhook URL
export SLACK_WEBHOOK_URL="$1"

# Create a test CFP
cat > test_cfp.py << EOL
from datetime import datetime, timedelta
from src.cfp_tracker.models.cfp import CFP
from src.cfp_tracker.notifications.slack_adapter import SlackAdapter

# Create a test CFP
test_cfp = CFP(
    conference_name="Test Conference 2024",
    submission_deadline=datetime.now() + timedelta(days=30),
    conference_start_date=datetime.now() + timedelta(days=60),
    conference_end_date=datetime.now() + timedelta(days=62),
    location="San Francisco, CA",
    is_virtual=False,
    topics=["python", "testing"],
    submission_url="https://example.com/cfp",
    source="test",
    source_url="https://example.com",
    description="A test conference to verify Slack notifications"
)

# Send to Slack
adapter = SlackAdapter("$1")
success = adapter.post_cfps([test_cfp])

if success:
    print("Test CFP sent successfully!")
else:
    print("Failed to send test CFP")
EOL

# Run the test
python3 test_cfp.py

# Clean up
rm test_cfp.py 
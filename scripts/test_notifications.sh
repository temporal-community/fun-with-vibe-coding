#!/bin/bash

# Check if webhook URL is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <slack_webhook_url>"
  echo "Example: $0 https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
  exit 1
fi

# Export the webhook URL
export SLACK_WEBHOOK_URL="$1"

# Run the notification service once (not in the background)
echo "Testing notification service with webhook URL..."
python3 src/cfp_tracker/scripts/run_notifications.py

# Check the exit status
if [ $? -eq 0 ]; then
  echo "Notification test completed successfully!"
  echo "Check your Slack channel for the notifications."
else
  echo "Notification test failed. Check the logs for errors."
fi 
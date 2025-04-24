#!/bin/bash

# Kill any existing notification processes
pkill -f "run_notifications.py"

# Start the notification service in the background
nohup python3 src/cfp_tracker/scripts/run_notifications.py > notifications.log 2>&1 &

echo "Notification service started. Check notifications.log for output." 
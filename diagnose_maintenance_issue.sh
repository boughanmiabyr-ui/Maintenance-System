#!/bin/bash

# Quick Diagnostic Script for Maintenance Event Issues
# Run this from your laptop to diagnose why maintenance events aren't ending

echo "=========================================="
echo "Maintenance Event Diagnostic"
echo "=========================================="
echo ""

# Variables
FLASK_IP="192.168.137.1"
FLASK_PORT="5000"
MACHINE_CODE="MACH001"
API_URL="http://$FLASK_IP:$FLASK_PORT/api/events"

echo "1. Checking Flask API is accessible..."
echo "   URL: $API_URL"
echo ""

# Test 1: Can reach Flask API
if curl -s "$API_URL/machines/list" > /dev/null 2>&1; then
    echo "   ✓ Flask API is reachable"
else
    echo "   ✗ Cannot reach Flask API"
    echo "   Fix: Make sure Flask is running on $FLASK_IP:$FLASK_PORT"
    echo "   Try: python main.py"
    exit 1
fi

echo ""
echo "2. Checking last maintenance event..."
echo ""

# Show the last event in database
mysql -u root -p -e "
USE maintenance_system_v2;
SELECT 
    id, 
    event_type, 
    event_status, 
    DATE_FORMAT(event_start_time, '%Y-%m-%d %H:%i:%s') as start_time,
    DATE_FORMAT(event_end_time, '%Y-%m-%d %H:%i:%s') as end_time,
    IFNULL(duration_seconds, 'NULL') as duration,
    IFNULL(end_user_id, 'NULL') as end_user
FROM machine_events 
WHERE event_type IN ('maintenance', 'reset_maintenance')
ORDER BY event_start_time DESC 
LIMIT 5;
"

echo ""
echo "3. Analysis:"
echo ""

# Check if last event is maintenance without end
LAST_EVENT=$(mysql -u root -p -N -e "
USE maintenance_system_v2;
SELECT event_status FROM machine_events 
WHERE event_type = 'maintenance'
ORDER BY id DESC LIMIT 1;
" 2>/dev/null)

if [ "$LAST_EVENT" = "started" ]; then
    echo "   ⚠️  ISSUE FOUND: Maintenance event is still 'started'"
    echo "   This means reset_maintenance was NEVER called"
    echo ""
    echo "   Possible Causes:"
    echo "   1. Raspberry Pi button press didn't trigger reset_system"
    echo "   2. reset_system called but send_event_async failed"
    echo "   3. API call timed out or network issue"
    echo ""
    echo "   ✓ Quick Fix: Manually end the event"
    echo "   Run this:"
    echo ""
    echo "   curl -X POST $API_URL/reset_maintenance/$MACHINE_CODE \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"end_user_id\": \"1414\", \"end_comment\": \"Fixed\"}'"
    echo ""
elif [ "$LAST_EVENT" = "ended" ]; then
    echo "   ✓ GOOD: Last maintenance event has been ended properly"
    echo "   Event is in database with event_end_time set"
    echo ""
    echo "   Check Dashboard:"
    echo "   1. Go to 'Machine Status Monitor' card"
    echo "   2. Click 'View Events' button on the machine"
    echo "   3. You should see the maintenance event as 'Ended'"
else
    echo "   ? UNKNOWN: Event status is '$LAST_EVENT'"
fi

echo ""
echo "=========================================="
echo ""

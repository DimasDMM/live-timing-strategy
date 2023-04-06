#!/usr/bin

echo "Request to restart server..."
curl -X GET --unix-socket /path/to/control.unit.sock \
    http://localhost:8090/control/applications/fastapi/restart

echo "Done!"

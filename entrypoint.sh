#!/bin/bash

# Fix config files if they were created as directories by Docker
if [ -d "/app/config.json" ]; then
    echo "Warning: config.json is a directory, removing and creating as file..."
    rm -rf /app/config.json
    echo '{"syslog_server":"","syslog_port":514,"protocol":"udp","log_type":"fortigate","log_count":10,"delay_ms":1000,"continuous":false}' > /app/config.json
fi

if [ -d "/app/configs.json" ]; then
    echo "Warning: configs.json is a directory, removing and creating as file..."
    rm -rf /app/configs.json
    echo '{}' > /app/configs.json
fi

# Execute the main command
exec python app.py

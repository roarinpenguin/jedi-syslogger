#!/bin/bash

# Ensure data directory exists
mkdir -p /app/data

# Initialize config files if they don't exist
if [ ! -f "/app/data/config.json" ]; then
    echo "Initializing config.json..."
    if [ -f "/app/config.json.example" ]; then
        cp /app/config.json.example /app/data/config.json
    else
        echo '{"syslog_server":"","syslog_port":514,"protocol":"udp","log_type":"fortigate","log_count":10,"delay_ms":1000,"continuous":false}' > /app/data/config.json
    fi
fi

if [ ! -f "/app/data/configs.json" ]; then
    echo "Initializing configs.json..."
    if [ -f "/app/configs.json.example" ]; then
        cp /app/configs.json.example /app/data/configs.json
    else
        echo '{}' > /app/data/configs.json
    fi
fi

# Execute the main command
exec python app.py

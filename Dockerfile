FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories and initialize config files
RUN mkdir -p custom_templates && \
    if [ ! -f config.json ]; then cp config.json.example config.json 2>/dev/null || echo '{"syslog_server":"","syslog_port":514,"protocol":"udp","log_type":"fortigate","log_count":10,"delay_ms":1000,"continuous":false}' > config.json; fi && \
    if [ ! -f configs.json ]; then cp configs.json.example configs.json 2>/dev/null || echo '{}' > configs.json; fi && \
    chmod +x entrypoint.sh

EXPOSE 8042

ENTRYPOINT ["/app/entrypoint.sh"]
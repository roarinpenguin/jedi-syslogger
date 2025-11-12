FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories and make entrypoint executable
RUN mkdir -p custom_templates data && \
    chmod +x entrypoint.sh

EXPOSE 8042

ENTRYPOINT ["/app/entrypoint.sh"]
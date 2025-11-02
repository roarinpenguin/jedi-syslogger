# Jedi Syslogger

A Flask-based syslog sender with Star Wars themed synthetic logs for security testing.

## Features

- Send syslog messages via TCP or UDP
- Pre-built log generators for major security platforms
- Custom template support
- Star Wars themed synthetic data
- Modern purple glossy UI
- Persistent configuration

## Quick Start

### Using Docker

```bash
docker-compose up -d
```

Access the UI at http://localhost:8042

### Manual Installation

```bash
pip install -r requirements.txt
python app.py
```

## Supported Log Types

- Fortigate Firewall
- Palo Alto Firewall
- SentinelOne Endpoint Protection
- Proofpoint
- Netskope
- Office 365
- Okta

## Custom Templates

Upload your own log templates (.txt files). The system will automatically replace:
- IP addresses with random IPs
- Usernames with Star Wars characters
- Hostnames with Star Wars themed hosts
- Timestamps with current time

## Configuration

All settings are persisted in `config.json` and include:
- Syslog server and port
- Protocol (TCP/UDP)
- Log type
- Number of logs per session
- Delay between logs
- Continuous mode

---

Crafted with ♡ by the RoarinPenguin
from flask import Flask, render_template, request, jsonify, Response
import socket
import time
import threading
import json
import os
import random
from datetime import datetime
from queue import Queue

app = Flask(__name__, template_folder='template')

CONFIG_FILE = 'config.json'
CONFIGS_FILE = 'configs.json'
TEMPLATES_DIR = 'custom_templates'

syslog_thread = None
stop_sending = False
log_queue = Queue()
recent_logs = []

# Star Wars themed data
STAR_WARS_USERS = [
    'luke.skywalker', 'leia.organa', 'han.solo', 'chewbacca', 'obi-wan.kenobi',
    'yoda', 'anakin.skywalker', 'padme.amidala', 'mace.windu', 'qui-gon.jinn',
    'darth.vader', 'emperor.palpatine', 'darth.maul', 'count.dooku', 'kylo.ren',
    'rey', 'finn', 'poe.dameron', 'bb8', 'r2d2', 'c3po', 'lando.calrissian',
    'ahsoka.tano', 'boba.fett', 'jango.fett', 'grievous', 'jabba.hutt'
]

STAR_WARS_HOSTS = [
    'tatooine-srv', 'coruscant-dc', 'hoth-relay', 'dagobah-db', 'endor-web',
    'naboo-mail', 'alderaan-gw', 'kamino-app', 'mustafar-fw', 'yavin-proxy',
    'bespin-cloud', 'jakku-edge', 'scarif-data', 'death-star', 'millennium-falcon',
    'x-wing-01', 'tie-fighter', 'star-destroyer', 'rebel-base', 'jedi-temple'
]

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'syslog_server': '',
        'syslog_port': 514,
        'protocol': 'udp',
        'log_type': 'fortigate',
        'log_count': 10,
        'delay_ms': 1000,
        'continuous': False
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_configs():
    if os.path.exists(CONFIGS_FILE):
        with open(CONFIGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_configs(configs):
    with open(CONFIGS_FILE, 'w') as f:
        json.dump(configs, f, indent=2)

def random_ip():
    return f"{random.randint(10, 192)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def random_user():
    return random.choice(STAR_WARS_USERS)

def random_host():
    return random.choice(STAR_WARS_HOSTS)

class LogGenerator:
    @staticmethod
    def fortigate():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        src_ip = random_ip()
        dst_ip = random_ip()
        user = random_user()
        action = random.choice(['accept', 'deny', 'close'])
        proto = random.choice(['tcp', 'udp', 'icmp'])
        sport = random.randint(1024, 65535)
        dport = random.choice([80, 443, 22, 3389, 8080])
        
        return f'date={timestamp} time={datetime.now().strftime("%H:%M:%S")} devname="{random_host()}" ' \
               f'logid="0000000013" type="traffic" subtype="forward" level="notice" ' \
               f'srcip={src_ip} srcport={sport} dstip={dst_ip} dstport={dport} ' \
               f'proto={proto} action={action} user="{user}" msg="Traffic {action}ed"'
    
    @staticmethod
    def paloalto():
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        src_ip = random_ip()
        dst_ip = random_ip()
        user = random_user()
        action = random.choice(['allow', 'deny', 'drop'])
        app = random.choice(['web-browsing', 'ssl', 'ssh', 'dns', 'smtp'])
        
        return f'{timestamp},{random.randint(100000, 999999)},TRAFFIC,end,2049,{timestamp},' \
               f'{src_ip},{dst_ip},0.0.0.0,0.0.0.0,Allow-All,,,{app},' \
               f'vsys1,trust,untrust,ethernet1/1,ethernet1/2,Log-Forwarding,' \
               f'{timestamp},{random.randint(1000, 9999)},{user},0,0,0,0,0,{action}'
    
    @staticmethod
    def sentinelone():
        timestamp = datetime.now().isoformat() + 'Z'
        host = random_host()
        user = random_user()
        threat_type = random.choice(['malware', 'ransomware', 'trojan', 'suspicious'])
        action = random.choice(['quarantine', 'kill', 'remediate', 'detected'])
        
        return f'{{"timestamp":"{timestamp}","event_type":"threat",' \
               f'"hostname":"{host}","username":"{user}",' \
               f'"threat_name":"Threat.{threat_type}.{random.randint(1000, 9999)}",' \
               f'"action":"{action}","src_ip":"{random_ip()}",' \
               f'"status":"completed","severity":"high"}}'
    
    @staticmethod
    def proofpoint():
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        user = random_user()
        sender = f"{random_user()}@empire.com"
        subject = random.choice([
            "Urgent: Death Star Plans",
            "RE: Rebel Alliance Meeting",
            "FW: Jedi Training Schedule",
            "SPAM: You won the Galactic Lottery"
        ])
        action = random.choice(['delivered', 'blocked', 'quarantined'])
        
        return f'{{"ts":"{timestamp}","type":"message",' \
               f'"recipient":"{user}@rebellion.net","sender":"{sender}",' \
               f'"subject":"{subject}","action":"{action}",' \
               f'"threat_status":"threat","threat_type":"phish",' \
               f'"sender_ip":"{random_ip()}"}}'
    
    @staticmethod
    def netskope():
        timestamp = int(time.time())
        user = random_user()
        host = random_host()
        app = random.choice(['Dropbox', 'Box', 'Google Drive', 'OneDrive', 'Salesforce'])
        action = random.choice(['allow', 'block', 'alert'])
        
        return f'{{"timestamp":{timestamp},"type":"page",' \
               f'"user":"{user}@rebellion.net","hostname":"{host}",' \
               f'"app":"{app}","activity":"Download","action":"{action}",' \
               f'"src_ip":"{random_ip()}","dst_ip":"{random_ip()}",' \
               f'"file_type":"pdf","dlp_action":"none"}}'
    
    @staticmethod
    def office365():
        timestamp = datetime.now().isoformat() + 'Z'
        user = random_user()
        operation = random.choice(['FileDownloaded', 'FileUploaded', 'UserLoggedIn', 
                                  'MailItemsAccessed', 'Send', 'Create'])
        workload = random.choice(['Exchange', 'SharePoint', 'OneDrive', 'AzureActiveDirectory'])
        
        return f'{{"CreationTime":"{timestamp}","Operation":"{operation}",' \
               f'"Workload":"{workload}","UserId":"{user}@rebellion.onmicrosoft.com",' \
               f'"ClientIP":"{random_ip()}","UserAgent":"Mozilla/5.0",' \
               f'"ObjectId":"document_{random.randint(1000, 9999)}.docx"}}'
    
    @staticmethod
    def okta():
        timestamp = datetime.now().isoformat() + 'Z'
        user = random_user()
        event = random.choice(['user.authentication.sso', 'user.session.start',
                              'user.account.lock', 'policy.evaluate_sign_on'])
        outcome = random.choice(['SUCCESS', 'FAILURE'])
        
        return f'{{"published":"{timestamp}","eventType":"{event}",' \
               f'"actor":{{"alternateId":"{user}@rebellion.net","displayName":"{user.replace(".", " ").title()}"}},' \
               f'"client":{{"ipAddress":"{random_ip()}","userAgent":{{"rawUserAgent":"Chrome/90.0"}}}},' \
               f'"outcome":{{"result":"{outcome}"}},' \
               f'"target":[{{"alternateId":"Jedi Portal","displayName":"Jedi Application"}}]}}'

    @staticmethod
    def custom_template(template_content):
        import re
        # Split template into lines and pick a random one
        lines = [line.strip() for line in template_content.strip().split('\n') if line.strip()]
        if not lines:
            return "No template content available"
        
        result = random.choice(lines)
        
        # Replace IPs with random IPs
        result = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', lambda m: random_ip(), result)
        
        # Update timestamps to current time
        result = re.sub(r'\bdate=\d{4}-\d{2}-\d{2}\b', f'date={datetime.now().strftime("%Y-%m-%d")}', result)
        result = re.sub(r'\btime=\d{2}:\d{2}:\d{2}\b', f'time={datetime.now().strftime("%H:%M:%S")}', result)
        result = re.sub(r'\beventtime=\d+\b', f'eventtime={int(time.time() * 1000000000)}', result)
        
        # Update timestamps in other formats
        result = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), result)
        result = re.sub(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', datetime.now().strftime("%Y/%m/%d %H:%M:%S"), result)
        
        return result

def get_log_generator(log_type, custom_template=None):
    generators = {
        'fortigate': LogGenerator.fortigate,
        'paloalto': LogGenerator.paloalto,
        'sentinelone': LogGenerator.sentinelone,
        'proofpoint': LogGenerator.proofpoint,
        'netskope': LogGenerator.netskope,
        'office365': LogGenerator.office365,
        'okta': LogGenerator.okta
    }
    
    if log_type == 'custom' and custom_template:
        return lambda: LogGenerator.custom_template(custom_template)
    
    return generators.get(log_type, LogGenerator.fortigate)

def send_syslog(message, server, port, protocol):
    try:
        # RFC 5424 format: <priority>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG
        priority = 134  # local0.info (16*8 + 6)
        version = 1
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        hostname = "jedi-syslogger"
        app_name = "jedi-syslogger"
        procid = "-"
        msgid = "-"
        structured_data = "-"
        
        # Format according to RFC 5424
        rfc5424_message = f"<{priority}>{version} {timestamp} {hostname} {app_name} {procid} {msgid} {structured_data} {message}"
        
        if protocol == 'tcp':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server, int(port)))
            sock.send(rfc5424_message.encode('utf-8') + b'\n')
            sock.close()
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(rfc5424_message.encode('utf-8'), (server, int(port)))
            sock.close()
        return True
    except Exception as e:
        print(f"Error sending syslog: {e}")
        return False

def syslog_sender_thread(config, custom_template=None):
    global stop_sending, recent_logs
    stop_sending = False
    
    generator = get_log_generator(config['log_type'], custom_template)
    count = 0
    max_count = config.get('log_count', 10)
    
    while not stop_sending:
        if not config.get('continuous', False) and count >= max_count:
            break
        
        log_message = generator()
        success = send_syslog(
            log_message,
            config['syslog_server'],
            config['syslog_port'],
            config['protocol']
        )
        
        if success:
            count += 1
            log_entry = {
                'count': count,
                'timestamp': datetime.now().isoformat(),
                'message': log_message
            }
            recent_logs.append(log_entry)
            if len(recent_logs) > 100:
                recent_logs.pop(0)
            log_queue.put(log_entry)
            print(f"Sent log {count}: {log_message[:100]}...")
        else:
            error_msg = {
                'count': count,
                'timestamp': datetime.now().isoformat(),
                'message': f'ERROR: Failed to send log to {config["syslog_server"]}:{config["syslog_port"]}',
                'error': True
            }
            recent_logs.append(error_msg)
            log_queue.put(error_msg)
        
        time.sleep(config.get('delay_ms', 1000) / 1000.0)
    
    stop_sending = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    if request.method == 'GET':
        return jsonify(load_config())
    else:
        config_data = request.json
        save_config(config_data)
        return jsonify({'status': 'success'})

@app.route('/api/configs', methods=['GET'])
def get_configs():
    return jsonify(load_configs())

@app.route('/api/configs/<name>', methods=['GET', 'PUT', 'DELETE'])
def manage_config(name):
    configs = load_configs()
    
    if request.method == 'GET':
        if name in configs:
            return jsonify(configs[name])
        return jsonify({'error': 'Config not found'}), 404
    
    elif request.method == 'PUT':
        configs[name] = request.json
        save_configs(configs)
        return jsonify({'status': 'success'})
    
    elif request.method == 'DELETE':
        if name in configs:
            del configs[name]
            save_configs(configs)
            return jsonify({'status': 'success'})
        return jsonify({'error': 'Config not found'}), 404

@app.route('/api/logs/stream')
def stream_logs():
    def generate():
        while True:
            try:
                log = log_queue.get(timeout=1)
                yield f"data: {json.dumps(log)}\n\n"
            except:
                yield f": keepalive\n\n"
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

@app.route('/api/logs/recent', methods=['GET'])
def get_recent_logs():
    return jsonify({'logs': recent_logs})

@app.route('/api/start', methods=['POST'])
def start_sending():
    global syslog_thread, stop_sending
    
    if syslog_thread and syslog_thread.is_alive():
        return jsonify({'status': 'error', 'message': 'Already sending logs'})
    
    config = load_config()
    custom_template = request.json.get('custom_template') if request.json else None
    
    stop_sending = False
    syslog_thread = threading.Thread(
        target=syslog_sender_thread,
        args=(config, custom_template),
        daemon=True
    )
    syslog_thread.start()
    
    return jsonify({'status': 'success'})

@app.route('/api/stop', methods=['POST'])
def stop_sending_logs():
    global stop_sending
    stop_sending = True
    return jsonify({'status': 'success'})

@app.route('/api/status', methods=['GET'])
def status():
    global syslog_thread
    is_running = syslog_thread and syslog_thread.is_alive()
    return jsonify({'running': is_running})

@app.route('/api/templates', methods=['GET'])
def list_templates():
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
    
    templates = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.txt')]
    return jsonify({'templates': templates})

@app.route('/api/template/<name>', methods=['GET'])
def get_template(name):
    filepath = os.path.join(TEMPLATES_DIR, name)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return jsonify({'content': f.read()})
    return jsonify({'error': 'Template not found'}), 404

@app.route('/api/upload_template', methods=['POST'])
def upload_template():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
    
    filepath = os.path.join(TEMPLATES_DIR, file.filename)
    file.save(filepath)
    
    return jsonify({'status': 'success', 'message': 'Template uploaded'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8042, debug=False, threaded=True)
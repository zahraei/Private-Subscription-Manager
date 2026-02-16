import os
import json
import ssl
import base64
import sys
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

BASE_DIR = "/root/privsub"
DATA_FILE = os.path.join(BASE_DIR, "subscriptions.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
FILES_DIR = os.path.join(BASE_DIR, "files")
LOG_FILE = os.path.join(BASE_DIR, "access.log")

SERVICE_FILE = "/etc/systemd/system/privsub.service"
PSM_COMMAND = "/usr/local/bin/psm"

RATE_LIMIT = 20
RATE_WINDOW = 600
MAX_LOG_SIZE = 2 * 1024 * 1024

ip_requests = {}


# =========================
# Utility
# =========================

def clear():
    os.system("clear")


def pause():
    input("\nPress Enter to continue...")


def ensure_dirs():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(FILES_DIR, exist_ok=True)


def load_json(path, default={}):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    ensure_dirs()
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def generate_token():
    return os.urandom(16).hex()


# =========================
# Logging
# =========================

def rotate_log():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        with open(LOG_FILE, "rb") as f:
            f.seek(-MAX_LOG_SIZE // 2, os.SEEK_END)
            data = f.read()
        with open(LOG_FILE, "wb") as f:
            f.write(data)


def log_event(msg):
    rotate_log()
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {msg}\n")


def view_logs():
    clear()
    if not os.path.exists(LOG_FILE):
        print("No logs found.")
    else:
        with open(LOG_FILE) as f:
            print(f.read())
    pause()


# =========================
# Rate Limit
# =========================

def check_rate(ip):
    now = time.time()
    requests = ip_requests.get(ip, [])
    requests = [r for r in requests if now - r < RATE_WINDOW]

    if len(requests) >= RATE_LIMIT:
        return False

    requests.append(now)
    ip_requests[ip] = requests
    return True


# =========================
# Subscription
# =========================

def create_subscription():
    data = load_json(DATA_FILE, {})
    clear()
    print("=== Create Subscription ===\n")

    while True:
        name = input("Subscription name: ").strip()
        if not name:
            print("Name cannot be empty.")
        elif name in data:
            print("Name already exists.")
        else:
            break

    token = generate_token()
    file_path = os.path.join(FILES_DIR, f"{name}.txt")
    open(file_path, "a").close()

    data[name] = {"file": file_path, "token": token}
    save_json(DATA_FILE, data)

    cfg = load_json(CONFIG_FILE, {})
    domain = cfg.get("domain", "your-domain.com")
    port = cfg.get("port", 2083)

    print("\nCreated successfully.")
    print(f"URL: https://{domain}:{port}/?name={name}&token={token}")
    pause()


def delete_subscription():
    data = load_json(DATA_FILE, {})
    clear()

    if not data:
        print("No subscriptions found.")
        pause()
        return

    names = list(data.keys())
    cfg = load_json(CONFIG_FILE, {})
    domain = cfg.get("domain", "")
    port = cfg.get("port", 2083)

    for i, name in enumerate(names, 1):
        print(f"{i}) {name}")
        print(f"   https://{domain}:{port}/?name={name}&token={data[name]['token']}")
        print("-" * 40)

    print("0) Cancel\n")

    try:
        choice = int(input("Select option: "))
        if choice == 0:
            return
        name = names[choice - 1]
    except:
        return

    confirm = input("Confirm delete? (y/n): ").lower()
    if confirm != "y":
        return

    if os.path.exists(data[name]["file"]):
        os.remove(data[name]["file"])

    del data[name]
    save_json(DATA_FILE, data)

    print("Deleted.")
    pause()


def select_subscription():
    data = load_json(DATA_FILE, {})
    if not data:
        return None

    names = list(data.keys())
    for i, name in enumerate(names, 1):
        print(f"{i}) {name}")

    print("0) Cancel")

    try:
        choice = int(input("\nSelect option: "))
        if choice == 0:
            return None
        return names[choice - 1]
    except:
        return None


def add_config():
    clear()
    name = select_subscription()
    if not name:
        return

    data = load_json(DATA_FILE, {})
    config = input("\nPaste full config:\n").strip()

    if not config:
        return

    with open(data[name]["file"], "a") as f:
        f.write(config + "\n")

    print("Added.")
    pause()


def remove_config():
    clear()
    name = select_subscription()
    if not name:
        return

    data = load_json(DATA_FILE, {})
    file_path = data[name]["file"]

    if not os.path.exists(file_path):
        return

    with open(file_path) as f:
        lines = [l.strip() for l in f if l.strip()]

    for i, line in enumerate(lines, 1):
        if "#" in line:
            display = line.split("#")[-1]
        else:
            display = line
        print(f"{i}) {display}")

    print("0) Cancel\n")

    try:
        choice = int(input("Select option: "))
        if choice == 0:
            return
        del lines[choice - 1]
    except:
        return

    with open(file_path, "w") as f:
        for l in lines:
            f.write(l + "\n")

    print("Removed.")
    pause()


def reset_token():
    clear()
    name = select_subscription()
    if not name:
        return

    data = load_json(DATA_FILE, {})
    data[name]["token"] = generate_token()
    save_json(DATA_FILE, data)

    print("Token reset.")
    pause()


# =========================
# HTTPS Server
# =========================

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        ip = self.client_address[0]

        if not check_rate(ip):
            self.send_response(429)
            self.end_headers()
            return

        data = load_json(DATA_FILE, {})
        cfg = load_json(CONFIG_FILE, {})

        query = parse_qs(urlparse(self.path).query)
        name = query.get("name", [""])[0]
        token = query.get("token", [""])[0]

        if name not in data or token != data[name]["token"]:
            self.send_response(403)
            self.end_headers()
            log_event(f"FORBIDDEN {ip}")
            return

        with open(data[name]["file"]) as f:
            content = f.read().strip()

        encoded = base64.b64encode(content.encode()).decode()

        self.send_response(200)
        self.end_headers()
        self.wfile.write(encoded.encode())

        log_event(f"SUCCESS {ip} {name}")


def run_server():
    cfg = load_json(CONFIG_FILE, {})
    domain = cfg["domain"]
    port = cfg["port"]

    cert = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
    key = f"/etc/letsencrypt/live/{domain}/privkey.pem"

    httpd = HTTPServer(("0.0.0.0", port), Handler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    httpd.serve_forever()


# =========================
# Install / Uninstall
# =========================

def install_service():
    clear()
    ensure_dirs()

    domain = input("Enter your server address (Domain address): ").strip()

    port_input = input("Enter HTTPS port (default 2083): ").strip()
    port = int(port_input) if port_input else 2083

    save_json(CONFIG_FILE, {"domain": domain, "port": port})

    data = load_json(DATA_FILE, {})
    if not data:
        create_subscription()

    service = f"""[Unit]
Description=Private Subscription Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 {os.path.abspath(__file__)} --run
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""

    with open(SERVICE_FILE, "w") as f:
        f.write(service)

    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", "privsub"])
    subprocess.run(["systemctl", "restart", "privsub"])

    with open(PSM_COMMAND, "w") as f:
        f.write(f"#!/bin/bash\npython3 {os.path.abspath(__file__)}\n")

    os.chmod(PSM_COMMAND, 0o755)

    print("Installed successfully.")
    pause()


def uninstall():
    clear()
    confirm = input(
        "Are you absolutely sure you want to REMOVE Private Subscription Manager? (yes/no): "
    ).lower()

    if confirm != "yes":
        return

    subprocess.run(["systemctl", "stop", "privsub"])
    subprocess.run(["systemctl", "disable", "privsub"])

    if os.path.exists(SERVICE_FILE):
        os.remove(SERVICE_FILE)

    subprocess.run(["systemctl", "daemon-reload"])

    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    if os.path.exists(PSM_COMMAND):
        os.remove(PSM_COMMAND)

    delete_files = input("Delete subscription files too? (y/n): ").lower()
    if delete_files == "y" and os.path.exists(BASE_DIR):
        subprocess.run(["rm", "-rf", BASE_DIR])

    print("Removed completely.")
    sys.exit()


# =========================

if "--run" in sys.argv:
    run_server()

while True:
    clear()
    print("========== PRIVATE SUBSCRIPTION MANAGER ==========\n")
    print("1) Install / Run Service")
    print("2) Create a new Subscription")
    print("3) Delete a Subscription")
    print("4) Add Config to subscription")
    print("5) Remove Config from subscription")
    print("6) Reset Config Token")
    print("7) View Logs")
    print("8) Uninstall Everything")
    print("0) Exit\n")

    choice = input("Select option: ").strip()

    if choice == "1":
        install_service()
    elif choice == "2":
        create_subscription()
    elif choice == "3":
        delete_subscription()
    elif choice == "4":
        add_config()
    elif choice == "5":
        remove_config()
    elif choice == "6":
        reset_token()
    elif choice == "7":
        view_logs()
    elif choice == "8":
        uninstall()
    elif choice == "0":
        sys.exit()
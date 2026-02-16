# Private-Subscription-Manager
Private Subscription Manager is a secure Python-based tool that allows you to manage multiple subscription files
# 📄 README.md
# Private Subscription Manager (PSM)

A lightweight HTTPS subscription management tool for VLESS/Vmess configs.

---

## Overview

Private Subscription Manager is a secure Python-based tool that allows you to:

- Create multiple subscription files
- Add or remove configs
- Generate secure HTTPS subscription links
- Apply request rate limiting
- View access logs
- Run as a persistent systemd service

Ideal for personal use or managing a limited number of servers.

---


## Quick Install

Run this command on Ubuntu:

```bash
bash <(curl -s https://raw.githubusercontent.com/zahraei/private-subscription-manager/main/install.sh)

## Features

- HTTPS support
- Rate limit: 20 requests per 10 minutes per IP
- Automatic log rotation (max 2MB)
- Complete uninstall option
- Quick CLI command: `psm`
- Multi-subscription support

---

## Menu Options

After running the program, you will see:

Install / Run Service
Create a new Subscription
Delete a Subscription
Add Config to subscription
Remove Config from subscription
Reset Config Token
View Logs
Uninstall Everything
Exit

### Menu Description

1️⃣ Install / Run Service  
Installs systemd service and starts HTTPS server.  
You will be prompted for domain and port.

2️⃣ Create a new Subscription  
Creates a new subscription file with a unique access token.

3️⃣ Delete a Subscription  
Deletes a selected subscription.

4️⃣ Add Config to subscription  
Adds a new config line to a subscription.

5️⃣ Remove Config from subscription  
Removes a specific config from a subscription.

6️⃣ Reset Config Token  
Generates a new access token for a subscription.

7️⃣ View Logs  
Displays access logs.

8️⃣ Uninstall Everything  
Removes the service, files, and CLI command.

---


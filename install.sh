#!/bin/bash

# ======================================
# Private Subscription Manager Installer
# ======================================

REPO_URL="https://github.com/YOUR_USERNAME/private-subscription-manager.git"
INSTALL_DIR="/root/private-subscription-manager"

echo ""
echo "=========================================="
echo "  Private Subscription Manager Installer  "
echo "=========================================="
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
  echo "? Please run this installer as root."
  exit 1
fi

echo "Updating system packages..."
apt update -y

echo "Installing required packages..."
apt install -y git python3 python3-pip curl

# Remove old installation if exists
if [ -d "$INSTALL_DIR" ]; then
    echo ""
    echo "Old installation detected. Removing..."
    rm -rf $INSTALL_DIR
fi

echo ""
echo "Cloning repository..."
git clone $REPO_URL $INSTALL_DIR

if [ ! -d "$INSTALL_DIR" ]; then
    echo "? Failed to clone repository."
    echo "Please check repository URL."
    exit 1
fi

cd $INSTALL_DIR

chmod +x privsub_manager.py

echo ""
echo "Starting Private Subscription Manager..."
echo ""

python3 privsub_manager.py
#!/usr/bin/env bash
set -o errexit

echo "=== Installing Chrome ==="
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb || apt -f install -y
rm google-chrome-stable_current_amd64.deb

echo "=== Installing Python Requirements ==="
pip install -r requirements.txt

#!/usr/bin/env bash
set -o errexit

echo "=== Downloading Portable Chrome ==="
mkdir -p chrome
cd chrome
wget https://storage.googleapis.com/chrome-for-testing-public/120.0.6099.71/linux64/chrome-linux64.zip
unzip chrome-linux64.zip
cd ..

echo "=== Installing Python Dependencies ==="
pip install -r requirements.txt

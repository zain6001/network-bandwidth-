#!/bin/bash

# Installation script for Network Bandwidth Monitor
# Run with: sudo bash install.sh

echo "======================================================================"
echo "Network Bandwidth Monitor - Installation Script"
echo "======================================================================"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run with sudo"
    echo "Usage: sudo bash install.sh"
    exit 1
fi

echo "[*] Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "[✓] Python 3 is installed"
echo

echo "[*] Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[✓] All dependencies installed successfully"
echo

echo "[*] Setting up permissions..."
chmod +x main.py

echo "[✓] Permissions configured"
echo

echo "======================================================================"
echo "Installation complete!"
echo "======================================================================"
echo
echo "To run the application:"
echo "  sudo python3 main.py"
echo
echo "For more information, see README.md"
echo

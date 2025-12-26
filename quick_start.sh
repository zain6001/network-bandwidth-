#!/bin/bash
# Quick start script with process detection improvements

echo "=========================================="
echo "Network Monitor - Process Detection Fix"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: Please run with sudo"
    echo "Usage: sudo ./quick_start.sh"
    exit 1
fi

echo "[1/3] Testing process detection..."
python3 test_process_detection.py

if [ $? -eq 0 ]; then
    echo ""
    echo "[2/3] Process detection working!"
    echo ""
    echo "[3/3] Starting Network Monitor GUI..."
    echo ""
    echo "Tips for seeing processes:"
    echo "  • Click 'Show All Network Processes' to see what's available"
    echo "  • Click 'Start Monitoring' to begin tracking"
    echo "  • Open a web browser or generate network traffic"
    echo "  • Processes will appear as they use the network"
    echo ""
    sleep 2
    python3 main.py
else
    echo ""
    echo "[2/3] Process detection test failed!"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Make sure you ran with sudo"
    echo "  2. Try generating network traffic (open browser, ping)"
    echo "  3. Check if psutil is installed: pip3 install psutil"
    echo ""
    echo "You can still try running the GUI:"
    echo "  sudo python3 main.py"
fi

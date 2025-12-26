#!/usr/bin/env python3
"""
Network Bandwidth Monitor - Main Entry Point
OS-Level Network Monitoring with Per-Process Tracking

Author: Network Monitor Team
Date: December 26, 2025
License: MIT

Description:
    This application monitors network traffic at the OS level using raw packet
    capture and maps each packet to the responsible process. It displays real-time
    bandwidth usage per process with a Tkinter GUI interface.

Requirements:
    - Linux operating system (tested on Kali Linux)
    - Python 3.7+
    - Root privileges (sudo)
    - Dependencies: scapy, psutil, netifaces

Usage:
    sudo python3 main.py
"""

import tkinter as tk
import sys
import os


def check_root():
    """Check if the application is running with root privileges"""
    if os.geteuid() != 0:
        print("=" * 70)
        print("ERROR: This application requires root privileges!")
        print("=" * 70)
        print("\nNetwork packet capture requires raw socket access, which is")
        print("only available to the root user.")
        print("\nPlease run the application with sudo:")
        print("  sudo python3 main.py")
        print("\n" + "=" * 70)
        return False
    return True


def check_dependencies():
    """Check if all required dependencies are installed"""
    missing = []
    
    try:
        import scapy
    except ImportError:
        missing.append("scapy")
    
    try:
        import psutil
    except ImportError:
        missing.append("psutil")
    
    try:
        import netifaces
    except ImportError:
        missing.append("netifaces")
    
    if missing:
        print("=" * 70)
        print("ERROR: Missing required dependencies!")
        print("=" * 70)
        print("\nThe following Python packages are not installed:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nPlease install them using:")
        print(f"  sudo pip3 install {' '.join(missing)}")
        print("\nOr install all requirements:")
        print("  sudo pip3 install -r requirements.txt")
        print("\n" + "=" * 70)
        return False
    
    return True


def main():
    """Main application entry point"""
    print("=" * 70)
    print("Network Bandwidth Monitor - Per-Process Traffic Tracking")
    print("=" * 70)
    print()
    
    # Check for root privileges
    if not check_root():
        sys.exit(1)
    
    print("[✓] Running with root privileges")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("[✓] All dependencies installed")
    print()
    
    # Import modules after dependency check
    try:
        from packet_capture import PacketCapture
        from database_logger import DatabaseLogger
        from gui import NetworkMonitorGUI
        from config import CAPTURE_INTERFACE
        
        print("[*] Initializing components...")
        
        # Initialize components
        packet_capture = PacketCapture(interface=CAPTURE_INTERFACE)
        database_logger = DatabaseLogger()
        
        print("[✓] Packet capture engine initialized")
        print("[✓] Database logger initialized")
        print()
        
        # Create GUI
        root = tk.Tk()
        app = NetworkMonitorGUI(root, packet_capture, database_logger)
        
        print("[✓] GUI initialized")
        print("[*] Starting application...")
        print()
        print("=" * 70)
        print("Application is running. Close the GUI window to exit.")
        print("=" * 70)
        print()
        
        # Start GUI main loop
        root.mainloop()
        
        # Cleanup
        print("\n[*] Shutting down...")
        if packet_capture.running:
            packet_capture.stop()
        print("[✓] Cleanup complete")
        print("\nThank you for using Network Bandwidth Monitor!")
        
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

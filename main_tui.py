#!/usr/bin/env python3
"""
Network Bandwidth Monitor - Terminal UI Version
OS-Level Network Monitoring with Per-Process Tracking

This version uses a terminal-based interface (curses) instead of GUI.
Works perfectly in any terminal without requiring a display server.

Usage:
    sudo python3 main_tui.py
"""

import sys
import os
import curses


def check_root():
    """Check if the application is running with root privileges"""
    if os.geteuid() != 0:
        print("=" * 70)
        print("ERROR: This application requires root privileges!")
        print("=" * 70)
        print("\nNetwork packet capture requires raw socket access.")
        print("\nPlease run with sudo:")
        print("  sudo python3 main_tui.py")
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
        print("\nPlease install them:")
        print(f"  sudo pip3 install {' '.join(missing)}")
        print("\nOr install all requirements:")
        print("  sudo pip3 install -r requirements.txt")
        print("\n" + "=" * 70)
        return False
    
    return True


def main():
    """Main application entry point"""
    print("=" * 70)
    print("Network Bandwidth Monitor - Terminal UI")
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
    print("[*] Initializing terminal interface...")
    print()
    
    try:
        from gui_tui import main_tui
        
        # Start curses application
        curses.wrapper(main_tui)
        
        print("\n[*] Shutting down...")
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

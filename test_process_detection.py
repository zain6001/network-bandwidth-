#!/usr/bin/env python3
"""
Test script to verify process detection is working
"""

import sys
import os

# Check if running as root
if os.geteuid() != 0:
    print("ERROR: This test must be run with sudo privileges!")
    print("Usage: sudo python3 test_process_detection.py")
    sys.exit(1)

from process_mapper import ProcessMapper
import psutil

def test_process_mapper():
    """Test the process mapper functionality"""
    print("=" * 70)
    print("Network Process Detection Test")
    print("=" * 70)
    
    mapper = ProcessMapper()
    
    # Update socket mappings
    print("\n[1] Updating socket mappings...")
    mapper.update_socket_mappings()
    print(f"    Socket inode map size: {len(mapper.socket_inode_map)}")
    
    # Get all network processes
    print("\n[2] Getting all network processes...")
    processes = mapper.get_all_network_processes()
    print(f"    Found {len(processes)} processes with network connections:")
    
    # Display processes
    for pid, name in sorted(processes, key=lambda x: x[1])[:20]:  # Show first 20
        print(f"    - PID {pid:6d}: {name}")
    
    if len(processes) > 20:
        print(f"    ... and {len(processes) - 20} more")
    
    # Test connection detection
    print("\n[3] Testing connection detection...")
    connections = psutil.net_connections(kind='inet')
    active_conns = [c for c in connections if c.laddr and c.raddr and c.pid]
    
    print(f"    Found {len(active_conns)} active connections with PIDs")
    
    if active_conns:
        # Test first few connections
        for conn in active_conns[:3]:
            src_ip = conn.laddr.ip
            src_port = conn.laddr.port
            dst_ip = conn.raddr.ip
            dst_port = conn.raddr.port
            
            print(f"\n    Testing: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
            print(f"    Expected PID: {conn.pid}")
            
            result = mapper.get_process_by_connection(
                src_ip, src_port, dst_ip, dst_port, 'TCP'
            )
            
            if result:
                print(f"    Found: PID {result['pid']}, Name: {result['name']}")
                if result['pid'] == conn.pid:
                    print("    ✓ MATCH!")
                else:
                    print("    ✗ MISMATCH!")
            else:
                print("    ✗ NOT FOUND!")
                
                # Try fallback method
                fallback = mapper.get_process_by_port(src_port, 'TCP')
                if fallback:
                    print(f"    Fallback found: PID {fallback['pid']}, Name: {fallback['name']}")
    
    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)
    
    if len(processes) == 0:
        print("\nWARNING: No network processes detected!")
        print("This could mean:")
        print("  - No processes have active network connections")
        print("  - Permission issues (make sure you're running with sudo)")
        print("  - Try opening a browser or running 'ping google.com' in another terminal")
        return False
    
    return True

if __name__ == "__main__":
    success = test_process_mapper()
    sys.exit(0 if success else 1)

"""
Process Identification Module
Maps network connections to processes using /proc and socket inodes
"""

import os
import psutil
import re
from collections import defaultdict


class ProcessMapper:
    def __init__(self):
        self.socket_inode_map = {}
        self.process_cache = {}
        
    def update_socket_mappings(self):
        """
        Build a mapping of socket inodes to process information
        by scanning /proc filesystem
        """
        self.socket_inode_map = {}
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                
                # Get all file descriptors for this process
                fd_path = f"/proc/{pid}/fd"
                if not os.path.exists(fd_path):
                    continue
                    
                for fd in os.listdir(fd_path):
                    try:
                        link = os.readlink(f"{fd_path}/{fd}")
                        # Check if it's a socket
                        if link.startswith('socket:['):
                            inode = link[8:-1]
                            self.socket_inode_map[inode] = {
                                'pid': pid,
                                'name': name
                            }
                    except (OSError, FileNotFoundError):
                        continue
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
                continue
    
    def get_process_by_connection(self, src_ip, src_port, dst_ip, dst_port, protocol):
        """
        Find process that owns a specific network connection
        """
        # Try to find matching connection using psutil
        try:
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                if conn.laddr and conn.raddr:
                    # Match outgoing connection (exact match)
                    if (conn.laddr.ip == src_ip and conn.laddr.port == src_port and
                        conn.raddr.ip == dst_ip and conn.raddr.port == dst_port):
                        if conn.pid:
                            return self._get_process_info(conn.pid)
                    
                    # Match incoming connection (exact match)
                    if (conn.raddr.ip == src_ip and conn.raddr.port == src_port and
                        conn.laddr.ip == dst_ip and conn.laddr.port == dst_port):
                        if conn.pid:
                            return self._get_process_info(conn.pid)
                    
                    # Partial match on local address and port (for NAT/routing scenarios)
                    if conn.laddr.port == src_port or conn.laddr.port == dst_port:
                        if conn.pid:
                            # Cache this as a potential match
                            potential_match = self._get_process_info(conn.pid)
                
                elif conn.laddr:
                    # UDP or listening sockets - match on port
                    if conn.laddr.port == src_port or conn.laddr.port == dst_port:
                        if conn.pid:
                            return self._get_process_info(conn.pid)
            
            # Return potential match if no exact match found
            if 'potential_match' in locals():
                return potential_match
                            
        except (psutil.AccessDenied, PermissionError):
            pass
            
        return None
    
    def _get_process_info(self, pid):
        """
        Get cached process information or fetch it
        """
        if pid in self.process_cache:
            return self.process_cache[pid]
        
        try:
            proc = psutil.Process(pid)
            info = {
                'pid': pid,
                'name': proc.name(),
                'cmdline': ' '.join(proc.cmdline()[:2]) if proc.cmdline() else proc.name()
            }
            self.process_cache[pid] = info
            return info
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {
                'pid': pid,
                'name': 'Unknown',
                'cmdline': 'Unknown'
            }
    
    def get_process_by_port(self, port, protocol=None):
        """
        Find process by listening/bound port (fallback method)
        """
        try:
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                if conn.laddr and conn.laddr.port == port:
                    if conn.pid:
                        return self._get_process_info(conn.pid)
                        
        except (psutil.AccessDenied, PermissionError):
            pass
            
        return None
    
    def get_all_network_processes(self):
        """
        Get all processes with active network connections
        """
        processes = set()
        
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.pid:
                    info = self._get_process_info(conn.pid)
                    if info:
                        processes.add((info['pid'], info['name']))
        except (psutil.AccessDenied, PermissionError):
            pass
            
        return list(processes)

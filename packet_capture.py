"""
Packet Capture Module
Captures network packets using Scapy and maps them to processes
"""

import threading
import time
from collections import defaultdict
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP, DNS, Raw
from scapy.layers.http import HTTPRequest
import socket

from process_mapper import ProcessMapper
from config import PACKET_TIMEOUT, BANDWIDTH_WINDOW


class PacketCapture:
    def __init__(self, interface=None):
        self.interface = interface
        self.running = False
        self.capture_thread = None
        self.process_mapper = ProcessMapper()
        
        # Statistics per process
        self.process_stats = defaultdict(lambda: {
            'upload_bytes': 0,
            'download_bytes': 0,
            'upload_packets': 0,
            'download_packets': 0,
            'protocols': set(),
            'last_seen': datetime.now(),
            'name': 'Unknown',
            'upload_rate': 0,
            'download_rate': 0,
            'last_upload_bytes': 0,
            'last_download_bytes': 0,
            'last_calc_time': time.time()
        })
        
        self.local_ips = self._get_local_ips()
        self.lock = threading.Lock()
        
    def _get_local_ips(self):
        """Get all local IP addresses"""
        local_ips = set()
        try:
            # Get hostname and IP
            hostname = socket.gethostname()
            local_ips.add(socket.gethostbyname(hostname))
            local_ips.add('127.0.0.1')
            local_ips.add('::1')
            
            # Get all interface IPs
            import netifaces
            for interface in netifaces.interfaces():
                try:
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            local_ips.add(addr['addr'])
                except:
                    pass
        except:
            # Fallback method using psutil
            import psutil
            addrs = psutil.net_if_addrs()
            for interface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == socket.AF_INET:
                        local_ips.add(addr.address)
        
        return local_ips
    
    def _classify_protocol(self, packet):
        """Classify the protocol of a packet"""
        protocols = []
        
        if packet.haslayer(TCP):
            protocols.append('TCP')
            # Check for common ports
            if packet.haslayer(Raw):
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    protocols.append('HTTP')
                elif packet[TCP].dport == 443 or packet[TCP].sport == 443:
                    protocols.append('HTTPS')
        
        if packet.haslayer(UDP):
            protocols.append('UDP')
            if packet[UDP].dport == 53 or packet[UDP].sport == 53:
                protocols.append('DNS')
        
        if packet.haslayer(DNS):
            protocols.append('DNS')
            
        return protocols if protocols else ['OTHER']
    
    def _process_packet(self, packet):
        """Process a captured packet"""
        try:
            if not packet.haslayer(IP):
                return
            
            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            packet_size = len(packet)
            
            # Determine protocol and ports
            src_port = 0
            dst_port = 0
            protocol = 'OTHER'
            
            if packet.haslayer(TCP):
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
                protocol = 'TCP'
            elif packet.haslayer(UDP):
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport
                protocol = 'UDP'
            
            # Determine if this is upload or download
            is_upload = src_ip in self.local_ips
            is_download = dst_ip in self.local_ips
            
            if not (is_upload or is_download):
                return
            
            # Find the process responsible for this packet
            process_info = None
            
            # Try multiple methods to find the process
            if is_upload:
                process_info = self.process_mapper.get_process_by_connection(
                    src_ip, src_port, dst_ip, dst_port, protocol
                )
                # Fallback: try finding by local port only
                if not process_info:
                    process_info = self.process_mapper.get_process_by_port(src_port, protocol)
            else:
                process_info = self.process_mapper.get_process_by_connection(
                    dst_ip, dst_port, src_ip, src_port, protocol
                )
                # Fallback: try finding by local port only
                if not process_info:
                    process_info = self.process_mapper.get_process_by_port(dst_port, protocol)
            
            if process_info:
                pid = process_info['pid']
                protocols = self._classify_protocol(packet)
                
                with self.lock:
                    stats = self.process_stats[pid]
                    stats['name'] = process_info['name']
                    stats['last_seen'] = datetime.now()
                    
                    if is_upload:
                        stats['upload_bytes'] += packet_size
                        stats['upload_packets'] += 1
                    else:
                        stats['download_bytes'] += packet_size
                        stats['download_packets'] += 1
                    
                    for proto in protocols:
                        stats['protocols'].add(proto)
                        
        except Exception as e:
            pass  # Silently ignore packet processing errors
    
    def _capture_packets(self):
        """Main packet capture loop"""
        try:
            # Update process mappings periodically
            self.process_mapper.update_socket_mappings()
            
            # Start sniffing
            sniff(
                iface=self.interface,
                prn=self._process_packet,
                store=False,
                stop_filter=lambda x: not self.running,
                timeout=PACKET_TIMEOUT
            )
        except Exception as e:
            print(f"Capture error: {e}")
    
    def calculate_bandwidth(self):
        """Calculate bandwidth rates for all processes"""
        current_time = time.time()
        
        with self.lock:
            for pid, stats in self.process_stats.items():
                time_diff = current_time - stats['last_calc_time']
                
                if time_diff >= BANDWIDTH_WINDOW:
                    # Calculate rates in bytes per second
                    upload_diff = stats['upload_bytes'] - stats['last_upload_bytes']
                    download_diff = stats['download_bytes'] - stats['last_download_bytes']
                    
                    stats['upload_rate'] = upload_diff / time_diff
                    stats['download_rate'] = download_diff / time_diff
                    
                    # Update last values
                    stats['last_upload_bytes'] = stats['upload_bytes']
                    stats['last_download_bytes'] = stats['download_bytes']
                    stats['last_calc_time'] = current_time
    
    def start(self):
        """Start packet capture"""
        if self.running:
            return
        
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
    
    def _capture_loop(self):
        """Continuous capture with periodic process mapping updates"""
        last_update = time.time()
        
        while self.running:
            # Update process mappings every 2 seconds for better accuracy
            if time.time() - last_update > 2:
                self.process_mapper.update_socket_mappings()
                last_update = time.time()
            
            self._capture_packets()
    
    def stop(self):
        """Stop packet capture"""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
    
    def get_process_stats(self):
        """Get current statistics for all processes"""
        with self.lock:
            return dict(self.process_stats)
    
    def reset_stats(self):
        """Reset all statistics"""
        with self.lock:
            self.process_stats.clear()

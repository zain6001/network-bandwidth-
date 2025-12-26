"""
Terminal-based UI for Network Monitor using curses
Works in any terminal without GUI display server
"""

import curses
import time
from datetime import datetime
from config import BANDWIDTH_ALERT_THRESHOLD


class NetworkMonitorTUI:
    def __init__(self, stdscr, packet_capture, database_logger):
        self.stdscr = stdscr
        self.packet_capture = packet_capture
        self.database_logger = database_logger
        self.monitoring = False
        self.session_id = None
        self.alert_threshold = BANDWIDTH_ALERT_THRESHOLD * 1024
        self.alerted_processes = set()
        self.alerts = []
        self.selected_row = 0
        self.show_help = False
        
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(1)  # Non-blocking input
        self.stdscr.timeout(100)
        
        # Initialize color pairs
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Header
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Stats
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Alert
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # High bandwidth
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Selected
            curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Status bar
    
    def add_alert(self, message, alert_type="INFO"):
        """Add alert message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.alerts.append(f"[{timestamp}] [{alert_type}] {message}")
        if len(self.alerts) > 10:
            self.alerts.pop(0)
    
    def format_bytes(self, bytes_val):
        """Format bytes to human readable"""
        if bytes_val < 1024:
            return f"{bytes_val:.0f} B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val/1024:.1f} KB"
        else:
            return f"{bytes_val/(1024*1024):.1f} MB"
    
    def draw_header(self):
        """Draw header"""
        height, width = self.stdscr.getmaxyx()
        
        title = "NETWORK BANDWIDTH MONITOR - PER-PROCESS TRACKING"
        subtitle = "OS-Level Network Traffic Monitoring"
        
        try:
            self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(0, (width - len(title)) // 2, title)
            self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
            
            self.stdscr.addstr(1, (width - len(subtitle)) // 2, subtitle)
            self.stdscr.addstr(2, 0, "=" * width)
        except:
            pass
    
    def draw_controls(self, y_pos):
        """Draw control instructions"""
        height, width = self.stdscr.getmaxyx()
        
        status = "MONITORING" if self.monitoring else "STOPPED"
        status_color = curses.color_pair(1) if self.monitoring else curses.color_pair(4)
        
        controls = [
            f"[S]tart  [Q]uit  [R]eset  [H]elp  [T]hreshold  Status: ",
            f"{status}"
        ]
        
        try:
            x = 2
            self.stdscr.addstr(y_pos, x, controls[0])
            x += len(controls[0])
            self.stdscr.attron(status_color | curses.A_BOLD)
            self.stdscr.addstr(y_pos, x, controls[1])
            self.stdscr.attroff(status_color | curses.A_BOLD)
        except:
            pass
    
    def draw_stats(self, y_pos):
        """Draw overall statistics"""
        stats = self.packet_capture.get_process_stats()
        
        total_upload = sum(s['upload_bytes'] for s in stats.values())
        total_download = sum(s['download_bytes'] for s in stats.values())
        active_procs = len(stats)
        
        try:
            self.stdscr.attron(curses.color_pair(2))
            self.stdscr.addstr(y_pos, 2, f"Total Upload: {self.format_bytes(total_upload)}")
            self.stdscr.addstr(y_pos, 30, f"Total Download: {self.format_bytes(total_download)}")
            self.stdscr.addstr(y_pos, 60, f"Active Processes: {active_procs}")
            self.stdscr.attroff(curses.color_pair(2))
        except:
            pass
    
    def draw_process_table(self, y_pos):
        """Draw process table"""
        height, width = self.stdscr.getmaxyx()
        stats = self.packet_capture.get_process_stats()
        
        # Header
        try:
            header = f"{'PID':<8} {'Process':<20} {'Up(KB/s)':<12} {'Down(KB/s)':<12} {'Total Up':<12} {'Total Down':<12} {'Protocol':<15}"
            self.stdscr.attron(curses.A_BOLD)
            self.stdscr.addstr(y_pos, 2, header[:width-4])
            self.stdscr.attroff(curses.A_BOLD)
            self.stdscr.addstr(y_pos + 1, 2, "-" * (width - 4))
        except:
            pass
        
        # Process rows
        row_num = 0
        max_rows = height - y_pos - 10  # Leave space for alerts
        
        sorted_stats = sorted(stats.items(), 
                            key=lambda x: x[1]['upload_rate'] + x[1]['download_rate'], 
                            reverse=True)
        
        for pid, data in sorted_stats[:max_rows]:
            y = y_pos + 2 + row_num
            if y >= height - 8:  # Leave room for alerts
                break
            
            upload_rate_kb = data['upload_rate'] / 1024
            download_rate_kb = data['download_rate'] / 1024
            protocols = ','.join(sorted(data['protocols']))[:14] if data['protocols'] else 'N/A'
            
            # Check for high bandwidth
            is_alert = (upload_rate_kb * 1024 > self.alert_threshold or 
                       download_rate_kb * 1024 > self.alert_threshold)
            
            if is_alert and pid not in self.alerted_processes:
                self.add_alert(
                    f"HIGH: {data['name']} (PID {pid}) - "
                    f"Up:{upload_rate_kb:.1f} Down:{download_rate_kb:.1f} KB/s",
                    "WARNING"
                )
                self.alerted_processes.add(pid)
                
                # Log to database
                max_rate = max(upload_rate_kb, download_rate_kb)
                self.database_logger.log_alert(
                    pid, data['name'], "BANDWIDTH_SPIKE", 
                    max_rate, self.alert_threshold / 1024
                )
            elif not is_alert:
                self.alerted_processes.discard(pid)
            
            # Format row
            line = f"{pid:<8} {data['name'][:19]:<20} {upload_rate_kb:<12.2f} {download_rate_kb:<12.2f} "
            line += f"{self.format_bytes(data['upload_bytes']):<12} {self.format_bytes(data['download_bytes']):<12} {protocols:<15}"
            
            try:
                if is_alert:
                    self.stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                    self.stdscr.addstr(y, 2, line[:width-4])
                    self.stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(y, 2, line[:width-4])
                
                # Log to database
                self.database_logger.log_traffic(
                    pid, data['name'], 
                    data['upload_bytes'], data['download_bytes'],
                    data['upload_rate'], data['download_rate'],
                    list(data['protocols'])
                )
            except:
                pass
            
            row_num += 1
        
        return y_pos + 2 + row_num + 1
    
    def draw_alerts(self, y_pos):
        """Draw alert panel"""
        height, width = self.stdscr.getmaxyx()
        
        try:
            self.stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
            self.stdscr.addstr(y_pos, 2, "RECENT ALERTS:")
            self.stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
            
            for i, alert in enumerate(self.alerts[-5:]):  # Show last 5
                if y_pos + 1 + i < height - 2:
                    if "WARNING" in alert:
                        self.stdscr.attron(curses.color_pair(3))
                    self.stdscr.addstr(y_pos + 1 + i, 2, alert[:width-4])
                    if "WARNING" in alert:
                        self.stdscr.attroff(curses.color_pair(3))
        except:
            pass
    
    def draw_help(self):
        """Draw help screen"""
        height, width = self.stdscr.getmaxyx()
        
        help_text = [
            "KEYBOARD SHORTCUTS",
            "",
            "S - Start/Stop monitoring",
            "Q - Quit application",
            "R - Reset statistics",
            "H - Toggle this help",
            "T - Set bandwidth threshold",
            "",
            "Press any key to continue..."
        ]
        
        y_start = (height - len(help_text)) // 2
        
        self.stdscr.clear()
        for i, line in enumerate(help_text):
            try:
                if i == 0:
                    self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                self.stdscr.addstr(y_start + i, (width - len(line)) // 2, line)
                if i == 0:
                    self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
            except:
                pass
        
        self.stdscr.refresh()
        self.stdscr.nodelay(0)
        self.stdscr.getch()
        self.stdscr.nodelay(1)
    
    def start_monitoring(self):
        """Start monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.session_id = self.database_logger.start_session()
        self.packet_capture.start()
        self.add_alert("Monitoring started", "INFO")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        self.packet_capture.stop()
        
        stats = self.packet_capture.get_process_stats()
        total_upload = sum(s['upload_bytes'] for s in stats.values())
        total_download = sum(s['download_bytes'] for s in stats.values())
        
        if self.session_id:
            self.database_logger.end_session(
                self.session_id, total_upload, total_download
            )
        
        self.add_alert("Monitoring stopped", "INFO")
    
    def reset_stats(self):
        """Reset statistics"""
        self.packet_capture.reset_stats()
        self.alerted_processes.clear()
        self.add_alert("Statistics reset", "INFO")
    
    def run(self):
        """Main loop"""
        import os
        if os.geteuid() != 0:
            self.stdscr.clear()
            self.stdscr.addstr(5, 5, "ERROR: This application must be run with sudo!")
            self.stdscr.addstr(7, 5, "Please run: sudo python3 main_tui.py")
            self.stdscr.addstr(9, 5, "Press any key to exit...")
            self.stdscr.refresh()
            self.stdscr.nodelay(0)
            self.stdscr.getch()
            return
        
        self.add_alert("Application started - Press 'S' to start monitoring", "INFO")
        self.add_alert("Press 'H' for help", "INFO")
        
        while True:
            try:
                self.stdscr.clear()
                height, width = self.stdscr.getmaxyx()
                
                # Draw UI
                self.draw_header()
                self.draw_controls(3)
                self.draw_stats(5)
                
                table_end = self.draw_process_table(7)
                self.draw_alerts(max(table_end + 1, height - 8))
                
                # Status bar
                try:
                    status_text = f" Threshold: {self.alert_threshold/1024:.0f} KB/s | Time: {datetime.now().strftime('%H:%M:%S')} "
                    self.stdscr.attron(curses.color_pair(6))
                    self.stdscr.addstr(height - 1, 0, status_text.ljust(width))
                    self.stdscr.attroff(curses.color_pair(6))
                except:
                    pass
                
                self.stdscr.refresh()
                
                # Calculate bandwidth
                if self.monitoring:
                    self.packet_capture.calculate_bandwidth()
                
                # Handle input
                key = self.stdscr.getch()
                
                if key == ord('q') or key == ord('Q'):
                    if self.monitoring:
                        self.stop_monitoring()
                    break
                elif key == ord('s') or key == ord('S'):
                    if self.monitoring:
                        self.stop_monitoring()
                    else:
                        self.start_monitoring()
                elif key == ord('r') or key == ord('R'):
                    self.reset_stats()
                elif key == ord('h') or key == ord('H'):
                    self.draw_help()
                elif key == ord('t') or key == ord('T'):
                    # Simple threshold adjustment
                    self.alert_threshold *= 2
                    if self.alert_threshold > 10240 * 1024:  # Max 10 MB
                        self.alert_threshold = 512 * 1024  # Reset to 512 KB
                    self.add_alert(f"Threshold set to {self.alert_threshold/1024:.0f} KB/s", "INFO")
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                if self.monitoring:
                    self.stop_monitoring()
                break
            except Exception as e:
                # Continue on errors
                pass


def main_tui(stdscr):
    """Main TUI entry point"""
    from packet_capture import PacketCapture
    from database_logger import DatabaseLogger
    from config import CAPTURE_INTERFACE
    
    packet_capture = PacketCapture(interface=CAPTURE_INTERFACE)
    database_logger = DatabaseLogger()
    
    app = NetworkMonitorTUI(stdscr, packet_capture, database_logger)
    app.run()


if __name__ == "__main__":
    curses.wrapper(main_tui)

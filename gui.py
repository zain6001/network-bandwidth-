"""
Tkinter GUI for Network Monitor
Real-time display of per-process network bandwidth usage
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime, timedelta
import threading
import os

from config import (GUI_REFRESH_RATE, WINDOW_WIDTH, WINDOW_HEIGHT, 
                    FONT_FAMILY, FONT_SIZE, BANDWIDTH_ALERT_THRESHOLD)
from report_generator import ReportGenerator


class NetworkMonitorGUI:
    def __init__(self, root, packet_capture, database_logger):
        self.root = root
        self.packet_capture = packet_capture
        self.database_logger = database_logger
        self.report_generator = ReportGenerator(database_logger)
        self.monitoring = False
        self.session_id = None
        self.alert_threshold = BANDWIDTH_ALERT_THRESHOLD * 1024  # Convert to bytes
        self.alerted_processes = set()
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the main GUI window"""
        self.root.title("Network Bandwidth Monitor - Per-Process Tracking")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Control Panel
        self.create_control_panel()
        
        # Statistics Panel
        self.create_stats_panel()
        
        # Process Table
        self.create_process_table()
        
        # Alert Panel
        self.create_alert_panel()
        
        # Status Bar
        self.create_status_bar()
        
    def create_control_panel(self):
        """Create control buttons panel"""
        control_frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=2)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start Button
        self.start_btn = tk.Button(
            control_frame, 
            text="Start Monitoring", 
            command=self.start_monitoring,
            bg="green", 
            fg="white",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Stop Button
        self.stop_btn = tk.Button(
            control_frame, 
            text="Stop Monitoring", 
            command=self.stop_monitoring,
            bg="red", 
            fg="white",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            width=15,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Reset Button
        reset_btn = tk.Button(
            control_frame, 
            text="Reset Stats", 
            command=self.reset_stats,
            font=(FONT_FAMILY, FONT_SIZE),
            width=12
        )
        reset_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Report Button
        report_btn = tk.Button(
            control_frame, 
            text="Daily Report", 
            command=self.show_daily_report,
            font=(FONT_FAMILY, FONT_SIZE),
            width=12
        )
        report_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Custom Report Button
        custom_report_btn = tk.Button(
            control_frame, 
            text="Generate Report", 
            command=self.show_custom_report_dialog,
            font=(FONT_FAMILY, FONT_SIZE),
            width=15,
            bg="#4CAF50",
            fg="white"
        )
        custom_report_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Show All Processes Button
        show_all_btn = tk.Button(
            control_frame, 
            text="Show All Network Processes", 
            command=self.show_all_processes,
            font=(FONT_FAMILY, FONT_SIZE),
            width=20
        )
        show_all_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Threshold Setting
        tk.Label(control_frame, text="Alert Threshold (KB/s):", 
                font=(FONT_FAMILY, FONT_SIZE)).pack(side=tk.LEFT, padx=5)
        
        self.threshold_var = tk.StringVar(value=str(BANDWIDTH_ALERT_THRESHOLD))
        threshold_entry = tk.Entry(control_frame, textvariable=self.threshold_var, 
                                  width=8, font=(FONT_FAMILY, FONT_SIZE))
        threshold_entry.pack(side=tk.LEFT, padx=5)
        
        set_threshold_btn = tk.Button(
            control_frame, 
            text="Set", 
            command=self.set_threshold,
            font=(FONT_FAMILY, FONT_SIZE),
            width=5
        )
        set_threshold_btn.pack(side=tk.LEFT, padx=5)
        
    def create_stats_panel(self):
        """Create overall statistics panel"""
        stats_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=2)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Total Upload
        tk.Label(stats_frame, text="Total Upload:", 
                font=(FONT_FAMILY, FONT_SIZE, "bold")).grid(row=0, column=0, padx=10, pady=5)
        self.total_upload_label = tk.Label(stats_frame, text="0 MB", 
                                          font=(FONT_FAMILY, FONT_SIZE))
        self.total_upload_label.grid(row=0, column=1, padx=10, pady=5)
        
        # Total Download
        tk.Label(stats_frame, text="Total Download:", 
                font=(FONT_FAMILY, FONT_SIZE, "bold")).grid(row=0, column=2, padx=10, pady=5)
        self.total_download_label = tk.Label(stats_frame, text="0 MB", 
                                            font=(FONT_FAMILY, FONT_SIZE))
        self.total_download_label.grid(row=0, column=3, padx=10, pady=5)
        
        # Active Processes
        tk.Label(stats_frame, text="Active Processes:", 
                font=(FONT_FAMILY, FONT_SIZE, "bold")).grid(row=0, column=4, padx=10, pady=5)
        self.active_proc_label = tk.Label(stats_frame, text="0", 
                                         font=(FONT_FAMILY, FONT_SIZE))
        self.active_proc_label.grid(row=0, column=5, padx=10, pady=5)
        
    def create_process_table(self):
        """Create the main process table"""
        # Table Frame
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("PID", "Process Name", "Upload (KB/s)", "Download (KB/s)", 
                  "Total Upload", "Total Download", "Protocols")
        
        self.tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("PID", text="PID")
        self.tree.heading("Process Name", text="Process Name")
        self.tree.heading("Upload (KB/s)", text="Upload (KB/s)")
        self.tree.heading("Download (KB/s)", text="Download (KB/s)")
        self.tree.heading("Total Upload", text="Total Upload")
        self.tree.heading("Total Download", text="Total Download")
        self.tree.heading("Protocols", text="Protocols")
        
        # Column widths
        self.tree.column("PID", width=80)
        self.tree.column("Process Name", width=200)
        self.tree.column("Upload (KB/s)", width=120)
        self.tree.column("Download (KB/s)", width=120)
        self.tree.column("Total Upload", width=120)
        self.tree.column("Total Download", width=120)
        self.tree.column("Protocols", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure tag for highlighted rows (alerts)
        self.tree.tag_configure('alert', background='#ffcccc')
        
    def create_alert_panel(self):
        """Create alert display panel"""
        alert_frame = tk.LabelFrame(self.root, text="Alerts", 
                                   font=(FONT_FAMILY, FONT_SIZE, "bold"))
        alert_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.alert_text = scrolledtext.ScrolledText(
            alert_frame, 
            height=5, 
            font=(FONT_FAMILY, FONT_SIZE),
            bg="#ffffcc"
        )
        self.alert_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame, 
            text="Ready - Click 'Start Monitoring' to begin",
            font=(FONT_FAMILY, FONT_SIZE),
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=5)
        
    def start_monitoring(self):
        """Start network monitoring"""
        if self.monitoring:
            return
        
        # Check if running as root
        import os
        if os.geteuid() != 0:
            messagebox.showerror(
                "Permission Error",
                "This application must be run with sudo privileges!\n\n"
                "Please run: sudo python3 main.py"
            )
            return
        
        self.monitoring = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Monitoring active - Capturing packets...")
        
        # Start session in database
        self.session_id = self.database_logger.start_session()
        
        # Update process mappings before starting
        self.add_alert("Updating process mappings...", "INFO")
        self.packet_capture.process_mapper.update_socket_mappings()
        
        # Get initial network process count
        network_procs = self.packet_capture.process_mapper.get_all_network_processes()
        self.add_alert(f"Found {len(network_procs)} processes with network connections", "INFO")
        
        # Start packet capture
        self.packet_capture.start()
        
        # Start GUI update loop
        self.update_display()
        
        self.add_alert("Monitoring started - Processes will appear as network traffic is detected", "INFO")
        
    def stop_monitoring(self):
        """Stop network monitoring"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Monitoring stopped")
        
        # Stop packet capture
        self.packet_capture.stop()
        
        # End session in database
        stats = self.packet_capture.get_process_stats()
        total_upload = sum(s['upload_bytes'] for s in stats.values())
        total_download = sum(s['download_bytes'] for s in stats.values())
        
        if self.session_id:
            self.database_logger.end_session(
                self.session_id, total_upload, total_download
            )
        
        self.add_alert("Monitoring stopped", "INFO")
        
    def reset_stats(self):
        """Reset all statistics"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all statistics?"):
            self.packet_capture.reset_stats()
            self.alerted_processes.clear()
            
            # Clear table
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.add_alert("Statistics reset", "INFO")
            
    def set_threshold(self):
        """Set bandwidth alert threshold"""
        try:
            threshold_kb = float(self.threshold_var.get())
            self.alert_threshold = threshold_kb * 1024  # Convert to bytes
            self.add_alert(f"Alert threshold set to {threshold_kb} KB/s", "INFO")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
            
    def update_display(self):
        """Update the display with current statistics"""
        if not self.monitoring:
            return
        
        # Calculate bandwidth rates
        self.packet_capture.calculate_bandwidth()
        
        # Get process statistics
        stats = self.packet_capture.get_process_stats()
        
        # Update totals
        total_upload = sum(s['upload_bytes'] for s in stats.values())
        total_download = sum(s['download_bytes'] for s in stats.values())
        
        self.total_upload_label.config(text=f"{total_upload / (1024*1024):.2f} MB")
        self.total_download_label.config(text=f"{total_download / (1024*1024):.2f} MB")
        self.active_proc_label.config(text=str(len(stats)))
        
        # Update process table
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add current processes
        for pid, data in sorted(stats.items(), 
                               key=lambda x: x[1]['upload_rate'] + x[1]['download_rate'], 
                               reverse=True):
            
            upload_rate_kb = data['upload_rate'] / 1024
            download_rate_kb = data['download_rate'] / 1024
            total_up_mb = data['upload_bytes'] / (1024 * 1024)
            total_down_mb = data['download_bytes'] / (1024 * 1024)
            protocols = ', '.join(sorted(data['protocols'])) if data['protocols'] else 'N/A'
            
            # Check for bandwidth spike
            tags = ()
            if (upload_rate_kb * 1024 > self.alert_threshold or 
                download_rate_kb * 1024 > self.alert_threshold):
                tags = ('alert',)
                
                # Log alert if not already logged for this process
                if pid not in self.alerted_processes:
                    self.add_alert(
                        f"HIGH BANDWIDTH: {data['name']} (PID {pid}) - "
                        f"Up: {upload_rate_kb:.1f} KB/s, Down: {download_rate_kb:.1f} KB/s",
                        "WARNING"
                    )
                    self.alerted_processes.add(pid)
                    
                    # Log to database
                    max_rate = max(upload_rate_kb, download_rate_kb)
                    self.database_logger.log_alert(
                        pid, data['name'], "BANDWIDTH_SPIKE", 
                        max_rate, self.alert_threshold / 1024
                    )
            else:
                # Remove from alerted set if bandwidth is back to normal
                self.alerted_processes.discard(pid)
            
            self.tree.insert('', 'end', values=(
                pid,
                data['name'],
                f"{upload_rate_kb:.2f}",
                f"{download_rate_kb:.2f}",
                f"{total_up_mb:.2f} MB",
                f"{total_down_mb:.2f} MB",
                protocols
            ), tags=tags)
            
            # Log to database periodically
            self.database_logger.log_traffic(
                pid, data['name'], 
                data['upload_bytes'], data['download_bytes'],
                data['upload_rate'], data['download_rate'],
                list(data['protocols'])
            )
        
        # Schedule next update
        self.root.after(GUI_REFRESH_RATE, self.update_display)
        
    def add_alert(self, message, alert_type="INFO"):
        """Add an alert to the alert panel"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        alert_msg = f"[{timestamp}] [{alert_type}] {message}\n"
        
        self.alert_text.insert(tk.END, alert_msg)
        self.alert_text.see(tk.END)
        
        # Keep only last 100 lines
        lines = int(self.alert_text.index('end-1c').split('.')[0])
        if lines > 100:
            self.alert_text.delete('1.0', '2.0')
            
    def show_daily_report(self):
        """Show daily traffic report"""
        report_data = self.database_logger.get_daily_report()
        
        # Create report window
        report_window = tk.Toplevel(self.root)
        report_window.title("Daily Traffic Report")
        report_window.geometry("800x400")
        
        # Create treeview for report
        columns = ("PID", "Process", "Upload", "Download", "Total", "Records")
        tree = ttk.Treeview(report_window, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130)
        
        # Add scrollbar
        vsb = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Populate report
        for row in report_data:
            pid, name, up, down, total, records = row
            tree.insert('', 'end', values=(
                pid, name,
                f"{up / (1024*1024):.2f} MB",
                f"{down / (1024*1024):.2f} MB",
                f"{total / (1024*1024):.2f} MB",
                records
            ))
        
        if not report_data:
            tk.Label(report_window, text="No data available for today",
                    font=(FONT_FAMILY, 12)).pack(pady=20)
    
    def show_all_processes(self):
        """Show all processes with active network connections"""
        processes = self.packet_capture.process_mapper.get_all_network_processes()
        
        # Create window
        proc_window = tk.Toplevel(self.root)
        proc_window.title("All Network Processes")
        proc_window.geometry("600x400")
        
        # Create treeview
        columns = ("PID", "Process Name")
        tree = ttk.Treeview(proc_window, columns=columns, show="headings")
        
        tree.heading("PID", text="PID")
        tree.heading("Process Name", text="Process Name")
        tree.column("PID", width=100)
        tree.column("Process Name", width=450)
        
        # Add scrollbar
        vsb = ttk.Scrollbar(proc_window, orient="vertical", command=tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Populate list
        for pid, name in sorted(processes, key=lambda x: x[1]):
            tree.insert('', 'end', values=(pid, name))
        
        # Add info label
        info_label = tk.Label(
            proc_window,
            text=f"Total network processes found: {len(processes)}\n"
                 f"Note: Start monitoring to see bandwidth usage",
            font=(FONT_FAMILY, FONT_SIZE),
            justify=tk.LEFT
        )
        info_label.pack(pady=10)
        
        if not processes:
            tk.Label(proc_window, text="No network processes found\n"
                                       "Try running as sudo or starting monitoring",
                    font=(FONT_FAMILY, 12)).pack(pady=20)
    
    def show_custom_report_dialog(self):
        """Show dialog to generate custom report with date range"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Generate Custom Report")
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        title_label = tk.Label(
            dialog,
            text="Generate Network Traffic Report",
            font=(FONT_FAMILY, 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Date range frame
        date_frame = tk.LabelFrame(dialog, text="Date Range", font=(FONT_FAMILY, FONT_SIZE))
        date_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Start date
        tk.Label(date_frame, text="Start Date (YYYY-MM-DD):", font=(FONT_FAMILY, FONT_SIZE)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        start_date_entry = tk.Entry(date_frame, textvariable=start_date_var, width=20, font=(FONT_FAMILY, FONT_SIZE))
        start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Start time
        tk.Label(date_frame, text="Start Time (HH:MM):", font=(FONT_FAMILY, FONT_SIZE)).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        start_time_var = tk.StringVar(value="00:00")
        start_time_entry = tk.Entry(date_frame, textvariable=start_time_var, width=20, font=(FONT_FAMILY, FONT_SIZE))
        start_time_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # End date
        tk.Label(date_frame, text="End Date (YYYY-MM-DD):", font=(FONT_FAMILY, FONT_SIZE)).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        end_date_entry = tk.Entry(date_frame, textvariable=end_date_var, width=20, font=(FONT_FAMILY, FONT_SIZE))
        end_date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # End time
        tk.Label(date_frame, text="End Time (HH:MM):", font=(FONT_FAMILY, FONT_SIZE)).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        end_time_var = tk.StringVar(value="23:59")
        end_time_entry = tk.Entry(date_frame, textvariable=end_time_var, width=20, font=(FONT_FAMILY, FONT_SIZE))
        end_time_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Quick date buttons
        quick_frame = tk.Frame(dialog)
        quick_frame.pack(pady=5)
        
        tk.Label(quick_frame, text="Quick Select:", font=(FONT_FAMILY, FONT_SIZE)).pack(side=tk.LEFT, padx=5)
        
        def set_today():
            today = datetime.now().strftime("%Y-%m-%d")
            start_date_var.set(today)
            end_date_var.set(today)
            start_time_var.set("00:00")
            end_time_var.set("23:59")
        
        def set_last_7_days():
            start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            end = datetime.now().strftime("%Y-%m-%d")
            start_date_var.set(start)
            end_date_var.set(end)
            start_time_var.set("00:00")
            end_time_var.set("23:59")
        
        def set_last_30_days():
            start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            end = datetime.now().strftime("%Y-%m-%d")
            start_date_var.set(start)
            end_date_var.set(end)
            start_time_var.set("00:00")
            end_time_var.set("23:59")
        
        tk.Button(quick_frame, text="Today", command=set_today, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_frame, text="Last 7 Days", command=set_last_7_days, width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_frame, text="Last 30 Days", command=set_last_30_days, width=10).pack(side=tk.LEFT, padx=2)
        
        # Format selection
        format_frame = tk.LabelFrame(dialog, text="Output Format", font=(FONT_FAMILY, FONT_SIZE))
        format_frame.pack(fill=tk.X, padx=20, pady=10)
        
        format_var = tk.StringVar(value="both")
        tk.Radiobutton(format_frame, text="Markdown (.md)", variable=format_var, value="md", font=(FONT_FAMILY, FONT_SIZE)).pack(anchor=tk.W, padx=10)
        tk.Radiobutton(format_frame, text="Word Document (.docx)", variable=format_var, value="docx", font=(FONT_FAMILY, FONT_SIZE)).pack(anchor=tk.W, padx=10)
        tk.Radiobutton(format_frame, text="Both Formats", variable=format_var, value="both", font=(FONT_FAMILY, FONT_SIZE)).pack(anchor=tk.W, padx=10)
        
        # Generate button
        def generate_report():
            try:
                # Parse dates
                start_date_str = f"{start_date_var.get()} {start_time_var.get()}:00"
                end_date_str = f"{end_date_var.get()} {end_time_var.get()}:59"
                
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
                
                if start_date >= end_date:
                    messagebox.showerror("Invalid Date Range", "Start date must be before end date!")
                    return
                
                # Ask for output directory
                output_dir = filedialog.askdirectory(title="Select Output Directory")
                if not output_dir:
                    return
                
                format_choice = format_var.get()
                base_filename = f"network_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
                
                success_files = []
                
                # Generate Markdown
                if format_choice in ["md", "both"]:
                    md_file = os.path.join(output_dir, f"{base_filename}.md")
                    success, result = self.report_generator.generate_markdown_report(
                        start_date, end_date, md_file
                    )
                    if success:
                        success_files.append(result)
                    else:
                        messagebox.showerror("Error", f"Failed to generate Markdown: {result}")
                
                # Generate Word
                if format_choice in ["docx", "both"]:
                    docx_file = os.path.join(output_dir, f"{base_filename}.docx")
                    success, result = self.report_generator.generate_word_report(
                        start_date, end_date, docx_file
                    )
                    if success:
                        success_files.append(result)
                    else:
                        messagebox.showerror("Error", f"Failed to generate Word: {result}")
                
                if success_files:
                    dialog.destroy()
                    msg = "Report(s) generated successfully:\n\n"
                    for f in success_files:
                        msg += f"- {f}\n"
                    messagebox.showinfo("Success", msg)
                    
            except ValueError as e:
                messagebox.showerror("Invalid Date", f"Please enter valid dates in YYYY-MM-DD format\n\n{e}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {e}")
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Generate Report",
            command=generate_report,
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            font=(FONT_FAMILY, FONT_SIZE),
            width=10
        ).pack(side=tk.LEFT, padx=5)

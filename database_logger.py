"""
Database Logging Module
Stores network traffic data in SQLite database
"""

import sqlite3
import threading
from datetime import datetime, timedelta
from config import DATABASE_FILE


class DatabaseLogger:
    def __init__(self, db_file=DATABASE_FILE):
        self.db_file = db_file
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.lock:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Create traffic log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS traffic_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pid INTEGER,
                    process_name TEXT,
                    upload_bytes INTEGER,
                    download_bytes INTEGER,
                    upload_rate REAL,
                    download_rate REAL,
                    total_bytes INTEGER,
                    protocols TEXT
                )
            ''')
            
            # Create session table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time DATETIME,
                    end_time DATETIME,
                    total_upload INTEGER,
                    total_download INTEGER
                )
            ''')
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pid INTEGER,
                    process_name TEXT,
                    alert_type TEXT,
                    bandwidth_value REAL,
                    threshold REAL
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON traffic_log(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_pid 
                ON traffic_log(pid)
            ''')
            
            conn.commit()
            conn.close()
    
    def log_traffic(self, pid, process_name, upload_bytes, download_bytes, 
                    upload_rate, download_rate, protocols):
        """Log traffic data for a process"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                total_bytes = upload_bytes + download_bytes
                protocols_str = ','.join(protocols) if protocols else 'UNKNOWN'
                
                cursor.execute('''
                    INSERT INTO traffic_log 
                    (pid, process_name, upload_bytes, download_bytes, 
                     upload_rate, download_rate, total_bytes, protocols)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (pid, process_name, upload_bytes, download_bytes,
                      upload_rate, download_rate, total_bytes, protocols_str))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Database logging error: {e}")
    
    def log_alert(self, pid, process_name, alert_type, bandwidth_value, threshold):
        """Log a bandwidth alert"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO alerts 
                    (pid, process_name, alert_type, bandwidth_value, threshold)
                    VALUES (?, ?, ?, ?, ?)
                ''', (pid, process_name, alert_type, bandwidth_value, threshold))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Alert logging error: {e}")
    
    def start_session(self):
        """Start a new monitoring session"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO sessions (start_time, total_upload, total_download)
                    VALUES (?, 0, 0)
                ''', (datetime.now(),))
                
                session_id = cursor.lastrowid
                conn.commit()
                conn.close()
                return session_id
            except Exception as e:
                print(f"Session start error: {e}")
                return None
    
    def end_session(self, session_id, total_upload, total_download):
        """End a monitoring session"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE sessions 
                    SET end_time = ?, total_upload = ?, total_download = ?
                    WHERE id = ?
                ''', (datetime.now(), total_upload, total_download, session_id))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Session end error: {e}")
    
    def get_traffic_report(self, start_date=None, end_date=None, pid=None):
        """Generate traffic report for specified time period"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                query = '''
                    SELECT pid, process_name, 
                           SUM(upload_bytes) as total_upload,
                           SUM(download_bytes) as total_download,
                           SUM(total_bytes) as total_data,
                           COUNT(*) as records
                    FROM traffic_log
                    WHERE 1=1
                '''
                params = []
                
                if start_date:
                    query += ' AND timestamp >= ?'
                    params.append(start_date)
                
                if end_date:
                    query += ' AND timestamp <= ?'
                    params.append(end_date)
                
                if pid:
                    query += ' AND pid = ?'
                    params.append(pid)
                
                query += ' GROUP BY pid, process_name ORDER BY total_data DESC'
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                conn.close()
                return results
            except Exception as e:
                print(f"Report generation error: {e}")
                return []
    
    def get_daily_report(self):
        """Get today's traffic report"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        return self.get_traffic_report(start_date=today, end_date=tomorrow)
    
    def get_recent_alerts(self, limit=10):
        """Get recent bandwidth alerts"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT timestamp, pid, process_name, alert_type, 
                           bandwidth_value, threshold
                    FROM alerts
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                results = cursor.fetchall()
                conn.close()
                return results
            except Exception as e:
                print(f"Alert retrieval error: {e}")
                return []
    
    def get_alerts_by_date_range(self, start_date, end_date):
        """Get alerts within date range for report"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT timestamp, pid, process_name, alert_type, 
                           bandwidth_value, threshold
                    FROM alerts
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                ''', (start_date, end_date))
                
                results = cursor.fetchall()
                conn.close()
                return results
            except Exception as e:
                print(f"Alert retrieval error: {e}")
                return []
    
    def get_detailed_report_data(self, start_date, end_date):
        """Get detailed data for report generation"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                # Get overall statistics
                cursor.execute('''
                    SELECT 
                        COUNT(DISTINCT pid) as unique_processes,
                        SUM(upload_bytes) as total_upload,
                        SUM(download_bytes) as total_download,
                        AVG(upload_rate) as avg_upload_rate,
                        AVG(download_rate) as avg_download_rate,
                        MAX(upload_rate) as max_upload_rate,
                        MAX(download_rate) as max_download_rate
                    FROM traffic_log
                    WHERE timestamp BETWEEN ? AND ?
                ''', (start_date, end_date))
                
                overall_stats = cursor.fetchone()
                
                # Get per-process statistics
                cursor.execute('''
                    SELECT 
                        pid, 
                        process_name,
                        SUM(upload_bytes) as total_upload,
                        SUM(download_bytes) as total_download,
                        AVG(upload_rate) as avg_upload_rate,
                        AVG(download_rate) as avg_download_rate,
                        MAX(upload_rate) as max_upload_rate,
                        MAX(download_rate) as max_download_rate,
                        COUNT(*) as records,
                        protocols
                    FROM traffic_log
                    WHERE timestamp BETWEEN ? AND ?
                    GROUP BY pid, process_name
                    ORDER BY (SUM(upload_bytes) + SUM(download_bytes)) DESC
                ''', (start_date, end_date))
                
                process_stats = cursor.fetchall()
                
                conn.close()
                return overall_stats, process_stats
            except Exception as e:
                print(f"Detailed report error: {e}")
                return None, []
    
    def get_sessions_in_range(self, start_date, end_date):
        """Get monitoring sessions within date range"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, start_time, end_time, total_upload, total_download
                    FROM sessions
                    WHERE start_time BETWEEN ? AND ?
                    ORDER BY start_time DESC
                ''', (start_date, end_date))
                
                results = cursor.fetchall()
                conn.close()
                return results
            except Exception as e:
                print(f"Session retrieval error: {e}")
                return []
    
    def cleanup_old_data(self, days=30):
        """Delete data older than specified days"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                cursor.execute('DELETE FROM traffic_log WHERE timestamp < ?', 
                             (cutoff_date,))
                cursor.execute('DELETE FROM alerts WHERE timestamp < ?', 
                             (cutoff_date,))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Cleanup error: {e}")

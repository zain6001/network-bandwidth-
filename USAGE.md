# Usage Examples and Tips

## Basic Usage

### Starting the Monitor

```bash
# Start the application
sudo python3 main.py
```

### Quick Test

1. Click "Start Monitoring"
2. Open a web browser and visit some websites
3. Watch processes appear in the table with their bandwidth usage
4. Observe protocol classification (HTTP, HTTPS, DNS, etc.)

---

## Common Use Cases

### 1. Monitoring Browser Traffic

**Scenario**: See how much bandwidth your browser uses

**Steps**:
1. Start monitoring
2. Open Firefox/Chrome
3. Browse various websites
4. Observe:
   - Process name: "firefox" or "chrome"
   - Protocols: HTTPS (443), HTTP (80), DNS (53)
   - Upload: Small (requests)
   - Download: Large (content)

### 2. Detecting Background Applications

**Scenario**: Find apps using internet in the background

**Steps**:
1. Close all visible applications
2. Start monitoring
3. Wait 30 seconds
4. Check the process table
5. Any process listed is using network

**Common findings**:
- System updates
- Cloud sync apps
- Chat applications
- Auto-update services

### 3. Bandwidth Spike Detection

**Scenario**: Get alerted when any process uses excessive bandwidth

**Steps**:
1. Set threshold (e.g., 1024 KB/s = 1 MB/s)
2. Click "Set"
3. Start monitoring
4. High bandwidth processes will:
   - Appear in RED in the table
   - Trigger alert in Alert Panel
   - Be logged to database

### 4. Tracking Download Managers

**Scenario**: Monitor download progress

**Process examples**:
- wget
- curl
- transmission (torrent)
- aria2

**What you'll see**:
- High download rates
- TCP protocol
- Increasing total download

### 5. Identifying Network-Heavy Processes

**Scenario**: Find which app is slowing down your network

**Steps**:
1. Start monitoring during slow network
2. Sort by download speed (click column header)
3. Top processes are the culprits

---

## Advanced Usage

### Custom Interface Selection

Edit `config.py`:

```python
CAPTURE_INTERFACE = "eth0"  # Or wlan0, wlp3s0, etc.
```

To find your interfaces:
```bash
ip addr show
```

### Changing Refresh Rate

For slower systems, increase refresh interval in `config.py`:

```python
GUI_REFRESH_RATE = 2000  # Update every 2 seconds
```

### Database Queries

Access the SQLite database directly:

```bash
sqlite3 network_monitor.db
```

**Useful queries**:

```sql
-- Top 10 processes by total traffic
SELECT process_name, 
       SUM(upload_bytes + download_bytes) as total
FROM traffic_log 
GROUP BY process_name 
ORDER BY total DESC 
LIMIT 10;

-- Traffic in last hour
SELECT * FROM traffic_log 
WHERE timestamp > datetime('now', '-1 hour');

-- All bandwidth alerts
SELECT * FROM alerts 
ORDER BY timestamp DESC;
```

### Generating Custom Reports

```python
from database_logger import DatabaseLogger
from datetime import datetime, timedelta

logger = DatabaseLogger()

# Get yesterday's data
yesterday = datetime.now() - timedelta(days=1)
today = datetime.now()

report = logger.get_traffic_report(
    start_date=yesterday,
    end_date=today
)

for row in report:
    print(f"PID: {row[0]}, Process: {row[1]}")
    print(f"Upload: {row[2]/1024/1024:.2f} MB")
    print(f"Download: {row[3]/1024/1024:.2f} MB")
    print()
```

---

## Protocol Detection Examples

### HTTP Traffic
```
Port 80 detected
Process: curl, wget, or HTTP-only apps
Visible: Unencrypted traffic
```

### HTTPS Traffic
```
Port 443 detected  
Process: Most modern browsers and apps
Visible: Only metadata, not content
```

### DNS Queries
```
Port 53 (UDP)
Process: systemd-resolved, browsers
Shows: Domain name lookups
```

### SSH Connections
```
Port 22 (TCP)
Process: ssh client
Shows: Encrypted remote connection
```

---

## Tips and Tricks

### 1. Reducing False Positives

Some processes show "Unknown" if they close quickly:
- Normal for short HTTP requests
- Can be ignored for most use cases

### 2. System Services

Common system processes you'll see:
- `systemd-resolved`: DNS resolution
- `NetworkManager`: Network management
- `cupsd`: Printer services (if network printer)

### 3. Performance Tips

For better performance on slower systems:
- Increase `GUI_REFRESH_RATE` to 2000-3000ms
- Specify exact interface instead of capturing all
- Close the daily report window when not needed

### 4. Security Notes

**What this tool CAN see**:
- Which processes use network
- How much data each process transfers
- Protocol types (HTTP, HTTPS, DNS, etc.)
- Source/destination IP addresses and ports

**What this tool CANNOT see**:
- Content of HTTPS traffic (encrypted)
- Passwords or sensitive data (encrypted)
- VPN tunnel contents (encrypted)

### 5. Monitoring VPN Usage

To see VPN traffic:
```python
# In config.py
CAPTURE_INTERFACE = "tun0"  # Or your VPN interface
```

---

## Troubleshooting Examples

### Problem: No processes showing

**Test**:
```bash
# Generate traffic manually
ping -c 10 google.com &
curl https://example.com
```

Then check if processes appear.

### Problem: High CPU usage

**Solution**:
```python
# In config.py
GUI_REFRESH_RATE = 3000  # Reduce update frequency
BANDWIDTH_WINDOW = 2     # Larger calculation window
```

### Problem: Seeing unknown processes

**Identify them**:
```bash
# In another terminal
ps aux | grep <PID>
```

---

## Real-World Scenarios

### Scenario 1: Data Cap Monitoring
Track which apps consume most data to stay under ISP limits.

### Scenario 2: Malware Detection
Unexpected processes with high network usage could indicate malware.

### Scenario 3: Network Debugging
Identify which service is causing connection issues.

### Scenario 4: Bandwidth Throttling
Detect if specific apps are being throttled by your ISP.

### Scenario 5: Development Testing
Monitor your own application's network behavior during development.

---

## Command Line Alternatives

If GUI is not available:

```bash
# Monitor with tcpdump (requires root)
sudo tcpdump -i any -n

# See active connections
netstat -tunap

# Process network usage (if nethogs installed)
sudo nethogs

# Our tool advantages:
# - Process mapping
# - Historical logging  
# - Alert system
# - Visual interface
```

---

## Keyboard Shortcuts

- `Ctrl+C` in terminal: Stop application
- Close window: Stop monitoring and exit
- Click column headers: Sort by that column

---

## Data Privacy

**Important**: This tool logs all process network activity to a database.

To clear logs:
```bash
rm network_monitor.db
# Or clean old data
sqlite3 network_monitor.db "DELETE FROM traffic_log WHERE timestamp < datetime('now', '-7 days');"
```

---

## Integration Ideas

### Export to CSV

```python
import sqlite3
import csv

conn = sqlite3.connect('network_monitor.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM traffic_log')

with open('traffic_export.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'PID', 'Process', 'Upload', 'Download'])
    writer.writerows(cursor.fetchall())
```

### Alert Webhook

Add to `gui.py` in `add_alert()` method:

```python
if alert_type == "WARNING":
    import requests
    requests.post('http://your-webhook-url', json={
        'message': message,
        'timestamp': timestamp
    })
```

---

**Happy Monitoring! 🚀**

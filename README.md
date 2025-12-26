# Network Bandwidth Monitor

## OS-Level Network Bandwidth Monitoring & Traffic Logger with Per-Process Tracking (Linux)

A comprehensive network monitoring tool for Kali Linux that captures real-time network traffic and identifies every running process using the internet. Features a Tkinter GUI with real-time bandwidth display, process identification, and SQLite logging.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-orange.svg)

---

## 🚀 Features

### Core Capabilities

- **OS-Level Packet Capture**: Uses raw sockets via Scapy to capture all network traffic
- **Per-Process Tracking**: Maps every packet to its source/destination process using `/proc` filesystem
- **Real-Time Monitoring**: Updates every second with live bandwidth statistics
- **Protocol Classification**: Identifies HTTP, HTTPS, DNS, TCP, UDP traffic
- **Bandwidth Calculation**: Displays upload/download speeds in KB/s and MB/s
- **SQLite Logging**: Stores all traffic data for historical analysis
- **Bandwidth Alerts**: Configurable thresholds with visual and logged alerts
- **Session Management**: Track multiple monitoring sessions
- **Daily Reports**: Generate comprehensive traffic reports

### GUI Features

- **Process Table**: Shows PID, process name, bandwidth rates, totals, and protocols
- **Real-Time Updates**: Automatic refresh every 1 second
- **Alert Panel**: Displays bandwidth spikes and important events
- **Statistics Dashboard**: Shows total upload/download and active process count
- **Start/Stop Controls**: Easy monitoring control
- **Configurable Thresholds**: Set custom bandwidth alert levels
- **Daily Reports**: View historical traffic data

---

## 📋 Requirements

### System Requirements

- **Operating System**: Kali Linux (or any Linux distribution)
- **Python**: Version 3.7 or higher
- **Privileges**: Root access (sudo) required for packet capture
- **Architecture**: x86_64 or ARM

### Python Dependencies

```
scapy==2.5.0
psutil==5.9.6
netifaces (installed via pip)
```

---

## 🔧 Installation

### 1. Clone or Download

```bash
cd /home/kali/netmonitor
```

### 2. Install Dependencies

Install required Python packages:

```bash
sudo pip3 install -r requirements.txt
```

Or install individually:

```bash
sudo pip3 install scapy psutil netifaces
```

### 3. Verify Installation

Check that all dependencies are installed:

```bash
python3 -c "import scapy, psutil, netifaces; print('All dependencies OK')"
```

---

## 🎯 Usage

### Two Interface Options

This application comes with TWO interface options:

1. **Terminal UI (Recommended)** - Works in any terminal, no GUI required
2. **Tkinter GUI** - Requires X11/display server

### Starting the Application

**IMPORTANT**: The application MUST be run with sudo privileges:

#### Terminal UI Version (Recommended)
```bash
sudo python3 main_tui.py
```
✓ Works in SSH sessions  
✓ No display server needed  
✓ Keyboard-driven interface  
✓ All features included  

#### GUI Version (Requires Display)
```bash
sudo python3 main.py
```
✓ Mouse-driven interface  
✓ Requires X11/Wayland  
✓ Traditional GUI windows

### Terminal UI Controls (main_tui.py)

**Keyboard Shortcuts**:
- **S** - Start/Stop monitoring
- **Q** - Quit application
- **R** - Reset statistics
- **H** - Show help screen
- **T** - Cycle through bandwidth thresholds (512KB → 1MB → 2MB → 5MB → 10MB)

**Interface**:
- Real-time process table with bandwidth rates
- Color-coded alerts (red = high bandwidth)
- Statistics dashboard at top
- Alert panel at bottom
- Status bar shows threshold and time

### GUI Controls (main.py)

1. **Start Monitoring**: Click to begin packet capture and process tracking
2. **Stop Monitoring**: Click to stop monitoring and save session data
3. **Reset Stats**: Clear all current statistics (does not delete database)
4. **Daily Report**: View today's traffic summary
5. **Alert Threshold**: Set bandwidth limit (KB/s) for spike detection

### Understanding the Display

#### Process Table Columns

- **PID**: Process ID
- **Process Name**: Name of the application/process
- **Upload (KB/s)**: Current upload speed
- **Download (KB/s)**: Current download speed  
- **Total Upload**: Cumulative upload since monitoring started
- **Total Download**: Cumulative download since monitoring started
- **Protocols**: Detected protocols (TCP, UDP, HTTP, HTTPS, DNS)

#### Color Coding

- **Red Highlighted Rows**: Process exceeded bandwidth threshold
- **Alert Panel**: Shows warnings and informational messages

---

## 📊 Database Structure

The application stores data in `network_monitor.db` with the following tables:

### traffic_log
Stores per-process traffic statistics:
- `timestamp`: When the data was logged
- `pid`: Process ID
- `process_name`: Name of the process
- `upload_bytes`: Bytes uploaded
- `download_bytes`: Bytes downloaded
- `upload_rate`: Upload rate (bytes/sec)
- `download_rate`: Download rate (bytes/sec)
- `protocols`: Detected protocols

### sessions
Tracks monitoring sessions:
- `start_time`: Session start timestamp
- `end_time`: Session end timestamp
- `total_upload`: Total upload during session
- `total_download`: Total download during session

### alerts
Records bandwidth spike alerts:
- `timestamp`: When alert occurred
- `pid`: Process that triggered alert
- `process_name`: Process name
- `alert_type`: Type of alert
- `bandwidth_value`: Measured bandwidth
- `threshold`: Configured threshold

---

## 🔍 How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Main Application                     │
│                          (main.py)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   GUI Layer  │ │ Packet       │ │  Database    │
│  (gui.py)    │ │ Capture      │ │  Logger      │
│              │ │ (packet_     │ │ (database_   │
│  - Tkinter   │ │  capture.py) │ │  logger.py)  │
│  - Display   │ │              │ │              │
│  - Controls  │ │  - Scapy     │ │  - SQLite    │
└──────────────┘ │  - Raw       │ │  - Logging   │
                 │    Sockets   │ │  - Reports   │
                 └──────┬───────┘ └──────────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │  Process     │
                 │  Mapper      │
                 │ (process_    │
                 │  mapper.py)  │
                 │              │
                 │  - /proc     │
                 │  - psutil    │
                 └──────────────┘
```

### Packet Capture Flow

1. **Scapy Capture**: Raw packet capture on network interface
2. **Protocol Analysis**: Extract IP addresses, ports, and protocols
3. **Direction Detection**: Determine if packet is upload or download
4. **Process Mapping**: Match packet to process using:
   - Active connections via `psutil.net_connections()`
   - Socket inode mapping via `/proc/<pid>/fd/`
5. **Statistics Update**: Increment counters and calculate rates
6. **Database Logging**: Store traffic data every GUI refresh
7. **Alert Detection**: Check thresholds and trigger alerts

### Process Identification

The application uses multiple techniques to map packets to processes:

1. **Active Connection Matching**: Matches 4-tuple (src_ip, src_port, dst_ip, dst_port) to active connections
2. **Socket Inode Mapping**: Scans `/proc/<pid>/fd/` for socket file descriptors
3. **Port-based Matching**: For UDP and listening sockets, matches by port number

---

## ⚙️ Configuration

Edit [config.py](config.py) to customize:

```python
# Refresh rate for GUI (milliseconds)
GUI_REFRESH_RATE = 1000

# Bandwidth alert threshold (KB/s)
BANDWIDTH_ALERT_THRESHOLD = 1024  # 1 MB/s

# Capture interface (None = all interfaces)
CAPTURE_INTERFACE = None

# Window size
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
```

---

## 🐛 Troubleshooting

### "Permission Error: must be run with sudo"

**Solution**: Always run with `sudo python3 main.py`

### "Missing required dependencies"

**Solution**: Install all dependencies:
```bash
sudo pip3 install -r requirements.txt
```

### No processes showing in table

**Causes**:
- No active network traffic
- Firewall blocking capture
- Wrong network interface

**Solutions**:
- Generate some traffic (browse web, ping, etc.)
- Check firewall settings
- Specify correct interface in config.py

### High CPU usage

**Causes**:
- Too many packets being captured
- GUI refresh rate too high

**Solutions**:
- Increase `GUI_REFRESH_RATE` in config.py
- Filter specific interface instead of all

### Process name shows "Unknown"

**Cause**: Process terminated before identification

**Solution**: Normal behavior for short-lived connections

---

## 📝 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- IPv6 support
- Additional protocol detection (FTP, SSH, etc.)
- Export reports to CSV/PDF
- Network interface selection in GUI
- Filtering and search capabilities
- Dark mode theme

---

## ⚠️ Disclaimer

This tool is intended for educational purposes and legitimate network monitoring on systems you own or have permission to monitor. Unauthorized network monitoring may be illegal in your jurisdiction. Use responsibly.

---

## 📧 Support

For issues, questions, or suggestions:
- Check the troubleshooting section above
- Review the code comments for technical details
- Test with verbose logging enabled

---

## 🎓 Technical Notes

### Why Root Privileges?

Raw packet capture requires creating raw sockets, which is a privileged operation on Linux. This prevents unprivileged users from sniffing network traffic.

### Performance Considerations

- Packet capture is done in a separate thread to avoid blocking GUI
- Statistics are calculated once per second to balance accuracy and performance
- Database writes are batched with GUI updates
- Process mappings are cached to reduce `/proc` filesystem access

### Limitations

- Only works on Linux (uses `/proc` filesystem)
- Requires root access
- Cannot decrypt encrypted traffic (HTTPS content)
- May miss very short-lived connections
- Accuracy depends on system load

---

**Made with ❤️ for network monitoring and security analysis**
# network-bandwidth-

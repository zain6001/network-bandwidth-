# Custom Report Generation Guide

## Overview
The Network Monitor now includes a powerful report generation feature that allows you to:
- ✅ Select custom date ranges (start date and end date)
- ✅ Generate reports in **Markdown (.md)** format
- ✅ Generate reports in **Word (.docx)** format
- ✅ Include all bandwidth spikes and alerts
- ✅ View detailed per-process statistics
- ✅ Export monitoring session data

## How to Generate Reports

### Method 1: Using the GUI (Recommended)

1. **Launch the application**:
   ```bash
   sudo python3 main.py
   ```

2. **Click "Generate Report" button** (green button in control panel)

3. **Select Date Range**:
   - Enter **Start Date** (YYYY-MM-DD format, e.g., 2025-12-20)
   - Enter **Start Time** (HH:MM format, e.g., 09:00)
   - Enter **End Date** (YYYY-MM-DD format, e.g., 2025-12-26)
   - Enter **End Time** (HH:MM format, e.g., 18:00)

4. **Quick Date Selection** (shortcuts):
   - Click **"Today"** - Report for today only
   - Click **"Last 7 Days"** - Report for past week
   - Click **"Last 30 Days"** - Report for past month

5. **Choose Output Format**:
   - ⭕ **Markdown (.md)** - Text-based format, great for version control
   - ⭕ **Word Document (.docx)** - Professional document format
   - ⭕ **Both Formats** - Generate both at once (recommended)

6. **Click "Generate Report"**

7. **Select output directory** where reports will be saved

8. **Done!** You'll see a success message with file paths

### Method 2: Programmatic Generation

```python
from datetime import datetime, timedelta
from database_logger import DatabaseLogger
from report_generator import ReportGenerator

# Initialize
db = DatabaseLogger()
reporter = ReportGenerator(db)

# Set date range
start_date = datetime(2025, 12, 20, 0, 0, 0)
end_date = datetime(2025, 12, 26, 23, 59, 59)

# Generate Markdown report
reporter.generate_markdown_report(start_date, end_date, "report.md")

# Generate Word report
reporter.generate_word_report(start_date, end_date, "report.docx")
```

## Report Contents

### 1. **Header Information**
- Report generation timestamp
- Date range covered

### 2. **Overall Statistics**
- Unique processes monitored
- Total upload/download bandwidth (in MB)
- Average upload/download rates (KB/s)
- Peak bandwidth rates

### 3. **Monitoring Sessions**
Table showing all monitoring sessions in the period:
- Session ID
- Start time
- End time
- Total upload/download per session

### 4. **Per-Process Traffic**
Detailed table for each process:
- PID (Process ID)
- Process Name
- Total Upload (MB)
- Total Download (MB)
- Total Data (MB)
- Average upload/download rates
- Maximum upload/download rates
- Protocols used (TCP, UDP, HTTP, HTTPS, DNS)

### 5. **Bandwidth Alerts & Spikes** ⚠️
Complete list of all bandwidth alerts:
- Timestamp of alert
- PID and process name
- Alert type (BANDWIDTH_SPIKE)
- Actual bandwidth value
- Threshold that was exceeded

Example:
```
| 2025-12-26 14:25:30 | 1234 | firefox | BANDWIDTH_SPIKE | 2048.5 KB/s | 1024.0 KB/s |
```

### 6. **Top 5 Bandwidth Consumers**
Ranked list showing:
- Process name and PID
- Total bandwidth consumed
- Upload/download breakdown

## Report File Naming

Reports are automatically named with the date range:
```
network_report_YYYYMMDD_YYYYMMDD.md
network_report_YYYYMMDD_YYYYMMDD.docx
```

Example:
```
network_report_20251220_20251226.md
network_report_20251220_20251226.docx
```

## Sample Markdown Report Structure

```markdown
# Network Traffic Report
**Report Generated:** 2025-12-26 14:30:00
**Period:** 2025-12-20 00:00 to 2025-12-26 23:59

---

## Overall Statistics

- **Unique Processes:** 15
- **Total Upload:** 245.67 MB
- **Total Download:** 1,234.89 MB
- **Total Data:** 1,480.56 MB
- **Average Upload Rate:** 85.3 KB/s
- **Average Download Rate:** 428.7 KB/s
- **Peak Upload Rate:** 2,456.8 KB/s
- **Peak Download Rate:** 15,234.2 KB/s

## Monitoring Sessions

Total sessions: 3

| Session ID | Start Time | End Time | Upload | Download |
|------------|------------|----------|---------|----------|
| 3 | 2025-12-26 09:00 | 17:30 | 120.45 MB | 678.90 MB |
| 2 | 2025-12-25 14:00 | 18:45 | 85.22 MB | 345.67 MB |
| 1 | 2025-12-24 10:15 | 16:30 | 40.00 MB | 210.32 MB |

## Per-Process Traffic

| PID | Process Name | Upload | Download | Total | Avg Up Rate | Avg Down Rate | Max Up Rate | Max Down Rate | Protocols |
|-----|--------------|--------|----------|-------|-------------|---------------|-------------|---------------|-----------|
| 1234 | firefox | 50.23 MB | 850.45 MB | 900.68 MB | 125.5 KB/s | 2,125.8 KB/s | 1,024.5 KB/s | 5,678.9 KB/s | TCP,HTTP,HTTPS,DNS |
| 5678 | chrome | 35.67 MB | 234.56 MB | 270.23 MB | 89.2 KB/s | 587.4 KB/s | 756.3 KB/s | 3,456.7 KB/s | TCP,HTTP,HTTPS |
| 9012 | python3 | 120.45 MB | 45.67 MB | 166.12 MB | 301.1 KB/s | 114.2 KB/s | 2,456.8 KB/s | 567.8 KB/s | TCP,UDP |

## Bandwidth Alerts & Spikes

Total alerts: 5

| Timestamp | PID | Process | Alert Type | Bandwidth | Threshold |
|-----------|-----|---------|------------|-----------|-----------|
| 2025-12-26 14:25:30 | 1234 | firefox | BANDWIDTH_SPIKE | 5678.9 KB/s | 1024.0 KB/s |
| 2025-12-26 12:15:45 | 9012 | python3 | BANDWIDTH_SPIKE | 2456.8 KB/s | 1024.0 KB/s |
| 2025-12-25 16:30:12 | 5678 | chrome | BANDWIDTH_SPIKE | 3456.7 KB/s | 1024.0 KB/s |
| 2025-12-25 10:45:22 | 1234 | firefox | BANDWIDTH_SPIKE | 4567.8 KB/s | 1024.0 KB/s |
| 2025-12-24 15:20:35 | 9012 | python3 | BANDWIDTH_SPIKE | 1890.5 KB/s | 1024.0 KB/s |

## Top 5 Bandwidth Consumers

1. **firefox** (PID 1234): 900.68 MB total
   - Upload: 50.23 MB
   - Download: 850.45 MB

2. **chrome** (PID 5678): 270.23 MB total
   - Upload: 35.67 MB
   - Download: 234.56 MB

3. **python3** (PID 9012): 166.12 MB total
   - Upload: 120.45 MB
   - Download: 45.67 MB
```

## Tips for Better Reports

1. **Run monitoring regularly** to collect data
2. **Set appropriate alert thresholds** to catch spikes
3. **Generate reports periodically** (daily/weekly)
4. **Use date ranges** that match your monitoring sessions
5. **Keep both formats**: MD for archiving, DOCX for presentations

## Troubleshooting

### "No data available"
- Make sure you've run monitoring sessions during the selected period
- Check that monitoring was started with the "Start Monitoring" button
- Verify the date range includes your monitoring sessions

### "No alerts"
- Alerts only appear when bandwidth exceeds the threshold
- Default threshold is 1024 KB/s (1 MB/s)
- Lower the threshold to catch more alerts

### "python-docx not installed" error
```bash
pip3 install --break-system-packages python-docx
```

## Command Line Quick Test

Test report generation from command line:
```bash
python3 demo_report.py
```

This generates sample reports for the last 7 days showing the feature in action.

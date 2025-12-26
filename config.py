"""
Configuration settings for Network Monitor
"""

# Refresh rate for GUI (in milliseconds)
GUI_REFRESH_RATE = 1000

# Database settings
DATABASE_FILE = "network_monitor.db"

# Bandwidth alert threshold (in KB/s)
BANDWIDTH_ALERT_THRESHOLD = 1024  # 1 MB/s

# Traffic capture settings
CAPTURE_INTERFACE = None  # None = all interfaces
PACKET_TIMEOUT = 1  # seconds

# Bandwidth calculation window (seconds)
BANDWIDTH_WINDOW = 1

# GUI settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
FONT_FAMILY = "Courier"
FONT_SIZE = 10

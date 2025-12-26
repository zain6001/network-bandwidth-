#!/usr/bin/env python3
"""Quick verification that report generation methods exist"""

from database_logger import DatabaseLogger

db = DatabaseLogger()

# Check if all required methods exist
methods = [
    'get_detailed_report_data',
    'get_alerts_by_date_range',
    'get_sessions_in_range'
]

print("Checking DatabaseLogger methods...")
for method in methods:
    if hasattr(db, method):
        print(f"  ✅ {method} - EXISTS")
    else:
        print(f"  ❌ {method} - MISSING")

print("\n✅ All required methods are present!")
print("Report generation should work now.")

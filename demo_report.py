#!/usr/bin/env python3
"""
Demo script to show report generation functionality
"""

import sys
from datetime import datetime, timedelta
from database_logger import DatabaseLogger
from report_generator import ReportGenerator

def main():
    print("=" * 70)
    print("Network Traffic Report Generator - Demo")
    print("=" * 70)
    print()
    
    # Initialize
    db = DatabaseLogger()
    reporter = ReportGenerator(db)
    
    # Set date range (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"Generating report for: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print()
    
    # Generate Markdown report
    print("[1/2] Generating Markdown report...")
    md_file = f"demo_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.md"
    success, result = reporter.generate_markdown_report(start_date, end_date, md_file)
    
    if success:
        print(f"✓ Markdown report created: {result}")
    else:
        print(f"✗ Failed: {result}")
    
    # Generate Word report
    print("[2/2] Generating Word document...")
    docx_file = f"demo_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.docx"
    success, result = reporter.generate_word_report(start_date, end_date, docx_file)
    
    if success:
        print(f"✓ Word report created: {result}")
    else:
        print(f"✗ Failed: {result}")
    
    print()
    print("=" * 70)
    print("Demo complete!")
    print()
    print("To generate custom reports:")
    print("  1. Run the GUI: sudo python3 main.py")
    print("  2. Click 'Generate Report' button")
    print("  3. Select date range")
    print("  4. Choose format (MD/Word/Both)")
    print("  5. Select output directory")
    print()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

"""
Manual Excel Status Testing
Create Excel file manually to test status column positioning
"""

import pandas as pd
import xlsxwriter
import json

def test_manual_excel_creation():
    """Create Excel file manually to test status positioning"""
    
    print("🧪 Manual Excel Status Positioning Test")
    print("=" * 50)
    
    # Load the test results
    try:
        with open('test_status_positioning/sample_document_report.json', 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("❌ Test results not found. Run CLI analysis first.")
        return
    
    # Extract category status
    category_status = results.get('category_status', {})
    metrics_data = results.get('metrics', {})
    
    print(f"📊 Category Status: {category_status}")
    
    # Prepare Excel data exactly like the desktop analyzer
    excel_path = "test_manual_status_excel.xlsx"
    
    # Create workbook and worksheet
    workbook = xlsxwriter.Workbook(excel_path)
    worksheet = workbook.add_worksheet('Detailed Metrics')
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'bg_color': '#2E5984',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter'
    })
    
    metric_header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter'
    })
    
    good_format = workbook.add_format({
        'bg_color': '#C6EFCE',
        'font_color': '#006100',
        'align': 'center'
    })
    
    warning_format = workbook.add_format({
        'bg_color': '#FFEB9C',
        'font_color': '#9C5700',
        'align': 'center'
    })
    
    poor_format = workbook.add_format({
        'bg_color': '#FFC7CE',
        'font_color': '#9C0006',
        'align': 'center'
    })
    
    unknown_format = workbook.add_format({
        'bg_color': '#ffffff',
        'font_color': '#6c757d',
        'align': 'center'
    })
    
    # Write title at row 1
    worksheet.merge_range('A1:F1', '📊 DETAILED QUALITY METRICS', header_format)
    
    # Write headers at row 3 (Excel row 3, index 2)
    headers = ['Metric', 'Score', 'Percentage', 'Status', 'Threshold', 'Details']
    for col_num, header in enumerate(headers):
        worksheet.write(2, col_num, header, metric_header_format)  # Row 3 in Excel
    
    # Prepare metrics rows
    metrics_rows = []
    for metric_name, status_text in category_status.items():
        # Convert status like the desktop analyzer
        if status_text == 'pass':
            score = 0.85
            status = 'PASS'
        elif status_text == 'warn':
            score = 0.70
            status = 'WARN'
        elif status_text == 'fail':
            score = 0.30
            status = 'FAIL'
        else:
            score = 0.50
            status = 'UNKNOWN'
        
        readable_name = metric_name.replace('_', ' ').title()
        
        metrics_rows.append({
            'Metric': readable_name,
            'Score': f"{score:.3f}",
            'Percentage': f"{score:.1%}",
            'Status': status,
            'Threshold': 'Varies by metric',
            'Details': f'Details for {readable_name}'
        })
    
    print(f"📊 Created {len(metrics_rows)} metrics rows")
    
    # Write data starting at row 4 (Excel row 4, index 3)
    data_start_row = 3  # 0-based index for row 4
    for i, row_data in enumerate(metrics_rows):
        excel_row = data_start_row + i  # Excel row number (0-based)
        worksheet.write(excel_row, 0, row_data['Metric'])
        worksheet.write(excel_row, 1, row_data['Score'])
        worksheet.write(excel_row, 2, row_data['Percentage'])
        worksheet.write(excel_row, 3, row_data['Status'])
        worksheet.write(excel_row, 4, row_data['Threshold'])
        worksheet.write(excel_row, 5, row_data['Details'])
        
        print(f"   📋 Row {excel_row+1}: {row_data['Metric']} -> {row_data['Status']}")
    
    # Apply status formatting
    for i, row_data in enumerate(metrics_rows):
        excel_row = data_start_row + i
        status = row_data['Status']
        
        if status == 'PASS':
            format_to_use = good_format
        elif status == 'WARN':
            format_to_use = warning_format
        elif status == 'FAIL':
            format_to_use = poor_format
        else:
            format_to_use = unknown_format
        
        # Apply format to the status cell
        worksheet.write(excel_row, 3, status, format_to_use)
        print(f"   🎨 Applied {status} format to cell D{excel_row+1}")
    
    # Set column widths
    worksheet.set_column('A:A', 20)  # Metric
    worksheet.set_column('B:B', 12)  # Score
    worksheet.set_column('C:C', 15)  # Percentage
    worksheet.set_column('D:D', 15)  # Status
    worksheet.set_column('E:E', 15)  # Threshold
    worksheet.set_column('F:F', 40)  # Details
    
    # Close workbook
    workbook.close()
    
    print(f"\n✅ Created test Excel file: {excel_path}")
    print("📋 Structure:")
    print("   - Row 1: Title")
    print("   - Row 3: Headers")
    print("   - Row 4+: Data")
    print("\n🔍 Please open the Excel file to verify status positioning!")
    
    # Try to open the file
    try:
        import os
        os.startfile(excel_path)
        print("📊 Opening Excel file...")
    except:
        print("📊 Excel file created (could not auto-open)")

if __name__ == "__main__":
    test_manual_excel_creation()

#!/usr/bin/env python3
"""
Test comprehensive status color coding in Excel reports
"""

import os
import pandas as pd
import xlsxwriter
from datetime import datetime

def create_color_coding_demo():
    """Create demo Excel with comprehensive status color coding"""
    
    print("🎨 Creating comprehensive status color coding demo...")
    
    # Create test data with various status columns
    test_data = [
        {
            'File Name': 'good_image.jpg',
            'Overall Status': 'EXCELLENT',
            'Sharpness Status': 'PASS',
            'Contrast Status': 'PASS',
            'Exposure Status': 'PASS',
            'Geometry Status': 'PASS',
            'Resolution Status': 'PASS',
            'SLA Status': 'COMPLIANT'
        },
        {
            'File Name': 'average_image.jpg',
            'Overall Status': 'ACCEPTABLE',
            'Sharpness Status': 'WARN',
            'Contrast Status': 'PASS',
            'Exposure Status': 'WARN',
            'Geometry Status': 'PASS',
            'Resolution Status': 'PASS',
            'SLA Status': 'WARNING'
        },
        {
            'File Name': 'poor_image.jpg',
            'Overall Status': 'POOR',
            'Sharpness Status': 'FAIL',
            'Contrast Status': 'FAIL',
            'Exposure Status': 'PASS',
            'Geometry Status': 'FAIL',
            'Resolution Status': 'WARN',
            'SLA Status': 'NON_COMPLIANT'
        }
    ]
    
    # Create Excel file
    output_file = "test_output/comprehensive_status_colors_demo.xlsx"
    os.makedirs("test_output", exist_ok=True)
    
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Define status color formats
        success_format = workbook.add_format({
            'bg_color': '#d4edda',
            'font_color': '#155724',
            'bold': True,
            'align': 'center',
            'border': 1
        })
        
        warning_format = workbook.add_format({
            'bg_color': '#fff3cd',
            'font_color': '#856404',
            'bold': True,
            'align': 'center',
            'border': 1
        })
        
        fail_format = workbook.add_format({
            'bg_color': '#f8d7da',
            'font_color': '#721c24',
            'bold': True,
            'align': 'center',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#B4C6E7',
            'font_color': 'black',
            'border': 1
        })
        
        # Universal status color coding function
        def apply_comprehensive_status_colors(worksheet, df, start_row=2):
            """Apply color coding to ALL status columns"""
            status_columns = []
            
            # Find all status-related columns
            for col_num, col_name in enumerate(df.columns):
                if any(keyword in str(col_name).upper() for keyword in ['STATUS', 'COMPLIANT', 'COMPLIANCE']):
                    status_columns.append((col_num, col_name))
            
            print(f"   🎨 Found {len(status_columns)} status columns to color code:")
            for _, col_name in status_columns:
                print(f"      • {col_name}")
            
            # Apply conditional formatting to each status column
            for col_num, col_name in status_columns:
                col_letter = chr(65 + col_num)
                last_row = start_row + len(df) - 1
                range_str = f"{col_letter}{start_row}:{col_letter}{last_row}"
                
                # Green for positive statuses
                for positive_status in ['PASS', 'EXCELLENT', 'GOOD', 'COMPLIANT', 'YES', 'SUCCESS']:
                    worksheet.conditional_format(range_str, {
                        'type': 'text',
                        'criteria': 'containing',
                        'value': positive_status,
                        'format': success_format
                    })
                
                # Yellow for warning statuses
                for warning_status in ['WARN', 'WARNING', 'ACCEPTABLE', 'CAUTION']:
                    worksheet.conditional_format(range_str, {
                        'type': 'text',
                        'criteria': 'containing',
                        'value': warning_status,
                        'format': warning_format
                    })
                
                # Red for failure statuses
                for failure_status in ['FAIL', 'POOR', 'BAD', 'NON_COMPLIANT', 'NO', 'ERROR']:
                    worksheet.conditional_format(range_str, {
                        'type': 'text',
                        'criteria': 'containing',
                        'value': failure_status,
                        'format': fail_format
                    })
        
        # Create test sheet
        df = pd.DataFrame(test_data)
        df.to_excel(writer, sheet_name='Status Colors Demo', index=False, startrow=2, header=False)
        
        worksheet = writer.sheets['Status Colors Demo']
        
        # Add title
        worksheet.merge_range('A1:G1', '🎨 COMPREHENSIVE STATUS COLOR CODING DEMO', title_format)
        
        # Add headers manually
        for col_num, column_title in enumerate(df.columns):
            worksheet.write(1, col_num, column_title, header_format)
        
        # Apply comprehensive status color coding
        apply_comprehensive_status_colors(worksheet, df, start_row=3)
        
        # Set column widths
        worksheet.set_column(0, 0, 20)  # File Name
        for i in range(1, len(df.columns)):
            worksheet.set_column(i, i, 18)
    
    print(f"✅ Created comprehensive status colors demo: {output_file}")
    print("📝 Manual verification:")
    print("   - Open Excel file")
    print("   - Verify ALL status columns are color coded:")
    print("     * Green: PASS, EXCELLENT, COMPLIANT, YES")
    print("     * Yellow: WARN, WARNING, ACCEPTABLE")
    print("     * Red: FAIL, POOR, NON_COMPLIANT, NO")
    print("   - Check that colors match the quality standards!")

if __name__ == "__main__":
    create_color_coding_demo()

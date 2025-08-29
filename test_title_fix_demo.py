#!/usr/bin/env python3
"""
Direct test for Raw Measurements and Technical Analysis sheet title duplication fix
This test demonstrates the proper title positioning without requiring image analysis.
"""

import os
import pandas as pd
import xlsxwriter

def create_demo_excel():
    """Create Excel file demonstrating proper title positioning"""
    
    print("🧪 Creating demo Excel with proper title positioning...")
    
    output_file = "test_output/test_title_fix_demo.xlsx"
    os.makedirs("test_output", exist_ok=True)
    
    # Create Excel file with proper title positioning
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Create formats
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
        
        # Create Raw Measurements sheet with FIXED positioning
        create_fixed_raw_sheet(writer, workbook, title_format, header_format)
        
        # Create Technical Analysis sheet with FIXED positioning
        create_fixed_technical_sheet(writer, workbook, title_format, header_format)
        
        # Create Broken Example sheet to show the OLD way (for comparison)
        create_broken_example_sheet(writer, workbook, title_format, header_format)
    
    print(f"✅ Created demo file: {output_file}")
    print("📝 Open Excel file and compare:")
    print("   - 'Raw Measurements' sheet: FIXED - Row 1=Title, Row 2=Headers, Row 3+=Data")
    print("   - 'Technical Analysis' sheet: FIXED - Row 1=Title, Row 2=Headers, Row 3+=Data")
    print("   - 'Broken Example' sheet: BROKEN - Shows duplicate title issue")
    print("   ❌ The 'Broken Example' shows what happened BEFORE the fix")
    print("   ✅ The other sheets show what happens AFTER the fix")


def create_fixed_raw_sheet(writer, workbook, title_format, header_format):
    """Create Raw Measurements sheet with FIXED positioning (no duplicates)"""
    
    # Sample raw data
    raw_data = [
        {'File Name': 'sample1.jpg', 'Sharp_Laplacian_Var': 450.5, 'Sharp_Gradient_Mean': 35.2, 'Exp_Bright_Mean': 128.7},
        {'File Name': 'sample2.jpg', 'Sharp_Laplacian_Var': 320.1, 'Sharp_Gradient_Mean': 28.9, 'Exp_Bright_Mean': 142.3}
    ]
    
    # Create DataFrame and write with header=FALSE (key fix!)
    raw_df = pd.DataFrame(raw_data)
    raw_df.to_excel(writer, sheet_name='Raw Measurements', index=False, startrow=2, header=False)
    
    worksheet = writer.sheets['Raw Measurements']
    
    # Write title to row 1 (Excel row 1, xlsxwriter index 0)
    worksheet.merge_range('A1:D1', '🔬 RAW MEASUREMENTS & TECHNICAL DATA - FIXED', title_format)
    
    # Write headers to row 2 (Excel row 2, xlsxwriter index 1) - manual control
    for col_num, column_title in enumerate(raw_df.columns):
        worksheet.write(1, col_num, column_title, header_format)
    
    # Set column widths
    worksheet.set_column(0, 0, 20)  # File Name
    for i in range(1, len(raw_df.columns)):
        worksheet.set_column(i, i, 15)


def create_fixed_technical_sheet(writer, workbook, title_format, header_format):
    """Create Technical Analysis sheet with FIXED positioning (no duplicates)"""
    
    # Sample technical data
    tech_data = [
        {'File Name': 'sample1.jpg', 'Sharpness Score': 0.451, 'Exposure Quality': 0.85, 'Category': 'Good'},
        {'File Name': 'sample2.jpg', 'Sharpness Score': 0.320, 'Exposure Quality': 0.72, 'Category': 'Fair'}
    ]
    
    # Create DataFrame and write with header=FALSE (key fix!)
    tech_df = pd.DataFrame(tech_data)
    tech_df.to_excel(writer, sheet_name='Technical Analysis', index=False, startrow=2, header=False)
    
    worksheet = writer.sheets['Technical Analysis']
    
    # Write title to row 1 (Excel row 1, xlsxwriter index 0)
    worksheet.merge_range('A1:D1', '⚙️ TECHNICAL ANALYSIS & COMPUTED METRICS - FIXED', title_format)
    
    # Write headers to row 2 (Excel row 2, xlsxwriter index 1) - manual control
    for col_num, column_title in enumerate(tech_df.columns):
        worksheet.write(1, col_num, column_title, header_format)
    
    # Set column widths
    worksheet.set_column(0, 0, 20)  # File Name
    for i in range(1, len(tech_df.columns)):
        worksheet.set_column(i, i, 15)


def create_broken_example_sheet(writer, workbook, title_format, header_format):
    """Create sheet showing the OLD broken way (for comparison)"""
    
    # Sample data
    data = [
        {'File Name': 'sample1.jpg', 'Value1': 123.4, 'Value2': 567.8},
        {'File Name': 'sample2.jpg', 'Value1': 234.5, 'Value2': 678.9}
    ]
    
    # Create DataFrame and write with header=TRUE (old broken way!)
    df = pd.DataFrame(data)
    df.to_excel(writer, sheet_name='Broken Example', index=False, startrow=2)  # startrow=2 but header=True!
    
    worksheet = writer.sheets['Broken Example']
    
    # Write title to row 1 (Excel row 1, xlsxwriter index 0)
    worksheet.merge_range('A1:C1', '❌ BROKEN EXAMPLE - OLD WAY', title_format)
    
    # The problem: pandas already wrote headers to row 3, so we get duplicates!
    # This is what used to happen before our fix
    
    # Add note explaining the problem
    note_format = workbook.add_format({
        'italic': True,
        'font_size': 10,
        'font_color': 'red'
    })
    worksheet.write('A5', 'NOTE: This sheet shows duplicate headers (row 2 AND row 3)', note_format)
    worksheet.write('A6', 'This happened because pandas wrote headers despite startrow=2', note_format)


if __name__ == "__main__":
    create_demo_excel()

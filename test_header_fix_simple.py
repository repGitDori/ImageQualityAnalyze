#!/usr/bin/env python3
"""
Test script to create a simple Excel report and verify header fix
"""

import pandas as pd
import xlsxwriter
import os

def test_excel_headers():
    """Create a simple test Excel file to demonstrate the fixed header behavior"""
    print("🧪 Testing Excel header fix...")
    
    # Create test output directory
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    excel_path = os.path.join(output_dir, "test_headers_fixed.xlsx")
    
    try:
        # Create Excel writer
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'bg_color': '#1a252f',
                'font_color': 'white',
                'align': 'center'
            })
            
            header_format = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'bg_color': '#2c5aa0',
                'font_color': 'white',
                'align': 'center',
                'border': 1
            })
            
            metric_header_format = workbook.add_format({
                'bold': True,
                'font_size': 12,
                'bg_color': '#f8f9fa',
                'font_color': '#212529',
                'align': 'center',
                'border': 1
            })
            
            # Test 1: Detailed Metrics Sheet (FIXED)
            print("📊 Creating 'Detailed Metrics' sheet...")
            
            metrics_data = [
                {'Metric': 'Completeness', 'Score': '0.800', 'Percentage': '80.0%', 'Status': 'EXCELLENT', 'Threshold': 'Varies', 'Details': 'Content bbox coverage: 0.811'},
                {'Metric': 'Foreign Objects', 'Score': '0.500', 'Percentage': '50.0%', 'Status': 'UNKNOWN', 'Threshold': 'Varies', 'Details': 'Foreign object flag: False'},
                {'Metric': 'Sharpness', 'Score': '0.850', 'Percentage': '85.0%', 'Status': 'EXCELLENT', 'Threshold': 'Varies', 'Details': 'Laplacian variance: 668.461'},
            ]
            
            metrics_df = pd.DataFrame(metrics_data)
            
            # Write DataFrame to Excel starting at row 2 (leaving row 1 for title)
            metrics_df.to_excel(writer, sheet_name='Detailed Metrics', index=False, startrow=2)
            
            # Get worksheet and add title
            worksheet = writer.sheets['Detailed Metrics']
            worksheet.merge_range('A1:F1', '📊 DETAILED QUALITY METRICS', title_format)
            
            # Format the headers that pandas created at row 2
            for col_num, column_title in enumerate(metrics_df.columns):
                worksheet.write(2, col_num, column_title, metric_header_format)
            
            # Test 2: Recommendations Sheet (FIXED)
            print("💡 Creating 'Recommendations' sheet...")
            
            recommendations_data = [
                {'Priority': 'CRITICAL', 'Category': 'Immediate Action Required', 'Recommendation': 'Ensure full document is captured with margins'},
                {'Priority': 'CRITICAL', 'Category': 'Immediate Action Required', 'Recommendation': 'Ensure black background and proper margins'},
                {'Priority': 'CRITICAL', 'Category': 'Immediate Action Required', 'Recommendation': 'Scan/photograph at higher DPI/resolution'},
            ]
            
            rec_df = pd.DataFrame(recommendations_data)
            
            # Write DataFrame to Excel starting at row 2
            rec_df.to_excel(writer, sheet_name='Recommendations', index=False, startrow=2)
            
            # Get worksheet and add title
            worksheet2 = writer.sheets['Recommendations']
            worksheet2.merge_range('A1:C1', '💡 QUALITY IMPROVEMENT RECOMMENDATIONS', title_format)
            
            # Format the headers that pandas created at row 2
            for col_num, column_title in enumerate(rec_df.columns):
                worksheet2.write(2, col_num, column_title, metric_header_format)
            
            # Set column widths
            worksheet.set_column('A:A', 20)  # Metric
            worksheet.set_column('B:B', 12)  # Score
            worksheet.set_column('C:C', 15)  # Percentage
            worksheet.set_column('D:D', 15)  # Status
            worksheet.set_column('E:E', 15)  # Threshold
            worksheet.set_column('F:F', 40)  # Details
            
            worksheet2.set_column('A:A', 15)  # Priority
            worksheet2.set_column('B:B', 25)  # Category
            worksheet2.set_column('C:C', 60)  # Recommendation
        
        print(f"✅ Test Excel file created: {excel_path}")
        print("🔍 Open the file and verify:")
        print("   - Row 1: Title (merged across columns)")
        print("   - Row 2: Column headers (formatted)")
        print("   - Row 3+: Data rows")
        print("   - NO duplicate headers!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test Excel: {e}")
        return False

if __name__ == "__main__":
    success = test_excel_headers()
    if success:
        print("\n🎉 Header fix test completed successfully!")
        print("📁 Check the 'test_output' folder for the generated Excel file.")
    else:
        print("\n💥 Test failed!")

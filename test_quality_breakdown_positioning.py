#!/usr/bin/env python3

"""
Quality Breakdown Sheet Positioning Test
Test the fixes specifically for the Quality Breakdown sheet
"""

import os
import json
import tempfile
from datetime import datetime

def test_quality_breakdown_positioning():
    """Test Quality Breakdown sheet positioning fix"""
    
    print("🧪 Quality Breakdown Sheet Positioning Test")
    print("=" * 55)
    
    # Create mock successful results for testing
    mock_successful_results = [
        {
            'filename': 'test_image1.jpg',
            'results': {
                'global': {
                    'score': 0.82,
                    'status': 'pass',
                    'stars': 3,
                    'critical_fail': False
                },
                'category_status': {
                    'completeness': 'pass',
                    'sharpness': 'pass',
                    'exposure': 'warn',
                    'contrast': 'pass',
                    'color': 'pass',
                    'geometry': 'pass',
                    'resolution': 'warn',
                    'noise': 'pass',
                    'format_integrity': 'pass',
                    'border_background': 'pass',
                    'document_shadow': 'pass'
                }
            }
        },
        {
            'filename': 'test_image2.jpg', 
            'results': {
                'global': {
                    'score': 0.65,
                    'status': 'warn',
                    'stars': 2,
                    'critical_fail': False
                },
                'category_status': {
                    'completeness': 'fail',
                    'sharpness': 'pass',
                    'exposure': 'fail',
                    'contrast': 'warn',
                    'color': 'pass',
                    'geometry': 'pass',
                    'resolution': 'fail',
                    'noise': 'warn',
                    'format_integrity': 'pass',
                    'border_background': 'pass',
                    'document_shadow': 'pass'
                }
            }
        }
    ]
    
    print(f"📊 Mock Data: {len(mock_successful_results)} images with various status combinations")
    
    # Import desktop analyzer for Excel creation
    try:
        from desktop_analyzer import ProfessionalDesktopImageQualityAnalyzer
        import tkinter as tk
        import xlsxwriter
        import pandas as pd
        
        # Create a temporary Excel file to test just the Quality Breakdown sheet
        test_excel_path = "test_quality_breakdown_positioning.xlsx"
        
        # Create workbook manually to test just this sheet
        workbook = xlsxwriter.Workbook(test_excel_path)
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#2E5984',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter'
        })
        
        success_format = workbook.add_format({
            'bg_color': '#C6EFCE',
            'font_color': '#006100',
            'align': 'center'
        })
        
        warning_format = workbook.add_format({
            'bg_color': '#FFEB9C',
            'font_color': '#9C5700',
            'align': 'center'
        })
        
        fail_format = workbook.add_format({
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006',
            'align': 'center'
        })
        
        # Create hidden root window and analyzer
        root = tk.Tk()
        root.withdraw()
        analyzer = ProfessionalDesktopImageQualityAnalyzer(root)
        
        # Use ExcelWriter context
        with pd.ExcelWriter(test_excel_path, engine='xlsxwriter') as writer:
            writer.book = workbook
            
            # Create Quality Breakdown sheet using the fixed method
            analyzer.create_quality_breakdown_sheet(
                writer, workbook, mock_successful_results,
                title_format, header_format, success_format, warning_format, fail_format
            )
        
        root.destroy()
        
        print(f"✅ Quality Breakdown sheet created successfully!")
        print(f"📊 Location: {test_excel_path}")
        
        print(f"\n🔍 Expected Structure:")
        print(f"   📋 Row 1: Title '🎯 QUALITY BREAKDOWN BY CATEGORY'")
        print(f"   📋 Row 2: Column Headers (File Name, Status columns for each category)")
        print(f"   📋 Row 3: First image data (test_image1.jpg)")
        print(f"   📋 Row 4: Second image data (test_image2.jpg)")
        
        print(f"\n🎨 Expected Status Formatting:")
        print(f"   ✅ PASS: Green background (#C6EFCE)")
        print(f"   ⚠️ WARN: Yellow background (#FFEB9C)")
        print(f"   ❌ FAIL: Red background (#FFC7CE)")
        
        print(f"\n📊 Categories with Status Columns:")
        categories = ['completeness', 'sharpness', 'exposure', 'contrast', 'color', 
                     'geometry', 'resolution', 'noise', 'format_integrity', 
                     'border_background', 'document_shadow']
        for i, cat in enumerate(categories, 1):
            print(f"   {i:2d}. {cat.replace('_', ' ').title()} Status")
        
        # Try to open the file
        try:
            os.startfile(test_excel_path)
            print(f"\n📊 Opening Excel file for verification...")
        except:
            print(f"\n📊 Excel file created (could not auto-open)")
            
    except Exception as e:
        print(f"❌ Error during Quality Breakdown test: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ Quality Breakdown positioning test complete!")
    print(f"🔍 Please verify the status columns are properly aligned with their headers")

if __name__ == "__main__":
    test_quality_breakdown_positioning()

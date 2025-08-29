#!/usr/bin/env python3
"""
Quick test for Raw Measurements and Technical Analysis sheet title duplication fix
"""

import os
import json
import pandas as pd
import xlsxwriter
from image_quality_analyzer.analyzer import ImageQualityAnalyzer

def test_title_positioning():
    """Create a simple test to verify title positioning in Excel sheets"""
    
    print("🧪 Testing Raw Measurements and Technical Analysis sheet title positioning...")
    
    # Analyze a few sample images
    analyzer = ImageQualityAnalyzer()
    sample_images = []
    
    # Find available sample images
    for img_file in ["sample_document.jpg", "sample_images/good_doc.jpg", "sample_images/blurry_doc.jpg"]:
        if os.path.exists(img_file):
            sample_images.append(img_file)
            if len(sample_images) >= 2:
                break
    
    if len(sample_images) == 0:
        print("❌ No sample images found")
        return
    
    print(f"📊 Analyzing {len(sample_images)} images...")
    
    # Analyze images
    results = []
    for img_path in sample_images:
        print(f"   Analyzing: {img_path}")
        result = analyzer.analyze_image(img_path)
        if result and result.get('success'):
            results.append({
                'filename': os.path.basename(img_path),
                'results': result
            })
    
    if len(results) == 0:
        print("❌ No successful analysis results")
        return
    
    # Create test Excel file
    output_file = "test_output/test_title_positioning_fixed.xlsx"
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
        
        # Test Raw Measurements sheet
        create_test_raw_sheet(writer, workbook, results, title_format, header_format)
        
        # Test Technical Analysis sheet  
        create_test_technical_sheet(writer, workbook, results, title_format, header_format)
    
    print(f"✅ Created test file: {output_file}")
    print("📝 Manual verification:")
    print("   - Open Excel file")
    print("   - Check 'Raw Measurements' sheet: Row 1=Title, Row 2=Headers, Row 3+=Data")
    print("   - Check 'Technical Analysis' sheet: Row 1=Title, Row 2=Headers, Row 3+=Data")
    print("   - Verify NO duplicate titles!")


def create_test_raw_sheet(writer, workbook, results, title_format, header_format):
    """Create Raw Measurements sheet with correct positioning"""
    
    # Create sample raw data
    raw_data = []
    for result in results:
        filename = result['filename']
        analysis = result['results']
        metrics = analysis.get('metrics', {})
        
        sharpness = metrics.get('sharpness', {})
        exposure = metrics.get('exposure', {})
        
        row_data = {
            'File Name': filename,
            'Sharp_Laplacian_Var': sharpness.get('laplacian_var', 0),
            'Sharp_Gradient_Mean': sharpness.get('gradient_magnitude_mean', 0),
            'Sharp_Edge_Density': sharpness.get('edge_density', 0),
            'Exp_Shadow_Clip_Pct': exposure.get('clipping', {}).get('shadow_clip_pct', 0),
            'Exp_Highlight_Clip_Pct': exposure.get('clipping', {}).get('highlight_clip_pct', 0),
            'Exp_Bright_Mean': exposure.get('brightness', {}).get('mean', 0),
        }
        raw_data.append(row_data)
    
    # Create DataFrame and write with header=False
    raw_df = pd.DataFrame(raw_data)
    raw_df.to_excel(writer, sheet_name='Raw Measurements', index=False, startrow=2, header=False)
    
    worksheet = writer.sheets['Raw Measurements']
    
    # Write title to row 1 (Excel row 1, index 0)
    worksheet.merge_range('A1:G1', '🔬 RAW MEASUREMENTS & TECHNICAL DATA', title_format)
    
    # Write headers to row 2 (Excel row 2, index 1)
    for col_num, column_title in enumerate(raw_df.columns):
        worksheet.write(1, col_num, column_title, header_format)
    
    # Set column widths
    worksheet.set_column(0, 0, 25)  # File Name
    for i in range(1, len(raw_df.columns)):
        worksheet.set_column(i, i, 12)


def create_test_technical_sheet(writer, workbook, results, title_format, header_format):
    """Create Technical Analysis sheet with correct positioning"""
    
    # Create sample technical data
    tech_data = []
    for result in results:
        filename = result['filename']
        analysis = result['results']
        metrics = analysis.get('metrics', {})
        
        sharpness = metrics.get('sharpness', {})
        exposure = metrics.get('exposure', {})
        
        laplacian = sharpness.get('laplacian_var', 0)
        dynamic_range = exposure.get('dynamic_range', {}).get('effective_range', 0)
        
        row_data = {
            'File Name': filename,
            'Sharpness Score': round(laplacian / 1000, 4),
            'Exposure Quality': round(dynamic_range, 4),
            'Sharpness Category': 'Good' if laplacian > 200 else 'Poor',
            'Exposure Category': 'Good' if dynamic_range > 0.15 else 'Poor',
            'Detail Preservation': 'High' if laplacian > 300 else 'Low',
        }
        tech_data.append(row_data)
    
    # Create DataFrame and write with header=False
    tech_df = pd.DataFrame(tech_data)
    tech_df.to_excel(writer, sheet_name='Technical Analysis', index=False, startrow=2, header=False)
    
    worksheet = writer.sheets['Technical Analysis']
    
    # Write title to row 1 (Excel row 1, index 0)
    worksheet.merge_range('A1:F1', '⚙️ TECHNICAL ANALYSIS & COMPUTED METRICS', title_format)
    
    # Write headers to row 2 (Excel row 2, index 1)
    for col_num, column_title in enumerate(tech_df.columns):
        worksheet.write(1, col_num, column_title, header_format)
    
    # Set column widths
    worksheet.set_column(0, 0, 25)  # File Name
    for i in range(1, len(tech_df.columns)):
        worksheet.set_column(i, i, 15)


if __name__ == "__main__":
    test_title_positioning()

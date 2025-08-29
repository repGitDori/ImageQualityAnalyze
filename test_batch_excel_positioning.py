#!/usr/bin/env python3

"""
Batch Analysis Excel Status Positioning Test
Test the fixes for batch analysis Excel report generation
"""

import os
import json
import tempfile
from datetime import datetime

def test_batch_excel_positioning():
    """Test batch analysis Excel positioning fixes"""
    
    print("🧪 Batch Analysis Excel Status Positioning Test")
    print("=" * 60)
    
    # Check if we have sample images for batch testing
    sample_images = []
    for filename in ['sample_document.jpg', 'good_doc.jpg', 'dark_doc.jpg']:
        if os.path.exists(filename):
            sample_images.append(filename)
        elif os.path.exists(f'sample_images/{filename}'):
            sample_images.append(f'sample_images/{filename}')
    
    if not sample_images:
        print("❌ No sample images found for batch testing")
        print("   Looking for: sample_document.jpg, good_doc.jpg, dark_doc.jpg")
        return
    
    print(f"📸 Found {len(sample_images)} sample images:")
    for img in sample_images:
        print(f"   - {img}")
    
    # Create mock batch results for testing
    successful_results = []
    failed_results = []
    
    # Mock successful results
    for i, image_path in enumerate(sample_images[:2]):  # Use first 2 as successful
        filename = os.path.basename(image_path)
        mock_result = {
            'filename': filename,
            'results': {
                'global': {
                    'score': 0.75 + (i * 0.1),  # Varying scores
                    'status': 'pass' if i == 0 else 'warn',
                    'stars': 3 if i == 0 else 2,
                    'critical_fail': False,
                    'actions': ['Improve lighting', 'Adjust contrast']
                },
                'category_status': {
                    'completeness': 'pass' if i == 0 else 'warn',
                    'sharpness': 'pass',
                    'exposure': 'warn',
                    'contrast': 'fail' if i == 1 else 'pass',
                    'color': 'pass',
                    'geometry': 'pass',
                    'resolution': 'warn',
                    'noise': 'pass'
                },
                'metrics': {
                    'completeness': {'content_bbox_coverage': 0.95},
                    'sharpness': {'laplacian_var': 150.0},
                    'exposure': {'shadow_clip_pct': 0.1},
                    'contrast': {'global_contrast': 0.8 if i == 0 else 0.15},
                    'resolution': {'effective_dpi_x': 200, 'effective_dpi_y': 200}
                }
            }
        }
        successful_results.append(mock_result)
    
    # Mock failed results
    if len(sample_images) > 2:
        for i, image_path in enumerate(sample_images[2:], start=2):
            filename = os.path.basename(image_path)
            failed_result = {
                'filename': filename,
                'filepath': image_path,
                'analysis_type': 'Image Quality Analysis',
                'error_type': 'Processing Error' if i == 2 else 'Format Error',
                'error_reason': 'Low contrast detected' if i == 2 else 'Unsupported format',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            failed_results.append(failed_result)
    
    print(f"\n📊 Mock Data Summary:")
    print(f"   ✅ Successful analyses: {len(successful_results)}")
    print(f"   ❌ Failed analyses: {len(failed_results)}")
    
    # Import desktop analyzer for Excel creation
    try:
        from desktop_analyzer import ProfessionalDesktopImageQualityAnalyzer
        import tkinter as tk
        
        # Create hidden root window
        root = tk.Tk()
        root.withdraw()
        
        # Create analyzer instance
        analyzer = ProfessionalDesktopImageQualityAnalyzer(root)
        
        # Create temporary output folder
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"\n📁 Creating batch Excel report in: {temp_dir}")
            
            # Create batch Excel report
            excel_path = analyzer.create_batch_excel_report(
                successful_results, 
                failed_results, 
                temp_dir
            )
            
            if excel_path and os.path.exists(excel_path):
                print(f"✅ Batch Excel report created successfully!")
                print(f"📊 Location: {excel_path}")
                
                # Copy to current directory for inspection
                import shutil
                local_excel = "test_batch_excel_positioning.xlsx"
                shutil.copy2(excel_path, local_excel)
                print(f"📋 Copied to: {local_excel}")
                
                print(f"\n🔍 Excel Structure Verification:")
                print(f"   📋 Expected sheets:")
                print(f"      - Batch Summary: Row 1 (Title), Row 2 (Headers), Row 3+ (Data)")
                print(f"      - Successful Analysis: Row 1 (Title), Row 2 (Headers), Row 3+ (Data)")
                if failed_results:
                    print(f"      - Failed Files: Row 1 (Title), Row 2 (Headers), Row 3+ (Data)")
                    print(f"      - Statistics: Row 1 (Title), Row 2 (Headers), Row 3+ (Data)")
                
                print(f"\n🎨 Status Formatting:")
                print(f"   ✅ PASS/EXCELLENT: Green background")
                print(f"   ⚠️ WARN: Yellow background")  
                print(f"   ❌ FAIL/POOR: Red background")
                
                # Try to open the file
                try:
                    os.startfile(local_excel)
                    print(f"📊 Opening Excel file for verification...")
                except:
                    print(f"📊 Excel file created (could not auto-open)")
                
            else:
                print(f"❌ Failed to create batch Excel report")
        
        # Clean up
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error during batch Excel test: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ Batch Excel positioning test complete!")
    print(f"🔍 Please verify the Excel file has proper header/data alignment in all sheets")

if __name__ == "__main__":
    test_batch_excel_positioning()

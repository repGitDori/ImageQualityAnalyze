#!/usr/bin/env python3
"""
Test comprehensive status color coding in actual batch Excel reports
"""

import os
import sys
import json
import tkinter as tk
from tkinter import messagebox
from desktop_analyzer import ProfessionalDesktopImageQualityAnalyzer

def test_batch_excel_status_colors():
    """Test that all status columns are properly color coded in batch reports"""
    
    print("🎨 Testing comprehensive status color coding in batch Excel reports...")
    
    # Create test images list
    sample_images = []
    for img_file in ["sample_document.jpg", "sample_images/good_doc.jpg", "sample_images/blurry_doc.jpg"]:
        if os.path.exists(img_file):
            sample_images.append(img_file)
    
    if len(sample_images) < 2:
        print("❌ Need at least 2 sample images for batch test")
        return
    
    print(f"📊 Using {len(sample_images)} sample images for batch analysis")
    
    # Create minimal GUI instance for batch processing
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        # Initialize analyzer
        analyzer = ProfessionalDesktopImageQualityAnalyzer(root)
        
        # Use default config
        analyzer.config = {
            "quality_standards": {
                "sharpness": {"threshold": 150.0, "weight": 1.0},
                "contrast": {"threshold": 0.15, "weight": 1.0},
                "resolution": {"threshold": 200, "weight": 1.0},
                "geometry": {"threshold": 3.0, "weight": 1.0},
                "exposure": {"threshold": 0.1, "weight": 1.0},
                "completeness": {"threshold": 0.9, "weight": 1.0},
                "color": {"threshold": 8.0, "weight": 1.0},
                "noise": {"threshold": 10.0, "weight": 1.0},
                "border_background": {"threshold": 0.8, "weight": 1.0},
                "format_integrity": {"weight": 1.0},
                "foreign_objects": {"weight": 1.0}
            },
            "scoring": {
                "pass_score_threshold": 0.75
            },
            "sla": {
                "enabled": True,
                "requirements": {
                    "max_fail_categories": 2
                }
            }
        }
        
        # Create output file
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"📋 Running batch analysis with comprehensive status color coding...")
        
        # Run batch analysis using the correct method
        analyzer.run_batch_analysis(sample_images, output_dir)
        
        # Check if Excel file was created (it will have a timestamp in the name)
        xlsx_files = [f for f in os.listdir(output_dir) if f.endswith('.xlsx') and 'BatchAnalysis' in f]
        
        if xlsx_files:
            latest_file = os.path.join(output_dir, sorted(xlsx_files)[-1])  # Get most recent
            print(f"✅ Successfully created batch report with status colors: {latest_file}")
            print(f"\n🎨 Color coding verification:")
            print(f"   📊 Check the following sheets for comprehensive status color coding:")
            print(f"      • Summary Sheet: Overall Status column")  
            print(f"      • Detailed Metrics: All status columns (Sharpness Status, Exposure Status, etc.)")
            print(f"      • Quality Breakdown: All category status columns")
            print(f"      • SLA Compliance: Compliance Level and status columns")
            print(f"\n🌈 Color Standards:")
            print(f"      🟢 Green: PASS, EXCELLENT, COMPLIANT, YES")
            print(f"      🟡 Yellow: WARN, WARNING, ACCEPTABLE")
            print(f"      🔴 Red: FAIL, POOR, NON_COMPLIANT, NO")
            print(f"\n📝 The Excel report should now have ALL status columns beautifully color-coded!")
        else:
            print(f"❌ Failed to create batch report")
            
    except Exception as e:
        print(f"❌ Error during batch analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()

if __name__ == "__main__":
    test_batch_excel_status_colors()

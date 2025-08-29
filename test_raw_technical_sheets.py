#!/usr/bin/env python3
"""
Quick test for Raw Measurements and Technical Analysis sheet title duplication fix
"""

import os
import sys
import json
from desktop_analyzer import ProfessionalDesktopImageQualityAnalyzer

def test_raw_technical_sheets():
    """Test that Raw Measurements and Technical Analysis sheets have proper titles"""
    
    print("🧪 Testing Raw Measurements and Technical Analysis sheet title positioning...")
    
    # Create test images
    sample_images = ["sample_images/good_doc.jpg", "sample_images/blurry_doc.jpg"]
    
    # Initialize analyzer
    analyzer = ProfessionalDesktopImageQualityAnalyzer()
    
    # Use basic default config
    config = {
        "quality_standards": {
            "sharpness": {"threshold": 100, "weight": 1.0},
            "exposure": {"threshold": 0.1, "weight": 1.0},
            "contrast": {"threshold": 0.1, "weight": 1.0},
            "geometry": {"threshold": 3.0, "weight": 1.0},
            "resolution": {"threshold": 200, "weight": 1.0},
            "completeness": {"threshold": 0.9, "weight": 1.0},
            "color": {"threshold": 10.0, "weight": 1.0},
            "noise": {"threshold": 10.0, "weight": 1.0},
            "border_background": {"threshold": 0.8, "weight": 1.0},
            "format_integrity": {"weight": 1.0},
            "foreign_objects": {"weight": 1.0}
        }
    }
    
    # Set config and run batch analysis
    analyzer.config = config
    output_file = "test_output/test_raw_technical_sheets.xlsx"
    
    print(f"📊 Running batch analysis on {len(sample_images)} images...")
    analyzer.export_batch_to_excel(sample_images, output_file)
    
    if os.path.exists(output_file):
        print(f"✅ Successfully created: {output_file}")
        print("📝 Manual verification needed:")
        print("   - Open the Excel file")
        print("   - Check 'Raw Measurements' sheet:")
        print("     * Row 1: Should have TITLE only")
        print("     * Row 2: Should have HEADERS only") 
        print("     * Row 3+: Should have DATA")
        print("   - Check 'Technical Analysis' sheet:")
        print("     * Row 1: Should have TITLE only")
        print("     * Row 2: Should have HEADERS only")
        print("     * Row 3+: Should have DATA")
        print("   - NO duplicate titles on row 3!")
    else:
        print(f"❌ Failed to create {output_file}")

if __name__ == "__main__":
    test_raw_technical_sheets()

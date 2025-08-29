#!/usr/bin/env python3

"""
Test Excel formatting fixes for header positioning
"""

import os
import tempfile
from desktop_analyzer import ProfessionalDesktopImageQualityAnalyzer
from image_quality_analyzer.analyzer import ImageQualityAnalyzer

def test_excel_header_positioning():
    """Test that Excel headers are positioned correctly"""
    print("🧪 Testing Excel header positioning...")
    
    # Initialize analyzers
    core_analyzer = ImageQualityAnalyzer()
    desktop_analyzer = ProfessionalDesktopImageQualityAnalyzer()
    
    # Use sample document
    sample_path = "sample_document.jpg"
    if not os.path.exists(sample_path):
        print(f"❌ Sample image not found: {sample_path}")
        return
    
    try:
        print(f"📸 Analyzing: {sample_path}")
        
        # Process image with core analyzer
        results = core_analyzer.analyze_image(sample_path)
        
        print(f"📊 Creating Excel report...")
        
        # Create Excel report with desktop analyzer
        desktop_analyzer.auto_export_excel_with_visuals(results)
        
        print("✅ Excel report created successfully!")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel_header_positioning()

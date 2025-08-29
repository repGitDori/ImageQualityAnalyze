#!/usr/bin/env python3

"""
Generate Excel report to verify status fix
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from desktop_analyzer import ProfessionalDesktopImageQualityAnalyzer

def generate_test_excel():
    """Generate Excel report to verify the status fix"""
    
    print("📊 Generating Excel report to verify status fix...")
    
    # Create the analyzer instance
    analyzer = ProfessionalDesktopImageQualityAnalyzer()
    
    # Test image
    test_image = 'sample_document.jpg'
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return False
    
    try:
        # Set the image path
        analyzer.current_image_path = test_image
        
        # Perform analysis 
        from image_quality_analyzer import ImageQualityAnalyzer
        core_analyzer = ImageQualityAnalyzer()
        result = core_analyzer.analyze_image(test_image)
        
        # Generate Excel report using the fixed method
        analyzer.auto_export_excel_with_visuals(result)
        
        print(f"✅ Excel report generated successfully!")
        print(f"\n📋 In the Excel file, the 'Detailed Metrics' sheet should now show:")
        print(f"   🟢 PASS - for categories like Sharpness, Color, Geometry, etc.")
        print(f"   🟡 WARN - for categories like Noise")
        print(f"   🔴 FAIL - for categories like Completeness, Exposure, etc.")
        print(f"\n   Instead of the previous EXCELLENT/FAIR/POOR values.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating Excel report: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("📊 Excel Status Fix Verification")
    print("=" * 40)
    
    if generate_test_excel():
        print(f"\n✅ Excel report generation test completed!")
        print(f"\n💡 Check the generated Excel file in the analysis_results folder")
        print(f"   to verify that the status column now shows PASS/WARN/FAIL")
        print(f"   instead of EXCELLENT/FAIR/POOR.")
    else:
        print(f"\n❌ Excel report generation test failed")

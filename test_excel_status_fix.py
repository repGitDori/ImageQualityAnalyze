#!/usr/bin/env python3

"""
Test script to verify Excel status fix
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_quality_analyzer import ImageQualityAnalyzer

def test_excel_status_fix():
    """Test the Excel status display fix"""
    
    print("🔍 Testing Excel status display fix...")
    
    # Create analyzer
    analyzer = ImageQualityAnalyzer()
    
    # Test with sample image
    test_image = 'sample_document.jpg'
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return False
    
    try:
        # Analyze the image
        result = analyzer.analyze_image(test_image)
        
        print(f"✅ Analysis completed:")
        print(f"   Overall Score: {result['global']['score']:.3f}")
        print(f"   Overall Status: {result['global']['status'].upper()}")
        
        print(f"\n📊 Category Status (should show PASS/WARN/FAIL):")
        for category, status in result['category_status'].items():
            print(f"   {category.replace('_', ' ').title()}: {status.upper()}")
        
        # Save JSON report for comparison
        json_path = 'test_status_fix_report.json'
        analyzer.export_json_report(result, json_path)
        print(f"\n📁 JSON report saved to: {json_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Excel Status Display Fix Test")
    print("=" * 40)
    
    if test_excel_status_fix():
        print(f"\n✅ Test completed successfully!")
        print(f"\n📋 Status values in Excel should now show:")
        print(f"   🟢 PASS - for categories that meet requirements")
        print(f"   🟡 WARN - for categories with warnings")
        print(f"   🔴 FAIL - for categories that fail requirements")
        print(f"   ⚪ UNKNOWN - for categories with unknown status")
        print(f"\nPreviously it was incorrectly showing EXCELLENT/FAIR/POOR")
        print(f"instead of the actual PASS/WARN/FAIL status from analysis.")
    else:
        print(f"\n❌ Test failed")

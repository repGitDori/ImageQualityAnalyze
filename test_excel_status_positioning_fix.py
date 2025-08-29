#!/usr/bin/env python3

"""
Test Excel Status Column Positioning
Verify that status values are correctly positioned in Excel output
"""

import os
import sys
import tempfile
from image_quality_analyzer import ImageQualityAnalyzer

def test_excel_status_positioning():
    """Test Excel status column positioning"""
    
    print("🧪 Testing Excel Status Column Positioning")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = ImageQualityAnalyzer()
    
    # Use sample document
    sample_path = "sample_document.jpg"
    if not os.path.exists(sample_path):
        print(f"❌ Sample image not found: {sample_path}")
        return
    
    try:
        print(f"📸 Analyzing: {sample_path}")
        
        # Process image
        results = analyzer.analyze_image(sample_path)
        
        # Debug: Print results structure
        print("\n🔍 Results Structure:")
        print(f"   📊 Global results keys: {list(results.get('global', {}).keys())}")
        print(f"   📊 Metrics keys: {list(results.get('metrics', {}).keys())}")
        print(f"   📊 Category status: {results.get('category_status', {})}")
        
        # Create temporary Excel file using desktop analyzer
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from desktop_analyzer import ProfessionalDesktopImageQualityAnalyzer
        import tkinter as tk
        
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create analyzer instance
        desktop_analyzer = ProfessionalDesktopImageQualityAnalyzer(root)
        
        print(f"📊 Creating Excel report...")
        
        # Create Excel report
        desktop_analyzer.auto_export_excel_with_visuals(results)
        
        print("✅ Excel report created successfully!")
        print("📋 Check the 'Detailed Metrics' sheet to verify:")
        print("   - Row 1: Title")
        print("   - Row 3: Headers (Metric, Score, Percentage, Status, Threshold, Details)")
        print("   - Row 4+: Data with properly formatted Status column")
        
        # Clean up
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel_status_positioning()

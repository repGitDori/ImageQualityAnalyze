#!/usr/bin/env python3
"""
Quick test script to verify Excel header duplication fix
"""

import os
import sys
from desktop_analyzer import ProfessionalDesktopImageQualityAnalyzer

def test_excel_export():
    """Test the Excel export with a sample image to verify header fix"""
    print("🧪 Testing Excel header duplication fix...")
    
    # Initialize analyzer with a dummy root (for testing)
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide the GUI
    
    analyzer = ProfessionalDesktopImageQualityAnalyzer(root)
    
    # Use sample image if it exists
    sample_image = "sample_document.jpg"
    if not os.path.exists(sample_image):
        print(f"❌ Sample image '{sample_image}' not found")
        return False
    
    try:
        print(f"📸 Analyzing {sample_image}...")
        
        # Run analysis
        results = analyzer.run_full_analysis(sample_image)
        
        if results:
            print("✅ Analysis completed successfully")
            
            # Export to Excel
            print("📊 Exporting to Excel...")
            analyzer.auto_export_excel_with_visuals(results)
            
            print("✅ Excel export completed - check the output folder for the report")
            print("🔍 Please verify that there are no duplicate headers in the Excel file")
            
            # Clean up GUI
            root.destroy()
            return True
        else:
            print("❌ Analysis failed")
            root.destroy()
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        root.destroy()
        return False

if __name__ == "__main__":
    success = test_excel_export()
    if success:
        print("\n🎉 Test completed! Check the Excel file to verify the header fix.")
    else:
        print("\n💥 Test failed!")

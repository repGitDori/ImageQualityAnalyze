#!/usr/bin/env python3

"""
Simple Quality Breakdown Test
Create a batch analysis to test Quality Breakdown sheet specifically
"""

import os
import sys

def test_quality_breakdown_simple():
    """Simple test for Quality Breakdown sheet positioning"""
    
    print("🧪 Quality Breakdown Sheet Test")
    print("=" * 40)
    
    # Check if we have sample images
    sample_images = []
    for filename in ['sample_document.jpg', 'good_doc.jpg']:
        if os.path.exists(filename):
            sample_images.append(filename)
        elif os.path.exists(f'sample_images/{filename}'):
            sample_images.append(f'sample_images/{filename}')
    
    if len(sample_images) < 2:
        print("❌ Need at least 2 sample images for batch test")
        print("   Looking for: sample_document.jpg, good_doc.jpg")
        return
    
    print(f"📸 Using sample images: {sample_images}")
    
    # Run CLI batch analysis to generate Excel with Quality Breakdown
    from image_quality_analyzer import ImageQualityAnalyzer
    
    try:
        print("\n📊 Running batch analysis...")
        
        # Create analyzer
        analyzer = ImageQualityAnalyzer()
        
        # Analyze both images
        results = []
        for image_path in sample_images:
            print(f"   Analyzing: {image_path}")
            result = analyzer.analyze_image(image_path)
            
            # Add filename to result
            result['filename'] = os.path.basename(image_path)
            results.append({
                'filename': os.path.basename(image_path),
                'results': result
            })
        
        print(f"✅ Analyzed {len(results)} images successfully")
        
        # Now create Excel using the desktop analyzer's batch method
        from desktop_analyzer import ProfessionalDesktopImageQualityAnalyzer
        import tkinter as tk
        import tempfile
        
        # Create hidden root and analyzer
        root = tk.Tk()
        root.withdraw()
        desktop_analyzer = ProfessionalDesktopImageQualityAnalyzer(root)
        
        # Create Excel report
        with tempfile.TemporaryDirectory() as temp_dir:
            excel_path = desktop_analyzer.create_batch_excel_report(
                results,  # successful_results
                [],       # failed_results
                temp_dir
            )
            
            if excel_path and os.path.exists(excel_path):
                # Copy to current directory
                import shutil
                local_excel = "test_quality_breakdown_fixed.xlsx"
                shutil.copy2(excel_path, local_excel)
                
                print(f"✅ Batch Excel created: {local_excel}")
                print(f"\n🔍 Quality Breakdown Sheet Verification:")
                print(f"   📋 Row 1: Title")
                print(f"   📋 Row 2: Headers (File Name + Status columns)")
                print(f"   📋 Row 3+: Data (with properly aligned status values)")
                
                print(f"\n🎨 Status Values Expected:")
                for i, img in enumerate(sample_images, 1):
                    print(f"   📸 Image {i} ({os.path.basename(img)}):")
                    result = results[i-1]['results']
                    category_status = result.get('category_status', {})
                    
                    status_summary = []
                    for cat, status in category_status.items():
                        if status == 'pass':
                            status_summary.append(f"✅{cat}")
                        elif status == 'warn':
                            status_summary.append(f"⚠️{cat}")
                        elif status == 'fail':
                            status_summary.append(f"❌{cat}")
                    
                    print(f"      {', '.join(status_summary[:3])}...")  # Show first 3
                
                # Try to open
                try:
                    os.startfile(local_excel)
                    print(f"\n📊 Opening Excel - check Quality Breakdown sheet!")
                except:
                    print(f"\n📊 Excel created - please open Quality Breakdown sheet")
            else:
                print(f"❌ Failed to create batch Excel")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ Quality Breakdown test complete!")

if __name__ == "__main__":
    test_quality_breakdown_simple()

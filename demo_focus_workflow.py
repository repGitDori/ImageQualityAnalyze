"""
Complete Example: Enhanced Focus Detection for Image Quality Analysis

This example demonstrates how to set up and use the enhanced focus detection
system to flag images as "out of focus" with specific reasons and generate
detailed reports.

Use Case: You want to analyze multiple images and specifically identify
which ones failed due to being out of focus or blurry.
"""

import json
from pathlib import Path
from datetime import datetime
from custom_focus_detection import EnhancedFocusDetector
from focus_excel_reporter import FocusEnhancedExcelReporter

def demo_enhanced_focus_workflow():
    """
    Complete workflow demonstration showing:
    1. Custom focus detection setup
    2. Single image analysis with detailed focus flags
    3. Batch analysis with focus filtering
    4. Excel report generation with focus-specific information
    """
    
    print("🎯 ENHANCED FOCUS DETECTION WORKFLOW DEMO")
    print("="*60)
    print("This demo shows how to:")
    print("- Flag images as 'OUT OF FOCUS' with specific reasons")
    print("- Generate detailed focus quality reports")
    print("- Filter and categorize images by focus quality")
    print("- Create Excel reports highlighting focus issues")
    
    # Step 1: Initialize Enhanced Focus Detector
    print(f"\n📋 STEP 1: Initialize Enhanced Focus Detection")
    print("-" * 40)
    
    try:
        detector = EnhancedFocusDetector("config_focus_detection.json")
        print("✅ Enhanced focus detector initialized with custom config")
    except Exception as e:
        print(f"⚠️  Using default config: {e}")
        detector = EnhancedFocusDetector()
    
    # Step 2: Analyze Sample Images
    print(f"\n🔍 STEP 2: Analyze Images for Focus Quality")
    print("-" * 40)
    
    # Find available images to analyze
    sample_images = []
    
    # Look for images in common locations
    search_paths = ['.', './sample_images', './test_images', './examples']
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.bmp']
    
    for search_path in search_paths:
        if Path(search_path).exists():
            for ext in image_extensions:
                sample_images.extend(Path(search_path).glob(ext))
    
    # Convert to strings and take first few for demo
    image_paths = [str(p) for p in sample_images[:3]]
    
    if not image_paths:
        # Create demo scenario if no real images
        print("📝 No sample images found - creating simulated analysis results")
        analysis_results = create_simulated_results()
        
    else:
        print(f"Found {len(image_paths)} images to analyze:")
        for img in image_paths:
            print(f"  📄 {img}")
        
        # Analyze each image
        analysis_results = []
        
        for image_path in image_paths:
            print(f"\n🔍 Analyzing: {Path(image_path).name}")
            
            try:
                result = detector.analyze_focus_quality(image_path, verbose=False)
                
                # Extract key information
                focus_analysis = result.get('focus_analysis', {})
                focus_level = focus_analysis.get('focus_level', 'unknown')
                focus_score = focus_analysis.get('focus_score', 0.0)
                
                # Show focus decision
                if focus_level in ['poor', 'unusable']:
                    print(f"   🔴 RESULT: Failed for OUT OF FOCUS ({focus_level})")
                    print(f"   📊 Focus Score: {focus_score:.1f} (threshold: ≥120)")
                elif focus_level == 'acceptable':
                    print(f"   🟡 RESULT: Soft focus - minor issues ({focus_level})")
                else:
                    print(f"   🟢 RESULT: Good focus quality ({focus_level})")
                
                # Prepare result for batch processing
                result_summary = {
                    'image_path': image_path,
                    'filename': Path(image_path).name,
                    'overall_score': result['global']['score'],
                    'overall_status': result['global']['status'],
                    'focus_analysis': focus_analysis,
                    'focus_recommendations': result.get('focus_recommendations', [])
                }
                analysis_results.append(result_summary)
                
            except Exception as e:
                print(f"   ❌ Error analyzing {image_path}: {e}")
    
    # Step 3: Generate Focus Summary
    print(f"\n📊 STEP 3: Focus Quality Summary")
    print("-" * 40)
    
    if analysis_results:
        focus_summary = summarize_focus_results(analysis_results)
        print_focus_summary(focus_summary)
        
        # Step 4: Filter Out-of-Focus Images
        print(f"\n🔴 STEP 4: Images Failed for OUT OF FOCUS")
        print("-" * 40)
        
        failed_images = filter_out_of_focus_images(analysis_results)
        
        if failed_images:
            print(f"Found {len(failed_images)} images that failed for focus issues:")
            
            for img in failed_images:
                filename = img['filename']
                focus_level = img['focus_analysis']['focus_level']
                focus_score = img['focus_analysis']['focus_score']
                issues = img['focus_analysis'].get('focus_issues', [])
                
                print(f"\n❌ {filename}")
                print(f"   Reason: OUT OF FOCUS ({focus_level})")
                print(f"   Score: {focus_score:.1f} (below threshold)")
                if issues:
                    print(f"   Issue: {issues[0]}")
        else:
            print("✅ No images failed for focus issues")
        
        # Step 5: Generate Excel Report
        print(f"\n📋 STEP 5: Generate Enhanced Focus Report")
        print("-" * 40)
        
        try:
            reporter = FocusEnhancedExcelReporter()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_file = f"enhanced_focus_analysis_{timestamp}.xlsx"
            
            reporter.generate_focus_report(analysis_results, excel_file)
            
            print(f"✅ Enhanced Excel report generated: {excel_file}")
            print("📊 Report includes:")
            print("   - Executive summary with focus statistics")
            print("   - Detailed focus quality analysis")
            print("   - Out-of-focus images with specific reasons")
            print("   - Focus improvement recommendations")
            print("   - Raw focus metrics data")
            
        except Exception as e:
            print(f"⚠️  Could not generate Excel report: {e}")
            print("   (pandas/openpyxl may not be installed)")
    
    else:
        print("No analysis results to process")
    
    # Step 6: Usage Instructions
    print(f"\n📖 STEP 6: How to Use This System")
    print("-" * 40)
    print_usage_instructions()
    
    print(f"\n✅ DEMO COMPLETE")
    print("="*60)


def create_simulated_results():
    """Create simulated analysis results for demonstration"""
    
    return [
        {
            'image_path': 'simulated_sharp_image.jpg',
            'filename': 'simulated_sharp_image.jpg',
            'overall_score': 0.89,
            'overall_status': 'pass',
            'focus_analysis': {
                'focus_level': 'good',
                'focus_score': 245.7,
                'confidence': 0.92,
                'focus_issues': [],
                'metrics_breakdown': {
                    'primary_sharpness': 245.7,
                    'edge_content': 0.018,
                    'high_freq_energy': 0.0024,
                    'local_variation': 890.0,
                    'gradient_strength': 15.3
                }
            },
            'focus_recommendations': []
        },
        {
            'image_path': 'simulated_blurry_image.jpg',
            'filename': 'simulated_blurry_image.jpg',
            'overall_score': 0.42,
            'overall_status': 'fail',
            'focus_analysis': {
                'focus_level': 'poor',
                'focus_score': 68.4,
                'confidence': 0.87,
                'focus_issues': [
                    'Out of focus - noticeable blur',
                    'Low edge content - soft focus or low contrast'
                ],
                'metrics_breakdown': {
                    'primary_sharpness': 68.4,
                    'edge_content': 0.007,
                    'high_freq_energy': 0.0003,
                    'local_variation': 125.0,
                    'gradient_strength': 6.8
                }
            },
            'focus_recommendations': [
                '🔴 CRITICAL: Image failed for OUT OF FOCUS - retake required',
                '📸 Use auto-focus or tap screen to focus on document',
                '🎯 Ensure proper distance - too close causes focus issues',
                '📱 Use tripod or stable surface to reduce camera shake'
            ]
        },
        {
            'image_path': 'simulated_soft_image.jpg',
            'filename': 'simulated_soft_image.jpg',
            'overall_score': 0.66,
            'overall_status': 'warn',
            'focus_analysis': {
                'focus_level': 'acceptable',
                'focus_score': 138.2,
                'confidence': 0.79,
                'focus_issues': ['Slightly soft focus - minor blur'],
                'metrics_breakdown': {
                    'primary_sharpness': 138.2,
                    'edge_content': 0.014,
                    'high_freq_energy': 0.0015,
                    'local_variation': 420.0,
                    'gradient_strength': 11.7
                }
            },
            'focus_recommendations': [
                '🟡 WARNING: Image is slightly soft - consider retaking for better quality',
                '🔧 Fine-tune focus or move slightly closer/further'
            ]
        }
    ]


def summarize_focus_results(results):
    """Summarize focus analysis results"""
    
    focus_distribution = {
        'excellent': 0, 'good': 0, 'acceptable': 0, 'poor': 0, 'unusable': 0
    }
    
    total_images = len(results)
    failed_for_focus = 0
    focus_scores = []
    
    for result in results:
        focus_analysis = result.get('focus_analysis', {})
        focus_level = focus_analysis.get('focus_level', 'unknown')
        
        if focus_level in focus_distribution:
            focus_distribution[focus_level] += 1
        
        if focus_level in ['poor', 'unusable']:
            failed_for_focus += 1
        
        focus_scores.append(focus_analysis.get('focus_score', 0.0))
    
    return {
        'total_images': total_images,
        'focus_distribution': focus_distribution,
        'failed_for_focus': failed_for_focus,
        'success_rate': (total_images - failed_for_focus) / total_images * 100 if total_images > 0 else 0,
        'average_focus_score': sum(focus_scores) / len(focus_scores) if focus_scores else 0
    }


def print_focus_summary(summary):
    """Print focus analysis summary"""
    
    focus_dist = summary['focus_distribution']
    
    print(f"Total Images Analyzed: {summary['total_images']}")
    print(f"\nFocus Quality Distribution:")
    print(f"  🟢 Excellent: {focus_dist['excellent']} images")
    print(f"  🟢 Good: {focus_dist['good']} images")
    print(f"  🟡 Acceptable: {focus_dist['acceptable']} images")
    print(f"  🔴 Poor (Out of Focus): {focus_dist['poor']} images")
    print(f"  🔴 Unusable (Severely Blurred): {focus_dist['unusable']} images")
    
    print(f"\nKey Statistics:")
    print(f"  Failed for Focus Issues: {summary['failed_for_focus']}")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
    print(f"  Average Focus Score: {summary['average_focus_score']:.1f}")


def filter_out_of_focus_images(results):
    """Filter images that failed specifically for focus issues"""
    
    failed_images = []
    
    for result in results:
        focus_analysis = result.get('focus_analysis', {})
        focus_level = focus_analysis.get('focus_level', 'unknown')
        
        if focus_level in ['poor', 'unusable']:
            failed_images.append(result)
    
    return failed_images


def print_usage_instructions():
    """Print instructions for using the enhanced focus detection system"""
    
    print("🔧 CUSTOMIZATION:")
    print("1. Edit 'config_focus_detection.json' to adjust focus thresholds")
    print("2. Modify focus classification levels based on your requirements")
    print("3. Add custom failure messages and recommendations")
    
    print("\n📝 INTEGRATION:")
    print("1. Import EnhancedFocusDetector in your scripts")
    print("2. Use analyze_focus_quality() for single images")
    print("3. Use batch_analyze_focus() for multiple images")
    print("4. Generate Excel reports with FocusEnhancedExcelReporter")
    
    print("\n🎯 FOCUS THRESHOLDS:")
    print("- Excellent: Laplacian ≥ 300 (Professional quality)")
    print("- Good: Laplacian ≥ 200 (Suitable for most uses)")
    print("- Acceptable: Laplacian ≥ 120 (Usable with minor issues)")
    print("- Poor: Laplacian ≥ 80 (Out of focus)")
    print("- Unusable: Laplacian < 80 (Severely out of focus)")
    
    print("\n💡 PRACTICAL USAGE:")
    print("```python")
    print("from custom_focus_detection import EnhancedFocusDetector")
    print("")
    print("detector = EnhancedFocusDetector('config_focus_detection.json')")
    print("result = detector.analyze_focus_quality('image.jpg')")
    print("")
    print("if result['focus_analysis']['focus_level'] in ['poor', 'unusable']:")
    print("    print('Image failed for OUT OF FOCUS')")
    print("```")


if __name__ == "__main__":
    demo_enhanced_focus_workflow()

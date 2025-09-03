"""
Test Enhanced Focus Detection System

This script demonstrates the enhanced focus detection capabilities with:
- Specific "out of focus" flagging
- Detailed focus quality analysis
- Custom focus thresholds
- Batch analysis with focus-specific reporting

Run this script to test the focus detection on sample images.
"""

import json
from pathlib import Path
from custom_focus_detection import EnhancedFocusDetector

def test_single_image_analysis():
    """Test enhanced focus analysis on a single image"""
    
    print("🔍 TESTING SINGLE IMAGE FOCUS ANALYSIS")
    print("="*50)
    
    # Initialize detector with custom config
    detector = EnhancedFocusDetector("config_focus_detection.json")
    
    # Test with sample image
    sample_image = "sample_document.jpg"
    
    if Path(sample_image).exists():
        print(f"\nAnalyzing: {sample_image}")
        result = detector.analyze_focus_quality(sample_image, verbose=True)
        
        # Extract key focus information
        focus_analysis = result.get('focus_analysis', {})
        focus_level = focus_analysis.get('focus_level', 'unknown')
        
        # Demonstrate decision logic
        if focus_level in ['poor', 'unusable']:
            print(f"\n🔴 RESULT: Image FAILED for OUT OF FOCUS")
            print(f"   Focus Level: {focus_level}")
            print(f"   This image would be flagged as unusable due to focus issues.")
        elif focus_level == 'acceptable':
            print(f"\n🟡 RESULT: Image has MINOR FOCUS ISSUES")
            print(f"   Focus Level: {focus_level}")
            print(f"   This image is usable but could be improved.")
        else:
            print(f"\n🟢 RESULT: Image has ACCEPTABLE FOCUS")
            print(f"   Focus Level: {focus_level}")
            print(f"   This image meets focus quality requirements.")
            
    else:
        print(f"Sample image '{sample_image}' not found.")
        print("Please ensure sample_document.jpg exists or modify the path.")

def test_batch_analysis():
    """Test batch analysis with focus detection"""
    
    print("\n\n🔍 TESTING BATCH FOCUS ANALYSIS")
    print("="*50)
    
    # Initialize detector
    detector = EnhancedFocusDetector("config_focus_detection.json")
    
    # Find sample images in the workspace
    sample_images = []
    
    # Look for common image files
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.bmp']
    
    for ext in image_extensions:
        sample_images.extend(Path('.').glob(ext))
        sample_images.extend(Path('./sample_images').glob(ext)) if Path('./sample_images').exists() else []
        sample_images.extend(Path('./test_images').glob(ext)) if Path('./test_images').exists() else []
    
    # Convert to strings and limit to first 5 for demo
    image_paths = [str(p) for p in sample_images[:5]]
    
    if image_paths:
        print(f"\nFound {len(image_paths)} images for batch analysis:")
        for img in image_paths:
            print(f"  - {img}")
        
        # Run batch analysis
        batch_results = detector.batch_analyze_focus(
            image_paths, 
            output_file="test_focus_analysis_results.json"
        )
        
        # Demonstrate filtering out-of-focus images
        print("\n🎯 FOCUS FILTERING RESULTS:")
        print("-" * 30)
        
        out_of_focus_images = []
        usable_images = []
        
        for result in batch_results['detailed_results']:
            if result.get('focus_level') in ['poor', 'unusable']:
                out_of_focus_images.append(result)
            else:
                usable_images.append(result)
        
        print(f"✅ Usable images: {len(usable_images)}")
        for img in usable_images:
            print(f"   - {img['filename']} ({img.get('focus_level', 'unknown')})")
        
        print(f"\n❌ Out-of-focus images: {len(out_of_focus_images)}")
        for img in out_of_focus_images:
            print(f"   - {img['filename']} ({img.get('focus_level', 'unknown')})")
            issues = img.get('focus_issues', [])
            if issues:
                print(f"     Reason: {issues[0]}")
                
    else:
        print("No sample images found in current directory.")
        print("Please add some .jpg, .png, or other image files to test batch analysis.")

def test_custom_thresholds():
    """Demonstrate custom threshold configuration"""
    
    print("\n\n🔧 TESTING CUSTOM FOCUS THRESHOLDS")
    print("="*50)
    
    # Load and display current configuration
    config_file = "config_focus_detection.json"
    
    if Path(config_file).exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        sharpness_config = config.get('sharpness', {})
        focus_classification = sharpness_config.get('focus_classification', {})
        
        print("\n📊 Current Focus Quality Thresholds:")
        print("-" * 40)
        
        for level, params in focus_classification.items():
            min_lap = params.get('min_laplacian', 0)
            description = params.get('description', '')
            print(f"{level.upper()}: Laplacian ≥ {min_lap}")
            print(f"  Description: {description}")
        
        print("\n💡 How to customize:")
        print("1. Edit 'config_focus_detection.json'")
        print("2. Adjust 'min_laplacian_variance' values")
        print("3. Lower values = more strict focus requirements")
        print("4. Higher values = more lenient focus requirements")
        
        print("\n📋 Example customizations:")
        print("- For strict document scanning: min_laplacian_variance: 300")
        print("- For casual photos: min_laplacian_variance: 100")
        print("- For archived documents: min_laplacian_variance: 250")
        
    else:
        print(f"Configuration file '{config_file}' not found.")

def demonstrate_focus_flags():
    """Show examples of focus flag messages"""
    
    print("\n\n📝 FOCUS FLAG EXAMPLES")
    print("="*50)
    
    examples = [
        {
            'scenario': 'Image with severe blur',
            'laplacian_var': 30.0,
            'expected_flag': 'OUT OF FOCUS - Severely blurred',
            'status': 'FAIL',
            'color': '🔴'
        },
        {
            'scenario': 'Image with moderate blur',
            'laplacian_var': 90.0,
            'expected_flag': 'OUT OF FOCUS - Noticeable blur',
            'status': 'FAIL', 
            'color': '🔴'
        },
        {
            'scenario': 'Image with slight softness',
            'laplacian_var': 140.0,
            'expected_flag': 'SOFT FOCUS - Minor issues',
            'status': 'WARN',
            'color': '🟡'
        },
        {
            'scenario': 'Sharp, in-focus image',
            'laplacian_var': 250.0,
            'expected_flag': 'SHARP - Good focus quality',
            'status': 'PASS',
            'color': '🟢'
        }
    ]
    
    print("Focus Quality Classification Examples:")
    print("-" * 40)
    
    for example in examples:
        print(f"\n{example['color']} {example['scenario']}:")
        print(f"   Laplacian Variance: {example['laplacian_var']}")
        print(f"   Flag: {example['expected_flag']}")
        print(f"   Status: {example['status']}")
        
        if example['status'] == 'FAIL':
            print(f"   Report would show: 'Image failed for OUT OF FOCUS'")

def main():
    """Run all focus detection tests"""
    
    print("🎯 ENHANCED FOCUS DETECTION TESTING")
    print("="*60)
    print("This script demonstrates custom focus detection features:")
    print("- Specific out-of-focus flagging")
    print("- Detailed focus quality analysis") 
    print("- Custom threshold configuration")
    print("- Batch processing with focus filtering")
    
    try:
        # Run all tests
        test_single_image_analysis()
        test_batch_analysis()
        test_custom_thresholds()
        demonstrate_focus_flags()
        
        print("\n✅ TESTING COMPLETE")
        print("="*60)
        print("The enhanced focus detection system provides:")
        print("1. 🎯 Specific 'OUT OF FOCUS' failure reasons")
        print("2. 📊 Detailed focus quality breakdown") 
        print("3. 🔧 Customizable focus thresholds")
        print("4. 📁 Batch analysis with focus filtering")
        print("5. 💡 Actionable focus improvement recommendations")
        
        print("\nTo customize for your needs:")
        print("- Edit config_focus_detection.json")
        print("- Adjust thresholds based on your requirements")
        print("- Use the EnhancedFocusDetector class in your workflow")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        print("Please check that all required files are present.")

if __name__ == "__main__":
    main()

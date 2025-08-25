"""
Quick test script to verify ImageQualityAnalyzer implementation
"""

import os
import sys
import numpy as np
import cv2

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_document():
    """Create a simple test document image"""
    print("📄 Creating test document...")
    
    # Create a document-like image
    height, width = 800, 600
    image = np.full((height, width, 3), 240, dtype=np.uint8)  # Light background
    
    # Add some "text" lines
    cv2.rectangle(image, (50, 100), (550, 120), (50, 50, 50), -1)
    cv2.rectangle(image, (50, 150), (450, 170), (50, 50, 50), -1)
    cv2.rectangle(image, (50, 200), (500, 220), (50, 50, 50), -1)
    cv2.rectangle(image, (50, 250), (480, 270), (50, 50, 50), -1)
    cv2.rectangle(image, (50, 300), (520, 320), (50, 50, 50), -1)
    
    # Add some noise/texture for realism
    noise = np.random.normal(0, 5, (height, width, 3))
    image = np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    # Save test image
    cv2.imwrite('test_document.jpg', image)
    print("✅ Test document created: test_document.jpg")
    return 'test_document.jpg'

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing configuration system...")
    
    try:
        from image_quality_analyzer.config import load_default_config, load_profile, list_profiles
        
        # Test default config
        config = load_default_config()
        assert isinstance(config, dict)
        assert 'resolution' in config
        print("✅ Default configuration loaded successfully")
        
        # Test profiles
        profiles = list_profiles()
        print(f"✅ Found {len(profiles)} configuration profiles:")
        for profile_id, info in profiles.items():
            print(f"   - {profile_id}: {info['name']}")
        
        # Test loading a profile
        archival_config = load_profile('archival_quality')
        assert archival_config['resolution']['min_dpi_text'] == 400
        print("✅ Archival profile loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_metrics():
    """Test individual metrics"""
    print("\n📊 Testing metrics computation...")
    
    try:
        from image_quality_analyzer.metrics.base import DocumentMaskGenerator
        from image_quality_analyzer.metrics.sharpness import SharpnessMetrics
        from image_quality_analyzer.metrics.exposure import ExposureMetrics
        
        # Load test image
        image = cv2.imread('test_document.jpg')
        assert image is not None, "Could not load test image"
        
        # Create document mask
        mask_generator = DocumentMaskGenerator()
        doc_mask = mask_generator.create_document_mask(image)
        assert np.any(doc_mask > 0), "Document mask is empty"
        print("✅ Document mask created")
        
        # Test sharpness metrics
        sharpness_computer = SharpnessMetrics()
        sharpness_result = sharpness_computer.compute(image, doc_mask, {'min_laplacian_variance': 100})
        assert 'laplacian_var' in sharpness_result
        print(f"✅ Sharpness computed: {sharpness_result['laplacian_var']:.2f}")
        
        # Test exposure metrics
        exposure_computer = ExposureMetrics()
        exposure_result = exposure_computer.compute(image, doc_mask, {})
        assert 'clipping' in exposure_result
        print(f"✅ Exposure computed: shadow clip {exposure_result['clipping']['shadow_clip_pct']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
        return False

def test_scoring():
    """Test scoring system"""
    print("\n🏆 Testing scoring system...")
    
    try:
        from image_quality_analyzer.scoring import QualityScorer, Status
        from image_quality_analyzer.config import load_default_config
        
        config = load_default_config()
        scorer = QualityScorer(config)
        
        # Test status conversion
        assert scorer._status_to_score(Status.PASS) == 1.0
        assert scorer._status_to_score(Status.WARN) == 0.75
        assert scorer._status_to_score(Status.FAIL) == 0.0
        print("✅ Status to score conversion works")
        
        # Test sharpness scoring
        good_sharpness = {'laplacian_var': 200.0}
        status = scorer._score_sharpness(good_sharpness, config['sharpness'])
        assert status == Status.PASS
        print("✅ Sharpness scoring works")
        
        return True
        
    except Exception as e:
        print(f"❌ Scoring test failed: {e}")
        return False

def test_full_analysis():
    """Test complete analysis pipeline"""
    print("\n🔍 Testing full analysis pipeline...")
    
    try:
        from image_quality_analyzer import ImageQualityAnalyzer
        
        # Initialize analyzer
        analyzer = ImageQualityAnalyzer()
        
        # Analyze test image
        result = analyzer.analyze_image('test_document.jpg')
        
        # Verify result structure
        required_keys = ['image_id', 'file_path', 'pixels', 'metrics', 'category_status', 'global']
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
        
        # Verify global results
        global_result = result['global']
        assert 0 <= global_result['score'] <= 1
        assert 1 <= global_result['stars'] <= 4
        assert global_result['status'] in ['pass', 'warn', 'fail']
        
        print(f"✅ Analysis completed successfully!")
        print(f"   Score: {global_result['score']:.2f}")
        print(f"   Stars: {'★' * global_result['stars']}{'☆' * (4 - global_result['stars'])}")
        print(f"   Status: {global_result['status'].upper()}")
        
        # Test JSON export
        analyzer.export_json_report(result, 'test_report.json')
        assert os.path.exists('test_report.json')
        print("✅ JSON export works")
        
        return True
        
    except Exception as e:
        print(f"❌ Full analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization():
    """Test visualization generation"""
    print("\n🎨 Testing visualization system...")
    
    try:
        from image_quality_analyzer.visualization import GraphGenerator
        from image_quality_analyzer import ImageQualityAnalyzer
        
        # Analyze image first
        analyzer = ImageQualityAnalyzer()
        result = analyzer.analyze_image('test_document.jpg')
        
        # Generate graphs
        graph_generator = GraphGenerator()
        os.makedirs('test_output', exist_ok=True)
        
        graph_files = graph_generator.generate_all_graphs(
            'test_document.jpg', result, 'test_output'
        )
        
        print(f"✅ Generated {len(graph_files)} visualization files:")
        for graph_type, file_path in graph_files.items():
            print(f"   - {graph_type}: {os.path.basename(file_path)}")
        
        # Test summary dashboard
        graph_generator.create_summary_dashboard(result, 'test_output/dashboard.png')
        print("✅ Summary dashboard created")
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    
    files_to_remove = [
        'test_document.jpg',
        'test_report.json'
    ]
    
    dirs_to_remove = ['test_output']
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Removed: {file}")
    
    import shutil
    for dir in dirs_to_remove:
        if os.path.exists(dir):
            shutil.rmtree(dir)
            print(f"   Removed directory: {dir}")

def main():
    """Run all tests"""
    print("🚀 ImageQualityAnalyzer - Quick Test Suite")
    print("=" * 50)
    
    # Create test document
    create_test_document()
    
    # Run tests
    tests = [
        ("Configuration System", test_configuration),
        ("Metrics Computation", test_metrics),
        ("Scoring System", test_scoring),
        ("Full Analysis Pipeline", test_full_analysis),
        ("Visualization System", test_visualization),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! ImageQualityAnalyzer is working correctly.")
        print("\n📖 Next steps:")
        print("   1. Check QUICKSTART.md for usage examples")
        print("   2. Try the CLI: python cli.py analyze <your_image.jpg>")
        print("   3. Review examples/basic_usage.py for Python API")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
    
    # Cleanup
    cleanup()
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

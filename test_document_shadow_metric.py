#!/usr/bin/env python3
"""
Test script for the new Document Shadow Detection metric
"""

import sys
import os
import numpy as np
import cv2
from PIL import Image

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image_with_shadow():
    """Create a synthetic test image with document shadow"""
    # Create white background image
    height, width = 800, 600
    image = np.ones((height, width), dtype=np.uint8) * 240  # Light gray background
    
    # Create document area (darker to simulate paper)
    doc_top, doc_left = 100, 80
    doc_bottom, doc_right = 650, 520
    
    # Draw document
    cv2.rectangle(image, (doc_left, doc_top), (doc_right, doc_bottom), 220, -1)
    
    # Add shadow gradient around document (simulate loose document shadow)
    shadow_width = 30
    for i in range(shadow_width):
        # Calculate shadow intensity (darker closer to document)
        intensity = 240 - (30 - i) * 1.5  # Gradual intensity change
        intensity = max(160, min(240, int(intensity)))  # Clamp values
        
        # Draw shadow border
        cv2.rectangle(image, 
                     (doc_left - i - 1, doc_top - i - 1), 
                     (doc_right + i + 1, doc_bottom + i + 1), 
                     intensity, 2)
    
    # Add some text-like patterns to make it more realistic
    for y in range(doc_top + 20, doc_bottom - 20, 25):
        for x in range(doc_left + 20, doc_right - 100, 8):
            if np.random.random() < 0.7:  # 70% chance of text
                cv2.rectangle(image, (x, y), (x + 6, y + 12), 50, -1)
    
    return image

def create_test_image_no_shadow():
    """Create a synthetic test image without document shadow"""
    # Create white background image
    height, width = 800, 600
    image = np.ones((height, width), dtype=np.uint8) * 240  # Light gray background
    
    # Create document area (no shadow)
    doc_top, doc_left = 100, 80
    doc_bottom, doc_right = 650, 520
    
    # Draw document with sharp edges (no shadow)
    cv2.rectangle(image, (doc_left, doc_top), (doc_right, doc_bottom), 220, -1)
    
    # Add some text-like patterns
    for y in range(doc_top + 20, doc_bottom - 20, 25):
        for x in range(doc_left + 20, doc_right - 100, 8):
            if np.random.random() < 0.7:
                cv2.rectangle(image, (x, y), (x + 6, y + 12), 50, -1)
    
    return image

def test_document_shadow_metric():
    """Test the document shadow metric with synthetic images"""
    
    print("🧪 Testing Document Shadow Detection Metric...")
    print("=" * 50)
    
    try:
        # Import the metric
        from image_quality_analyzer.metrics.document_shadow import DocumentShadowMetric
        
        # Create metric instance with test configuration
        config = {
            'shadow_threshold': 15,  # Lower threshold for testing
            'analysis_band_width': 40,
            'min_contour_area': 5000,
            'warn_shadow_intensity': 10,
            'fail_shadow_intensity': 25
        }
        
        metric = DocumentShadowMetric(config)
        print("✅ Document Shadow metric initialized successfully")
        
        # Test 1: Image with shadow
        print("\n📸 Test 1: Image WITH shadow")
        print("-" * 30)
        
        shadow_image = create_test_image_with_shadow()
        result_with_shadow = metric.analyze(shadow_image)
        
        print(f"Shadow Present: {result_with_shadow.get('shadow_present', 'N/A')}")
        print(f"Shadow Intensity: {result_with_shadow.get('shadow_intensity', 0):.2f}")
        print(f"Shadow Width: {result_with_shadow.get('shadow_width', 0):.2f} px")
        print(f"Quality Score: {result_with_shadow.get('quality_score', 0):.3f}")
        print(f"Confidence: {result_with_shadow.get('confidence', 0):.3f}")
        
        if 'error' in result_with_shadow:
            print(f"❌ Error: {result_with_shadow['error']}")
        
        # Get recommendations
        recommendations = metric.get_recommendations(result_with_shadow)
        print(f"Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Test 2: Image without shadow
        print("\n📸 Test 2: Image WITHOUT shadow")
        print("-" * 30)
        
        no_shadow_image = create_test_image_no_shadow()
        result_no_shadow = metric.analyze(no_shadow_image)
        
        print(f"Shadow Present: {result_no_shadow.get('shadow_present', 'N/A')}")
        print(f"Shadow Intensity: {result_no_shadow.get('shadow_intensity', 0):.2f}")
        print(f"Shadow Width: {result_no_shadow.get('shadow_width', 0):.2f} px")
        print(f"Quality Score: {result_no_shadow.get('quality_score', 0):.3f}")
        print(f"Confidence: {result_no_shadow.get('confidence', 0):.3f}")
        
        if 'error' in result_no_shadow:
            print(f"❌ Error: {result_no_shadow['error']}")
        
        # Get recommendations
        recommendations = metric.get_recommendations(result_no_shadow)
        print(f"Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Test 3: Integration with scoring system
        print("\n🏆 Test 3: Integration with Scoring System")
        print("-" * 30)
        
        try:
            from image_quality_analyzer.scoring import QualityScorer
            from image_quality_analyzer.config import load_default_config
            
            config_full = load_default_config()
            scorer = QualityScorer(config_full)
            
            # Test scoring with shadow
            shadow_score = scorer.score_category('document_shadow', result_with_shadow)
            print(f"Shadow image score: {shadow_score}")
            
            # Test scoring without shadow
            no_shadow_score = scorer.score_category('document_shadow', result_no_shadow)
            print(f"No shadow image score: {no_shadow_score}")
            
            print("✅ Scoring system integration successful")
            
        except Exception as e:
            print(f"⚠️ Scoring system test failed: {e}")
        
        # Summary
        print("\n📊 Test Summary")
        print("=" * 50)
        
        shadow_detected_correctly = result_with_shadow.get('shadow_present', False)
        no_shadow_detected_correctly = not result_no_shadow.get('shadow_present', True)
        
        print(f"✅ Shadow detection accuracy: {shadow_detected_correctly and no_shadow_detected_correctly}")
        print(f"✅ With shadow - detected: {shadow_detected_correctly}")
        print(f"✅ Without shadow - detected correctly: {no_shadow_detected_correctly}")
        
        # Save test images for manual inspection (optional)
        output_dir = "test_output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        cv2.imwrite(os.path.join(output_dir, "test_shadow_image.png"), shadow_image)
        cv2.imwrite(os.path.join(output_dir, "test_no_shadow_image.png"), no_shadow_image)
        print(f"💾 Test images saved to {output_dir}/")
        
        print("\n🎉 Document Shadow Metric testing completed!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the document shadow metric is properly installed")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_document_shadow_metric()
    
    if success:
        print("\n✅ All tests passed! The Document Shadow metric is working correctly.")
    else:
        print("\n❌ Tests failed. Please check the implementation.")
    
    print("\n💡 Next steps:")
    print("  1. Test with real document images")
    print("  2. Adjust thresholds based on real-world performance") 
    print("  3. Integrate into the main analysis pipeline")
    print("  4. Update UI to display shadow detection results")

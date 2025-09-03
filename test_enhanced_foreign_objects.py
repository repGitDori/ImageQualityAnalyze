"""
Test Enhanced Foreign Objects Detection System

This script tests the enhanced foreign objects detection system with 
various scenarios including clips, tools, black objects, and shadows.
"""

import os
import sys
import numpy as np
import cv2
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from enhanced_foreign_objects import (
    EnhancedForeignObjectsDetector,
    analyze_document_with_foreign_objects,
    print_foreign_objects_analysis
)


def create_test_image_with_clip(width=800, height=600, save_path="test_clip_image.jpg"):
    """Create a test image with simulated clip/tool artifacts"""
    
    print(f"🎨 Creating test image with clip artifacts: {save_path}")
    
    # Create white document background
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Add some document text simulation (dark rectangles)
    for i in range(5):
        x = 50 + i * 120
        y = 100 + i * 80
        cv2.rectangle(image, (x, y), (x + 100, y + 20), (50, 50, 50), -1)
    
    # Add clip/tool simulation (metallic object near edge)
    # Simulate pixelated background around clip
    clip_x, clip_y = 20, 50
    clip_w, clip_h = 40, 150
    
    # Create pixelated background effect
    for y in range(clip_y - 30, clip_y + clip_h + 30, 10):
        for x in range(clip_x - 20, clip_x + clip_w + 20, 10):
            if 0 <= x < width and 0 <= y < height:
                # Random grayish pixels to simulate pixelation
                color = np.random.randint(80, 150, 3)
                cv2.rectangle(image, (x, y), (x + 8, y + 8), tuple(map(int, color)), -1)
    
    # Add the clip itself (non-black metallic color)
    clip_color = (120, 100, 80)  # Brownish metallic
    cv2.rectangle(image, (clip_x, clip_y), (clip_x + clip_w, clip_y + clip_h), clip_color, -1)
    
    # Add some highlight on clip
    cv2.rectangle(image, (clip_x + 5, clip_y + 5), (clip_x + 15, clip_y + clip_h - 5), (180, 160, 140), -1)
    
    cv2.imwrite(save_path, image)
    return save_path


def create_test_image_with_black_object(width=800, height=600, save_path="test_black_object.jpg"):
    """Create a test image with black object penetrating document"""
    
    print(f"🎨 Creating test image with black object: {save_path}")
    
    # Create white document background
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Add some document text simulation
    for i in range(8):
        x = 50 + (i % 3) * 200
        y = 80 + (i // 3) * 100
        cv2.rectangle(image, (x, y), (x + 150, y + 15), (30, 30, 30), -1)
        cv2.rectangle(image, (x, y + 25), (x + 120, y + 40), (30, 30, 30), -1)
    
    # Add black object (simulated finger/hand) penetrating document area
    # Create irregular shape using ellipse and rectangles
    black_color = (10, 10, 10)
    
    # Main finger/object shape
    cv2.ellipse(image, (300, 200), (40, 120), 45, 0, 360, black_color, -1)
    cv2.ellipse(image, (350, 280), (35, 100), 30, 0, 360, black_color, -1)
    
    # Add shadow effect around black object
    shadow_color = (180, 180, 180)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    
    # Create mask for black objects
    black_mask = cv2.inRange(image, (0, 0, 0), (50, 50, 50))
    shadow_mask = cv2.dilate(black_mask, kernel) - black_mask
    
    # Apply shadow
    image[shadow_mask > 0] = shadow_color
    
    cv2.imwrite(save_path, image)
    return save_path


def create_test_image_with_both(width=800, height=600, save_path="test_combined_objects.jpg"):
    """Create a test image with both clips and black objects"""
    
    print(f"🎨 Creating test image with combined foreign objects: {save_path}")
    
    # Create white document background
    image = np.ones((height, width, 3), dtype=np.uint8) * 240
    
    # Add document content
    for i in range(6):
        x = 80 + (i % 2) * 300
        y = 100 + (i // 2) * 120
        cv2.rectangle(image, (x, y), (x + 200, y + 20), (40, 40, 40), -1)
        cv2.rectangle(image, (x, y + 30), (x + 180, y + 50), (40, 40, 40), -1)
        cv2.rectangle(image, (x, y + 60), (x + 220, y + 80), (40, 40, 40), -1)
    
    # Add clip on left edge
    clip_x, clip_y = 5, 100
    clip_w, clip_h = 25, 200
    
    # Pixelated background
    for y in range(clip_y - 20, clip_y + clip_h + 20, 8):
        for x in range(0, clip_x + clip_w + 30, 8):
            if 0 <= x < width and 0 <= y < height:
                color = np.random.randint(60, 120, 3)
                cv2.rectangle(image, (x, y), (x + 6, y + 6), tuple(map(int, color)), -1)
    
    # The clip itself
    cv2.rectangle(image, (clip_x, clip_y), (clip_x + clip_w, clip_y + clip_h), (90, 70, 60), -1)
    
    # Add black object (hand/finger) in document area
    black_color = (5, 5, 5)
    cv2.ellipse(image, (500, 350), (60, 80), 20, 0, 360, black_color, -1)
    cv2.ellipse(image, (460, 420), (40, 60), -10, 0, 360, black_color, -1)
    
    # Add severe shadow
    shadow_area = image[250:500, 400:650]
    shadow_area = cv2.addWeighted(shadow_area, 0.6, np.zeros_like(shadow_area), 0, -30)
    image[250:500, 400:650] = shadow_area
    
    cv2.imwrite(save_path, image)
    return save_path


def test_enhanced_foreign_objects_detection():
    """Test the enhanced foreign objects detection system"""
    
    print("🧪 TESTING ENHANCED FOREIGN OBJECTS DETECTION")
    print("="*60)
    
    # Create test images
    test_images = []
    
    # Test 1: Clip/tool detection
    clip_image = create_test_image_with_clip()
    test_images.append(("Clip/Tool Detection", clip_image))
    
    # Test 2: Black object detection  
    black_image = create_test_image_with_black_object()
    test_images.append(("Black Object Detection", black_image))
    
    # Test 3: Combined detection
    combined_image = create_test_image_with_both()
    test_images.append(("Combined Foreign Objects", combined_image))
    
    # Test 4: Real image if available
    sample_image = "sample_document.jpg"
    if os.path.exists(sample_image):
        test_images.append(("Real Document", sample_image))
    
    # Run tests on each image
    all_results = {}
    
    for test_name, image_path in test_images:
        print(f"\n🔬 TEST: {test_name}")
        print("-" * 40)
        
        try:
            # Analyze image
            output_file = f"test_results_{test_name.lower().replace(' ', '_').replace('/', '_')}.json"
            results = analyze_document_with_foreign_objects(image_path, output_file)
            
            all_results[test_name] = results
            
            # Show status
            if results['foreign_object_flag']:
                print(f"🔴 RESULT: FAILED - Foreign objects detected")
                print(f"📊 Coverage: {results['foreign_object_area_pct']:.2f}%")
                print(f"🔢 Objects: {results['summary']['total_objects_detected']}")
            else:
                print(f"🟢 RESULT: PASSED - No significant foreign objects")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            continue
    
    # Generate summary report
    print(f"\n📋 SUMMARY REPORT")
    print("="*60)
    
    passed_count = 0
    failed_count = 0
    
    for test_name, results in all_results.items():
        status = "FAILED" if results['foreign_object_flag'] else "PASSED"
        coverage = results['foreign_object_area_pct']
        objects = results['summary']['total_objects_detected']
        
        if results['foreign_object_flag']:
            failed_count += 1
            print(f"🔴 {test_name:<25} | {status:<6} | {coverage:>6.1f}% | {objects:>2} objects")
        else:
            passed_count += 1
            print(f"🟢 {test_name:<25} | {status:<6} | {coverage:>6.1f}% | {objects:>2} objects")
    
    print("-" * 60)
    print(f"✅ PASSED: {passed_count}    ❌ FAILED: {failed_count}    📊 TOTAL: {len(all_results)}")
    
    # Test configuration loading
    test_custom_config()
    
    return all_results


def test_custom_config():
    """Test custom configuration loading"""
    
    print(f"\n⚙️ TESTING CUSTOM CONFIGURATION")
    print("-" * 40)
    
    config_file = "config_foreign_objects.json"
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Initialize detector with custom config
            detector = EnhancedForeignObjectsDetector(config)
            print(f"✅ Custom configuration loaded successfully")
            print(f"📎 Clip threshold: {config['foreign_objects']['failure_thresholds']['clip_area_pct']}%")
            print(f"⚫ Black object threshold: {config['foreign_objects']['failure_thresholds']['black_object_area_pct']}%")
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
    else:
        print(f"⚠️ Configuration file not found: {config_file}")
        print(f"   Using default configuration")


def demonstrate_batch_processing():
    """Demonstrate batch processing of multiple images"""
    
    print(f"\n📦 BATCH PROCESSING DEMONSTRATION")
    print("-" * 40)
    
    # Create multiple test images
    test_images = [
        create_test_image_with_clip(save_path="batch_test_1.jpg"),
        create_test_image_with_black_object(save_path="batch_test_2.jpg"),
        create_test_image_with_both(save_path="batch_test_3.jpg")
    ]
    
    batch_results = []
    failed_images = []
    
    for i, image_path in enumerate(test_images, 1):
        print(f"\n📸 Processing image {i}: {Path(image_path).name}")
        
        try:
            results = analyze_document_with_foreign_objects(
                image_path, 
                f"batch_result_{i}.json"
            )
            
            batch_results.append({
                'image': image_path,
                'results': results
            })
            
            if results['foreign_object_flag']:
                failed_images.append({
                    'image': image_path,
                    'reasons': results['failure_reasons'],
                    'coverage': results['foreign_object_area_pct']
                })
            
        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")
    
    # Batch summary
    print(f"\n📊 BATCH PROCESSING SUMMARY")
    print(f"📁 Total Images: {len(test_images)}")
    print(f"✅ Successfully Processed: {len(batch_results)}")
    print(f"❌ Failed Quality Check: {len(failed_images)}")
    
    if failed_images:
        print(f"\n🔴 FAILED IMAGES:")
        for i, failed in enumerate(failed_images, 1):
            print(f"   {i}. {Path(failed['image']).name} ({failed['coverage']:.1f}% coverage)")
            for reason in failed['reasons']:
                print(f"      • {reason}")


if __name__ == "__main__":
    # Run comprehensive test suite
    try:
        # Main testing
        results = test_enhanced_foreign_objects_detection()
        
        # Batch processing demo
        demonstrate_batch_processing()
        
        print(f"\n🎉 TESTING COMPLETED!")
        print(f"🔍 Enhanced foreign objects detection system is ready for use")
        print(f"📝 Check the generated JSON files for detailed results")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()

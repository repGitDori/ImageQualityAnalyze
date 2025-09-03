"""
Simple Foreign Objects Analyzer - Easy Integration

This script provides a simple interface to add foreign objects detection
to your existing image quality analysis workflow.

Usage:
    python simple_foreign_objects.py <image_path>
    python simple_foreign_objects.py <image_path> --config custom_config.json
    python simple_foreign_objects.py batch <folder_path>
"""

import os
import sys
import argparse
import json
import glob
from pathlib import Path
from typing import List, Dict, Any

# Import our enhanced detection system
from enhanced_foreign_objects import (
    EnhancedForeignObjectsDetector,
    analyze_document_with_foreign_objects
)


def analyze_single_image(image_path: str, config_path: str = None, 
                        output_file: str = None) -> Dict[str, Any]:
    """
    Analyze a single image for foreign objects
    
    Args:
        image_path: Path to image file
        config_path: Optional custom configuration file
        output_file: Optional output JSON file
        
    Returns:
        Analysis results dictionary
    """
    
    print(f"🔍 ANALYZING: {Path(image_path).name}")
    
    # Load configuration if provided
    config = None
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"📋 Using configuration: {config_path}")
    
    # Initialize detector
    detector = EnhancedForeignObjectsDetector(config)
    
    # Analyze image
    results = analyze_document_with_foreign_objects(
        image_path, 
        output_file or f"{Path(image_path).stem}_foreign_objects.json"
    )
    
    return results


def analyze_batch_folder(folder_path: str, config_path: str = None,
                        output_dir: str = None) -> Dict[str, Any]:
    """
    Analyze all images in a folder for foreign objects
    
    Args:
        folder_path: Path to folder containing images
        config_path: Optional custom configuration file
        output_dir: Optional output directory
        
    Returns:
        Batch analysis results
    """
    
    print(f"📁 BATCH ANALYSIS: {folder_path}")
    
    # Find all image files
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(folder_path, ext)))
        image_files.extend(glob.glob(os.path.join(folder_path, ext.upper())))
    
    if not image_files:
        print(f"❌ No image files found in {folder_path}")
        return {}
    
    print(f"📸 Found {len(image_files)} images")
    
    # Setup output directory
    if not output_dir:
        output_dir = os.path.join(folder_path, "foreign_objects_analysis")
    os.makedirs(output_dir, exist_ok=True)
    
    # Load configuration if provided
    config = None
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"📋 Using configuration: {config_path}")
    
    # Initialize detector
    detector = EnhancedForeignObjectsDetector(config)
    
    # Process each image
    batch_results = {
        'total_images': len(image_files),
        'processed': 0,
        'passed': 0,
        'failed': 0,
        'failed_foreign_objects': 0,
        'results': []
    }
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n📷 Processing {i}/{len(image_files)}: {Path(image_path).name}")
        
        try:
            # Analyze image
            output_file = os.path.join(output_dir, f"{Path(image_path).stem}_analysis.json")
            results = analyze_document_with_foreign_objects(image_path, output_file)
            
            # Update counters
            batch_results['processed'] += 1
            
            if results['foreign_object_flag']:
                batch_results['failed'] += 1
                batch_results['failed_foreign_objects'] += 1
                print(f"   ❌ FAILED: Foreign objects detected ({results['foreign_object_area_pct']:.1f}% coverage)")
            else:
                batch_results['passed'] += 1
                print(f"   ✅ PASSED: No significant foreign objects")
            
            # Add to results
            batch_results['results'].append({
                'image_path': image_path,
                'result': results,
                'passed': not results['foreign_object_flag']
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    # Save batch summary
    summary_file = os.path.join(output_dir, "batch_summary.json")
    with open(summary_file, 'w') as f:
        # Make JSON serializable
        json_results = convert_for_json(batch_results)
        json.dump(json_results, f, indent=2)
    
    # Print summary
    print_batch_summary(batch_results, output_dir)
    
    return batch_results


def print_batch_summary(results: Dict[str, Any], output_dir: str) -> None:
    """Print formatted batch summary"""
    
    print(f"\n📊 BATCH ANALYSIS SUMMARY")
    print("="*50)
    print(f"📁 Output Directory: {output_dir}")
    print(f"📷 Total Images: {results['total_images']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    
    if results['failed'] > 0:
        failure_rate = (results['failed'] / results['total_images']) * 100
        print(f"📈 Failure Rate: {failure_rate:.1f}%")
        
        print(f"\n🔴 FAILED IMAGES:")
        failed_count = 0
        for result in results['results']:
            if not result['passed']:
                failed_count += 1
                image_name = Path(result['image_path']).name
                coverage = result['result']['foreign_object_area_pct']
                reasons = result['result']['failure_reasons']
                print(f"   {failed_count}. {image_name} ({coverage:.1f}% coverage)")
                for reason in reasons[:2]:  # Show first 2 reasons
                    print(f"      • {reason}")


def convert_for_json(obj):
    """Convert numpy arrays and other objects for JSON serialization"""
    
    import numpy as np
    
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {k: convert_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_for_json(item) for item in obj]
    elif isinstance(obj, tuple):
        return [convert_for_json(item) for item in obj]
    else:
        return obj


def main():
    """Main command line interface"""
    
    parser = argparse.ArgumentParser(
        description="Analyze images for foreign objects (clips, tools, hands, etc.)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python simple_foreign_objects.py document.jpg
    python simple_foreign_objects.py document.jpg --config custom_config.json
    python simple_foreign_objects.py batch ./images/
    python simple_foreign_objects.py batch ./images/ --output ./results/
        """
    )
    
    parser.add_argument(
        'command',
        help='Command: image_path for single image, or "batch" for batch processing'
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        help='Path to image file or folder (required for batch command)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to custom configuration JSON file'
    )
    
    parser.add_argument(
        '--output',
        help='Output file (single image) or directory (batch)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command.lower() == 'batch':
            if not args.path:
                print("❌ Error: Folder path required for batch processing")
                return
            
            if not os.path.isdir(args.path):
                print(f"❌ Error: {args.path} is not a valid directory")
                return
            
            # Batch processing
            results = analyze_batch_folder(args.path, args.config, args.output)
            
            if results['failed_foreign_objects'] > 0:
                print(f"\n🔴 BATCH FAILED: {results['failed_foreign_objects']} images have foreign objects")
            else:
                print(f"\n🟢 BATCH PASSED: All images passed foreign object checks")
        
        else:
            # Single image processing
            image_path = args.command
            
            if not os.path.exists(image_path):
                print(f"❌ Error: Image file {image_path} not found")
                return
            
            # Analyze single image
            results = analyze_single_image(image_path, args.config, args.output)
            
            if results['foreign_object_flag']:
                print(f"\n🔴 IMAGE FAILED: Foreign objects detected")
                print(f"📊 Coverage: {results['foreign_object_area_pct']:.2f}%")
                print(f"🔧 Check the analysis JSON file for detailed recommendations")
            else:
                print(f"\n🟢 IMAGE PASSED: No significant foreign objects detected")
    
    except KeyboardInterrupt:
        print(f"\n⚠️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🔍 FOREIGN OBJECTS ANALYZER")
    print("="*40)
    
    if len(sys.argv) == 1:
        print("Usage: python simple_foreign_objects.py <image_path>")
        print("       python simple_foreign_objects.py batch <folder_path>")
        print("       python simple_foreign_objects.py --help")
        print("\nExample:")
        print("  python simple_foreign_objects.py document.jpg")
        print("  python simple_foreign_objects.py batch ./images/")
    else:
        main()

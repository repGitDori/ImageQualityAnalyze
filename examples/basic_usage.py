"""
Example usage of ImageQualityAnalyzer
"""

import os
import sys
from pathlib import Path

# Add the package to the path for local testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_quality_analyzer import ImageQualityAnalyzer, load_default_config, load_profile
from image_quality_analyzer.visualization import GraphGenerator


def analyze_single_image_example():
    """Example: Analyze a single image"""
    
    print("=== Single Image Analysis Example ===")
    
    # Load configuration (you can customize this)
    config = load_default_config()
    
    # Initialize analyzer
    analyzer = ImageQualityAnalyzer(config)
    
    # Example image path (replace with your actual image)
    image_path = "sample_document.jpg"
    
    if not os.path.exists(image_path):
        print(f"Sample image not found at {image_path}")
        print("Please provide a document image to analyze.")
        return
    
    try:
        # Analyze the image
        result = analyzer.analyze_image(image_path)
        
        # Print summary
        print(f"\nAnalysis Results for {result['image_id']}:")
        print(f"Overall Score: {result['global']['score']:.2f}")
        print(f"Star Rating: {'★' * result['global']['stars']}{'☆' * (4 - result['global']['stars'])}")
        print(f"Status: {result['global']['status'].upper()}")
        
        # Print category results
        print("\nCategory Status:")
        for category, status in result['category_status'].items():
            emoji = "✅" if status == "pass" else "⚠️" if status == "warn" else "❌"
            print(f"  {emoji} {category.replace('_', ' ').title()}: {status.upper()}")
        
        # Print action items if any
        if result['global']['actions']:
            print("\nRecommended Actions:")
            for action in result['global']['actions']:
                print(f"  {action}")
        
        # Export results
        analyzer.export_json_report(result, "output/single_analysis.json")
        print(f"\nDetailed report saved to: output/single_analysis.json")
        
        # Generate visualizations
        graph_generator = GraphGenerator()
        os.makedirs("output/graphs", exist_ok=True)
        graph_files = graph_generator.generate_all_graphs(image_path, result, "output/graphs")
        
        print("\nGenerated visualizations:")
        for graph_type, file_path in graph_files.items():
            print(f"  {graph_type}: {file_path}")
        
        # Create summary dashboard
        graph_generator.create_summary_dashboard(result, "output/summary_dashboard.png")
        print("Summary dashboard: output/summary_dashboard.png")
        
    except Exception as e:
        print(f"Error analyzing image: {e}")


def batch_analysis_example():
    """Example: Batch analysis of multiple images"""
    
    print("\n=== Batch Analysis Example ===")
    
    # Load configuration (try different profile)
    config = load_profile('document_lenient')  # More forgiving thresholds
    
    # Initialize analyzer
    analyzer = ImageQualityAnalyzer(config)
    
    # Example image paths (replace with your actual images)
    image_paths = [
        "sample1.jpg",
        "sample2.jpg", 
        "sample3.jpg"
    ]
    
    # Filter to existing files
    existing_paths = [path for path in image_paths if os.path.exists(path)]
    
    if not existing_paths:
        print("No sample images found. Please add some document images to analyze.")
        return
    
    # Progress callback
    def progress_callback(current, total, path):
        print(f"Analyzing {current}/{total}: {os.path.basename(path)}")
    
    try:
        # Analyze batch
        results = analyzer.analyze_batch(existing_paths, progress_callback)
        
        # Print summary statistics
        print(f"\n=== Batch Analysis Summary ===")
        print(f"Total Images: {len(results)}")
        
        # Count by status
        status_counts = {}
        score_sum = 0
        valid_results = 0
        
        for result in results:
            if 'error' not in result:
                status = result['global']['status']
                status_counts[status] = status_counts.get(status, 0) + 1
                score_sum += result['global']['score']
                valid_results += 1
        
        if valid_results > 0:
            avg_score = score_sum / valid_results
            print(f"Average Score: {avg_score:.2f}")
            
            print("Status Distribution:")
            for status, count in status_counts.items():
                print(f"  {status.title()}: {count}")
        
        # Export batch results
        os.makedirs("output", exist_ok=True)
        analyzer.export_csv_comparison(results, "output/batch_comparison.csv")
        print(f"\nBatch comparison saved to: output/batch_comparison.csv")
        
        # Save individual reports
        for result in results:
            if 'error' not in result:
                filename = f"output/{result['image_id']}_report.json"
                analyzer.export_json_report(result, filename)
        
        print(f"Individual reports saved to output/ directory")
        
    except Exception as e:
        print(f"Error in batch analysis: {e}")


def configuration_examples():
    """Examples of different configuration options"""
    
    print("\n=== Configuration Examples ===")
    
    # Default configuration
    default_config = load_default_config()
    print("Default configuration loaded")
    
    # Available profiles
    from image_quality_analyzer.config import list_profiles
    profiles = list_profiles()
    
    print(f"\nAvailable profiles:")
    for profile_id, info in profiles.items():
        print(f"  {profile_id}: {info['name']}")
        print(f"    {info['description']}")
    
    # Load a specific profile
    archival_config = load_profile('archival_quality')
    print(f"\nArchival quality profile loaded")
    print(f"Min DPI: {archival_config['resolution']['min_dpi_text']}")
    print(f"Min bit depth: {archival_config['format_integrity']['bit_depth_min']}")
    
    # Custom configuration example
    custom_config = load_default_config()
    
    # Customize thresholds
    custom_config['sharpness']['min_laplacian_variance'] = 200.0  # Stricter
    custom_config['geometry']['max_skew_deg_pass'] = 0.5  # Very strict
    
    print(f"\nCustom configuration created with stricter thresholds")
    
    # Save custom configuration
    from image_quality_analyzer.config import save_config_to_file
    os.makedirs("configs", exist_ok=True)
    save_config_to_file(custom_config, "configs/custom_strict.json")
    print("Custom configuration saved to: configs/custom_strict.json")


def main():
    """Run all examples"""
    
    print("ImageQualityAnalyzer Examples")
    print("=" * 50)
    
    # Configuration examples
    configuration_examples()
    
    # Single image analysis
    analyze_single_image_example()
    
    # Batch analysis
    batch_analysis_example()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("Check the 'output' directory for generated reports and visualizations.")


if __name__ == "__main__":
    main()

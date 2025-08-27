"""
Test Script for Excel Export Functionality
This script helps verify that the Excel export is working correctly.
"""

import json
import os

def load_sample_results():
    """Load sample analysis results for testing"""
    sample_results = {
        "global": {
            "overall_score": 0.875,
            "score": 0.875,  # Alternative key
            "stars": 4,
            "status": "excellent",
            "analysis_time": 2.34,
            "actions": [
                "✅ Image quality is excellent for document processing",
                "⚠️ Consider slight contrast enhancement for archival purposes",
                "💡 Document meets professional scanning standards"
            ]
        },
        "metrics": {
            "sharpness": {
                "score": 0.920,
                "value": 0.920,  # Alternative key
                "details": "Image is sharp with clear text boundaries",
                "threshold": 0.7
            },
            "exposure": {
                "score": 0.851,
                "details": "Good lighting with minimal shadows",
                "threshold": 0.6
            },
            "contrast": {
                "score": 0.765,
                "details": "Adequate contrast for text readability",
                "threshold": 0.7
            },
            "geometry": {
                "score": 0.890,
                "details": "Document well-aligned with minimal skew",
                "threshold": 0.8
            },
            "noise": {
                "score": 0.823,
                "details": "Low noise levels, clean image",
                "threshold": 0.7
            },
            "color": {
                "score": 0.780,
                "details": "Good color balance and saturation",
                "threshold": 0.6
            }
        }
    }
    return sample_results

def test_excel_export_data_structure():
    """Test that our Excel export can handle the data structure"""
    print("🧪 Testing Excel Export Data Structure")
    print("=" * 50)
    
    results = load_sample_results()
    
    # Test global data extraction
    global_results = results.get('global', {})
    print(f"📊 Global Results Keys: {list(global_results.keys())}")
    
    overall_score = global_results.get('overall_score', global_results.get('score', 0))
    print(f"📊 Overall Score: {overall_score}")
    
    stars = global_results.get('stars', 0)
    print(f"📊 Stars: {stars}")
    
    status = global_results.get('status', 'Unknown')
    print(f"📊 Status: {status}")
    
    actions = global_results.get('actions', [])
    print(f"📊 Actions: {len(actions)} recommendations found")
    
    # Test metrics data extraction
    metrics_data = results.get('metrics', {})
    print(f"\n📊 Metrics Data Keys: {list(metrics_data.keys())}")
    
    for metric_name, metric_data in metrics_data.items():
        if isinstance(metric_data, dict):
            score = metric_data.get('score', metric_data.get('value', 0))
            details = metric_data.get('details', 'No details')
        else:
            score = float(metric_data) if isinstance(metric_data, (int, float)) else 0
            details = 'Direct score value'
        
        print(f"   {metric_name}: {score:.3f} - {details[:30]}...")
    
    print("\n✅ Data structure test completed!")
    print("📊 This structure should populate the Excel export correctly.")

def get_status_from_score(score):
    """Convert numeric score to status text (same as in main app)"""
    if score >= 0.8:
        return 'EXCELLENT'
    elif score >= 0.6:
        return 'GOOD'
    elif score >= 0.4:
        return 'FAIR'
    else:
        return 'POOR'

def preview_excel_content():
    """Preview what would be in the Excel sheets"""
    print("\n📊 Excel Content Preview")
    print("=" * 50)
    
    results = load_sample_results()
    
    # Preview Summary Sheet
    print("\n📋 SUMMARY SHEET PREVIEW:")
    global_results = results.get('global', {})
    overall_score = global_results.get('overall_score', global_results.get('score', 0))
    stars = global_results.get('stars', 0)
    status = global_results.get('status', 'Unknown')
    
    print(f"   Overall Score: {overall_score:.3f}")
    print(f"   Quality Rating: {stars} out of 4 stars")
    print(f"   Status: {status.upper()}")
    print(f"   Quality Gauge: {'█' * int(overall_score * 10)}{'░' * (10 - int(overall_score * 10))} {overall_score:.1%}")
    
    # Preview Metrics Sheet
    print("\n📊 METRICS SHEET PREVIEW:")
    metrics_data = results.get('metrics', {})
    
    print(f"{'Metric':<15} {'Score':<8} {'Percentage':<12} {'Status':<10}")
    print("-" * 50)
    
    for metric_name, metric_data in metrics_data.items():
        if isinstance(metric_data, dict):
            score = metric_data.get('score', metric_data.get('value', 0))
        else:
            score = float(metric_data) if isinstance(metric_data, (int, float)) else 0
        
        status = get_status_from_score(score)
        readable_name = metric_name.replace('_', ' ').title()
        
        print(f"{readable_name:<15} {score:<8.3f} {score:<12.1%} {status:<10}")
    
    # Preview Recommendations
    print("\n💡 RECOMMENDATIONS SHEET PREVIEW:")
    actions = global_results.get('actions', [])
    
    for i, action in enumerate(actions, 1):
        clean_action = str(action).replace('✅', '').replace('⚠️', '').replace('💡', '').strip()
        if '✅' in str(action):
            priority = 'INFO'
        elif '⚠️' in str(action):
            priority = 'WARNING'
        elif '💡' in str(action):
            priority = 'INFO'
        else:
            priority = 'GENERAL'
        
        print(f"   {i}. [{priority}] {clean_action}")

if __name__ == "__main__":
    test_excel_export_data_structure()
    preview_excel_content()
    
    print("\n" + "=" * 50)
    print("🎯 Ready for Excel Export Testing!")
    print("Run an analysis in the main app to see these improvements in action.")

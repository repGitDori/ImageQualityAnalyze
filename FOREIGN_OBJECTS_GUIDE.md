# Enhanced Foreign Objects Detection System

## Overview

This enhanced foreign objects detection system specifically identifies and flags two critical types of foreign objects that interfere with document image quality:

1. **Tools/Clips** - Physical objects holding pages down that create pixelated backgrounds with non-black borders
2. **Black Foreign Objects** - Hands, fingers, or dark objects that penetrate deep into the document area

## Quick Start

### Single Image Analysis
```bash
python simple_foreign_objects.py document.jpg
```

### Batch Analysis
```bash
python simple_foreign_objects.py batch ./images/
```

### With Custom Configuration
```bash
python simple_foreign_objects.py document.jpg --config config_foreign_objects.json
```

## Detection Features

### 🔧 Tool/Clip Detection
- **Pixelated Background Analysis** - Detects interference patterns around clips
- **Non-Black Border Detection** - Identifies metallic/colored surfaces of tools
- **Edge Proximity Check** - Focuses on typical clip locations near image edges
- **Aspect Ratio Filtering** - Distinguishes clips from text/content

### ⚫ Black Object Detection  
- **Document Penetration Analysis** - Measures how deep objects go into document area
- **Contrast Ratio Calculation** - Distinguishes foreign objects from text/content
- **Shadow Detection** - Identifies shadows cast by hands/objects
- **Object Classification** - Categorizes detected objects (round, linear, large, small)

### 🌑 Shadow & Reflection Analysis
- **LAB Color Space Analysis** - Better shadow detection using luminance channel
- **Statistical Threshold Detection** - Dynamic shadow/reflection thresholds
- **Document Area Focus** - Concentrates on shadows within document boundaries

## Configuration Options

Edit `config_foreign_objects.json` to customize detection sensitivity:

```json
{
  "foreign_objects": {
    "clip_detection": {
      "min_contour_area": 1000,          // Minimum size for clip detection
      "max_border_luminance": 0.15,      // Black border threshold  
      "pixelation_threshold": 0.3,       // Background pixelation indicator
      "failure_threshold": 2.0           // % coverage to fail image
    },
    "black_object_detection": {
      "min_darkness_threshold": 0.1,     // Maximum luminance for "black"
      "min_object_area": 500,             // Minimum size for detection
      "document_penetration": 0.05,      // How deep into document (5%)
      "contrast_ratio": 2.0,              // Contrast with surrounding area
      "failure_threshold": 1.0            // % coverage to fail image
    },
    "failure_thresholds": {
      "combined_area_pct": 3.0            // Total foreign object coverage limit
    }
  }
}
```

## Output Analysis

### Success Example
```
🟢 IMAGE PASSED: No significant foreign objects detected
📊 Coverage: 0.00% of image
```

### Failure Example  
```
🔴 IMAGE FAILED: Foreign objects detected
📊 Coverage: 5.37% of image
🔢 Objects Found: 2

🔴 FAILURE REASONS:
   1. Tools/clips detected covering 2.1% of image  
   2. Black objects penetrating 3.3% of document

💡 RECOMMENDATIONS:
   1. 🔴 CRITICAL: Remove clips, tools, or holders from document area
   2. 👋 Keep hands away from document during capture
   3. 📸 Use timer mode or remote shutter to avoid hand interference
```

## Integration with Existing Workflow

### Method 1: Standalone Analysis
```python
from enhanced_foreign_objects import analyze_document_with_foreign_objects

results = analyze_document_with_foreign_objects("document.jpg")
if results['foreign_object_flag']:
    print("❌ FAILED: Foreign objects detected")
    for reason in results['failure_reasons']:
        print(f"   • {reason}")
```

### Method 2: Integration with ImageQualityAnalyzer  
```python
from foreign_objects_integration import ForeignObjectsIntegration

integration = ForeignObjectsIntegration()
results = integration.analyze_image_comprehensive("document.jpg")

if not results['overall_pass']:
    print("❌ FAILED IMAGE QUALITY:")
    for reason in results['failure_reasons']:
        print(f"   • {reason}")
```

### Method 3: Batch Processing
```python
from foreign_objects_integration import ForeignObjectsIntegration

integration = ForeignObjectsIntegration()
results = integration.batch_analyze_with_foreign_objects([
    "doc1.jpg", "doc2.jpg", "doc3.jpg"
], "batch_results/")

print(f"Failed: {results['failed_foreign_objects']}/{results['total_images']}")
```

## Advanced Usage

### Custom Detection Parameters
```python
from enhanced_foreign_objects import EnhancedForeignObjectsDetector

# Load custom configuration
with open('my_config.json', 'r') as f:
    config = json.load(f)

detector = EnhancedForeignObjectsDetector(config)

# Create document mask (normally from document detection)
image = cv2.imread("document.jpg")
doc_mask = create_document_mask(image)  # Your document detection

# Analyze foreign objects
results = detector.analyze_foreign_objects(image, doc_mask)
```

### Excel Report Integration
The system generates detailed JSON reports that can be integrated with Excel reporting:

```python
# The JSON output contains structured data perfect for Excel:
{
  "foreign_object_flag": true,
  "foreign_object_area_pct": 5.37,
  "failure_reasons": [...],
  "recommendations": [...],
  "detailed_results": {
    "clips_and_tools": {...},
    "black_objects": {...},
    "shadows_reflections": {...}
  }
}
```

## File Structure

```
ImageQualityAnalyze/
├── enhanced_foreign_objects.py          # Core detection system
├── config_foreign_objects.json          # Configuration file
├── simple_foreign_objects.py            # Simple CLI interface  
├── test_enhanced_foreign_objects.py     # Test suite
├── foreign_objects_integration.py       # Integration with main analyzer
└── FOREIGN_OBJECTS_GUIDE.md            # This guide
```

## Troubleshooting

### Common Issues

1. **High False Positive Rate**
   - Adjust `min_contour_area` and `min_object_area` to larger values
   - Increase `failure_threshold` percentages
   - Fine-tune `contrast_ratio` for better text discrimination

2. **Missing Detections**
   - Lower `min_darkness_threshold` to catch lighter objects
   - Reduce `document_penetration` threshold
   - Decrease `pixelation_threshold` for clip detection

3. **JSON Serialization Errors**
   - The system includes automatic numpy array conversion
   - All results are JSON-serializable by default

### Performance Tips

- **Batch Processing**: Use batch mode for multiple images to amortize initialization costs
- **Custom Configuration**: Create task-specific configs for different document types
- **Document Masks**: Provide accurate document masks for better detection accuracy

## Examples

### Example 1: Detect Person's Hand Over Document
```bash
python simple_foreign_objects.py hand_over_document.jpg
```
Output: Detects black objects penetrating document area with shadow analysis

### Example 2: Detect Paper Clips
```bash  
python simple_foreign_objects.py clipped_document.jpg
```
Output: Identifies metallic clips with pixelated background interference

### Example 3: Batch Process Scanned Documents
```bash
python simple_foreign_objects.py batch ./scanned_docs/ --output ./quality_results/
```
Output: Processes all images with comprehensive batch reporting

## Quality Impact Assessment

The system provides automatic quality impact assessment:

- **LOW**: < 2% coverage - Minor impact on quality
- **MODERATE**: 2-5% coverage - Some quality loss  
- **HIGH**: 5-10% coverage - Significant quality degradation
- **SEVERE**: > 10% coverage - Document unusable

## Integration Notes

This enhanced foreign objects detection system:
- ✅ Works standalone or integrates with existing ImageQualityAnalyzer
- ✅ Provides specific "out of focus" style flagging for foreign objects  
- ✅ Generates detailed failure reasons and recommendations
- ✅ Supports batch processing with comprehensive reporting
- ✅ Uses configurable thresholds for different sensitivity levels
- ✅ Exports results to JSON for Excel integration

The system is specifically designed to address your request for flagging images with foreign objects and providing detailed reasons for failure, similar to the "out of focus" detection you requested.

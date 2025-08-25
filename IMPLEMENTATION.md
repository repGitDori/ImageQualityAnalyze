# ImageQualityAnalyze - Implementation Guide

## 🎯 Project Overview

This implementation provides a comprehensive image quality analysis system for document photos and scans, following the detailed specification provided. The system includes:

- **Objective Metrics Computation**: 11 categories of quality metrics
- **Visual Analysis Tools**: Interactive graphs and heatmaps  
- **Configurable Parameters**: JSON-based configuration system
- **Scoring System**: 4-star quality rating with pass/warn/fail flags
- **Export Capabilities**: JSON reports, CSV batch comparison
- **CLI Interface**: Command-line tools for easy usage

## 🏗️ Architecture

### Core Components

```
image_quality_analyzer/
├── __init__.py          # Package initialization
├── analyzer.py          # Main ImageQualityAnalyzer class
├── config.py            # Configuration management
├── scoring.py           # Quality scoring and flagging
├── visualization.py     # Graph and visualization generation
└── metrics/             # Individual metrics modules
    ├── __init__.py
    ├── base.py          # Base metrics class
    ├── completeness.py  # Document completeness
    ├── sharpness.py     # Focus and sharpness
    ├── exposure.py      # Brightness and illumination
    ├── contrast.py      # Image contrast
    ├── geometry.py      # Skew and rotation
    ├── color.py         # Color accuracy and hue cast
    ├── noise.py         # Noise analysis
    ├── border_background.py  # Border and background control
    ├── foreign_objects.py    # Foreign object detection
    ├── format_integrity.py   # File format analysis
    └── resolution.py    # Resolution and DPI analysis
```

## 📊 Implemented Metrics

### 1. Completeness of Capture ✅
- **Primary**: Content bbox coverage ratio
- **Secondary**: Edge touch detection, margin analysis
- **Algorithm**: Otsu thresholding → largest contour → bounding box analysis

### 2. Sharpness/Focus ✅
- **Primary**: Laplacian variance on document area
- **Secondary**: Gradient magnitude, edge density, frequency analysis
- **Algorithm**: Sobel gradients → Laplacian filter → variance computation

### 3. Exposure & Illumination ✅
- **Primary**: Shadow/highlight clipping percentages
- **Secondary**: Illumination uniformity via tile-based analysis
- **Algorithm**: Luminance histogram → percentile analysis → local uniformity

### 4. Contrast ✅
- **Primary**: Global contrast (P95 - P5)
- **Secondary**: RMS contrast, local contrast variation
- **Algorithm**: Luminance percentiles → contrast computation

### 5. Geometry (Skew/Rotation) ✅
- **Primary**: Skew angle via Hough line detection
- **Secondary**: Line angle variation, warp estimation
- **Algorithm**: Canny edges → Hough lines → median angle

### 6. Border & Background Control ✅
- **Primary**: Margin ratios, background luminance
- **Secondary**: Background uniformity
- **Algorithm**: Document bbox → margin computation → background sampling

### 7. Noise Analysis ✅
- **Primary**: Background noise standard deviation
- **Secondary**: JPEG blockiness detection
- **Algorithm**: Gaussian smoothing → noise estimation → blockiness analysis

### 8. Color/Hue Cast ✅
- **Primary**: Hue cast estimation from paper background
- **Secondary**: Gray chart analysis (when available)
- **Algorithm**: LAB color space → chrominance analysis → hue angle

### 9. Foreign Objects ✅
- **Primary**: Foreign object detection flag
- **Secondary**: Object area percentage
- **Algorithm**: Background contour analysis → size thresholding

### 10. Format Integrity ✅
- **Primary**: Format validation, bit depth check
- **Secondary**: JPEG quality analysis
- **Algorithm**: Metadata extraction → validation against allowed formats

### 11. Resolution ✅
- **Primary**: Effective DPI extraction
- **Secondary**: Pixel dimensions, megapixel count
- **Algorithm**: EXIF/metadata parsing → DPI validation

## 🎨 Visualization System

### Graph Types Implemented

1. **Luminance Histograms** 📊
   - Regular and cumulative histograms
   - Clipping zone visualization
   - P5/P95 markers

2. **Illumination Heatmap** 🗺️
   - Tile-based illumination mapping
   - Hot/cold spot identification
   - Uniformity ratio display

3. **Sharpness Heatmap** 🎯
   - Local sharpness visualization
   - Laplacian variance mapping
   - Focus quality distribution

4. **Margin Bar Chart** 📏
   - Four-bar display (left/right/top/bottom)
   - Threshold line overlays
   - Color-coded pass/warn/fail

5. **Skew Dial** 🧭
   - Polar coordinate display
   - Color-coded angle zones
   - Current skew indicator

6. **Document Overlay** 🎭
   - Original image with mask overlay
   - Bounding box visualization
   - Detection quality check

## ⚙️ Configuration System

### Default Profile: "Document-Black-Background-Strict"
```json
{
  "resolution": {"min_dpi_text": 300, "min_dpi_archival": 400},
  "sharpness": {"min_laplacian_variance": 150.0, "warn_laplacian_variance": 120.0},
  "geometry": {"max_skew_deg_pass": 1.0, "max_skew_deg_warn": 3.0},
  "border_background": {
    "max_side_margin_ratio_pass": 0.10,
    "max_side_margin_ratio_warn": 0.12,
    "max_bg_median_luminance": 0.10
  }
}
```

### Additional Profiles
- **Document-Lenient**: More forgiving thresholds for legacy documents
- **Archival-Quality**: High standards for preservation (400+ DPI, 16-bit)

## 🏆 Scoring System

### Tri-State Flagging
- **PASS**: Metric within acceptable thresholds
- **WARN**: Metric in caution zone (needs attention)
- **FAIL**: Metric exceeds failure thresholds

### Star Rating (1-4 ★)
- **4 Stars**: Score ≥ 90% (Excellent)
- **3 Stars**: Score ≥ 80% (Good)  
- **2 Stars**: Score ≥ 65% (Acceptable)
- **1 Star**: Score < 65% (Poor)

### Critical Failures
Categories that trigger immediate failure:
- Completeness (document incomplete)
- Border/Background (requirements not met)
- Resolution (below minimum DPI)
- Geometry (extreme skew)

## 📁 Export Formats

### JSON Report Schema
```json
{
  "image_id": "document_001",
  "file_path": "/path/to/image.jpg",
  "pixels": {"w": 3000, "h": 4000},
  "dpi": {"x": 300, "y": 300},
  "metrics": {
    "sharpness": {"laplacian_var": 185.3},
    "contrast": {"global_contrast": 0.27},
    // ... all metric categories
  },
  "category_status": {
    "sharpness": "pass",
    "contrast": "pass"
    // ... all categories
  },
  "global": {
    "score": 0.93,
    "stars": 4,
    "status": "pass",
    "actions": []
  }
}
```

### CSV Batch Comparison
Columns as specified: `image_id,file_path,px_w,px_h,dpi_x,dpi_y,lap_var,global_contrast,skew_deg,bg_median_lum,left_ratio,right_ratio,top_ratio,bottom_ratio,noise_std,illum_uniformity,gray_deltaE,hue_cast_deg,format,bit_depth,score,stars,status`

## 🖥️ Usage Examples

### Single Image Analysis
```python
from image_quality_analyzer import ImageQualityAnalyzer, load_default_config

# Initialize with default config
analyzer = ImageQualityAnalyzer(load_default_config())

# Analyze image
result = analyzer.analyze_image("document.jpg")
print(f"Score: {result['global']['score']:.2f}")
print(f"Stars: {'★' * result['global']['stars']}")

# Export results
analyzer.export_json_report(result, "report.json")
```

### Batch Processing
```python
# Analyze multiple images
image_paths = ["doc1.jpg", "doc2.jpg", "doc3.jpg"]
results = analyzer.analyze_batch(image_paths)

# Export CSV comparison
analyzer.export_csv_comparison(results, "batch_comparison.csv")
```

### Command Line Interface
```bash
# Analyze single image with visualizations
python cli.py analyze document.jpg --output results/

# Batch analysis
python cli.py batch ./documents/ --csv --output batch_results/

# List available profiles
python cli.py profiles

# Export configuration
python cli.py export-config archival_quality config.json
```

## 🛠️ Installation & Setup

### Dependencies
```
numpy>=1.21.0
opencv-python>=4.5.0
Pillow>=8.3.0
matplotlib>=3.5.0
seaborn>=0.11.0
scipy>=1.7.0
scikit-image>=0.19.0
pandas>=1.3.0
click>=8.0.0
jsonschema>=4.0.0
```

### Installation
```bash
# Clone repository
git clone <repository-url>
cd ImageQualityAnalyze

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

## 🔧 Customization Options

### Custom Thresholds
```python
from image_quality_analyzer.config import load_default_config

config = load_default_config()

# Adjust sharpness requirements
config['sharpness']['min_laplacian_variance'] = 200.0

# Stricter geometry tolerances
config['geometry']['max_skew_deg_pass'] = 0.5

analyzer = ImageQualityAnalyzer(config)
```

### Adding Custom Metrics
```python
from image_quality_analyzer.metrics.base import BaseMetrics

class CustomMetrics(BaseMetrics):
    def compute(self, image, doc_mask, config, metadata=None):
        # Your custom analysis here
        return {'custom_metric': value}

# Register with analyzer
analyzer.metrics_computers['custom'] = CustomMetrics()
```

## 🎯 Performance Considerations

### Optimization Strategies
1. **Tile Size Tuning**: Adjust tile sizes for local analysis based on image resolution
2. **Mask Caching**: Document mask reused across multiple metrics
3. **Selective Computation**: Skip expensive metrics when not needed
4. **Batch Processing**: Parallel processing for multiple images

### Memory Usage
- Typical memory usage: 50-200MB per image (depending on resolution)
- Peak usage during visualization generation
- Automatic cleanup of intermediate arrays

## 📈 Validation & Testing

### Test Coverage
- Unit tests for all metric components
- Integration tests for complete analysis pipeline
- Configuration validation tests
- Error handling verification

### Accuracy Validation
- Metrics validated against known reference images
- Cross-validation with manual quality assessments
- Threshold tuning based on real-world data

## 🔮 Future Enhancements

### Potential Improvements
1. **Machine Learning Integration**: CNN-based quality assessment
2. **OCR Integration**: Text readability scoring
3. **Advanced Color Analysis**: ICC profile support
4. **Real-time Analysis**: Video stream processing
5. **Web Interface**: Browser-based quality checker
6. **API Server**: RESTful quality analysis service

### Plugin Architecture
Framework designed for easy extension with custom metrics and analyzers.

## 📞 Support & Contributing

This implementation follows the open specification and can be freely modified. The modular architecture allows for easy customization and extension.

Key design principles:
- ✅ **Modular**: Each metric is independent
- ✅ **Configurable**: All parameters user-adjustable  
- ✅ **Extensible**: Easy to add new metrics
- ✅ **Testable**: Comprehensive test coverage
- ✅ **Production-Ready**: Error handling and validation

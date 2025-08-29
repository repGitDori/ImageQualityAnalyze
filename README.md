# ImageQualityAnalyze

An advanced image quality checker for document photos and scans that provides:
- Objective metrics computation
- Interactive graphs for human review
- User-configurable parameters
- Pass/Warn/Fail flagging system
- Export capabilities for batch comparison

## Features

- **Comprehensive Metrics**: Resolution, sharpness, exposure, contrast, geometry, noise, color accuracy
- **Visual Analysis**: Histograms, heatmaps, margin charts, skew dials, and more
- **Configurable Thresholds**: JSON-based parameter system with sensible defaults
- **Scoring System**: 4-star quality rating with category-based evaluation
- **Export Options**: JSON reports, CSV batch comparison, visualization graphs

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### GUI Interfaces (Recommended)

**Main Interface:** `desktop_analyzer.py` - Complete professional interface
```bash
python desktop_analyzer.py
# OR double-click: launch_analyzer.bat
```

**Alternative Interfaces:** Located in `Extra/` folder
- **Tabbed:** `python Extra/tabbed_analyzer.py` (clean 3-tab workflow)
- **Wizard:** `python Extra/wizard_analyzer.py` (step-by-step guidance)

### Programmatic Usage

```python
from image_quality_analyzer import ImageQualityAnalyzer, load_default_config

# Load default configuration
config = load_default_config()

# Initialize analyzer
analyzer = ImageQualityAnalyzer(config)

# Analyze an image
result = analyzer.analyze_image("path/to/document.jpg")

# Generate visualizations
analyzer.generate_graphs(result, output_dir="graphs/")

# Export report
analyzer.export_json_report(result, "report.json")
```

## Configuration

The system uses JSON-based configuration for all parameters:

```json
{
  "resolution": {
    "min_dpi_text": 300,
    "min_dpi_archival": 400
  },
  "exposure": {
    "max_shadow_clip_pct": 0.5,
    "max_highlight_clip_pct": 0.5,
    "illumination_uniformity_warn": 0.15,
    "illumination_uniformity_fail": 0.25
  },
  // ... more parameters
}
```

## Usage Examples

### Single Image Analysis
```python
result = analyzer.analyze_image("document.jpg")
print(f"Overall score: {result['global']['score']:.2f}")
print(f"Stars: {'★' * result['global']['stars']}{'☆' * (4 - result['global']['stars'])}")
```

### Batch Processing
```python
results = analyzer.analyze_batch(["img1.jpg", "img2.jpg", "img3.jpg"])
analyzer.export_csv_comparison(results, "batch_report.csv")
```

## License

Free to use and modify. Based on general imaging science principles and open guidelines.

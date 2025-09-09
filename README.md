# ImageQualityAnalyze

**Author:** Dorian Lapi  
**License:** Dual License (Non-commercial: MIT, Commercial: Proprietary)  
**Copyright:** © 2025 Dorian Lapi

⚠️ **IMPORTANT: DUAL LICENSE SYSTEM** ⚠️

**🆓 FREE for:** Personal, Educational, Research, Non-profit use  
**💼 COMMERCIAL LICENSE REQUIRED for:** Business, Enterprise, Revenue-generating use

📧 **Commercial Licensing:** [databasemaestro@gmail.com](mailto:databasemaestro@gmail.com)

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

## 🤝 Contributing

**Contributions are welcome!** I'd love your help to make ImageQualityAnalyzer even better.

### 🎯 **How to Contribute:**
- 🐛 **Report bugs** or suggest features
- 💻 **Submit code** improvements and new features  
- 📚 **Improve documentation** and examples
- 🧪 **Add test cases** and edge case handling
- 🌟 **Share your use cases** and success stories

### 📞 **Get in Touch:**
- **Email**: [databasemaestro@gmail.com](mailto:databasemaestro@gmail.com)
- **Subject**: "ImageQualityAnalyzer Contribution - [Your Topic]"

### 📋 **Contribution Guide:**
See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Setting up the development environment
- Code style and testing requirements
- Attribution requirements for contributions
- Areas looking for contributors

**Your ideas and contributions help make document image analysis better for everyone!** 🚀

## License

**DUAL LICENSE SYSTEM - Copyright © 2025 Dorian Lapi**

### 🆓 **Non-Commercial Use (MIT License)**
Free for personal, educational, research, and non-profit use.

### 💼 **Commercial Use (Proprietary License Required)**
🚨 **COMMERCIAL LICENSE REQUIRED for:**
- Business or enterprise use
- Commercial products or services  
- Organizations with revenue > $10,000/year
- Corporate environments
- Resale or redistribution for profit

📧 **Get Commercial License:** [databasemaestro@gmail.com](mailto:databasemaestro@gmail.com)

### ⚖️ **Legal Protection**
- ✅ Dual licensing protects against unauthorized commercial use
- ✅ Strong anti-theft and anti-scam provisions
- ✅ Digital tracking and audit capabilities
- ✅ Legal enforcement for violations

### 🛡️ **No Warranties**
Software provided "AS IS" without warranties or promises:
- No guarantee of performance or results
- No liability for damages or losses
- User assumes all risks
- No warranty of fitness for purpose

See `LICENSE`, `DUAL_LICENSE.txt` for complete terms.

### Attribution Requirements
When using this code, you must:
1. **Include attribution to Dorian Lapi** as the original author
2. **Preserve copyright notice** in all copies
3. **Obtain commercial license** for business use
4. **Comply with dual license terms**

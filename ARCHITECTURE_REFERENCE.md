# Architecture Quick Reference

## 🏗️ System Overview
**Image Quality Analyzer** - Professional document quality analysis system with modular architecture.

## 🎯 Core Principles
- **Modular Design**: Independent, swappable components
- **Plugin Architecture**: Extensible metrics system
- **Configuration-Driven**: JSON-based customizable profiles
- **Multi-Interface**: Desktop GUI, Web UI, CLI support

## 📊 Layer Architecture

### 1. **UI Layer** - User Interfaces
```
┌─ Desktop GUI (Tkinter) ─┬─ Web UI (Vue.js) ─┬─ CLI Tool ─┐
│  • Professional tabs    │  • Browser access │  • Batch   │
│  • Real-time progress   │  • Upload/analyze │  • Script  │
│  • Excel export        │  • Results display │  • CI/CD   │
└─────────────────────────┴───────────────────┴───────────┘
```

### 2. **Application Layer** - Core Engine
```
┌─ ImageQualityAnalyzer ─┬─ Configuration ─┬─ Scoring ─────┐
│  • analyze_image()     │  • Profiles     │  • Weighted   │
│  • run_metrics()       │  • Thresholds   │  • P/W/F      │
│  • compile_results()   │  • Validation   │  • Confidence │
└─────────────────────────┴─────────────────┴──────────────┘
```

### 3. **Metrics Layer** - Analysis Engines
```
┌─ Base Metric Interface ─┬─ 12+ Specialized Metrics ────────┐
│  • analyze()            │  📸 Sharpness  📊 Contrast      │
│  • get_score()          │  💡 Exposure   🔊 Noise         │
│  • get_recommendations()│  📏 Resolution 📐 Geometry      │
└──────────────────────────┴──────────────────────────────────┘
```

### 4. **Visualization Layer** - Reporting
```
┌─ Chart Generator ─┬─ Excel Reports (9 Sheets) ─┬─ JSON/CSV ─┐
│  • Dashboards     │  • Executive Summary       │  • Raw     │
│  • Histograms     │  • Detailed Metrics        │  • Batch   │
│  • Heatmaps       │  • Recommendations         │  • Config  │
└────────────────────┴────────────────────────────┴───────────┘
```

### 5. **Data Layer** - Configuration & Storage
```
┌─ JSON Configs ─┬─ Quality Profiles ─┬─ Results Storage ────┐
│  • Thresholds  │  • Document        │  • Analysis reports  │
│  • Metrics     │  • Photo           │  • Visualization     │
│  • Validation  │  • ID Card         │  • Temp files        │
└────────────────┴────────────────────┴──────────────────────┘
```

## 🔌 Key Components

### Core Classes
```python
# Main Engine
ImageQualityAnalyzer          # Primary analysis orchestrator
QualityScoring               # Scoring and classification system
ConfigurationManager         # Profile and settings management

# Metrics System
BaseMetric                   # Interface for all metrics
SharpnessMetric             # Laplacian, Sobel, FFT analysis
ContrastMetric              # RMS, Michelson contrast
ExposureMetric              # Brightness, histogram analysis
GeometryMetric              # Skew detection, boundaries
# ... 8 more specialized metrics

# Visualization
GraphGenerator              # Chart creation and export
ExcelReporter               # 9-sheet professional reports
VisualizationManager        # Dashboard generation
```

### File Structure
```
image_quality_analyzer/
├── analyzer.py             # 🎯 Main analysis engine
├── config.py               # ⚙️ Configuration management
├── scoring.py              # 📊 Quality scoring system
├── visualization.py        # 📈 Chart generation
└── metrics/                # 📐 Analysis modules
    ├── base.py            #    Interface definition
    ├── sharpness.py       #    Image sharpness
    ├── contrast.py        #    Contrast analysis
    ├── exposure.py        #    Brightness/exposure
    ├── noise.py           #    Noise detection
    ├── resolution.py      #    DPI/resolution check
    ├── geometry.py        #    Skew/geometry
    ├── color.py           #    Color analysis
    ├── border_background.py #  Background detection
    ├── completeness.py    #    Content coverage
    ├── foreign_objects.py #    Unwanted objects
    ├── format_integrity.py#    File validation
    └── utils.py           #    Shared utilities
```

## 🎨 Design Patterns

### 1. **Plugin Architecture**
- Metrics as independent plugins
- Enable/disable per profile
- Easy addition of new metrics

### 2. **Observer Pattern**
- GUI progress tracking
- Event-driven updates
- Decoupled communication

### 3. **Strategy Pattern**
- Algorithm selection by image type
- Profile-based analysis behavior
- Runtime configuration

### 4. **Factory Pattern**
- Dynamic metric instantiation
- Chart type creation
- Export format selection

## 📈 Data Flow
```
Image Input → Validation → Profile Loading → Metric Analysis
     ↓             ↓            ↓              ↓
File Check → Type Check → Config Apply → Parallel Execution
     ↓             ↓            ↓              ↓
Security → Format Check → Threshold Set → Score Calculation
     ↓             ↓            ↓              ↓
Process → Preprocessing → Quality Check → Results Compilation
     ↓             ↓            ↓              ↓
Output → Visualization → Report Export → JSON/Excel/Charts
```

## 🚀 Quick Start API

### Basic Usage
```python
from image_quality_analyzer import ImageQualityAnalyzer, load_default_config

# Initialize
config = load_default_config()
analyzer = ImageQualityAnalyzer(config)

# Analyze
result = analyzer.analyze_image("document.jpg")
score = result['global']['overall_score']
status = result['global']['quality_level']  # pass/warn/fail

# Visualize
analyzer.generate_graphs(result, "output/")
analyzer.export_excel_report(result, "report.xlsx")
```

### Configuration
```python
# Load profile
config = load_config_profile("document")  # or "photo", "id_card"

# Customize thresholds
config['metrics']['sharpness']['threshold'] = 0.8
config['scoring']['weights']['sharpness'] = 0.3

# Apply changes
analyzer.update_config(config)
```

## 📋 Analysis Results Schema
```json
{
  "metadata": {
    "image_path": "string",
    "analysis_timestamp": "ISO datetime",
    "config_profile": "string",
    "processing_time": "seconds"
  },
  "global": {
    "overall_score": 0.85,           // 0.0 - 1.0
    "quality_level": "pass",         // pass|warn|fail
    "confidence": 0.92               // 0.0 - 1.0
  },
  "metrics": {
    "sharpness": {
      "score": 0.87,
      "status": "pass",
      "measurements": { /* raw data */ },
      "recommendations": ["strings"]
    }
    // ... 11 more metrics
  },
  "visualizations": {
    "dashboard_path": "output/dashboard.png",
    "chart_paths": ["histograms.png", "overlay.png"]
  }
}
```

## 📊 Quality Profiles

### Document Profile
- Focus on text clarity, geometry, completeness
- Strict sharpness requirements
- Page boundary detection
- Skew correction validation

### Photo Profile  
- Color accuracy emphasis
- Natural image characteristics
- Artistic blur tolerance
- Exposure latitude

### ID Card Profile
- High resolution requirements
- Face detection ready
- Security features preservation
- Uniform background preference

## 🛠️ Extension Points

### Adding Custom Metrics
```python
class CustomMetric(BaseMetric):
    def analyze(self, image):
        # Your analysis logic
        return measurements
    
    def get_score(self, measurements):
        # Your scoring logic
        return score
    
    def get_recommendations(self, score):
        # Your improvement suggestions
        return recommendations
```

### Custom Export Formats
```python
class CustomExporter:
    def export(self, result, output_path):
        # Your export logic
        pass
```

## 🔧 Configuration Files

### Profile Structure
```json
{
  "name": "document",
  "description": "Document analysis profile",
  "metrics": {
    "sharpness": {
      "enabled": true,
      "threshold": 0.7,
      "algorithm": "laplacian",
      "weight": 0.25
    }
  },
  "scoring": {
    "pass_threshold": 0.8,
    "warn_threshold": 0.6,
    "overall_weights": { /* metric weights */ }
  }
}
```

## 📱 User Interfaces

### Desktop App Features
- ✅ Professional tabbed interface
- ✅ Real-time progress indicators
- ✅ Quality standards editor
- ✅ Batch processing
- ✅ 9-sheet Excel reports
- ✅ Drag & drop support

### Web UI Features  
- ✅ Browser-based access
- ✅ Upload interface
- ✅ Interactive results
- ✅ Mobile responsive
- ✅ Share/download results

### CLI Features
- ✅ Batch processing
- ✅ Scriptable automation
- ✅ CI/CD integration
- ✅ Configuration management
- ✅ Output format selection

## 🚀 Performance Features

### Optimization
- **Lazy Loading**: Metrics loaded on demand
- **Caching**: Intermediate results cached
- **Parallel Processing**: Multi-threaded metrics
- **Memory Management**: Efficient large file handling
- **Progressive Enhancement**: Basic → detailed analysis

### Scalability
- **Batch Processing**: Multi-image handling
- **Resource Pooling**: Shared computation resources
- **Configurable Depth**: Adjustable analysis detail
- **Error Isolation**: Individual metric failures handled

## 🔒 Security Features

### Input Validation
- File type checking
- Size limits
- Path sanitization
- Memory protection

### Data Protection
- Local processing only
- Automatic temp cleanup
- Configuration validation
- Sanitized error messages

---

## 📚 Related Documents
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture
- **[README.md](README.md)** - Project overview and setup
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Implementation details

## 🎯 Quick Commands

```bash
# Setup
pip install -r requirements.txt

# Desktop App
python desktop_analyzer.py

# CLI Analysis
python cli.py --input image.jpg --profile document

# Web UI
cd web_ui && npm run dev

# Tests
python -m pytest tests/
```

---
*Architecture Reference - Image Quality Analyzer v2.0*

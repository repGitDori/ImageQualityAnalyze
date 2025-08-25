# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies

```powershell
# Navigate to project directory
cd C:\Users\Lapi\Documents\ImageQualityAnalyze

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Test with Sample Image

```powershell
# Create a test image (or use your own document photo)
python -c "
import cv2
import numpy as np

# Create a simple test document
img = np.full((800, 600, 3), 240, dtype=np.uint8)
cv2.rectangle(img, (50, 100), (550, 120), (50, 50, 50), -1)
cv2.rectangle(img, (50, 150), (450, 170), (50, 50, 50), -1) 
cv2.rectangle(img, (50, 200), (500, 220), (50, 50, 50), -1)
cv2.imwrite('test_document.jpg', img)
print('Created test_document.jpg')
"
```

### 3. Run Analysis

```powershell
# Analyze single image with CLI
python cli.py analyze test_document.jpg --output results --verbose

# Or use Python directly
python -c "
from image_quality_analyzer import ImageQualityAnalyzer
analyzer = ImageQualityAnalyzer()
result = analyzer.analyze_image('test_document.jpg')
print(f'Score: {result[\"global\"][\"score\"]:.2f}')
print(f'Stars: {\"★\" * result[\"global\"][\"stars\"]}')
"
```

### 4. View Results

```powershell
# Check generated files
dir results\
dir results\graphs\

# View JSON report
type results\test_document_report.json
```

## 🎯 Example Output

```
🔍 Analysis Results for test_document
📊 Overall Score: 0.85
⭐ Star Rating: ★★★☆ (3/4)
✅ Status: PASS

📋 Category Status:
  ✅ Completeness: PASS
  ✅ Foreign Objects: PASS
  ✅ Sharpness: PASS
  ✅ Exposure: PASS
  ✅ Contrast: PASS
  ⚠️ Geometry: WARN
  ✅ Border Background: PASS
  ✅ Noise: PASS
  ✅ Color: PASS
  ✅ Format Integrity: PASS
  ✅ Resolution: PASS

💡 Recommended Actions:
  ⚠️ Straighten document or adjust camera angle

📁 Report saved to: results\test_document_report.json
```

## 📁 Generated Files

- `results/test_document_report.json` - Complete analysis report
- `results/test_document_dashboard.png` - Visual summary
- `results/graphs/test_document_histograms.png` - Luminance analysis
- `results/graphs/test_document_illumination.png` - Illumination heatmap
- `results/graphs/test_document_sharpness.png` - Sharpness map
- `results/graphs/test_document_margins.png` - Margin analysis
- `results/graphs/test_document_skew_dial.png` - Skew visualization
- `results/graphs/test_document_overlay.png` - Document detection

## 🔧 Common Commands

```powershell
# List available configuration profiles
python cli.py profiles

# Use lenient profile for older documents  
python cli.py analyze old_document.jpg --profile document_lenient

# Batch process a folder
python cli.py batch documents_folder/ --output batch_results/

# Export configuration for customization
python cli.py export-config default my_config.json

# Analyze with custom config
python cli.py analyze document.jpg --config my_config.json
```

## 🛠️ Troubleshooting

### Common Issues

**"Could not load image"**
- Check image file exists and is readable
- Supported formats: JPG, PNG, TIFF
- Try with absolute path

**"Import errors"**
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

**Poor quality scores**
- Use `--verbose` flag to see detailed analysis
- Check individual category status
- Adjust lighting/focus and retake photo
- Try `document_lenient` profile

## 📚 Next Steps

1. **Read the main README.md** for detailed documentation
2. **Check examples/basic_usage.py** for Python API examples  
3. **Review IMPLEMENTATION.md** for technical details
4. **Customize configurations** in `configs/` directory
5. **Run tests** with `python -m pytest tests/`

## 💡 Pro Tips

- Use good lighting and avoid shadows
- Keep document flat and straight
- Ensure black/dark background
- Maintain adequate margins around document
- Use tripod or stable surface for sharpness
- Check DPI requirements for your use case

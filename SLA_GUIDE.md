# 🎯 SLA (Service Level Agreement) Functionality Guide

## Overview

The Image Quality Analyzer now includes comprehensive SLA (Service Level Agreement) functionality that allows you to:

- Define quality standards and requirements for your document processing workflow
- Compare analysis results against predefined service level agreements
- Generate compliance reports showing whether images meet your quality standards
- Track compliance rates across batch processing operations
- Receive targeted recommendations for meeting SLA requirements

## 📋 What is SLA in Image Quality Analysis?

An SLA (Service Level Agreement) in this context defines the minimum acceptable quality standards for processed documents. It includes:

1. **Minimum Overall Score**: The lowest acceptable quality score (e.g., 75%)
2. **Category Requirements**: Which quality categories must pass (e.g., sharpness, resolution)
3. **Failure Limits**: Maximum number of categories allowed to fail (e.g., max 1 failure)
4. **Performance Targets**: Specific metric thresholds (e.g., minimum 300 DPI resolution)

## 🚀 Getting Started

### Enable SLA Evaluation

SLA evaluation is controlled by the configuration file. By default, it's enabled with reasonable standards:

```json
{
  "sla": {
    "enabled": true,
    "name": "Default Document Quality SLA",
    "description": "Standard quality requirements for document processing"
  }
}
```

### Using SLA with CLI

Analyze a single image with SLA information:
```bash
python cli.py analyze document.jpg --verbose
```

Batch analysis with SLA summary:
```bash
python cli.py batch my_documents/ --verbose
```

Use custom SLA configuration:
```bash
python cli.py analyze document.jpg --config my_sla_config.json --verbose
```

## ⚙️ SLA Configuration

### Basic SLA Settings

```json
{
  "sla": {
    "enabled": true,
    "name": "My Quality SLA",
    "description": "Custom quality requirements",
    "requirements": {
      "min_overall_score": 0.75,
      "max_fail_categories": 1,
      "required_pass_categories": ["completeness", "sharpness", "resolution"]
    }
  }
}
```

### Advanced Performance Targets

```json
{
  "sla": {
    "requirements": {
      "performance_targets": {
        "sharpness_min_laplacian": 150.0,
        "contrast_min_global": 0.20,
        "resolution_min_dpi": 300,
        "noise_max_std": 0.04,
        "geometry_max_skew": 1.0,
        "exposure_max_highlight_clip": 0.5,
        "exposure_max_shadow_clip": 0.5
      }
    }
  }
}
```

### Compliance Levels

```json
{
  "sla": {
    "compliance_levels": {
      "excellent": {"min_score": 0.90, "description": "Exceeds requirements"},
      "compliant": {"min_score": 0.75, "description": "Meets requirements"},
      "warning": {"min_score": 0.60, "description": "Below SLA but usable"},
      "non_compliant": {"min_score": 0.0, "description": "Does not meet SLA"}
    }
  }
}
```

## 📊 SLA Report Outputs

### CLI Output
```
🎯 SLA Compliance:
  ✅ Level: COMPLIANT
  📋 SLA: High-Quality Document Processing SLA
  🎯 Compliant: YES
  📊 Score Requirement: 80.0% (Actual: 85.3%)
  💡 SLA Recommendations:
    ✅ SLA COMPLIANT: All requirements met
```

### JSON Reports
```json
{
  "sla": {
    "enabled": true,
    "sla_name": "Document Quality SLA",
    "compliance": {
      "level": "compliant",
      "overall_compliant": true,
      "requirements_met": {
        "minimum_score": {
          "required": 0.75,
          "actual": 0.853,
          "compliant": true
        },
        "category_failures": {
          "max_allowed": 1,
          "actual": 0,
          "compliant": true
        }
      }
    },
    "recommendations": ["✅ SLA COMPLIANT: All requirements met"]
  }
}
```

### Excel Reports

The Excel export now includes a dedicated "SLA Compliance" sheet showing:
- File-by-file compliance status
- Compliance level (Excellent/Compliant/Warning/Non-compliant)
- Specific requirement comparisons
- SLA recommendations
- Batch compliance summary statistics

### CSV Exports

CSV files now include SLA columns:
- `sla_enabled`: Whether SLA evaluation was performed
- `sla_compliance_level`: Compliance level (excellent/compliant/warning/non_compliant)
- `sla_overall_compliant`: Overall compliance (True/False)
- `sla_score_compliant`: Score requirement met (True/False)
- `sla_category_compliant`: Category requirements met (True/False)
- `sla_performance_compliant`: Performance targets met (True/False)

## 🔧 Configuration Examples

### Strict Archival Quality SLA
```json
{
  "sla": {
    "enabled": true,
    "name": "Archival Quality SLA",
    "requirements": {
      "min_overall_score": 0.90,
      "max_fail_categories": 0,
      "required_pass_categories": ["completeness", "sharpness", "resolution", "contrast"],
      "performance_targets": {
        "sharpness_min_laplacian": 300.0,
        "resolution_min_dpi": 400,
        "contrast_min_global": 0.30
      }
    }
  }
}
```

### Relaxed General Use SLA
```json
{
  "sla": {
    "enabled": true,
    "name": "General Use SLA",
    "requirements": {
      "min_overall_score": 0.60,
      "max_fail_categories": 3,
      "required_pass_categories": ["completeness"],
      "performance_targets": {
        "sharpness_min_laplacian": 100.0,
        "resolution_min_dpi": 150
      }
    }
  }
}
```

## 📈 Batch SLA Summary

When processing multiple images, you'll see batch SLA statistics:

```
🎯 SLA Compliance Summary:
SLA: Document Quality SLA
Overall Compliance Rate: 75.0%
Compliance Breakdown:
  ✅ Excellent: 12
  ✅ Compliant: 8
  ⚠️ Warning: 5
  ❌ Non-compliant: 3
```

## 🎯 SLA Use Cases

### Document Digitization Projects
- Set minimum DPI requirements
- Ensure completeness and sharpness standards
- Track compliance rates across scanning batches

### Quality Control Workflows
- Define acceptance criteria for processed documents
- Automatically flag documents that don't meet standards
- Generate compliance reports for auditing

### Processing Pipeline Integration
- Use SLA status to route documents for different processing paths
- Reject or flag non-compliant documents for manual review
- Monitor quality trends over time

### Vendor Management
- Define quality standards for outsourced scanning services
- Track vendor performance against SLA requirements
- Generate compliance reports for contract management

## ⚡ Quick Start Examples

### Basic Usage
```bash
# Analyze with default SLA
python cli.py analyze document.jpg --verbose

# Batch analysis with SLA summary
python cli.py batch documents/ --verbose --csv
```

### Custom SLA
```bash
# Use strict archival SLA
python cli.py analyze document.jpg --config config_strict_sla.json

# Use relaxed general SLA  
python cli.py analyze document.jpg --config config_relaxed_sla.json
```

### Desktop Application
The desktop analyzer automatically includes SLA information in Excel reports when SLA is enabled in the configuration.

## 📋 SLA Requirements Reference

| Requirement | Description | Example |
|------------|-------------|---------|
| `min_overall_score` | Minimum quality score (0.0-1.0) | 0.75 = 75% |
| `max_fail_categories` | Max categories that can fail | 1 = only 1 failure allowed |
| `required_pass_categories` | Categories that must pass | ["sharpness", "resolution"] |
| `sharpness_min_laplacian` | Minimum sharpness metric | 150.0 |
| `contrast_min_global` | Minimum contrast metric | 0.20 |
| `resolution_min_dpi` | Minimum resolution in DPI | 300 |
| `noise_max_std` | Maximum noise standard deviation | 0.04 |
| `geometry_max_skew` | Maximum document skew degrees | 1.0 |
| `exposure_max_highlight_clip` | Max highlight clipping % | 0.5 |
| `exposure_max_shadow_clip` | Max shadow clipping % | 0.5 |

## 🔍 Troubleshooting

### SLA Not Showing
- Check that `"enabled": true` in your config
- Verify SLA configuration syntax is correct
- Use `--verbose` flag to see SLA output

### All Documents Non-Compliant
- Review your SLA requirements - they may be too strict
- Check performance targets against your actual image quality
- Consider using a more relaxed SLA configuration

### Missing SLA Columns in CSV
- Ensure SLA is enabled in configuration
- Re-run analysis with updated config
- Check that you're using the latest version

---

The SLA functionality provides a powerful way to ensure consistent quality standards across your document processing workflows. By defining clear requirements and tracking compliance, you can maintain high-quality results and identify areas for improvement in your imaging processes.

"""
Configuration management for ImageQualityAnalyzer
Handles loading, validation, and default parameter sets
"""

import json
import os
from typing import Dict, Any
from jsonschema import validate, ValidationError


# Default configuration as specified in the spec
DEFAULT_CONFIG = {
    "resolution": {
        "min_dpi_text": 300,
        "min_dpi_archival": 400
    },
    "exposure": {
        "max_shadow_clip_pct": 0.5,
        "max_highlight_clip_pct": 0.5,
        "target_bg_median_lum": 0.10,
        "illumination_uniformity_warn": 0.15,
        "illumination_uniformity_fail": 0.25
    },
    "contrast": {
        "min_global_contrast": 0.20,
        "warn_global_contrast": 0.15
    },
    "sharpness": {
        "min_laplacian_variance": 150.0,
        "warn_laplacian_variance": 120.0
    },
    "noise": {
        "max_bg_noise_std": 0.04,
        "warn_bg_noise_std": 0.06
    },
    "geometry": {
        "max_skew_deg_pass": 1.0,
        "max_skew_deg_warn": 3.0
    },
    "border_background": {
        "require_black_background": True,
        "max_side_margin_ratio_pass": 0.10,
        "max_side_margin_ratio_warn": 0.12,
        "max_bg_median_luminance": 0.10
    },
    "color": {
        "enable_color_checks": True,
        "max_gray_deltaE_pass": 5.0,
        "max_gray_deltaE_warn": 8.0,
        "max_hue_cast_degrees_warn": 6.0
    },
    "format_integrity": {
        "allowed_formats": ["tiff", "png", "jpeg"],
        "jpeg_quality_warn": 0.85,
        "bit_depth_min": 8
    },
    "completeness": {
        "min_margin_px": 8,
        "min_content_bbox_coverage": 0.90
    },
    "document_shadow": {
        "shadow_threshold": 25,
        "analysis_band_width": 50,
        "min_contour_area": 10000,
        "gaussian_blur_kernel": 3,
        "canny_low": 50,
        "canny_high": 150,
        "warn_shadow_intensity": 20,
        "fail_shadow_intensity": 40
    },
    "scoring": {
        "four_star_weight": 1.0,
        "three_star_weight": 1.0,
        "two_star_weight": 1.0,
        "pass_score_threshold": 0.80,
        "warn_score_threshold": 0.65
    },
    "sla": {
        "enabled": True,
        "name": "Default Document Quality SLA",
        "description": "Standard quality requirements for document processing",
        "requirements": {
            "min_overall_score": 0.75,
            "max_fail_categories": 1,
            "required_pass_categories": ["completeness", "sharpness", "resolution"],
            "performance_targets": {
                "sharpness_min_laplacian": 150.0,
                "contrast_min_global": 0.20,
                "resolution_min_dpi": 300,
                "noise_max_std": 0.04,
                "geometry_max_skew": 1.0,
                "exposure_max_highlight_clip": 0.5,
                "exposure_max_shadow_clip": 0.5
            }
        },
        "compliance_levels": {
            "excellent": {"min_score": 0.90, "description": "Exceeds all SLA requirements"},
            "compliant": {"min_score": 0.75, "description": "Meets all SLA requirements"},
            "warning": {"min_score": 0.60, "description": "Below SLA but usable"},
            "non_compliant": {"min_score": 0.0, "description": "Does not meet SLA requirements"}
        }
    }
}

# JSON Schema for configuration validation
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "resolution": {
            "type": "object",
            "properties": {
                "min_dpi_text": {"type": "number"},
                "min_dpi_archival": {"type": "number"}
            },
            "required": ["min_dpi_text"]
        },
        "exposure": {
            "type": "object",
            "properties": {
                "max_shadow_clip_pct": {"type": "number"},
                "max_highlight_clip_pct": {"type": "number"},
                "target_bg_median_lum": {"type": "number"},
                "illumination_uniformity_warn": {"type": "number"},
                "illumination_uniformity_fail": {"type": "number"}
            }
        },
        "contrast": {
            "type": "object",
            "properties": {
                "min_global_contrast": {"type": "number"},
                "warn_global_contrast": {"type": "number"}
            }
        },
        "sharpness": {
            "type": "object",
            "properties": {
                "min_laplacian_variance": {"type": "number"},
                "warn_laplacian_variance": {"type": "number"}
            }
        },
        "noise": {
            "type": "object",
            "properties": {
                "max_bg_noise_std": {"type": "number"},
                "warn_bg_noise_std": {"type": "number"}
            }
        },
        "geometry": {
            "type": "object",
            "properties": {
                "max_skew_deg_pass": {"type": "number"},
                "max_skew_deg_warn": {"type": "number"}
            }
        },
        "border_background": {
            "type": "object",
            "properties": {
                "require_black_background": {"type": "boolean"},
                "max_side_margin_ratio_pass": {"type": "number"},
                "max_side_margin_ratio_warn": {"type": "number"},
                "max_bg_median_luminance": {"type": "number"}
            },
            "required": ["max_side_margin_ratio_pass"]
        },
        "color": {
            "type": "object",
            "properties": {
                "enable_color_checks": {"type": "boolean"},
                "max_gray_deltaE_pass": {"type": "number"},
                "max_gray_deltaE_warn": {"type": "number"},
                "max_hue_cast_degrees_warn": {"type": "number"}
            }
        },
        "format_integrity": {
            "type": "object",
            "properties": {
                "allowed_formats": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "jpeg_quality_warn": {"type": "number"},
                "bit_depth_min": {"type": "number"}
            }
        },
        "completeness": {
            "type": "object",
            "properties": {
                "min_margin_px": {"type": "number"},
                "min_content_bbox_coverage": {"type": "number"}
            }
        },
        "document_shadow": {
            "type": "object",
            "properties": {
                "shadow_threshold": {"type": "number"},
                "analysis_band_width": {"type": "number"},
                "min_contour_area": {"type": "number"},
                "gaussian_blur_kernel": {"type": "number"},
                "canny_low": {"type": "number"},
                "canny_high": {"type": "number"},
                "warn_shadow_intensity": {"type": "number"},
                "fail_shadow_intensity": {"type": "number"}
            }
        },
        "scoring": {
            "type": "object",
            "properties": {
                "four_star_weight": {"type": "number"},
                "three_star_weight": {"type": "number"},
                "two_star_weight": {"type": "number"},
                "pass_score_threshold": {"type": "number"},
                "warn_score_threshold": {"type": "number"}
            }
        },
        "sla": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "requirements": {
                    "type": "object",
                    "properties": {
                        "min_overall_score": {"type": "number"},
                        "max_fail_categories": {"type": "number"},
                        "required_pass_categories": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "performance_targets": {
                            "type": "object",
                            "properties": {
                                "sharpness_min_laplacian": {"type": "number"},
                                "contrast_min_global": {"type": "number"},
                                "resolution_min_dpi": {"type": "number"},
                                "noise_max_std": {"type": "number"},
                                "geometry_max_skew": {"type": "number"},
                                "exposure_max_highlight_clip": {"type": "number"},
                                "exposure_max_shadow_clip": {"type": "number"}
                            }
                        }
                    }
                },
                "compliance_levels": {
                    "type": "object",
                    "properties": {
                        "excellent": {
                            "type": "object",
                            "properties": {
                                "min_score": {"type": "number"},
                                "description": {"type": "string"}
                            }
                        },
                        "compliant": {
                            "type": "object",
                            "properties": {
                                "min_score": {"type": "number"},
                                "description": {"type": "string"}
                            }
                        },
                        "warning": {
                            "type": "object",
                            "properties": {
                                "min_score": {"type": "number"},
                                "description": {"type": "string"}
                            }
                        },
                        "non_compliant": {
                            "type": "object",
                            "properties": {
                                "min_score": {"type": "number"},
                                "description": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    }
}


def load_default_config() -> Dict[str, Any]:
    """Load the default configuration."""
    return DEFAULT_CONFIG.copy()


def load_config_from_file(filepath: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            config = json.load(f)
        validate_config(config)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {filepath}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration against schema."""
    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Invalid configuration: {e.message}")


def save_config_to_file(config: Dict[str, Any], filepath: str) -> None:
    """Save configuration to a JSON file."""
    validate_config(config)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two configurations, with override_config taking precedence."""
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


# Predefined profiles
PROFILES = {
    "document_black_background_strict": {
        "name": "Document-Black-Background-Strict",
        "description": "Strict quality control for documents on black backgrounds",
        "config": DEFAULT_CONFIG
    },
    
    "document_lenient": {
        "name": "Document-Lenient", 
        "description": "More forgiving thresholds for legacy documents",
        "config": merge_configs(DEFAULT_CONFIG, {
            "geometry": {
                "max_skew_deg_pass": 2.0,
                "max_skew_deg_warn": 5.0
            },
            "border_background": {
                "max_side_margin_ratio_pass": 0.15,
                "max_side_margin_ratio_warn": 0.20
            },
            "sharpness": {
                "min_laplacian_variance": 100.0,
                "warn_laplacian_variance": 80.0
            }
        })
    },
    
    "archival_quality": {
        "name": "Archival-Quality",
        "description": "High standards for archival preservation",
        "config": merge_configs(DEFAULT_CONFIG, {
            "resolution": {
                "min_dpi_text": 400,
                "min_dpi_archival": 600
            },
            "sharpness": {
                "min_laplacian_variance": 200.0,
                "warn_laplacian_variance": 160.0
            },
            "noise": {
                "max_bg_noise_std": 0.02,
                "warn_bg_noise_std": 0.03
            },
            "format_integrity": {
                "allowed_formats": ["tiff", "png"],
                "bit_depth_min": 16
            }
        })
    }
}


def load_profile(profile_name: str) -> Dict[str, Any]:
    """Load a predefined configuration profile."""
    if profile_name not in PROFILES:
        available = ", ".join(PROFILES.keys())
        raise ValueError(f"Unknown profile '{profile_name}'. Available profiles: {available}")
    
    return PROFILES[profile_name]["config"].copy()


def list_profiles() -> Dict[str, Dict[str, str]]:
    """List all available configuration profiles."""
    return {
        name: {"name": profile["name"], "description": profile["description"]}
        for name, profile in PROFILES.items()
    }

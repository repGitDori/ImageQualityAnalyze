"""
Format integrity and metadata metrics
"""

import os
from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np
from typing import Dict, Any, Optional
from .base import BaseMetrics
from .utils import MetricsUtils


class FormatIntegrityMetrics(BaseMetrics):
    """Metrics for file format and metadata analysis"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze file format and integrity"""
        
        # If metadata was provided, use it; otherwise extract basic info
        if metadata:
            format_info = self._analyze_metadata(metadata, config)
        else:
            format_info = self._basic_format_analysis(config)
        
        return format_info
    
    def _analyze_metadata(self, metadata: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze provided metadata"""
        
        format_name = metadata.get('format', 'unknown').lower()
        bit_depth = metadata.get('bit_depth', 8)
        
        # Check against allowed formats
        allowed_formats = config.get('allowed_formats', ['tiff', 'png', 'jpeg'])
        format_allowed = format_name in allowed_formats
        
        # Extract JPEG quality if available
        jpeg_quality = metadata.get('jpeg_quality', None)
        
        return {
            'format_name': format_name,
            'format_allowed': format_allowed,
            'bit_depth': int(bit_depth),
            'jpeg_quality': jpeg_quality,
            'compression': metadata.get('compression', None)
        }
    
    def _basic_format_analysis(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Basic format analysis when no metadata available"""
        
        return {
            'format_name': 'unknown',
            'format_allowed': False,
            'bit_depth': 8,  # Assumption
            'jpeg_quality': None,
            'compression': None
        }


class ResolutionMetrics(BaseMetrics):
    """Metrics for resolution and DPI analysis"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze image resolution"""
        
        h, w = image.shape[:2]
        
        # Extract DPI from metadata if available
        if metadata:
            dpi_x = metadata.get('dpi_x', 72)
            dpi_y = metadata.get('dpi_y', 72)
        else:
            dpi_x = dpi_y = 72  # Default assumption
        
        return {
            'effective_dpi_x': float(dpi_x),
            'effective_dpi_y': float(dpi_y),
            'pixel_width': int(w),
            'pixel_height': int(h),
            'megapixels': float((w * h) / 1_000_000)
        }

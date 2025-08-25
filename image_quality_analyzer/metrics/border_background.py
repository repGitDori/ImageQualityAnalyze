"""
Border and background control metrics
"""

import numpy as np
from typing import Dict, Any, Optional
from .base import BaseMetrics
from .utils import MetricsUtils


class BorderBackgroundMetrics(BaseMetrics):
    """Metrics for border margins and background control"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Compute border and background metrics
        
        - Margin ratios (normalized by document size)
        - Background median luminance
        - Background uniformity
        """
        
        # Get document bounding box
        x_min, y_min, x_max, y_max = MetricsUtils.get_document_bbox(doc_mask)
        
        h, w = image.shape[:2]
        doc_width = x_max - x_min
        doc_height = y_max - y_min
        
        # Compute margin ratios (normalized by document dimensions)
        left_margin_ratio = x_min / doc_width if doc_width > 0 else 0.0
        right_margin_ratio = (w - x_max) / doc_width if doc_width > 0 else 0.0
        top_margin_ratio = y_min / doc_height if doc_height > 0 else 0.0
        bottom_margin_ratio = (h - y_max) / doc_height if doc_height > 0 else 0.0
        
        # Analyze background
        luminance = MetricsUtils.convert_to_luminance(image)
        bg_mask = 1 - doc_mask
        bg_pixels = luminance[bg_mask > 0]
        
        if len(bg_pixels) > 0:
            bg_median_lum = np.median(bg_pixels)
            bg_mean_lum = np.mean(bg_pixels)
            bg_std = np.std(bg_pixels)
        else:
            bg_median_lum = 0.0
            bg_mean_lum = 0.0
            bg_std = 0.0
        
        return {
            'bg_median_lum': float(bg_median_lum),
            'bg_mean_lum': float(bg_mean_lum),
            'bg_std': float(bg_std),
            'left_margin_ratio': float(left_margin_ratio),
            'right_margin_ratio': float(right_margin_ratio),
            'top_margin_ratio': float(top_margin_ratio),
            'bottom_margin_ratio': float(bottom_margin_ratio),
            'margins_px': {
                'left': int(x_min),
                'right': int(w - x_max),
                'top': int(y_min),
                'bottom': int(h - y_max)
            }
        }

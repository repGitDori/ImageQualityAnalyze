"""
Color and hue cast metrics
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional
from .base import BaseMetrics
from .utils import MetricsUtils


class ColorMetrics(BaseMetrics):
    """Metrics for color accuracy and hue cast detection"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Compute color metrics if enabled"""
        
        if not config.get('enable_color_checks', True):
            return {'enabled': False}
        
        if len(image.shape) != 3:
            return {'enabled': False, 'reason': 'grayscale_image'}
        
        # Estimate hue cast from paper background
        hue_cast = self._estimate_hue_cast(image, doc_mask)
        
        return {
            'enabled': True,
            'hue_cast_degrees': float(hue_cast),
            'gray_deltaE': None  # Would need color chart detection
        }
    
    def _estimate_hue_cast(self, image: np.ndarray, doc_mask: np.ndarray) -> float:
        """Estimate hue cast from document background"""
        
        # Erode document mask to get paper background (avoiding text)
        kernel = np.ones((20, 20), np.uint8)
        eroded_mask = cv2.erode(doc_mask.astype(np.uint8), kernel, iterations=1)
        
        if np.sum(eroded_mask) == 0:
            return 0.0
        
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Extract a and b channels (chrominance)
        a_channel = lab[:, :, 1].astype(np.float32) - 128  # Center around 0
        b_channel = lab[:, :, 2].astype(np.float32) - 128
        
        # Sample paper background
        paper_a = a_channel[eroded_mask > 0]
        paper_b = b_channel[eroded_mask > 0]
        
        if len(paper_a) == 0:
            return 0.0
        
        # Compute mean hue angle
        mean_a = np.mean(paper_a)
        mean_b = np.mean(paper_b)
        
        hue_radians = np.arctan2(mean_b, mean_a)
        hue_degrees = np.degrees(hue_radians)
        
        return hue_degrees

"""
Foreign objects detection metrics
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional
from .base import BaseMetrics
from .utils import MetricsUtils


class ForeignObjectsMetrics(BaseMetrics):
    """Metrics for detecting foreign objects in document capture"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Detect foreign objects like hands, clips, etc."""
        
        # Simplified implementation - could be enhanced with ML models
        foreign_object_flag, area_pct = self._detect_foreign_objects(image, doc_mask)
        
        return {
            'foreign_object_flag': bool(foreign_object_flag),
            'foreign_object_area_pct': float(area_pct)
        }
    
    def _detect_foreign_objects(self, image: np.ndarray, doc_mask: np.ndarray) -> tuple:
        """Simple heuristic-based foreign object detection"""
        
        # Create background mask (non-document area)
        bg_mask = 1 - doc_mask
        
        # Look for large connected components in background
        # that might be foreign objects
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Threshold and find contours in background
        _, thresh = cv2.threshold(gray * bg_mask, 50, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        total_bg_area = np.sum(bg_mask)
        foreign_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            # Consider objects larger than 1% of background as potentially foreign
            if area > total_bg_area * 0.01:
                foreign_area += area
        
        area_pct = (foreign_area / total_bg_area * 100) if total_bg_area > 0 else 0.0
        foreign_flag = area_pct > 2.0  # Threshold for foreign object detection
        
        return foreign_flag, area_pct

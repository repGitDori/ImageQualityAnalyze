"""
Completeness metrics - checks if document capture is complete
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional
from .base import BaseMetrics
from .utils import MetricsUtils


class CompletenessMetrics(BaseMetrics):
    """Metrics for document capture completeness"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Compute completeness metrics
        
        Checks:
        - Content bbox coverage (what fraction of image contains document)
        - Edge touch detection (document touching image boundaries)
        - Margin adequacy
        """
        
        h, w = image.shape[:2]
        image_area = h * w
        
        # Get document bounding box
        x_min, y_min, x_max, y_max = MetricsUtils.get_document_bbox(doc_mask)
        doc_bbox_area = (x_max - x_min) * (y_max - y_min)
        
        # Content bbox coverage
        content_bbox_coverage = doc_bbox_area / image_area if image_area > 0 else 0.0
        
        # Check if document touches image edges
        min_margin_px = config.get('min_margin_px', 8)
        edge_touch_flag = (
            x_min <= min_margin_px or 
            y_min <= min_margin_px or 
            x_max >= w - min_margin_px or 
            y_max >= h - min_margin_px
        )
        
        # Compute actual margins
        left_margin = x_min
        right_margin = w - x_max
        top_margin = y_min
        bottom_margin = h - y_max
        
        # Check for content near edges (more detailed analysis)
        edge_violations = self._check_content_near_edges(doc_mask, min_margin_px)
        
        # Compute document aspect ratio (for sanity check)
        doc_width = x_max - x_min
        doc_height = y_max - y_min
        aspect_ratio = doc_width / doc_height if doc_height > 0 else 0.0
        
        return {
            'content_bbox_coverage': float(content_bbox_coverage),
            'edge_touch_flag': bool(edge_touch_flag),
            'margins': {
                'left_px': int(left_margin),
                'right_px': int(right_margin), 
                'top_px': int(top_margin),
                'bottom_px': int(bottom_margin)
            },
            'edge_violations': edge_violations,
            'document_bbox': {
                'x_min': int(x_min),
                'y_min': int(y_min),
                'x_max': int(x_max),
                'y_max': int(y_max),
                'width': int(doc_width),
                'height': int(doc_height),
                'aspect_ratio': float(aspect_ratio)
            }
        }
    
    def _check_content_near_edges(self, doc_mask: np.ndarray, margin: int) -> Dict[str, bool]:
        """
        Check if document content is too close to image edges
        
        Args:
            doc_mask: Document mask
            margin: Minimum margin in pixels
            
        Returns:
            Dictionary with edge violation flags
        """
        h, w = doc_mask.shape
        
        # Create edge strips
        left_strip = doc_mask[:, :margin]
        right_strip = doc_mask[:, -margin:]
        top_strip = doc_mask[:margin, :]
        bottom_strip = doc_mask[-margin:, :]
        
        return {
            'left_violation': np.any(left_strip > 0),
            'right_violation': np.any(right_strip > 0),
            'top_violation': np.any(top_strip > 0),
            'bottom_violation': np.any(bottom_strip > 0)
        }
    
    def _detect_cropped_text(self, image: np.ndarray, doc_mask: np.ndarray, 
                           margin: int = 20) -> bool:
        """
        Detect if text appears to be cropped at image edges
        
        This is a simplified version - in practice you might use OCR or 
        more sophisticated text detection methods.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Apply document mask
        masked_gray = gray * doc_mask
        
        # Look for high-contrast edges near image boundaries
        edges = cv2.Canny(masked_gray, 50, 150)
        
        h, w = edges.shape
        
        # Check edge density near borders
        border_regions = [
            edges[:margin, :],      # top
            edges[-margin:, :],     # bottom  
            edges[:, :margin],      # left
            edges[:, -margin:]      # right
        ]
        
        # If there are many edges near borders, text might be cropped
        edge_densities = [np.sum(region > 0) / region.size for region in border_regions]
        
        # Threshold for "too many edges" - this is heuristic and may need tuning
        threshold = 0.05
        return any(density > threshold for density in edge_densities)

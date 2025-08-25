"""
Contrast metrics computation
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional
from .base import BaseMetrics
from .utils import MetricsUtils


class ContrastMetrics(BaseMetrics):
    """Metrics for image contrast analysis"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Compute contrast metrics
        
        Primary metric: Global contrast (P95 - P5)
        Secondary metrics: RMS contrast, local contrast variation
        """
        
        # Convert to luminance
        luminance = MetricsUtils.convert_to_luminance(image)
        
        # Apply document mask
        valid_pixels = luminance[doc_mask > 0]
        
        if len(valid_pixels) == 0:
            return {
                'global_contrast': 0.0,
                'rms_contrast': 0.0,
                'local_contrast': {
                    'mean': 0.0,
                    'std': 0.0
                }
            }
        
        # Global contrast (P95 - P5)
        p5 = np.percentile(valid_pixels, 5)
        p95 = np.percentile(valid_pixels, 95)
        global_contrast = p95 - p5
        
        # RMS contrast
        mean_luminance = np.mean(valid_pixels)
        rms_contrast = np.sqrt(np.mean((valid_pixels - mean_luminance) ** 2))
        
        # Local contrast analysis
        local_contrast_stats = self._compute_local_contrast(luminance, doc_mask)
        
        return {
            'global_contrast': float(global_contrast),
            'rms_contrast': float(rms_contrast),
            'percentiles': {
                'p5': float(p5),
                'p95': float(p95)
            },
            'mean_luminance': float(mean_luminance),
            'local_contrast': local_contrast_stats
        }
    
    def _compute_local_contrast(self, luminance: np.ndarray, doc_mask: np.ndarray,
                               tile_size: int = 64) -> Dict[str, float]:
        """Compute local contrast statistics across image tiles"""
        
        tiles = MetricsUtils.create_tile_grid(luminance.shape, tile_size)
        local_contrasts = []
        
        for y1, x1, y2, x2 in tiles:
            tile_luminance = luminance[y1:y2, x1:x2]
            tile_mask = doc_mask[y1:y2, x1:x2]
            
            if np.sum(tile_mask) < (tile_size * tile_size * 0.1):
                continue
            
            tile_valid = tile_luminance[tile_mask > 0]
            if len(tile_valid) > 10:  # Need sufficient pixels
                tile_contrast = np.std(tile_valid)
                local_contrasts.append(tile_contrast)
        
        if len(local_contrasts) == 0:
            return {'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0}
        
        local_contrasts = np.array(local_contrasts)
        
        return {
            'mean': float(np.mean(local_contrasts)),
            'std': float(np.std(local_contrasts)),
            'min': float(np.min(local_contrasts)),
            'max': float(np.max(local_contrasts)),
            'num_tiles': int(len(local_contrasts))
        }

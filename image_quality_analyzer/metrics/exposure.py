"""
Exposure and brightness metrics computation
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional, Tuple
from .base import BaseMetrics
from .utils import MetricsUtils


class ExposureMetrics(BaseMetrics):
    """Metrics for exposure, brightness, and illumination uniformity"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Compute exposure and illumination metrics
        
        Metrics:
        - Shadow/highlight clipping percentages
        - Illumination uniformity (local variation)
        - Overall brightness statistics
        - Dynamic range utilization
        """
        
        # Convert to luminance
        luminance = MetricsUtils.convert_to_luminance(image)
        
        # Apply document mask
        doc_luminance = luminance * doc_mask
        valid_pixels = doc_luminance[doc_mask > 0]
        
        if len(valid_pixels) == 0:
            return self._empty_result()
        
        # Clipping analysis
        clipping_metrics = self._analyze_clipping(valid_pixels)
        
        # Illumination uniformity
        uniformity_metrics = self._analyze_illumination_uniformity(luminance, doc_mask)
        
        # Brightness statistics  
        brightness_stats = self._compute_brightness_statistics(valid_pixels)
        
        # Dynamic range analysis
        dynamic_range = self._analyze_dynamic_range(valid_pixels)
        
        # Background brightness (for background check)
        bg_brightness = self._analyze_background_brightness(luminance, doc_mask)
        
        return {
            'clipping': clipping_metrics,
            'illumination_uniformity': uniformity_metrics,
            'brightness': brightness_stats,
            'dynamic_range': dynamic_range,
            'background': bg_brightness
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result when no valid pixels"""
        return {
            'clipping': {
                'shadow_clip_pct': 0.0,
                'highlight_clip_pct': 0.0
            },
            'illumination_uniformity': {
                'uniformity_ratio': 1.0,
                'local_std': 0.0,
                'local_mean': 0.0
            },
            'brightness': {
                'mean': 0.0,
                'median': 0.0,
                'std': 0.0
            },
            'dynamic_range': {
                'range': 0.0,
                'utilization': 0.0
            },
            'background': {
                'median': 0.0,
                'mean': 0.0
            }
        }
    
    def _analyze_clipping(self, pixels: np.ndarray, 
                         shadow_threshold: float = 0.0, 
                         highlight_threshold: float = 1.0) -> Dict[str, float]:
        """
        Analyze shadow and highlight clipping
        
        Args:
            pixels: Normalized pixel values (0-1)
            shadow_threshold: Threshold for shadow clipping
            highlight_threshold: Threshold for highlight clipping
        """
        total_pixels = len(pixels)
        
        shadow_clipped = np.sum(pixels <= shadow_threshold)
        highlight_clipped = np.sum(pixels >= highlight_threshold)
        
        shadow_clip_pct = (shadow_clipped / total_pixels) * 100.0
        highlight_clip_pct = (highlight_clipped / total_pixels) * 100.0
        
        return {
            'shadow_clip_pct': float(shadow_clip_pct),
            'highlight_clip_pct': float(highlight_clip_pct),
            'shadow_clipped_pixels': int(shadow_clipped),
            'highlight_clipped_pixels': int(highlight_clipped),
            'total_pixels': int(total_pixels)
        }
    
    def _analyze_illumination_uniformity(self, luminance: np.ndarray, 
                                       doc_mask: np.ndarray,
                                       tile_size: int = 64) -> Dict[str, float]:
        """
        Analyze illumination uniformity using local statistics
        
        Computes local mean luminance across tiles and measures variation
        """
        h, w = luminance.shape
        tiles = MetricsUtils.create_tile_grid((h, w), tile_size)
        
        local_means = []
        
        for y1, x1, y2, x2 in tiles:
            tile_luminance = luminance[y1:y2, x1:x2]
            tile_mask = doc_mask[y1:y2, x1:x2]
            
            # Skip tiles with insufficient document content
            if np.sum(tile_mask) < (tile_size * tile_size * 0.1):
                continue
            
            tile_valid = tile_luminance[tile_mask > 0]
            if len(tile_valid) > 0:
                local_means.append(np.mean(tile_valid))
        
        if len(local_means) == 0:
            return {
                'uniformity_ratio': 1.0,
                'local_std': 0.0,
                'local_mean': 0.0,
                'coefficient_of_variation': 0.0
            }
        
        local_means = np.array(local_means)
        mean_of_means = np.mean(local_means)
        std_of_means = np.std(local_means)
        
        # Uniformity ratio: std/mean (lower is better)
        uniformity_ratio = std_of_means / mean_of_means if mean_of_means > 0 else 0.0
        
        # Coefficient of variation
        cv = (std_of_means / mean_of_means) * 100 if mean_of_means > 0 else 0.0
        
        return {
            'uniformity_ratio': float(uniformity_ratio),
            'local_std': float(std_of_means),
            'local_mean': float(mean_of_means),
            'coefficient_of_variation': float(cv),
            'num_tiles_analyzed': int(len(local_means))
        }
    
    def _compute_brightness_statistics(self, pixels: np.ndarray) -> Dict[str, float]:
        """Compute comprehensive brightness statistics"""
        
        return {
            'mean': float(np.mean(pixels)),
            'median': float(np.median(pixels)),
            'std': float(np.std(pixels)),
            'min': float(np.min(pixels)),
            'max': float(np.max(pixels)),
            'percentiles': MetricsUtils.compute_percentiles(pixels, [5, 10, 25, 75, 90, 95])
        }
    
    def _analyze_dynamic_range(self, pixels: np.ndarray) -> Dict[str, float]:
        """
        Analyze dynamic range utilization
        """
        p5 = np.percentile(pixels, 5)
        p95 = np.percentile(pixels, 95)
        
        # Effective dynamic range (5th to 95th percentile)
        effective_range = p95 - p5
        
        # Utilization: how much of the 0-1 range is used
        utilization = effective_range
        
        # Full range
        full_range = np.max(pixels) - np.min(pixels)
        
        return {
            'effective_range': float(effective_range),
            'full_range': float(full_range),
            'utilization': float(utilization),
            'p5_value': float(p5),
            'p95_value': float(p95)
        }
    
    def _analyze_background_brightness(self, luminance: np.ndarray, 
                                     doc_mask: np.ndarray) -> Dict[str, float]:
        """
        Analyze background (non-document) area brightness
        
        This is important for checking background requirements
        """
        # Create background mask (inverse of document mask)
        bg_mask = 1 - doc_mask
        
        bg_pixels = luminance[bg_mask > 0]
        
        if len(bg_pixels) == 0:
            return {
                'median': 0.0,
                'mean': 0.0,
                'std': 0.0,
                'max': 0.0
            }
        
        return {
            'median': float(np.median(bg_pixels)),
            'mean': float(np.mean(bg_pixels)),
            'std': float(np.std(bg_pixels)),
            'max': float(np.max(bg_pixels)),
            'pixel_count': int(len(bg_pixels))
        }
    
    def create_illumination_map(self, luminance: np.ndarray, doc_mask: np.ndarray, 
                               tile_size: int = 32) -> np.ndarray:
        """
        Create an illumination heatmap for visualization
        
        Returns:
            2D array representing local illumination levels
        """
        h, w = luminance.shape
        map_h = (h // tile_size) + 1
        map_w = (w // tile_size) + 1
        
        illum_map = np.zeros((map_h, map_w))
        
        for map_y in range(map_h):
            for map_x in range(map_w):
                y1 = map_y * tile_size
                x1 = map_x * tile_size
                y2 = min(y1 + tile_size, h)
                x2 = min(x1 + tile_size, w)
                
                tile_luminance = luminance[y1:y2, x1:x2]
                tile_mask = doc_mask[y1:y2, x1:x2]
                
                if np.sum(tile_mask) > 0:
                    valid_pixels = tile_luminance[tile_mask > 0]
                    illum_map[map_y, map_x] = np.mean(valid_pixels)
        
        return illum_map

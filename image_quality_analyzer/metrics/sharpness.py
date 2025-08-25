"""
Sharpness/Focus metrics computation
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional
from .base import BaseMetrics
from .utils import MetricsUtils


class SharpnessMetrics(BaseMetrics):
    """Metrics for image sharpness and focus quality"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Compute sharpness metrics
        
        Methods:
        - Laplacian variance (primary method)
        - Gradient magnitude
        - Edge density
        - Local sharpness heatmap
        """
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Apply document mask
        masked_gray = gray * doc_mask
        
        # Primary metric: Laplacian variance
        laplacian_var = self._compute_laplacian_variance(masked_gray, doc_mask)
        
        # Secondary metrics
        gradient_magnitude = self._compute_gradient_magnitude(masked_gray, doc_mask)
        edge_density = self._compute_edge_density(masked_gray, doc_mask)
        
        # Local sharpness analysis
        sharpness_map, tile_stats = self._compute_local_sharpness(masked_gray, doc_mask)
        
        # Frequency domain analysis
        freq_metrics = self._compute_frequency_metrics(masked_gray, doc_mask)
        
        return {
            'laplacian_var': float(laplacian_var),
            'gradient_magnitude_mean': float(gradient_magnitude),
            'edge_density': float(edge_density),
            'local_sharpness': {
                'mean': float(np.mean(tile_stats)),
                'std': float(np.std(tile_stats)),
                'min': float(np.min(tile_stats)),
                'max': float(np.max(tile_stats)),
                'percentiles': MetricsUtils.compute_percentiles(tile_stats, [10, 25, 50, 75, 90])
            },
            'frequency_metrics': freq_metrics,
            'sharpness_map_shape': sharpness_map.shape
        }
    
    def _compute_laplacian_variance(self, gray: np.ndarray, doc_mask: np.ndarray) -> float:
        """
        Compute Laplacian variance - primary sharpness metric
        
        Higher values indicate sharper images
        """
        # Apply Laplacian filter
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        
        # Only consider document area
        laplacian_masked = laplacian * doc_mask
        
        # Compute variance of non-zero pixels
        valid_pixels = laplacian_masked[doc_mask > 0]
        
        if len(valid_pixels) == 0:
            return 0.0
        
        return float(np.var(valid_pixels))
    
    def _compute_gradient_magnitude(self, gray: np.ndarray, doc_mask: np.ndarray) -> float:
        """
        Compute mean gradient magnitude in document area
        """
        # Sobel gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Magnitude
        grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Only consider document area
        valid_pixels = grad_magnitude[doc_mask > 0]
        
        if len(valid_pixels) == 0:
            return 0.0
        
        return float(np.mean(valid_pixels))
    
    def _compute_edge_density(self, gray: np.ndarray, doc_mask: np.ndarray) -> float:
        """
        Compute edge density using Canny edge detector
        """
        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Apply document mask
        edges_masked = edges * doc_mask
        
        # Compute density
        total_doc_pixels = np.sum(doc_mask > 0)
        edge_pixels = np.sum(edges_masked > 0)
        
        if total_doc_pixels == 0:
            return 0.0
        
        return float(edge_pixels / total_doc_pixels)
    
    def _compute_local_sharpness(self, gray: np.ndarray, doc_mask: np.ndarray, 
                                tile_size: int = 64) -> tuple:
        """
        Compute local sharpness using tile-based analysis
        
        Returns:
            (sharpness_map, tile_statistics)
        """
        h, w = gray.shape
        tiles = MetricsUtils.create_tile_grid((h, w), tile_size)
        
        sharpness_map = np.zeros((h // tile_size + 1, w // tile_size + 1))
        tile_stats = []
        
        for i, (y1, x1, y2, x2) in enumerate(tiles):
            tile_gray = gray[y1:y2, x1:x2]
            tile_mask = doc_mask[y1:y2, x1:x2]
            
            # Skip tiles with no document content
            if np.sum(tile_mask) < (tile_size * tile_size * 0.1):
                continue
            
            # Compute Laplacian variance for this tile
            tile_laplacian = cv2.Laplacian(tile_gray, cv2.CV_64F)
            tile_laplacian_masked = tile_laplacian * tile_mask
            valid_pixels = tile_laplacian_masked[tile_mask > 0]
            
            if len(valid_pixels) > 0:
                sharpness = np.var(valid_pixels)
                tile_stats.append(sharpness)
                
                # Map to sharpness map grid
                map_y = y1 // tile_size
                map_x = x1 // tile_size
                if map_y < sharpness_map.shape[0] and map_x < sharpness_map.shape[1]:
                    sharpness_map[map_y, map_x] = sharpness
        
        return sharpness_map, np.array(tile_stats)
    
    def _compute_frequency_metrics(self, gray: np.ndarray, doc_mask: np.ndarray) -> Dict[str, float]:
        """
        Analyze frequency domain characteristics
        """
        # Apply document mask
        masked_gray = gray * doc_mask
        
        # Get document region for FFT analysis
        x_min, y_min, x_max, y_max = MetricsUtils.get_document_bbox(doc_mask)
        doc_region = masked_gray[y_min:y_max, x_min:x_max]
        
        if doc_region.size == 0:
            return {
                'high_freq_energy': 0.0,
                'mid_freq_energy': 0.0,
                'low_freq_energy': 0.0,
                'spectral_centroid': 0.0
            }
        
        # Compute 2D FFT
        f_transform = np.fft.fft2(doc_region.astype(np.float32))
        f_magnitude = np.abs(f_transform)
        
        # Shift zero frequency to center
        f_magnitude_shifted = np.fft.fftshift(f_magnitude)
        
        # Create frequency masks (rings)
        h, w = f_magnitude_shifted.shape
        center_y, center_x = h // 2, w // 2
        
        # Create coordinate grids
        y, x = np.ogrid[:h, :w]
        distances = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Define frequency bands
        max_freq = min(h, w) // 2
        low_freq_mask = distances <= max_freq * 0.3
        mid_freq_mask = (distances > max_freq * 0.3) & (distances <= max_freq * 0.7)
        high_freq_mask = distances > max_freq * 0.7
        
        # Compute energy in each band
        total_energy = np.sum(f_magnitude_shifted**2)
        if total_energy == 0:
            return {
                'high_freq_energy': 0.0,
                'mid_freq_energy': 0.0,
                'low_freq_energy': 0.0,
                'spectral_centroid': 0.0
            }
        
        low_energy = np.sum(f_magnitude_shifted[low_freq_mask]**2) / total_energy
        mid_energy = np.sum(f_magnitude_shifted[mid_freq_mask]**2) / total_energy
        high_energy = np.sum(f_magnitude_shifted[high_freq_mask]**2) / total_energy
        
        # Compute spectral centroid
        spectral_centroid = np.sum(distances * f_magnitude_shifted**2) / total_energy
        spectral_centroid_normalized = spectral_centroid / max_freq
        
        return {
            'high_freq_energy': float(high_energy),
            'mid_freq_energy': float(mid_energy),
            'low_freq_energy': float(low_energy),
            'spectral_centroid': float(spectral_centroid_normalized)
        }

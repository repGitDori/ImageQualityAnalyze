"""
Noise metrics computation
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional
from .base import BaseMetrics
from .utils import MetricsUtils


class NoiseMetrics(BaseMetrics):
    """Metrics for image noise analysis"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Compute noise metrics"""
        
        # Estimate noise from background/paper areas
        bg_noise = self._estimate_background_noise(image, doc_mask)
        
        # Detect compression artifacts (simplified)
        blockiness = self._detect_blockiness(image)
        
        return {
            'bg_noise_std': float(bg_noise),
            'blockiness_index': float(blockiness)
        }
    
    def _estimate_background_noise(self, image: np.ndarray, doc_mask: np.ndarray) -> float:
        """Estimate noise standard deviation from paper background"""
        
        # Convert to luminance
        luminance = MetricsUtils.convert_to_luminance(image)
        
        # Erode document mask to get paper areas (avoiding text edges)
        kernel = np.ones((10, 10), np.uint8)
        eroded_mask = cv2.erode(doc_mask.astype(np.uint8), kernel, iterations=2)
        
        if np.sum(eroded_mask) == 0:
            return 0.0
        
        # Sample paper background
        paper_pixels = luminance[eroded_mask > 0]
        
        if len(paper_pixels) < 100:  # Need sufficient samples
            return 0.0
        
        # Estimate noise using local variation
        # Apply slight smoothing to remove texture, leaving noise
        smoothed = cv2.GaussianBlur(luminance, (3, 3), 1.0)
        noise_image = luminance - smoothed
        
        noise_pixels = noise_image[eroded_mask > 0]
        return np.std(noise_pixels)
    
    def _detect_blockiness(self, image: np.ndarray) -> float:
        """Detect JPEG-like blocking artifacts"""
        
        # Simplified blockiness detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Compute gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Look for periodic patterns (8-pixel boundaries for JPEG)
        # This is a simplified measure - real implementation would be more sophisticated
        block_size = 8
        h, w = gray.shape
        
        block_energy = 0.0
        total_energy = 0.0
        
        # Sample vertical block boundaries
        for x in range(block_size, w, block_size):
            if x < w:
                vertical_diff = np.abs(grad_x[:, x])
                block_energy += np.sum(vertical_diff)
        
        # Sample horizontal block boundaries  
        for y in range(block_size, h, block_size):
            if y < h:
                horizontal_diff = np.abs(grad_y[y, :])
                block_energy += np.sum(horizontal_diff)
        
        total_energy = np.sum(np.abs(grad_x)) + np.sum(np.abs(grad_y))
        
        if total_energy == 0:
            return 0.0
        
        return block_energy / total_energy

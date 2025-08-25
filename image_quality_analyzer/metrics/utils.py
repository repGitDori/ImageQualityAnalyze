"""
Utility functions for metrics computation
"""

import numpy as np
import cv2
from typing import Tuple, Dict


class MetricsUtils:
    """Utility methods shared by all metrics classes"""
    
    @staticmethod
    def create_document_mask(image: np.ndarray, method: str = 'otsu') -> np.ndarray:
        """
        Create document mask using various methods
        
        Args:
            image: Input image
            method: Thresholding method ('otsu', 'adaptive', 'combined')
            
        Returns:
            Binary mask where 1 indicates document area
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        if method == 'otsu':
            _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == 'adaptive':
            mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        elif method == 'combined':
            # Use both methods and combine
            _, otsu_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            adaptive_mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY, 11, 2)
            mask = cv2.bitwise_and(otsu_mask, adaptive_mask)
        else:
            raise ValueError(f"Unknown thresholding method: {method}")
        
        # Find largest contour (assumed to be document)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            mask = np.zeros_like(mask)
            cv2.fillPoly(mask, [largest_contour], 255)
        
        return (mask > 0).astype(np.uint8)
    
    @staticmethod
    def get_document_bbox(doc_mask: np.ndarray) -> Tuple[int, int, int, int]:
        """
        Get bounding box of document area
        
        Returns:
            (x_min, y_min, x_max, y_max) tuple
        """
        coords = np.where(doc_mask > 0)
        if len(coords[0]) == 0:
            return (0, 0, doc_mask.shape[1], doc_mask.shape[0])
        
        y_min, y_max = coords[0].min(), coords[0].max()
        x_min, x_max = coords[1].min(), coords[1].max()
        
        return (x_min, y_min, x_max, y_max)
    
    @staticmethod
    def convert_to_luminance(image: np.ndarray) -> np.ndarray:
        """Convert image to luminance using ITU-R BT.709 coefficients"""
        if len(image.shape) == 2:
            return image.astype(np.float32) / 255.0
        
        # OpenCV uses BGR, convert to RGB coefficients
        # Y = 0.299*R + 0.587*G + 0.114*B
        luminance = 0.114 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.299 * image[:, :, 2]
        return luminance.astype(np.float32) / 255.0
    
    @staticmethod
    def create_tile_grid(image_shape: Tuple[int, int], tile_size: int = 64) -> np.ndarray:
        """
        Create a grid of tiles for local analysis
        
        Args:
            image_shape: (height, width) of image
            tile_size: Size of each tile in pixels
            
        Returns:
            Array of tile coordinates: [[y1, x1, y2, x2], ...]
        """
        h, w = image_shape[:2]
        tiles = []
        
        for y in range(0, h, tile_size):
            for x in range(0, w, tile_size):
                y2 = min(y + tile_size, h)
                x2 = min(x + tile_size, w)
                tiles.append([y, x, y2, x2])
        
        return np.array(tiles)
    
    @staticmethod
    def compute_percentiles(data: np.ndarray, percentiles: list = [5, 95]) -> Dict[str, float]:
        """Compute percentiles of data"""
        data_flat = data.flatten()
        data_flat = data_flat[~np.isnan(data_flat)]  # Remove NaN values
        
        if len(data_flat) == 0:
            return {f"p{p}": 0.0 for p in percentiles}
        
        values = np.percentile(data_flat, percentiles)
        return {f"p{p}": float(v) for p, v in zip(percentiles, values)}
    
    @staticmethod
    def normalize_image(image: np.ndarray) -> np.ndarray:
        """Normalize image to 0-1 range"""
        image = image.astype(np.float32)
        if image.max() > 1:
            image = image / 255.0
        return image

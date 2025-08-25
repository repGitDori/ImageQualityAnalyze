"""
Geometry metrics - skew, rotation, and warp detection
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional, List, Tuple
from .base import BaseMetrics
from .utils import MetricsUtils


class GeometryMetrics(BaseMetrics):
    """Metrics for geometric distortions: skew, rotation, warp"""
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Compute geometry metrics
        
        Primary metric: Skew angle using Hough transform on text lines
        Secondary: Page curvature/warp estimation
        """
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Apply document mask
        masked_gray = gray * doc_mask
        
        # Detect skew angle
        skew_angle = self._detect_skew_angle(masked_gray, doc_mask)
        
        # Detect text line angles for analysis
        line_angles = self._detect_text_line_angles(masked_gray, doc_mask)
        
        # Estimate page warp/curvature
        warp_index = self._estimate_warp_index(masked_gray, doc_mask)
        
        # Document orientation analysis
        orientation_metrics = self._analyze_document_orientation(doc_mask)
        
        return {
            'skew_angle_deg': float(skew_angle),
            'skew_angle_abs': float(abs(skew_angle)),
            'line_angles': {
                'detected_lines': len(line_angles),
                'angle_std': float(np.std(line_angles)) if len(line_angles) > 0 else 0.0,
                'angle_range': float(np.ptp(line_angles)) if len(line_angles) > 0 else 0.0
            },
            'warp_index': float(warp_index),
            'orientation': orientation_metrics
        }
    
    def _detect_skew_angle(self, gray: np.ndarray, doc_mask: np.ndarray) -> float:
        """
        Detect skew angle using Hough transform on text lines
        
        Returns angle in degrees (-45 to 45, positive = clockwise)
        """
        # Edge detection for line finding
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Apply document mask to edges
        edges = edges * doc_mask
        
        # Hough line detection
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is None or len(lines) == 0:
            return 0.0
        
        # Extract angles and filter for text-like lines
        angles = []
        for line in lines:
            rho, theta = line[0]
            angle_deg = np.degrees(theta) - 90  # Convert to skew angle
            
            # Filter to reasonable text line angles (-45 to 45 degrees)
            if -45 <= angle_deg <= 45:
                angles.append(angle_deg)
        
        if len(angles) == 0:
            return 0.0
        
        # Use median angle to reduce outlier influence
        return np.median(angles)
    
    def _detect_text_line_angles(self, gray: np.ndarray, doc_mask: np.ndarray) -> List[float]:
        """
        Detect individual text line angles for variation analysis
        """
        # More sensitive edge detection for text
        edges = cv2.Canny(gray, 30, 100, apertureSize=3)
        edges = edges * doc_mask
        
        # Probabilistic Hough lines for better line segment detection
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                               minLineLength=50, maxLineGap=10)
        
        if lines is None:
            return []
        
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate angle
            if x2 - x1 != 0:
                angle_rad = np.arctan2(y2 - y1, x2 - x1)
                angle_deg = np.degrees(angle_rad)
                
                # Normalize to -45 to 45 range
                if angle_deg > 45:
                    angle_deg -= 90
                elif angle_deg < -45:
                    angle_deg += 90
                
                angles.append(angle_deg)
        
        return angles
    
    def _estimate_warp_index(self, gray: np.ndarray, doc_mask: np.ndarray) -> float:
        """
        Estimate page warp/curvature using line straightness analysis
        
        Returns a warp index (0 = straight, higher = more warped)
        """
        # Find text lines using Hough
        edges = cv2.Canny(gray, 50, 150)
        edges = edges * doc_mask
        
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80,
                               minLineLength=100, maxLineGap=20)
        
        if lines is None or len(lines) < 3:
            return 0.0
        
        # Analyze line curvature by fitting polynomials
        warp_scores = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Extract pixels along the line
            line_pixels = self._extract_line_pixels(edges, (x1, y1), (x2, y2))
            
            if len(line_pixels) < 20:  # Need enough points
                continue
            
            # Measure deviation from straight line
            warp_score = self._measure_line_curvature(line_pixels)
            warp_scores.append(warp_score)
        
        if len(warp_scores) == 0:
            return 0.0
        
        # Return mean warp score
        return np.mean(warp_scores)
    
    def _extract_line_pixels(self, edges: np.ndarray, start: Tuple[int, int], 
                            end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Extract pixel coordinates along a line segment"""
        x1, y1 = start
        x2, y2 = end
        
        # Bresenham's line algorithm to get pixels along line
        pixels = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            if 0 <= x < edges.shape[1] and 0 <= y < edges.shape[0]:
                if edges[y, x] > 0:  # Edge pixel
                    pixels.append((x, y))
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return pixels
    
    def _measure_line_curvature(self, pixels: List[Tuple[int, int]]) -> float:
        """
        Measure curvature of a line by fitting polynomial and measuring deviation
        """
        if len(pixels) < 3:
            return 0.0
        
        # Convert to numpy arrays
        points = np.array(pixels)
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        
        # Fit polynomial (degree 2 for curvature detection)
        try:
            # Choose the axis with more variation for fitting
            if np.std(x_coords) > np.std(y_coords):
                # Fit y = f(x)
                coeffs = np.polyfit(x_coords, y_coords, 2)
                y_fitted = np.polyval(coeffs, x_coords)
                deviations = np.abs(y_coords - y_fitted)
            else:
                # Fit x = f(y)
                coeffs = np.polyfit(y_coords, x_coords, 2)
                x_fitted = np.polyval(coeffs, y_coords)
                deviations = np.abs(x_coords - x_fitted)
            
            # Return RMS deviation as warp measure
            return np.sqrt(np.mean(deviations ** 2))
            
        except np.linalg.LinAlgError:
            return 0.0
    
    def _analyze_document_orientation(self, doc_mask: np.ndarray) -> Dict[str, Any]:
        """
        Analyze document orientation (portrait vs landscape, aspect ratio)
        """
        # Get document bounding box
        x_min, y_min, x_max, y_max = MetricsUtils.get_document_bbox(doc_mask)
        
        doc_width = x_max - x_min
        doc_height = y_max - y_min
        
        if doc_height == 0:
            aspect_ratio = 0.0
        else:
            aspect_ratio = doc_width / doc_height
        
        # Determine likely orientation
        if aspect_ratio > 1.2:
            orientation = "landscape"
        elif aspect_ratio < 0.8:
            orientation = "portrait"
        else:
            orientation = "square"
        
        return {
            'aspect_ratio': float(aspect_ratio),
            'orientation': orientation,
            'doc_width_px': int(doc_width),
            'doc_height_px': int(doc_height)
        }

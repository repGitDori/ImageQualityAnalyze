#!/usr/bin/env python3
"""
Document Shadow Detection Metric

Detects the subtle shadow gradient around the edges of a loose document
that sits on top of another flat document. This is common in document
imaging and quality control.

The shadow characteristics:
- Soft and gradual (not a hard edge)
- Localized around the perimeter of the top document
- Forms a continuous halo-like band
- Creates a radial gradient around document perimeter

Algorithm:
1. Preprocessing - Convert to grayscale, apply noise reduction
2. Detect Document Edge - Use edge detection to find document contours
3. Define Analysis Band - Create buffer region around detected contour
4. Measure Intensity Gradient - Sample pixel values perpendicular to edge
5. Classify Shadow - Determine if gradient indicates shadow presence
6. Output Metrics - Shadow presence, intensity, and width measurements
"""

import cv2
import numpy as np
from scipy import ndimage
from typing import Dict, Any, Optional
from .base import BaseMetrics


def ensure_grayscale(image):
    """Convert image to grayscale if needed"""
    if image is None:
        return None
    
    # Handle PIL Image
    if hasattr(image, 'convert'):
        return np.array(image.convert('L'))
    
    # Handle numpy array
    if isinstance(image, np.ndarray):
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            return image
    
    return None


def safe_divide(a, b):
    """Safe division that handles division by zero"""
    if b == 0:
        return 0.0
    return float(a) / float(b)


class DocumentShadowMetric(BaseMetrics):
    """
    Document Shadow Detection and Analysis
    
    Detects loose document shadows by analyzing intensity gradients
    around document edges to identify the characteristic halo pattern.
    """
    
    def compute(self, image: np.ndarray, doc_mask: np.ndarray, 
                config: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Compute document shadow metrics
        
        Args:
            image: Input image (BGR format from OpenCV)
            doc_mask: Binary mask of document area
            config: Configuration parameters for shadow detection
            metadata: Optional image metadata
            
        Returns:
            Dictionary containing shadow analysis metrics
        """
        return self.analyze(image, config)
    
    def __init__(self, config=None):
        super().__init__()
        
        # Default configuration parameters
        self.config = config or {}
        self.shadow_threshold = self.config.get('shadow_threshold', 20)  # Intensity difference threshold
        self.analysis_band_width = self.config.get('analysis_band_width', 50)  # Pixels to analyze outward
        self.min_contour_area = self.config.get('min_contour_area', 10000)  # Minimum document area
        self.gaussian_blur_kernel = self.config.get('gaussian_blur_kernel', 3)  # Noise reduction
        self.canny_low = self.config.get('canny_low', 50)  # Canny edge detection low threshold
        self.canny_high = self.config.get('canny_high', 150)  # Canny edge detection high threshold
        
    def analyze(self, image, config=None):
        """
        Analyze image for document shadow presence and characteristics
        
        Args:
            image: Input image (PIL Image or numpy array)
            config: Optional configuration override
            
        Returns:
            dict: Analysis results containing shadow metrics
        """
        # Use provided config or instance config
        if config:
            # Update instance config with provided config
            for key, value in config.items():
                setattr(self, key, value)
        try:
            # Step 1: Preprocessing
            gray_image = ensure_grayscale(image)
            
            if gray_image is None:
                return self._create_error_result("Failed to convert image to grayscale")
            
            # Apply Gaussian blur to reduce noise
            if self.gaussian_blur_kernel > 0:
                blurred = cv2.GaussianBlur(gray_image, (self.gaussian_blur_kernel, self.gaussian_blur_kernel), 0)
            else:
                blurred = gray_image.copy()
            
            # Step 2: Detect Document Edge
            edge_data = self._detect_document_edge(blurred)
            if edge_data is None:
                return self._create_error_result("Could not detect document edges")
            
            contour, edges = edge_data
            
            # Step 3: Define Analysis Band & Step 4: Measure Intensity Gradient
            shadow_metrics = self._analyze_shadow_gradient(blurred, contour)
            
            # Step 5: Classify Shadow
            shadow_classification = self._classify_shadow(shadow_metrics)
            
            # Step 6: Output Metrics
            result = {
                'shadow_present': shadow_classification['shadow_present'],
                'shadow_intensity': shadow_metrics['avg_intensity_diff'],
                'shadow_width': shadow_metrics['avg_shadow_width'],
                'shadow_coverage': shadow_metrics['shadow_coverage_percent'],
                'perimeter_analyzed': shadow_metrics['perimeter_length'],
                'confidence': shadow_classification['confidence'],
                'quality_score': shadow_classification['quality_score'],
                
                # Detailed measurements
                'measurements': {
                    'edge_intensity_avg': shadow_metrics['edge_intensity_avg'],
                    'outer_intensity_avg': shadow_metrics['outer_intensity_avg'],
                    'intensity_difference': shadow_metrics['avg_intensity_diff'],
                    'gradient_variance': shadow_metrics['gradient_variance'],
                    'shadow_pixels_detected': shadow_metrics['shadow_pixel_count'],
                    'total_analysis_pixels': shadow_metrics['total_analysis_pixels'],
                    'document_contour_area': shadow_metrics['contour_area']
                },
                
                # Processing info
                'processing_info': {
                    'image_dimensions': gray_image.shape,
                    'analysis_band_width': self.analysis_band_width,
                    'shadow_threshold': self.shadow_threshold,
                    'contour_points': len(contour),
                    'edge_detection_method': 'canny_with_contours'
                }
            }
            
            return result
            
        except Exception as e:
            return self._create_error_result(f"Shadow analysis failed: {str(e)}")
    
    def _detect_document_edge(self, gray_image):
        """
        Step 2: Detect Document Edge using Canny edge detection and contour finding
        
        Args:
            gray_image: Grayscale image array
            
        Returns:
            tuple: (largest_contour, edges) or None if detection fails
        """
        try:
            # Apply Canny edge detection
            edges = cv2.Canny(gray_image, self.canny_low, self.canny_high)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # Find the largest contour (likely the main document)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Check if contour is large enough to be a document
            area = cv2.contourArea(largest_contour)
            if area < self.min_contour_area:
                return None
            
            # Approximate contour to polygon for cleaner edges
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx_contour = cv2.approxPolyDP(largest_contour, epsilon, True)
            
            return (approx_contour, edges)
            
        except Exception as e:
            print(f"Edge detection failed: {e}")
            return None
    
    def _analyze_shadow_gradient(self, gray_image, contour):
        """
        Steps 3 & 4: Define Analysis Band and Measure Intensity Gradient
        
        Args:
            gray_image: Grayscale image array
            contour: Document edge contour
            
        Returns:
            dict: Shadow gradient analysis metrics
        """
        height, width = gray_image.shape
        
        # Create masks for analysis band
        contour_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.drawContours(contour_mask, [contour], -1, 255, -1)
        
        # Create dilated mask for outer boundary
        kernel = np.ones((self.analysis_band_width * 2, self.analysis_band_width * 2), np.uint8)
        dilated_mask = cv2.dilate(contour_mask, kernel, iterations=1)
        
        # Analysis band = dilated area - original contour
        analysis_band = dilated_mask - contour_mask
        
        # Sample intensity values along the edge
        intensity_samples = []
        shadow_widths = []
        gradient_variances = []
        
        # Get contour points for sampling
        contour_points = contour.reshape(-1, 2)
        
        for point in contour_points[::5]:  # Sample every 5th point for efficiency
            x, y = point
            
            # Sample perpendicular to edge outward
            samples = self._sample_perpendicular_gradient(gray_image, x, y, contour_mask)
            if samples:
                intensity_samples.append(samples)
                
                # Calculate shadow width (distance where gradient stabilizes)
                shadow_width = self._calculate_shadow_width(samples)
                shadow_widths.append(shadow_width)
                
                # Calculate gradient variance (smooth gradient has low variance)
                if len(samples) > 1:
                    gradient = np.diff(samples)
                    gradient_variances.append(np.var(gradient))
        
        if not intensity_samples:
            return self._create_empty_shadow_metrics()
        
        # Calculate aggregate metrics
        intensity_samples = np.array(intensity_samples)
        edge_intensities = intensity_samples[:, 0] if intensity_samples.size > 0 else [128]
        outer_intensities = intensity_samples[:, -1] if intensity_samples.size > 1 else [128]
        
        avg_edge_intensity = np.mean(edge_intensities)
        avg_outer_intensity = np.mean(outer_intensities)
        avg_intensity_diff = avg_outer_intensity - avg_edge_intensity
        
        # Shadow coverage calculation
        shadow_pixels = np.sum(analysis_band > 0)
        total_pixels = analysis_band.size
        shadow_coverage_percent = (shadow_pixels / total_pixels) * 100 if total_pixels > 0 else 0
        
        return {
            'edge_intensity_avg': float(avg_edge_intensity),
            'outer_intensity_avg': float(avg_outer_intensity),
            'avg_intensity_diff': float(avg_intensity_diff),
            'avg_shadow_width': float(np.mean(shadow_widths)) if shadow_widths else 0,
            'gradient_variance': float(np.mean(gradient_variances)) if gradient_variances else 0,
            'shadow_coverage_percent': float(shadow_coverage_percent),
            'shadow_pixel_count': int(shadow_pixels),
            'total_analysis_pixels': int(total_pixels),
            'perimeter_length': float(cv2.arcLength(contour, True)),
            'contour_area': float(cv2.contourArea(contour)),
            'sample_count': len(intensity_samples)
        }
    
    def _sample_perpendicular_gradient(self, image, x, y, contour_mask, num_samples=20):
        """
        Sample pixel intensities perpendicular to edge outward from document
        
        Args:
            image: Grayscale image
            x, y: Edge point coordinates
            contour_mask: Mask of document area
            num_samples: Number of samples to take outward
            
        Returns:
            list: Intensity values from edge outward
        """
        height, width = image.shape
        samples = []
        
        # Find direction perpendicular to edge (outward from document)
        # Simple approach: try multiple directions and pick the one going outward
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        
        best_samples = []
        max_valid_samples = 0
        
        for dx, dy in directions:
            current_samples = []
            
            for i in range(num_samples):
                sample_x = int(x + dx * i * 2)
                sample_y = int(y + dy * i * 2)
                
                # Check bounds
                if 0 <= sample_x < width and 0 <= sample_y < height:
                    # Skip if still inside document (for first few samples, this is expected)
                    if i > 2 and contour_mask[sample_y, sample_x] > 0:
                        break
                    
                    current_samples.append(image[sample_y, sample_x])
                else:
                    break
            
            if len(current_samples) > max_valid_samples:
                max_valid_samples = len(current_samples)
                best_samples = current_samples
        
        return best_samples if len(best_samples) >= 5 else []
    
    def _calculate_shadow_width(self, intensity_samples):
        """
        Calculate shadow width (distance where gradient stabilizes)
        
        Args:
            intensity_samples: List of intensity values from edge outward
            
        Returns:
            int: Shadow width in pixels
        """
        if len(intensity_samples) < 3:
            return 0
        
        # Find point where intensity stabilizes (gradient becomes minimal)
        gradients = np.diff(intensity_samples)
        
        # Look for where gradient drops below threshold
        stabilization_threshold = 2  # Intensity units per pixel
        
        for i, gradient in enumerate(gradients):
            if abs(gradient) < stabilization_threshold:
                return i * 2  # Multiply by sampling distance
        
        return len(intensity_samples) * 2  # If never stabilizes, return full width
    
    def _classify_shadow(self, shadow_metrics):
        """
        Step 5: Classify Shadow based on measured gradients
        
        Args:
            shadow_metrics: Dictionary of shadow analysis results
            
        Returns:
            dict: Shadow classification results
        """
        intensity_diff = shadow_metrics['avg_intensity_diff']
        gradient_variance = shadow_metrics['gradient_variance']
        shadow_width = shadow_metrics['avg_shadow_width']
        
        # Shadow present if intensity difference exceeds threshold
        shadow_present = intensity_diff > self.shadow_threshold
        
        # Calculate confidence based on multiple factors
        confidence_factors = []
        
        # Factor 1: Intensity difference strength
        intensity_confidence = min(intensity_diff / (self.shadow_threshold * 2), 1.0)
        confidence_factors.append(intensity_confidence)
        
        # Factor 2: Gradient smoothness (low variance indicates smooth shadow)
        if gradient_variance > 0:
            smoothness_confidence = max(0, 1.0 - (gradient_variance / 100))
            confidence_factors.append(smoothness_confidence)
        
        # Factor 3: Shadow width reasonableness
        if 5 <= shadow_width <= 100:  # Reasonable shadow width range
            width_confidence = 1.0
        else:
            width_confidence = 0.5
        confidence_factors.append(width_confidence)
        
        overall_confidence = np.mean(confidence_factors)
        
        # Calculate quality score (higher is better - less shadow)
        if shadow_present:
            # Quality decreases with shadow intensity
            quality_score = max(0.0, 1.0 - (intensity_diff / 100.0))
        else:
            quality_score = 1.0
        
        return {
            'shadow_present': shadow_present,
            'confidence': float(overall_confidence),
            'quality_score': float(quality_score),
            'classification_details': {
                'intensity_confidence': float(intensity_confidence),
                'smoothness_confidence': float(confidence_factors[1] if len(confidence_factors) > 1 else 0),
                'width_confidence': float(width_confidence)
            }
        }
    
    def _create_empty_shadow_metrics(self):
        """Create default metrics when analysis fails"""
        return {
            'edge_intensity_avg': 128.0,
            'outer_intensity_avg': 128.0,
            'avg_intensity_diff': 0.0,
            'avg_shadow_width': 0.0,
            'gradient_variance': 0.0,
            'shadow_coverage_percent': 0.0,
            'shadow_pixel_count': 0,
            'total_analysis_pixels': 0,
            'perimeter_length': 0.0,
            'contour_area': 0.0,
            'sample_count': 0
        }
    
    def _create_error_result(self, error_message):
        """Create error result structure"""
        return {
            'shadow_present': False,
            'shadow_intensity': 0.0,
            'shadow_width': 0.0,
            'shadow_coverage': 0.0,
            'perimeter_analyzed': 0.0,
            'confidence': 0.0,
            'quality_score': 0.5,  # Neutral score for errors
            'error': error_message,
            'measurements': self._create_empty_shadow_metrics(),
            'processing_info': {
                'error': error_message,
                'analysis_band_width': self.analysis_band_width,
                'shadow_threshold': self.shadow_threshold
            }
        }
    
    def get_score(self, analysis_result):
        """
        Calculate quality score from analysis results
        
        Args:
            analysis_result: Result from analyze() method
            
        Returns:
            float: Quality score (0.0 to 1.0, higher is better)
        """
        if 'error' in analysis_result:
            return 0.5  # Neutral score for errors
        
        return analysis_result.get('quality_score', 0.5)
    
    def get_recommendations(self, analysis_result):
        """
        Generate recommendations based on shadow analysis
        
        Args:
            analysis_result: Result from analyze() method
            
        Returns:
            list: List of recommendation strings
        """
        recommendations = []
        
        if 'error' in analysis_result:
            recommendations.append("⚠️ Shadow analysis could not be completed - check image quality and document edges")
            return recommendations
        
        shadow_present = analysis_result.get('shadow_present', False)
        shadow_intensity = analysis_result.get('shadow_intensity', 0)
        shadow_width = analysis_result.get('shadow_width', 0)
        confidence = analysis_result.get('confidence', 0)
        
        if shadow_present:
            if shadow_intensity > 50:
                recommendations.append("❌ Strong document shadow detected - ensure flat document placement")
                recommendations.append("💡 Use document holder or press document flat against scanning surface")
            elif shadow_intensity > 30:
                recommendations.append("⚠️ Moderate shadow detected - improve document flatness")
                recommendations.append("💡 Check lighting conditions and document positioning")
            else:
                recommendations.append("⚠️ Minor shadow detected - consider improving document placement")
            
            if shadow_width > 30:
                recommendations.append("📏 Wide shadow detected - document may be significantly raised")
            
            if confidence < 0.5:
                recommendations.append("❓ Shadow detection confidence is low - manual verification recommended")
        else:
            if confidence > 0.8:
                recommendations.append("✅ No significant document shadow detected - good document flatness")
            else:
                recommendations.append("✅ No shadow detected, but confidence is moderate - image quality may affect detection")
        
        # General recommendations
        recommendations.append("💡 For best results: ensure document is completely flat against scanning surface")
        recommendations.append("💡 Use consistent lighting to minimize shadows")
        
        return recommendations


def create_document_shadow_metric(config=None):
    """
    Factory function to create DocumentShadowMetric instance
    
    Args:
        config: Configuration dictionary
        
    Returns:
        DocumentShadowMetric: Configured metric instance
    """
    return DocumentShadowMetric(config)


# Example usage and testing
if __name__ == "__main__":
    # Test the metric
    import sys
    import os
    from PIL import Image
    
    # Add parent directory to path for imports
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    def test_document_shadow_metric():
        """Test function for document shadow detection"""
        print("Testing Document Shadow Metric...")
        
        # Create metric instance
        config = {
            'shadow_threshold': 25,
            'analysis_band_width': 40,
            'min_contour_area': 5000
        }
        metric = DocumentShadowMetric(config)
        
        # Test with a sample image (you would replace this with actual image)
        test_image = np.ones((800, 600), dtype=np.uint8) * 200  # White background
        
        # Simulate a document with shadow
        cv2.rectangle(test_image, (100, 100), (500, 600), 220, -1)  # Document area
        
        # Add gradual shadow around document
        for i in range(20):
            intensity = 200 - (i * 2)
            cv2.rectangle(test_image, (100-i, 100-i), (500+i, 600+i), intensity, 2)
        
        # Run analysis
        result = metric.analyze(test_image)
        
        print("Analysis Results:")
        print(f"Shadow Present: {result['shadow_present']}")
        print(f"Shadow Intensity: {result['shadow_intensity']:.2f}")
        print(f"Shadow Width: {result['shadow_width']:.2f}")
        print(f"Quality Score: {result['quality_score']:.2f}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        print("\nRecommendations:")
        recommendations = metric.get_recommendations(result)
        for rec in recommendations:
            print(f"  {rec}")
    
    # Uncomment to run test
    # test_document_shadow_metric()

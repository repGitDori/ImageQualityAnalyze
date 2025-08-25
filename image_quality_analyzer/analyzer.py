"""
Main ImageQualityAnalyzer class
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, Any, List, Optional, Union
from PIL import Image
from PIL.ExifTags import TAGS

from .config import load_default_config, validate_config
from .metrics import *
from .scoring import QualityScorer


class ImageQualityAnalyzer:
    """
    Main image quality analyzer for document photos/scans
    
    Provides comprehensive quality analysis including:
    - Objective metrics computation
    - Quality scoring and flagging  
    - Report generation
    - Batch processing capabilities
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize analyzer with configuration
        
        Args:
            config: Configuration dictionary. If None, uses default config.
        """
        self.config = config or load_default_config()
        validate_config(self.config)
        
        # Initialize metrics computers
        self.metrics_computers = {
            'completeness': CompletenessMetrics(),
            'foreign_objects': ForeignObjectsMetrics(),
            'sharpness': SharpnessMetrics(),
            'exposure': ExposureMetrics(),
            'contrast': ContrastMetrics(),
            'color': ColorMetrics(),
            'geometry': GeometryMetrics(),
            'border_background': BorderBackgroundMetrics(),
            'noise': NoiseMetrics(),
            'format_integrity': FormatIntegrityMetrics(),
            'resolution': ResolutionMetrics()
        }
        
        # Initialize scorer
        self.scorer = QualityScorer(self.config)
    
    def analyze_image(self, image_path: str, 
                     image_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a single image for quality metrics
        
        Args:
            image_path: Path to image file
            image_id: Optional identifier for the image
            
        Returns:
            Complete analysis report as per schema in spec
        """
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Extract metadata
        metadata = self._extract_metadata(image_path)
        
        # Generate image ID if not provided
        if image_id is None:
            image_id = os.path.splitext(os.path.basename(image_path))[0]
        
        # Create document mask
        doc_mask = self._create_document_mask(image)
        
        # Compute all metrics
        metrics = self._compute_all_metrics(image, doc_mask, metadata)
        
        # Score metrics and determine status
        scoring_result = self.scorer.score_all_categories(metrics)
        
        # Build complete report
        report = {
            'image_id': image_id,
            'file_path': image_path,
            'pixels': {
                'w': image.shape[1],
                'h': image.shape[0]
            },
            'dpi': {
                'x': metadata.get('dpi_x', 72),
                'y': metadata.get('dpi_y', 72)
            },
            'metrics': metrics,
            'category_status': scoring_result['category_status'],
            'global': scoring_result['global']
        }
        
        return report
    
    def analyze_batch(self, image_paths: List[str], 
                     progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """
        Analyze a batch of images
        
        Args:
            image_paths: List of paths to image files
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of analysis reports
        """
        
        results = []
        
        for i, path in enumerate(image_paths):
            try:
                result = self.analyze_image(path)
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, len(image_paths), path)
                    
            except Exception as e:
                print(f"Error analyzing {path}: {e}")
                # Add error result
                results.append({
                    'image_id': os.path.basename(path),
                    'file_path': path,
                    'error': str(e),
                    'global': {'status': 'error', 'score': 0.0, 'stars': 0}
                })
        
        return results
    
    def export_json_report(self, result: Dict[str, Any], output_path: str) -> None:
        """Export single analysis result to JSON file"""
        
        # Handle case where output_path has no directory
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Convert NumPy types to native Python types for JSON serialization
        def convert_for_json(obj):
            if isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_for_json(item) for item in obj]
            return obj
        
        result_converted = convert_for_json(result)
        
        with open(output_path, 'w') as f:
            json.dump(result_converted, f, indent=2)
    
    def export_csv_comparison(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export batch results to CSV for comparison
        
        Uses the CSV schema specified in the spec
        """
        
        import pandas as pd
        
        rows = []
        
        for result in results:
            if 'error' in result:
                continue
                
            metrics = result.get('metrics', {})
            
            # Extract key metrics for CSV as per spec schema
            row = {
                'image_id': result.get('image_id', ''),
                'file_path': result.get('file_path', ''),
                'px_w': result.get('pixels', {}).get('w', 0),
                'px_h': result.get('pixels', {}).get('h', 0),
                'dpi_x': result.get('dpi', {}).get('x', 0),
                'dpi_y': result.get('dpi', {}).get('y', 0),
                'lap_var': metrics.get('sharpness', {}).get('laplacian_var', 0),
                'global_contrast': metrics.get('contrast', {}).get('global_contrast', 0),
                'skew_deg': metrics.get('geometry', {}).get('skew_angle_abs', 0),
                'bg_median_lum': metrics.get('border_background', {}).get('bg_median_lum', 0),
                'left_ratio': metrics.get('border_background', {}).get('left_margin_ratio', 0),
                'right_ratio': metrics.get('border_background', {}).get('right_margin_ratio', 0),
                'top_ratio': metrics.get('border_background', {}).get('top_margin_ratio', 0),
                'bottom_ratio': metrics.get('border_background', {}).get('bottom_margin_ratio', 0),
                'noise_std': metrics.get('noise', {}).get('bg_noise_std', 0),
                'illum_uniformity': metrics.get('exposure', {}).get('illumination_uniformity', {}).get('uniformity_ratio', 0),
                'gray_deltaE': metrics.get('color', {}).get('gray_deltaE', ''),
                'hue_cast_deg': metrics.get('color', {}).get('hue_cast_degrees', 0),
                'format': metrics.get('format_integrity', {}).get('format_name', ''),
                'bit_depth': metrics.get('format_integrity', {}).get('bit_depth', 0),
                'score': result.get('global', {}).get('score', 0),
                'stars': result.get('global', {}).get('stars', 0),
                'status': result.get('global', {}).get('status', '')
            }
            
            rows.append(row)
        
        # Create DataFrame and save
        df = pd.DataFrame(rows)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
    
    def _extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """Extract metadata from image file"""
        
        try:
            with Image.open(image_path) as pil_image:
                # Basic format info
                metadata = {
                    'format': pil_image.format.lower() if pil_image.format else 'unknown',
                    'mode': pil_image.mode,
                    'size': pil_image.size
                }
                
                # Try to extract DPI
                dpi = pil_image.info.get('dpi', (72, 72))
                metadata['dpi_x'] = dpi[0]
                metadata['dpi_y'] = dpi[1]
                
                # Extract EXIF if available
                if hasattr(pil_image, '_getexif') and pil_image._getexif():
                    exif = pil_image._getexif()
                    
                    # Look for relevant EXIF tags
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        if tag == 'XResolution':
                            metadata['dpi_x'] = value
                        elif tag == 'YResolution':
                            metadata['dpi_y'] = value
                        elif tag == 'BitsPerSample':
                            metadata['bit_depth'] = value if isinstance(value, int) else value[0]
                
                # Estimate bit depth from mode if not found
                if 'bit_depth' not in metadata:
                    if pil_image.mode == 'L':
                        metadata['bit_depth'] = 8
                    elif pil_image.mode == 'RGB':
                        metadata['bit_depth'] = 8
                    elif pil_image.mode == 'RGBA':
                        metadata['bit_depth'] = 8
                    else:
                        metadata['bit_depth'] = 8
                
                return metadata
                
        except Exception as e:
            print(f"Warning: Could not extract metadata from {image_path}: {e}")
            return {
                'format': 'unknown',
                'dpi_x': 72,
                'dpi_y': 72,
                'bit_depth': 8
            }
    
    def _create_document_mask(self, image: np.ndarray, method: str = 'otsu') -> np.ndarray:
        """Create document mask using the base metrics method"""
        
        from .metrics.base import DocumentMaskGenerator
        mask_generator = DocumentMaskGenerator()
        return mask_generator.create_document_mask(image, method)
    
    def _compute_all_metrics(self, image: np.ndarray, doc_mask: np.ndarray, 
                           metadata: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Compute all metric categories"""
        
        metrics = {}
        
        for category, computer in self.metrics_computers.items():
            try:
                config_cat = self.config.get(category, {})
                category_metrics = computer.compute(image, doc_mask, config_cat, metadata)
                metrics[category] = category_metrics
                
            except Exception as e:
                print(f"Warning: Error computing {category} metrics: {e}")
                metrics[category] = {}
        
        return metrics
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update analyzer configuration"""
        
        validate_config(new_config)
        self.config = new_config
        self.scorer = QualityScorer(self.config)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        
        return self.config.copy()

"""
Basic tests for ImageQualityAnalyzer
"""

import pytest
import numpy as np
import cv2
import tempfile
import os
import json
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_quality_analyzer import ImageQualityAnalyzer, load_default_config
from image_quality_analyzer.config import validate_config, load_profile
from image_quality_analyzer.scoring import QualityScorer, Status


class TestConfiguration:
    """Test configuration management"""
    
    def test_load_default_config(self):
        """Test loading default configuration"""
        config = load_default_config()
        
        assert isinstance(config, dict)
        assert 'resolution' in config
        assert 'exposure' in config
        assert 'sharpness' in config
        
        # Check specific values
        assert config['resolution']['min_dpi_text'] == 300
        assert config['sharpness']['min_laplacian_variance'] == 150.0
    
    def test_validate_config(self):
        """Test configuration validation"""
        config = load_default_config()
        
        # Should not raise exception
        validate_config(config)
        
        # Test invalid config
        invalid_config = {'invalid': 'config'}
        try:
            validate_config(invalid_config)
            assert False, "Should have raised validation error"
        except ValueError:
            pass  # Expected
    
    def test_load_profiles(self):
        """Test loading predefined profiles"""
        
        # Test default profile exists
        config = load_profile('document_black_background_strict')
        assert isinstance(config, dict)
        
        # Test archival profile
        archival_config = load_profile('archival_quality')
        assert archival_config['resolution']['min_dpi_text'] == 400
        assert archival_config['format_integrity']['bit_depth_min'] == 16


class TestMetrics:
    """Test metrics computation"""
    
    def create_test_image(self, width=800, height=600):
        """Create a simple test image"""
        # Create a simple document-like image
        image = np.full((height, width, 3), 240, dtype=np.uint8)  # Light gray background
        
        # Add some "text" (dark rectangles)
        cv2.rectangle(image, (100, 100), (700, 120), (50, 50, 50), -1)
        cv2.rectangle(image, (100, 150), (600, 170), (50, 50, 50), -1)
        cv2.rectangle(image, (100, 200), (650, 220), (50, 50, 50), -1)
        
        return image
    
    def create_test_mask(self, image):
        """Create a simple document mask"""
        # Simple thresholding to create mask
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Dilate to include more area
        kernel = np.ones((20, 20), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        return (mask > 0).astype(np.uint8)
    
    def test_base_metrics(self):
        """Test base metrics functionality"""
        from image_quality_analyzer.metrics.base import BaseMetrics
        
        base = BaseMetrics()
        image = self.create_test_image()
        
        # Test luminance conversion
        luminance = base.convert_to_luminance(image)
        assert luminance.shape == image.shape[:2]
        assert 0 <= luminance.max() <= 1
        assert 0 <= luminance.min() <= 1
        
        # Test document mask creation
        doc_mask = base.create_document_mask(image)
        assert doc_mask.shape == image.shape[:2]
        assert doc_mask.dtype == np.uint8
        assert np.any(doc_mask > 0)  # Should find some document area
    
    def test_sharpness_metrics(self):
        """Test sharpness metrics computation"""
        from image_quality_analyzer.metrics.sharpness import SharpnessMetrics
        
        metrics = SharpnessMetrics()
        image = self.create_test_image()
        doc_mask = self.create_test_mask(image)
        config = {'min_laplacian_variance': 100.0}
        
        result = metrics.compute(image, doc_mask, config)
        
        assert 'laplacian_var' in result
        assert isinstance(result['laplacian_var'], float)
        assert result['laplacian_var'] >= 0
        
        assert 'local_sharpness' in result
        assert 'mean' in result['local_sharpness']
    
    def test_exposure_metrics(self):
        """Test exposure metrics computation"""
        from image_quality_analyzer.metrics.exposure import ExposureMetrics
        
        metrics = ExposureMetrics()
        image = self.create_test_image()
        doc_mask = self.create_test_mask(image)
        config = {}
        
        result = metrics.compute(image, doc_mask, config)
        
        assert 'clipping' in result
        assert 'shadow_clip_pct' in result['clipping']
        assert 'highlight_clip_pct' in result['clipping']
        
        assert 'illumination_uniformity' in result
        assert 'uniformity_ratio' in result['illumination_uniformity']


class TestScoring:
    """Test scoring and flagging system"""
    
    def test_quality_scorer_initialization(self):
        """Test QualityScorer initialization"""
        config = load_default_config()
        scorer = QualityScorer(config)
        
        assert hasattr(scorer, 'config')
        assert hasattr(scorer, 'category_weights')
        assert hasattr(scorer, 'critical_categories')
    
    def test_status_to_score_conversion(self):
        """Test status to score conversion"""
        config = load_default_config()
        scorer = QualityScorer(config)
        
        assert scorer._status_to_score(Status.PASS) == 1.0
        assert scorer._status_to_score(Status.WARN) == 0.75
        assert scorer._status_to_score(Status.FAIL) == 0.0
    
    def test_sharpness_scoring(self):
        """Test sharpness scoring logic"""
        config = load_default_config()
        scorer = QualityScorer(config)
        
        # Test pass case
        metrics = {'laplacian_var': 200.0}
        status = scorer._score_sharpness(metrics, config['sharpness'])
        assert status == Status.PASS
        
        # Test warn case
        metrics = {'laplacian_var': 130.0}
        status = scorer._score_sharpness(metrics, config['sharpness'])
        assert status == Status.WARN
        
        # Test fail case
        metrics = {'laplacian_var': 100.0}
        status = scorer._score_sharpness(metrics, config['sharpness'])
        assert status == Status.FAIL


class TestAnalyzer:
    """Test main analyzer functionality"""
    
    def create_temp_image(self):
        """Create a temporary test image file"""
        image = np.full((600, 800, 3), 240, dtype=np.uint8)
        
        # Add some content
        cv2.rectangle(image, (100, 100), (700, 120), (50, 50, 50), -1)
        cv2.rectangle(image, (100, 150), (600, 170), (50, 50, 50), -1)
        
        # Save to temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
        os.close(temp_fd)
        
        cv2.imwrite(temp_path, image)
        return temp_path
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        config = load_default_config()
        analyzer = ImageQualityAnalyzer(config)
        
        assert hasattr(analyzer, 'config')
        assert hasattr(analyzer, 'metrics_computers')
        assert hasattr(analyzer, 'scorer')
        
        # Check that all expected metrics computers are present
        expected_metrics = {
            'completeness', 'foreign_objects', 'sharpness', 'exposure',
            'contrast', 'color', 'geometry', 'border_background', 
            'noise', 'format_integrity', 'resolution'
        }
        
        assert set(analyzer.metrics_computers.keys()) == expected_metrics
    
    @patch('cv2.imread')
    def test_analyze_image_error_handling(self, mock_imread):
        """Test error handling when image cannot be loaded"""
        mock_imread.return_value = None
        
        analyzer = ImageQualityAnalyzer()
        
        with pytest.raises(ValueError, match="Could not load image"):
            analyzer.analyze_image("nonexistent.jpg")
    
    def test_analyze_image_basic(self):
        """Test basic image analysis functionality"""
        temp_path = self.create_temp_image()
        
        try:
            analyzer = ImageQualityAnalyzer()
            result = analyzer.analyze_image(temp_path)
            
            # Check result structure
            assert 'image_id' in result
            assert 'file_path' in result
            assert 'pixels' in result
            assert 'metrics' in result
            assert 'category_status' in result
            assert 'global' in result
            
            # Check global results
            global_result = result['global']
            assert 'score' in global_result
            assert 'stars' in global_result
            assert 'status' in global_result
            
            # Score should be between 0 and 1
            assert 0 <= global_result['score'] <= 1
            
            # Stars should be 1-4
            assert 1 <= global_result['stars'] <= 4
            
            # Status should be valid
            assert global_result['status'] in ['pass', 'warn', 'fail']
            
        finally:
            os.unlink(temp_path)
    
    def test_export_json_report(self):
        """Test JSON report export"""
        temp_image = self.create_temp_image()
        
        try:
            analyzer = ImageQualityAnalyzer()
            result = analyzer.analyze_image(temp_image)
            
            # Export to temporary file
            temp_fd, temp_json = tempfile.mkstemp(suffix='.json')
            os.close(temp_fd)
            
            try:
                analyzer.export_json_report(result, temp_json)
                
                # Verify file exists and is valid JSON
                assert os.path.exists(temp_json)
                
                with open(temp_json, 'r') as f:
                    loaded_result = json.load(f)
                
                # Should be the same data
                assert loaded_result['image_id'] == result['image_id']
                assert loaded_result['global']['score'] == result['global']['score']
                
            finally:
                os.unlink(temp_json)
                
        finally:
            os.unlink(temp_image)


if __name__ == '__main__':
    pytest.main([__file__])

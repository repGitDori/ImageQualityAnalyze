"""
Foreign Objects Integration Module

Copyright (c) 2025 Dorian Lapi
Licensed under the MIT License - see LICENSE file for details

This module integrates the enhanced foreign objects detection with the 
existing ImageQualityAnalyzer system, providing seamless integration
with your current workflow.

Original Author: Dorian Lapi
"""

import os
import sys
import numpy as np
import cv2
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add paths for imports
sys.path.append(str(Path(__file__).parent))

from enhanced_foreign_objects import EnhancedForeignObjectsDetector

# Try to import existing analyzer components
try:
    sys.path.append(str(Path(__file__).parent / "image_quality_analyzer"))
    from image_quality_analyzer.core.analyzer import ImageQualityAnalyzer
    from image_quality_analyzer.core.base_metrics import BaseMetrics
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False
    print("⚠️ ImageQualityAnalyzer not available - using standalone mode")


class ForeignObjectsIntegration:
    """Integration layer for foreign objects detection with existing analyzer"""
    
    def __init__(self, config_path: str = None):
        """Initialize integration with optional custom configuration"""
        
        self.config_path = config_path or "config_foreign_objects.json"
        self.config = self._load_config()
        
        # Initialize foreign objects detector
        self.detector = EnhancedForeignObjectsDetector(self.config)
        
        # Initialize main analyzer if available
        if ANALYZER_AVAILABLE:
            self.analyzer = ImageQualityAnalyzer()
        else:
            self.analyzer = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading config {self.config_path}: {e}")
        
        # Return default configuration
        return self.detector._get_default_config()
    
    def analyze_image_comprehensive(self, image_path: str) -> Dict[str, Any]:
        """
        Comprehensive image analysis including foreign objects detection
        
        Args:
            image_path: Path to image file
            
        Returns:
            Complete analysis results including foreign objects
        """
        
        print(f"🔍 COMPREHENSIVE ANALYSIS: {Path(image_path).name}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Initialize results structure
        results = {
            'image_path': image_path,
            'image_shape': image.shape,
            'analysis_type': 'comprehensive_with_foreign_objects',
            'overall_pass': True,
            'failure_reasons': []
        }
        
        # Run main image quality analysis if available
        if self.analyzer:
            try:
                main_results = self.analyzer.analyze_image(image_path)
                results['main_analysis'] = main_results
                
                # Check if main analysis failed
                if 'overall_score' in main_results and main_results['overall_score'] < 0.7:
                    results['overall_pass'] = False
                    results['failure_reasons'].append("Failed standard image quality checks")
                    
            except Exception as e:
                print(f"⚠️ Main analysis error: {e}")
                results['main_analysis'] = {'error': str(e)}
        
        # Create document mask (simplified - would normally use document detection)
        doc_mask = self._create_document_mask(image)
        
        # Run foreign objects analysis
        try:
            foreign_objects_results = self.detector.analyze_foreign_objects(image, doc_mask)
            results['foreign_objects'] = foreign_objects_results
            
            # Check foreign objects failure
            if foreign_objects_results['foreign_object_flag']:
                results['overall_pass'] = False
                results['failure_reasons'].extend(foreign_objects_results['failure_reasons'])
            
        except Exception as e:
            print(f"❌ Foreign objects analysis error: {e}")
            results['foreign_objects'] = {'error': str(e)}
        
        # Generate final assessment
        results['final_assessment'] = self._generate_final_assessment(results)
        
        return results
    
    def batch_analyze_with_foreign_objects(self, image_paths: List[str], 
                                         output_dir: str = "batch_analysis_output") -> Dict[str, Any]:
        """
        Batch analysis of multiple images with foreign objects detection
        
        Args:
            image_paths: List of image file paths
            output_dir: Directory for output files
            
        Returns:
            Batch analysis results
        """
        
        print(f"📦 BATCH ANALYSIS: {len(image_paths)} images")
        print("="*50)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        batch_results = {
            'total_images': len(image_paths),
            'processed_images': 0,
            'passed_images': 0,
            'failed_images': 0,
            'failed_foreign_objects': 0,
            'individual_results': [],
            'summary_by_failure_type': {},
            'recommendations': []
        }
        
        failed_images = []
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"\n📸 Processing {i}/{len(image_paths)}: {Path(image_path).name}")
            
            try:
                # Analyze individual image
                result = self.analyze_image_comprehensive(image_path)
                batch_results['individual_results'].append(result)
                batch_results['processed_images'] += 1
                
                # Update counters
                if result['overall_pass']:
                    batch_results['passed_images'] += 1
                else:
                    batch_results['failed_images'] += 1
                    failed_images.append(result)
                    
                    # Check if foreign objects caused failure
                    if (result.get('foreign_objects', {}).get('foreign_object_flag', False)):
                        batch_results['failed_foreign_objects'] += 1
                
                # Save individual result
                result_file = os.path.join(output_dir, f"analysis_{i:03d}_{Path(image_path).stem}.json")
                with open(result_file, 'w') as f:
                    json.dump(self._make_json_serializable(result), f, indent=2)
                
                print(f"   {'✅ PASSED' if result['overall_pass'] else '❌ FAILED'}")
                
            except Exception as e:
                print(f"❌ Error processing {image_path}: {e}")
                batch_results['individual_results'].append({
                    'image_path': image_path,
                    'error': str(e),
                    'overall_pass': False
                })
        
        # Generate batch summary
        batch_results['failure_analysis'] = self._analyze_batch_failures(failed_images)
        batch_results['batch_recommendations'] = self._generate_batch_recommendations(failed_images)
        
        # Save batch summary
        summary_file = os.path.join(output_dir, "batch_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(self._make_json_serializable(batch_results), f, indent=2)
        
        self._print_batch_summary(batch_results)
        
        return batch_results
    
    def _create_document_mask(self, image: np.ndarray) -> np.ndarray:
        """Create a simple document mask (placeholder for proper document detection)"""
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Simple threshold to separate document from background
        _, mask = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Clean up mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask.astype(np.uint8)
    
    def _generate_final_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final assessment combining all analysis results"""
        
        assessment = {
            'overall_quality': 'PASS' if results['overall_pass'] else 'FAIL',
            'confidence_score': 0.0,
            'primary_issues': [],
            'severity': 'NONE'
        }
        
        # Analyze main quality issues
        if 'main_analysis' in results and not results.get('main_analysis', {}).get('error'):
            main = results['main_analysis']
            if 'overall_score' in main:
                assessment['confidence_score'] = main['overall_score']
                if main['overall_score'] < 0.5:
                    assessment['primary_issues'].append('Poor overall image quality')
        
        # Analyze foreign objects issues
        if 'foreign_objects' in results and not results.get('foreign_objects', {}).get('error'):
            foreign = results['foreign_objects']
            if foreign.get('foreign_object_flag', False):
                coverage = foreign.get('foreign_object_area_pct', 0)
                if coverage > 5.0:
                    assessment['severity'] = 'HIGH'
                    assessment['primary_issues'].append(f'Significant foreign object interference ({coverage:.1f}%)')
                elif coverage > 2.0:
                    assessment['severity'] = 'MEDIUM'
                    assessment['primary_issues'].append(f'Moderate foreign object interference ({coverage:.1f}%)')
                else:
                    assessment['severity'] = 'LOW'
                    assessment['primary_issues'].append(f'Minor foreign object interference ({coverage:.1f}%)')
        
        # Set severity if not already set
        if assessment['severity'] == 'NONE' and not results['overall_pass']:
            assessment['severity'] = 'MEDIUM'
        
        return assessment
    
    def _analyze_batch_failures(self, failed_images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze common failure patterns in batch results"""
        
        failure_types = {
            'foreign_objects_clips': 0,
            'foreign_objects_black': 0,
            'foreign_objects_shadows': 0,
            'foreign_objects_combined': 0,
            'quality_issues': 0
        }
        
        for result in failed_images:
            foreign = result.get('foreign_objects', {})
            
            if foreign.get('foreign_object_flag', False):
                details = foreign.get('detailed_results', {})
                
                if details.get('clips_and_tools', {}).get('clip_flag', False):
                    failure_types['foreign_objects_clips'] += 1
                
                if details.get('black_objects', {}).get('black_object_flag', False):
                    failure_types['foreign_objects_black'] += 1
                
                if details.get('shadows_reflections', {}).get('shadow_flag', False):
                    failure_types['foreign_objects_shadows'] += 1
                
                if (details.get('clips_and_tools', {}).get('clip_flag', False) and
                    details.get('black_objects', {}).get('black_object_flag', False)):
                    failure_types['foreign_objects_combined'] += 1
            
            if 'main_analysis' in result:
                failure_types['quality_issues'] += 1
        
        return failure_types
    
    def _generate_batch_recommendations(self, failed_images: List[Dict[str, Any]]) -> List[str]:
        """Generate batch-level recommendations"""
        
        recommendations = []
        
        if not failed_images:
            recommendations.append("✅ All images passed quality checks")
            return recommendations
        
        failure_count = len(failed_images)
        foreign_failures = sum(1 for r in failed_images 
                              if r.get('foreign_objects', {}).get('foreign_object_flag', False))
        
        if foreign_failures > failure_count * 0.5:
            recommendations.extend([
                "🔴 CRITICAL: High foreign object failure rate detected",
                "📎 Review document capture setup to minimize clips/tools in frame",
                "👋 Train operators to keep hands away from document during capture",
                "💡 Improve lighting setup to reduce shadows and reflections"
            ])
        
        if foreign_failures > 0:
            recommendations.extend([
                "📋 Implement pre-capture checklist for foreign object removal",
                "🎯 Consider automated document area detection to focus analysis",
                "⚙️ Adjust foreign object detection sensitivity if needed"
            ])
        
        return recommendations
    
    def _print_batch_summary(self, batch_results: Dict[str, Any]) -> None:
        """Print formatted batch analysis summary"""
        
        print(f"\n📊 BATCH ANALYSIS SUMMARY")
        print("="*50)
        print(f"📁 Total Images: {batch_results['total_images']}")
        print(f"✅ Passed: {batch_results['passed_images']}")
        print(f"❌ Failed: {batch_results['failed_images']}")
        print(f"🔍 Foreign Objects Failures: {batch_results['failed_foreign_objects']}")
        
        if batch_results['failed_images'] > 0:
            failure_rate = (batch_results['failed_images'] / batch_results['total_images']) * 100
            print(f"📈 Failure Rate: {failure_rate:.1f}%")
        
        # Print failure analysis
        failure_analysis = batch_results.get('failure_analysis', {})
        if any(failure_analysis.values()):
            print(f"\n🔍 FAILURE BREAKDOWN:")
            for failure_type, count in failure_analysis.items():
                if count > 0:
                    readable_type = failure_type.replace('_', ' ').title()
                    print(f"   • {readable_type}: {count}")
        
        # Print recommendations
        recommendations = batch_results.get('batch_recommendations', [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
    
    def _make_json_serializable(self, obj):
        """Convert numpy arrays and other non-serializable objects for JSON"""
        
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj


def create_integrated_workflow_demo():
    """Create a demonstration of the integrated workflow"""
    
    print("🔧 INTEGRATED WORKFLOW DEMONSTRATION")
    print("="*50)
    
    # Initialize integration
    integration = ForeignObjectsIntegration()
    
    # Check if main analyzer is available
    if integration.analyzer:
        print("✅ Main ImageQualityAnalyzer integrated successfully")
    else:
        print("⚠️ Running in standalone foreign objects mode")
    
    # Create sample images if they don't exist
    sample_images = []
    
    # Use existing sample if available
    if os.path.exists("sample_document.jpg"):
        sample_images.append("sample_document.jpg")
    
    # Create test images for demonstration
    from test_enhanced_foreign_objects import (
        create_test_image_with_clip,
        create_test_image_with_black_object,
        create_test_image_with_both
    )
    
    sample_images.extend([
        create_test_image_with_clip(save_path="integration_test_clip.jpg"),
        create_test_image_with_black_object(save_path="integration_test_black.jpg"),
        create_test_image_with_both(save_path="integration_test_combined.jpg")
    ])
    
    # Run batch analysis
    print(f"\n🔄 Running integrated batch analysis...")
    results = integration.batch_analyze_with_foreign_objects(
        sample_images, 
        "integrated_analysis_output"
    )
    
    print(f"\n🎉 Integrated workflow demonstration completed!")
    print(f"📁 Results saved to: integrated_analysis_output/")
    
    return results


if __name__ == "__main__":
    try:
        results = create_integrated_workflow_demo()
        
        print(f"\n📋 Integration Summary:")
        print(f"   Analyzer Available: {ANALYZER_AVAILABLE}")
        print(f"   Images Processed: {results['processed_images']}")
        print(f"   Foreign Object Failures: {results['failed_foreign_objects']}")
        print(f"\n🔍 Enhanced foreign objects detection is now integrated!")
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
        import traceback
        traceback.print_exc()

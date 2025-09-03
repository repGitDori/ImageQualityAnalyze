"""
Enhanced Focus Detection and Customization for Image Quality Analyzer

This module provides customized focus detection capabilities with specific 
"out of focus" flagging and detailed reporting for batch analysis.

Features:
- Enhanced sharpness detection with multiple algorithms
- Specific "out of focus" labeling and reasons
- Customizable thresholds for different focus levels
- Detailed focus analysis breakdown in reports
- Batch processing with focus-specific filtering
"""

import json
import numpy as np
from typing import Dict, Any, List, Tuple
from pathlib import Path
from image_quality_analyzer import ImageQualityAnalyzer


class EnhancedFocusDetector:
    """Enhanced focus detection with customizable thresholds and detailed reporting"""
    
    def __init__(self, config_path: str = None):
        """Initialize with custom focus detection configuration"""
        
        # Load base configuration
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._get_default_focus_config()
        
        # Initialize analyzer with our custom config
        self.analyzer = ImageQualityAnalyzer(self.config)
    
    def _get_default_focus_config(self) -> Dict[str, Any]:
        """Get default configuration with enhanced focus detection thresholds"""
        
        return {
            "sharpness": {
                # Enhanced focus detection thresholds
                "min_laplacian_variance": 200.0,     # Sharp/in-focus
                "warn_laplacian_variance": 120.0,    # Slightly soft
                "fail_laplacian_variance": 80.0,     # Out of focus
                "critical_fail_laplacian": 50.0,     # Severely out of focus
                
                # Additional focus quality measures
                "min_edge_density": 0.015,           # Minimum edge content
                "min_high_freq_energy": 0.001,       # High frequency content
                "local_sharpness_threshold": 100.0,  # Local variation threshold
                
                # Focus classification labels
                "focus_classification": {
                    "excellent": {"min_laplacian": 300.0, "description": "Perfectly Sharp - Professional Quality"},
                    "good": {"min_laplacian": 200.0, "description": "Sharp - Suitable for Most Uses"}, 
                    "acceptable": {"min_laplacian": 120.0, "description": "Slightly Soft - Usable with Minor Issues"},
                    "poor": {"min_laplacian": 80.0, "description": "Out of Focus - Noticeable Blur"},
                    "unusable": {"min_laplacian": 0.0, "description": "Severely Out of Focus - Unusable"}
                }
            },
            "scoring": {
                "pass_score_threshold": 0.75,
                "warn_score_threshold": 0.60
            },
            # Include other necessary config sections
            "exposure": {"max_shadow_clip_pct": 2.0, "max_highlight_clip_pct": 2.0},
            "contrast": {"min_global_contrast": 0.15, "warn_global_contrast": 0.10},
            "geometry": {"max_skew_deg_pass": 2.0, "max_skew_deg_warn": 5.0},
            "resolution": {"min_dpi_text": 150},
            "completeness": {"min_content_bbox_coverage": 0.80},
            "border_background": {"max_side_margin_ratio_pass": 0.15},
            "noise": {"max_bg_noise_std": 0.08},
            "format_integrity": {"bit_depth_min": 8}
        }
    
    def analyze_focus_quality(self, image_path: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Analyze image with enhanced focus detection
        
        Args:
            image_path: Path to image file
            verbose: Print detailed focus analysis
            
        Returns:
            Dictionary with enhanced focus analysis results
        """
        
        # Run standard analysis
        results = self.analyzer.analyze_image(image_path)
        
        # Enhance with focus-specific analysis
        focus_analysis = self._analyze_focus_details(results)
        results['focus_analysis'] = focus_analysis
        
        # Add focus-specific recommendations
        focus_recommendations = self._generate_focus_recommendations(focus_analysis)
        results['focus_recommendations'] = focus_recommendations
        
        if verbose:
            self._print_focus_report(results, image_path)
        
        return results
    
    def _analyze_focus_details(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and analyze focus-specific details from results"""
        
        # Get sharpness metrics
        sharpness_metrics = results['metrics'].get('sharpness', {})
        
        laplacian_var = sharpness_metrics.get('laplacian_var', 0.0)
        edge_density = sharpness_metrics.get('edge_density', 0.0)
        gradient_mag = sharpness_metrics.get('gradient_magnitude_mean', 0.0)
        
        # Get frequency analysis
        freq_metrics = sharpness_metrics.get('frequency_metrics', {})
        high_freq_energy = freq_metrics.get('high_freq_energy', 0.0)
        
        # Local sharpness statistics
        local_sharpness = sharpness_metrics.get('local_sharpness', {})
        local_mean = local_sharpness.get('mean', 0.0)
        local_std = local_sharpness.get('std', 0.0)
        
        # Determine focus quality level
        focus_level = self._classify_focus_level(
            laplacian_var, edge_density, high_freq_energy, local_mean
        )
        
        # Analyze focus issues
        focus_issues = self._identify_focus_issues(
            laplacian_var, edge_density, local_std, gradient_mag
        )
        
        # Calculate confidence score
        confidence = self._calculate_focus_confidence(
            laplacian_var, edge_density, high_freq_energy
        )
        
        return {
            'focus_level': focus_level,
            'focus_score': laplacian_var,
            'focus_issues': focus_issues,
            'confidence': confidence,
            'metrics_breakdown': {
                'primary_sharpness': laplacian_var,
                'edge_content': edge_density,
                'high_freq_energy': high_freq_energy,
                'local_variation': local_std,
                'gradient_strength': gradient_mag
            }
        }
    
    def _classify_focus_level(self, laplacian_var: float, edge_density: float, 
                            high_freq_energy: float, local_mean: float) -> str:
        """Classify focus quality into specific levels"""
        
        config = self.config['sharpness']
        
        # Multiple criteria for robust classification
        criteria_score = 0
        
        # Primary criterion: Laplacian variance
        if laplacian_var >= config['min_laplacian_variance']:
            criteria_score += 3
        elif laplacian_var >= config['warn_laplacian_variance']:
            criteria_score += 2
        elif laplacian_var >= config['fail_laplacian_variance']:
            criteria_score += 1
        
        # Secondary criterion: Edge density
        if edge_density >= config['min_edge_density']:
            criteria_score += 1
        
        # Tertiary criterion: High frequency content
        if high_freq_energy >= config['min_high_freq_energy']:
            criteria_score += 1
        
        # Classification based on combined score
        if criteria_score >= 4:
            return 'excellent'
        elif criteria_score >= 3:
            return 'good'
        elif criteria_score >= 2:
            return 'acceptable'
        elif criteria_score >= 1:
            return 'poor'
        else:
            return 'unusable'
    
    def _identify_focus_issues(self, laplacian_var: float, edge_density: float,
                             local_std: float, gradient_mag: float) -> List[str]:
        """Identify specific focus-related issues"""
        
        issues = []
        config = self.config['sharpness']
        
        # Primary focus issues
        if laplacian_var < config['critical_fail_laplacian']:
            issues.append("Severely out of focus - major blur detected")
        elif laplacian_var < config['fail_laplacian_variance']:
            issues.append("Out of focus - noticeable blur")
        elif laplacian_var < config['warn_laplacian_variance']:
            issues.append("Slightly soft focus - minor blur")
        
        # Edge content issues
        if edge_density < config['min_edge_density'] * 0.5:
            issues.append("Very low edge content - possible motion blur or extreme defocus")
        elif edge_density < config['min_edge_density']:
            issues.append("Low edge content - soft focus or low contrast")
        
        # Local variation issues
        if local_std > 5000:
            issues.append("Inconsistent focus across image - focus on wrong area")
        elif local_std < 100:
            issues.append("Uniform blur - camera shake or motion blur")
        
        # Gradient strength issues
        if gradient_mag < 5.0:
            issues.append("Very weak gradients - severe focus or contrast issues")
        
        return issues
    
    def _calculate_focus_confidence(self, laplacian_var: float, edge_density: float,
                                  high_freq_energy: float) -> float:
        """Calculate confidence in focus assessment"""
        
        # Confidence based on multiple metrics alignment
        confidence_factors = []
        
        # Factor 1: Absolute sharpness level
        if laplacian_var > 300:
            confidence_factors.append(0.9)
        elif laplacian_var > 150:
            confidence_factors.append(0.8)
        elif laplacian_var > 80:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.6)
        
        # Factor 2: Edge content sufficiency
        if edge_density > 0.02:
            confidence_factors.append(0.9)
        elif edge_density > 0.015:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.7)
        
        # Factor 3: Frequency content
        if high_freq_energy > 0.002:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.8)
        
        return float(np.mean(confidence_factors))
    
    def _generate_focus_recommendations(self, focus_analysis: Dict[str, Any]) -> List[str]:
        """Generate specific focus improvement recommendations"""
        
        recommendations = []
        focus_level = focus_analysis['focus_level']
        focus_issues = focus_analysis['focus_issues']
        confidence = focus_analysis['confidence']
        
        # Level-specific recommendations
        if focus_level in ['poor', 'unusable']:
            recommendations.append("🔴 CRITICAL: Image failed for OUT OF FOCUS - retake required")
            recommendations.append("📸 Use auto-focus or tap screen to focus on document")
            recommendations.append("🎯 Ensure proper distance - too close causes focus issues")
            recommendations.append("📱 Use tripod or stable surface to reduce camera shake")
        
        elif focus_level == 'acceptable':
            recommendations.append("🟡 WARNING: Image is slightly soft - consider retaking for better quality")
            recommendations.append("🔧 Fine-tune focus or move slightly closer/further")
        
        # Issue-specific recommendations
        for issue in focus_issues:
            if "motion blur" in issue.lower():
                recommendations.append("⚡ Use faster shutter speed or better stabilization")
            elif "camera shake" in issue.lower():
                recommendations.append("📱 Hold camera steady or use timer/remote")
            elif "inconsistent focus" in issue.lower():
                recommendations.append("🎯 Focus on center of document, not edges or background")
            elif "low contrast" in issue.lower():
                recommendations.append("💡 Improve lighting to enhance detail visibility")
        
        # Confidence-based recommendations
        if confidence < 0.7:
            recommendations.append("⚠️ Focus assessment has lower confidence - verify manually")
        
        return recommendations
    
    def _print_focus_report(self, results: Dict[str, Any], image_path: str) -> None:
        """Print detailed focus quality report"""
        
        focus_analysis = results['focus_analysis']
        global_results = results.get('global', {})
        focus_recommendations = results['focus_recommendations']
        
        print(f"\n{'='*60}")
        print(f"🔍 FOCUS QUALITY ANALYSIS: {Path(image_path).name}")
        print(f"{'='*60}")
        
        # Overall status
        overall_status = global_results.get('status', 'unknown')
        overall_score = global_results.get('score', 0.0)
        
        print(f"\n📊 OVERALL ASSESSMENT:")
        print(f"   Score: {overall_score:.3f}")
        print(f"   Status: {overall_status.upper()}")
        
        # Focus-specific analysis
        focus_level = focus_analysis['focus_level']
        focus_score = focus_analysis['focus_score']
        confidence = focus_analysis['confidence']
        
        focus_labels = self.config['sharpness'].get('focus_classification', {
            'excellent': {'description': 'Perfectly Sharp - Professional Quality'},
            'good': {'description': 'Sharp - Suitable for Most Uses'}, 
            'acceptable': {'description': 'Slightly Soft - Usable with Minor Issues'},
            'poor': {'description': 'Out of Focus - Noticeable Blur'},
            'unusable': {'description': 'Severely Out of Focus - Unusable'}
        })
        focus_description = focus_labels.get(focus_level, {}).get('description', "Unknown")
        
        print(f"\n🎯 FOCUS ANALYSIS:")
        print(f"   Focus Level: {focus_level.upper()}")
        print(f"   Description: {focus_description}")
        print(f"   Focus Score: {focus_score:.1f}")
        print(f"   Confidence: {confidence:.1%}")
        
        # Detailed metrics
        metrics = focus_analysis['metrics_breakdown']
        print(f"\n📈 FOCUS METRICS BREAKDOWN:")
        print(f"   Primary Sharpness (Laplacian): {metrics['primary_sharpness']:.1f}")
        print(f"   Edge Content: {metrics['edge_content']:.4f}")
        print(f"   High Frequency Energy: {metrics['high_freq_energy']:.6f}")
        print(f"   Local Variation: {metrics['local_variation']:.1f}")
        print(f"   Gradient Strength: {metrics['gradient_strength']:.1f}")
        
        # Issues detected
        focus_issues = focus_analysis['focus_issues']
        if focus_issues:
            print(f"\n🚨 FOCUS ISSUES DETECTED:")
            for i, issue in enumerate(focus_issues, 1):
                print(f"   {i}. {issue}")
        
        # Recommendations
        if focus_recommendations:
            print(f"\n💡 FOCUS RECOMMENDATIONS:")
            for i, rec in enumerate(focus_recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Summary decision
        print(f"\n{'='*60}")
        if focus_level in ['poor', 'unusable']:
            print(f"🔴 DECISION: IMAGE FAILED FOR OUT OF FOCUS")
            print(f"   Reason: {focus_description}")
            print(f"   Action: RETAKE REQUIRED")
        elif focus_level == 'acceptable':
            print(f"🟡 DECISION: IMAGE USABLE BUT SOFT")
            print(f"   Reason: Minor focus issues detected")
            print(f"   Action: Consider retaking for optimal quality")
        else:
            print(f"🟢 DECISION: IMAGE FOCUS ACCEPTABLE")
            print(f"   Quality: {focus_description}")
            print(f"   Action: Ready for use")
        
        print(f"{'='*60}\n")
    
    def batch_analyze_focus(self, image_paths: List[str], 
                          output_file: str = None) -> Dict[str, Any]:
        """
        Analyze multiple images with focus-specific batch reporting
        
        Args:
            image_paths: List of image file paths
            output_file: Optional JSON output file path
            
        Returns:
            Dictionary with batch analysis results
        """
        
        print(f"\n🔍 BATCH FOCUS ANALYSIS - {len(image_paths)} images")
        print("="*60)
        
        results = []
        focus_summary = {
            'excellent': 0,
            'good': 0, 
            'acceptable': 0,
            'poor': 0,
            'unusable': 0
        }
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"\n[{i}/{len(image_paths)}] Analyzing: {Path(image_path).name}")
            
            try:
                # Analyze image
                result = self.analyze_focus_quality(image_path, verbose=False)
                
                # Extract focus info
                focus_level = result['focus_analysis']['focus_level']
                focus_score = result['focus_analysis']['focus_score']
                overall_score = result['global']['score']
                overall_status = result['global']['status']
                
                # Update summary
                focus_summary[focus_level] += 1
                
                # Store result
                result_summary = {
                    'image_path': image_path,
                    'filename': Path(image_path).name,
                    'focus_level': focus_level,
                    'focus_score': focus_score,
                    'overall_score': overall_score,
                    'overall_status': overall_status,
                    'focus_issues': result['focus_analysis']['focus_issues'],
                    'focus_recommendations': result['focus_recommendations']
                }
                results.append(result_summary)
                
                # Print quick status
                if focus_level in ['poor', 'unusable']:
                    print(f"   🔴 FAILED - OUT OF FOCUS ({focus_level})")
                elif focus_level == 'acceptable':
                    print(f"   🟡 SOFT - Minor focus issues")
                else:
                    print(f"   🟢 GOOD - Focus acceptable")
                
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                results.append({
                    'image_path': image_path,
                    'filename': Path(image_path).name,
                    'error': str(e)
                })
        
        # Compile batch results
        batch_results = {
            'summary': {
                'total_images': len(image_paths),
                'focus_distribution': focus_summary,
                'out_of_focus_count': focus_summary['poor'] + focus_summary['unusable'],
                'usable_count': len(image_paths) - (focus_summary['poor'] + focus_summary['unusable'])
            },
            'detailed_results': results
        }
        
        # Print batch summary
        self._print_batch_summary(batch_results)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(batch_results, f, indent=2)
            print(f"\n📁 Results saved to: {output_file}")
        
        return batch_results
    
    def _print_batch_summary(self, batch_results: Dict[str, Any]) -> None:
        """Print summary of batch focus analysis"""
        
        summary = batch_results['summary']
        focus_dist = summary['focus_distribution']
        
        print(f"\n{'='*60}")
        print(f"📊 BATCH FOCUS ANALYSIS SUMMARY")
        print(f"{'='*60}")
        
        print(f"\n📈 FOCUS QUALITY DISTRIBUTION:")
        print(f"   🟢 Excellent: {focus_dist['excellent']} images")
        print(f"   🟢 Good: {focus_dist['good']} images") 
        print(f"   🟡 Acceptable: {focus_dist['acceptable']} images")
        print(f"   🔴 Poor (Out of Focus): {focus_dist['poor']} images")
        print(f"   🔴 Unusable (Severely Out of Focus): {focus_dist['unusable']} images")
        
        print(f"\n🎯 KEY STATISTICS:")
        total = summary['total_images']
        usable = summary['usable_count']
        out_of_focus = summary['out_of_focus_count']
        
        print(f"   Total Images: {total}")
        print(f"   Usable Images: {usable} ({usable/total*100:.1f}%)")
        print(f"   Out of Focus: {out_of_focus} ({out_of_focus/total*100:.1f}%)")
        
        if out_of_focus > 0:
            print(f"\n🔴 IMAGES FAILED FOR OUT OF FOCUS:")
            for result in batch_results['detailed_results']:
                if result.get('focus_level') in ['poor', 'unusable']:
                    filename = result['filename']
                    level = result['focus_level']
                    issues = result.get('focus_issues', [])
                    print(f"   • {filename} - {level.upper()}")
                    if issues:
                        main_issue = issues[0] if issues else "Focus quality below threshold"
                        print(f"     Reason: {main_issue}")
        
        print(f"{'='*60}")


def main():
    """Example usage of enhanced focus detection"""
    
    # Create enhanced focus detector
    detector = EnhancedFocusDetector()
    
    # Analyze single image
    print("🔍 SINGLE IMAGE ANALYSIS:")
    result = detector.analyze_focus_quality("sample_document.jpg")
    
    # Example batch analysis
    print("\n🔍 BATCH ANALYSIS EXAMPLE:")
    sample_images = [
        "sample_document.jpg",
        # Add more image paths here
    ]
    
    # Only analyze existing images
    existing_images = [img for img in sample_images if Path(img).exists()]
    
    if existing_images:
        batch_results = detector.batch_analyze_focus(
            existing_images, 
            output_file="focus_analysis_results.json"
        )
    else:
        print("No sample images found. Please add image paths to analyze.")


if __name__ == "__main__":
    main()

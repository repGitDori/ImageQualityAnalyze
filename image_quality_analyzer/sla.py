"""
SLA (Service Level Agreement) evaluation system
Compares analysis results against defined quality standards
"""

from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SLAComplianceLevel(Enum):
    """SLA compliance levels"""
    EXCELLENT = "excellent"
    COMPLIANT = "compliant"  
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"


class SLAEvaluator:
    """Evaluates image quality results against Custom Quality Standards (SLA)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sla_config = config.get('sla', {})
        self.quality_standards = config.get('quality_standards', {})
        self.enabled = self.sla_config.get('enabled', False)
        
    def evaluate_sla_compliance(self, metrics: Dict[str, Any], 
                               category_status: Dict[str, str],
                               global_score: float) -> Dict[str, Any]:
        """
        Evaluate SLA compliance for analysis results
        
        Args:
            metrics: Raw metrics from analysis
            category_status: Pass/warn/fail status for each category  
            global_score: Overall quality score
            
        Returns:
            Dict containing SLA evaluation results
        """
        
        if not self.enabled:
            return {
                "enabled": False,
                "message": "SLA evaluation disabled"
            }
            
        sla_name = self.sla_config.get('name', 'Custom Quality Standards')
        sla_description = self.sla_config.get('description', 'Quality evaluation based on custom thresholds')
        
        # Use Custom Quality Standards as SLA requirements
        # Check overall score requirement (from scoring config)
        scoring_config = self.config.get('scoring', {})
        min_overall_score = scoring_config.get('pass_score_threshold', 0.80)
        score_compliant = global_score >= min_overall_score
        
        # Check category failure limits (configurable or default)
        sla_requirements = self.sla_config.get('requirements', {})
        max_fail_categories = sla_requirements.get('max_fail_categories', 1)
        fail_count = sum(1 for status in category_status.values() if status == 'fail')
        category_fail_compliant = fail_count <= max_fail_categories
        
        # Check required pass categories (configurable)
        required_pass_categories = sla_requirements.get('required_pass_categories', [])
        required_pass_violations = []
        for category in required_pass_categories:
            if category_status.get(category, 'fail') != 'pass':
                required_pass_violations.append(category)
        required_pass_compliant = len(required_pass_violations) == 0
        
        # Check performance targets using Custom Quality Standards
        performance_violations = self._check_custom_quality_standards(metrics, category_status)
        performance_compliant = len(performance_violations) == 0
        
        # Determine overall compliance level
        overall_compliant = (score_compliant and 
                           category_fail_compliant and 
                           required_pass_compliant and
                           performance_compliant)
        
        compliance_level = self._determine_compliance_level(global_score)
        compliance_info = self.sla_config.get('compliance_levels', {}).get(compliance_level.value, {})
        
        # Generate SLA-specific recommendations
        sla_recommendations = self._generate_sla_recommendations(
            score_compliant, category_fail_compliant, required_pass_compliant,
            performance_compliant, required_pass_violations, performance_violations,
            min_overall_score, max_fail_categories
        )
        
        return {
            "enabled": True,
            "sla_name": sla_name,
            "sla_description": sla_description,
            "compliance": {
                "level": compliance_level.value,
                "description": compliance_info.get('description', ''),
                "overall_compliant": overall_compliant,
                "score": global_score,
                "requirements_met": {
                    "minimum_score": {
                        "required": min_overall_score,
                        "actual": global_score,
                        "compliant": score_compliant
                    },
                    "category_failures": {
                        "max_allowed": max_fail_categories,
                        "actual": fail_count,
                        "compliant": category_fail_compliant
                    },
                    "required_categories": {
                        "required": required_pass_categories,
                        "violations": required_pass_violations,
                        "compliant": required_pass_compliant
                    },
                    "performance_targets": {
                        "violations": performance_violations,
                        "compliant": performance_compliant
                    }
                }
            },
            "recommendations": sla_recommendations
        }
    
    def _check_custom_quality_standards(self, metrics: Dict[str, Any], 
                                       category_status: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check metrics against Custom Quality Standards thresholds"""
        violations = []
        
        # Check each quality standard category that failed
        for category, status in category_status.items():
            if status == 'fail':
                category_config = self.quality_standards.get(category, {})
                violation_info = self._get_violation_details(category, metrics, category_config)
                if violation_info:
                    violations.append(violation_info)
        
        return violations
    
    def _get_violation_details(self, category: str, metrics: Dict[str, Any], 
                             category_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get detailed violation information for a specific category"""
        
        category_metrics = metrics.get(category, {})
        threshold = category_config.get('threshold')
        
        if category == 'sharpness':
            actual = category_metrics.get('laplacian_var', 0)
            if threshold and actual < threshold:
                return {
                    'category': 'Sharpness',
                    'metric': 'Laplacian Variance',
                    'required': f'>= {threshold}',
                    'actual': round(actual, 2),
                    'description': f'Image sharpness below quality standard ({actual:.1f} < {threshold})'
                }
                
        elif category == 'contrast':
            actual = category_metrics.get('global_contrast', 0)
            if threshold and actual < threshold:
                return {
                    'category': 'Contrast',
                    'metric': 'Global Contrast',
                    'required': f'>= {threshold}',
                    'actual': round(actual, 3),
                    'description': f'Image contrast below quality standard ({actual:.3f} < {threshold})'
                }
                
        elif category == 'resolution':
            actual_x = category_metrics.get('effective_dpi_x', 0)
            actual_y = category_metrics.get('effective_dpi_y', 0)
            actual_min = min(actual_x, actual_y)
            if threshold and actual_min < threshold:
                return {
                    'category': 'Resolution',
                    'metric': 'Minimum DPI',
                    'required': f'>= {threshold} DPI',
                    'actual': f'{actual_min} DPI',
                    'description': f'Image resolution below quality standard ({actual_min} DPI < {threshold} DPI)'
                }
                
        elif category == 'geometry':
            actual = category_metrics.get('skew_angle_abs', 0)
            if threshold and actual > threshold:
                return {
                    'category': 'Geometry',
                    'metric': 'Skew Angle',
                    'required': f'<= {threshold}°',
                    'actual': f'{round(actual, 2)}°',
                    'description': f'Document skew above quality standard ({actual:.1f}° > {threshold}°)'
                }
                
        elif category == 'exposure':
            # Check multiple exposure metrics
            shadow_clip = category_metrics.get('clipping', {}).get('shadow_clip_pct', 0)
            highlight_clip = category_metrics.get('clipping', {}).get('highlight_clip_pct', 0)
            
            # Use exposure config thresholds if available
            exposure_config = self.config.get('exposure', {})
            max_shadow = exposure_config.get('max_shadow_clip_pct', 0.5)
            max_highlight = exposure_config.get('max_highlight_clip_pct', 0.5)
            
            if shadow_clip > max_shadow or highlight_clip > max_highlight:
                return {
                    'category': 'Exposure',
                    'metric': 'Clipping',
                    'required': f'Shadow <= {max_shadow}%, Highlight <= {max_highlight}%',
                    'actual': f'Shadow: {shadow_clip:.1f}%, Highlight: {highlight_clip:.1f}%',
                    'description': f'Image exposure clipping exceeds quality standards'
                }
        
        return None
        
    def _determine_compliance_level(self, score: float) -> SLAComplianceLevel:
        """Determine compliance level based on score and requirements"""
        compliance_levels = self.sla_config.get('compliance_levels', {})
        
        excellent_min = compliance_levels.get('excellent', {}).get('min_score', 0.90)
        compliant_min = compliance_levels.get('compliant', {}).get('min_score', 0.75)
        warning_min = compliance_levels.get('warning', {}).get('min_score', 0.60)
        
        if score >= excellent_min:
            return SLAComplianceLevel.EXCELLENT
        elif score >= compliant_min:
            return SLAComplianceLevel.COMPLIANT
        elif score >= warning_min:
            return SLAComplianceLevel.WARNING
        else:
            return SLAComplianceLevel.NON_COMPLIANT
    
    def _generate_sla_recommendations(self, score_compliant: bool, 
                                    category_fail_compliant: bool,
                                    required_pass_compliant: bool,
                                    performance_compliant: bool,
                                    required_pass_violations: List[str],
                                    performance_violations: List[Dict[str, Any]],
                                    min_score: float,
                                    max_fail_categories: int) -> List[str]:
        """Generate SLA-specific recommendations"""
        recommendations = []
        
        if not score_compliant:
            recommendations.append(
                f"🎯 SLA REQUIREMENT: Achieve minimum overall score of {min_score:.1%} "
                f"for SLA compliance"
            )
        
        if not category_fail_compliant:
            recommendations.append(
                f"🎯 SLA REQUIREMENT: Reduce failing categories to {max_fail_categories} or fewer "
                f"for SLA compliance"
            )
        
        if not required_pass_compliant:
            categories_str = ', '.join(required_pass_violations)
            recommendations.append(
                f"🎯 SLA REQUIREMENT: These critical categories must pass: {categories_str}"
            )
        
        if not performance_compliant:
            for violation in performance_violations[:3]:  # Show top 3 violations
                recommendations.append(
                    f"🎯 SLA TARGET: {violation['description']}"
                )
        
        if score_compliant and category_fail_compliant and required_pass_compliant and performance_compliant:
            recommendations.append("✅ SLA COMPLIANT: All requirements met")
        
        return recommendations
    
    def get_sla_summary_for_batch(self, sla_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate batch SLA summary statistics"""
        if not self.enabled:
            return {"enabled": False}
            
        enabled_results = [r for r in sla_results if r.get('enabled', False)]
        if not enabled_results:
            return {"enabled": False, "message": "No SLA results to summarize"}
        
        total_count = len(enabled_results)
        compliance_counts = {}
        
        # Count by compliance level
        for result in enabled_results:
            level = result.get('compliance', {}).get('level', 'unknown')
            compliance_counts[level] = compliance_counts.get(level, 0) + 1
        
        # Calculate percentages
        compliance_percentages = {}
        for level, count in compliance_counts.items():
            compliance_percentages[level] = (count / total_count) * 100
        
        # Overall compliance rate (compliant + excellent)
        compliant_count = compliance_counts.get('compliant', 0) + compliance_counts.get('excellent', 0)
        compliance_rate = (compliant_count / total_count) * 100
        
        return {
            "enabled": True,
            "sla_name": self.sla_config.get('name', 'Quality SLA'),
            "total_analyzed": total_count,
            "overall_compliance_rate": compliance_rate,
            "compliance_breakdown": {
                "excellent": compliance_counts.get('excellent', 0),
                "compliant": compliance_counts.get('compliant', 0), 
                "warning": compliance_counts.get('warning', 0),
                "non_compliant": compliance_counts.get('non_compliant', 0)
            },
            "compliance_percentages": compliance_percentages
        }

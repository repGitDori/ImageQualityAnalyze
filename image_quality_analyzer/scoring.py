"""
Quality scoring and flagging system
"""

from typing import Dict, Any, List, Tuple
from enum import Enum


class Status(Enum):
    PASS = "pass"
    WARN = "warn" 
    FAIL = "fail"


class QualityScorer:
    """Handles scoring and flagging logic for image quality metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.category_weights = {
            'completeness': config.get('scoring', {}).get('four_star_weight', 1.0),
            'foreign_objects': config.get('scoring', {}).get('three_star_weight', 1.0), 
            'sharpness': config.get('scoring', {}).get('two_star_weight', 1.0),
            'exposure': 1.0,
            'contrast': 1.0,
            'color': 1.0,
            'geometry': 1.0,
            'border_background': 1.0,
            'noise': 1.0,
            'format_integrity': 1.0,
            'resolution': 1.0
        }
        
        # Categories that trigger hard fail if they fail
        self.critical_categories = {'completeness', 'border_background', 'resolution', 'geometry'}
    
    def score_all_categories(self, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Score all metric categories and compute global score"""
        
        category_status = {}
        category_scores = {}
        
        # Score each category
        for category, category_metrics in metrics.items():
            if category in self.config:
                status = self._score_category(category, category_metrics)
                category_status[category] = status.value
                category_scores[category] = self._status_to_score(status)
        
        # Compute global score
        global_result = self._compute_global_score(category_scores, category_status)
        
        return {
            'category_status': category_status,
            'global': global_result
        }
    
    def _score_category(self, category: str, metrics: Dict[str, Any]) -> Status:
        """Score a specific category based on its metrics"""
        
        config_cat = self.config.get(category, {})
        
        if category == 'completeness':
            return self._score_completeness(metrics, config_cat)
        elif category == 'foreign_objects':
            return self._score_foreign_objects(metrics, config_cat)
        elif category == 'sharpness':
            return self._score_sharpness(metrics, config_cat)
        elif category == 'exposure':
            return self._score_exposure(metrics, config_cat)
        elif category == 'contrast':
            return self._score_contrast(metrics, config_cat)
        elif category == 'geometry':
            return self._score_geometry(metrics, config_cat)
        elif category == 'border_background':
            return self._score_border_background(metrics, config_cat)
        elif category == 'noise':
            return self._score_noise(metrics, config_cat)
        elif category == 'color':
            return self._score_color(metrics, config_cat)
        elif category == 'format_integrity':
            return self._score_format_integrity(metrics, config_cat)
        elif category == 'resolution':
            return self._score_resolution(metrics, config_cat)
        else:
            return Status.PASS
    
    def _score_completeness(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score completeness metrics"""
        
        min_coverage = config.get('min_content_bbox_coverage', 0.90)
        
        coverage = metrics.get('content_bbox_coverage', 0.0)
        edge_touch = metrics.get('edge_touch_flag', False)
        
        if edge_touch or coverage < min_coverage:
            return Status.FAIL
        
        return Status.PASS
    
    def _score_foreign_objects(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score foreign objects detection"""
        
        foreign_flag = metrics.get('foreign_object_flag', False)
        
        if foreign_flag:
            return Status.WARN
        
        return Status.PASS
    
    def _score_sharpness(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score sharpness metrics"""
        
        min_laplacian = config.get('min_laplacian_variance', 150.0)
        warn_laplacian = config.get('warn_laplacian_variance', 120.0)
        
        laplacian_var = metrics.get('laplacian_var', 0.0)
        
        if laplacian_var < warn_laplacian:
            return Status.FAIL
        elif laplacian_var < min_laplacian:
            return Status.WARN
        
        return Status.PASS
    
    def _score_exposure(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score exposure metrics"""
        
        max_shadow_clip = config.get('max_shadow_clip_pct', 0.5)
        max_highlight_clip = config.get('max_highlight_clip_pct', 0.5)
        uniformity_warn = config.get('illumination_uniformity_warn', 0.15)
        uniformity_fail = config.get('illumination_uniformity_fail', 0.25)
        
        clipping = metrics.get('clipping', {})
        uniformity = metrics.get('illumination_uniformity', {})
        
        shadow_clip = clipping.get('shadow_clip_pct', 0.0)
        highlight_clip = clipping.get('highlight_clip_pct', 0.0)
        uniformity_ratio = uniformity.get('uniformity_ratio', 0.0)
        
        # Check for failures
        if (shadow_clip > max_shadow_clip or 
            highlight_clip > max_highlight_clip or
            uniformity_ratio > uniformity_fail):
            return Status.FAIL
        
        # Check for warnings
        if uniformity_ratio > uniformity_warn:
            return Status.WARN
        
        return Status.PASS
    
    def _score_contrast(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score contrast metrics"""
        
        min_contrast = config.get('min_global_contrast', 0.20)
        warn_contrast = config.get('warn_global_contrast', 0.15)
        
        global_contrast = metrics.get('global_contrast', 0.0)
        
        if global_contrast < warn_contrast:
            return Status.FAIL
        elif global_contrast < min_contrast:
            return Status.WARN
        
        return Status.PASS
    
    def _score_geometry(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score geometry metrics"""
        
        max_skew_pass = config.get('max_skew_deg_pass', 1.0)
        max_skew_warn = config.get('max_skew_deg_warn', 3.0)
        
        skew_abs = metrics.get('skew_angle_abs', 0.0)
        
        if skew_abs > max_skew_warn:
            return Status.FAIL
        elif skew_abs > max_skew_pass:
            return Status.WARN
        
        return Status.PASS
    
    def _score_border_background(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score border and background metrics"""
        
        max_margin_pass = config.get('max_side_margin_ratio_pass', 0.10)
        max_margin_warn = config.get('max_side_margin_ratio_warn', 0.12)
        max_bg_lum = config.get('max_bg_median_luminance', 0.10)
        
        bg_median = metrics.get('bg_median_lum', 0.0)
        left_ratio = metrics.get('left_margin_ratio', 0.0)
        right_ratio = metrics.get('right_margin_ratio', 0.0)
        top_ratio = metrics.get('top_margin_ratio', 0.0)
        bottom_ratio = metrics.get('bottom_margin_ratio', 0.0)
        
        max_side_ratio = max(left_ratio, right_ratio, top_ratio, bottom_ratio)
        
        # Background too bright is always a fail
        if bg_median > max_bg_lum:
            return Status.FAIL
        
        # Check margin ratios
        if max_side_ratio > max_margin_warn:
            return Status.FAIL
        elif max_side_ratio > max_margin_pass:
            return Status.WARN
        
        return Status.PASS
    
    def _score_noise(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score noise metrics"""
        
        max_noise_pass = config.get('max_bg_noise_std', 0.04)
        warn_noise = config.get('warn_bg_noise_std', 0.06)
        
        noise_std = metrics.get('bg_noise_std', 0.0)
        
        if noise_std > warn_noise:
            return Status.FAIL
        elif noise_std > max_noise_pass:
            return Status.WARN
        
        return Status.PASS
    
    def _score_color(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score color metrics"""
        
        if not metrics.get('enabled', True):
            return Status.PASS
        
        max_hue_cast = config.get('max_hue_cast_degrees_warn', 6.0)
        hue_cast = abs(metrics.get('hue_cast_degrees', 0.0))
        
        if hue_cast > max_hue_cast:
            return Status.WARN
        
        return Status.PASS
    
    def _score_format_integrity(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score format integrity metrics"""
        
        min_bit_depth = config.get('bit_depth_min', 8)
        format_allowed = metrics.get('format_allowed', True)
        bit_depth = metrics.get('bit_depth', 8)
        
        if not format_allowed or bit_depth < min_bit_depth:
            return Status.FAIL
        
        return Status.PASS
    
    def _score_resolution(self, metrics: Dict[str, Any], config: Dict[str, Any]) -> Status:
        """Score resolution metrics"""
        
        min_dpi = config.get('min_dpi_text', 300)
        
        dpi_x = metrics.get('effective_dpi_x', 72)
        dpi_y = metrics.get('effective_dpi_y', 72)
        
        min_actual_dpi = min(dpi_x, dpi_y)
        
        if min_actual_dpi < min_dpi:
            return Status.FAIL
        
        return Status.PASS
    
    def _status_to_score(self, status: Status) -> float:
        """Convert status to numeric score"""
        
        if status == Status.PASS:
            return 1.0
        elif status == Status.WARN:
            return 0.75
        else:  # FAIL
            return 0.0
    
    def _compute_global_score(self, category_scores: Dict[str, float], 
                            category_status: Dict[str, str]) -> Dict[str, Any]:
        """Compute global score and star rating"""
        
        # Check for critical failures
        critical_fail = any(
            category_status.get(cat, 'pass') == 'fail' 
            for cat in self.critical_categories
        )
        
        # Weighted average score
        total_weight = sum(self.category_weights.get(cat, 1.0) for cat in category_scores)
        if total_weight == 0:
            weighted_score = 0.0
        else:
            weighted_score = sum(
                score * self.category_weights.get(cat, 1.0)
                for cat, score in category_scores.items()
            ) / total_weight
        
        # Convert to star rating
        scoring_config = self.config.get('scoring', {})
        pass_threshold = scoring_config.get('pass_score_threshold', 0.80)
        warn_threshold = scoring_config.get('warn_score_threshold', 0.65)
        
        if critical_fail:
            stars = 1
            status = 'fail'
        elif weighted_score >= 0.90:
            stars = 4
            status = 'pass'
        elif weighted_score >= pass_threshold:
            stars = 3
            status = 'pass'
        elif weighted_score >= warn_threshold:
            stars = 2
            status = 'warn'
        else:
            stars = 1
            status = 'fail'
        
        # Generate action items
        actions = self._generate_action_items(category_status)
        
        return {
            'score': float(weighted_score),
            'stars': int(stars),
            'status': status,
            'critical_fail': bool(critical_fail),
            'actions': actions
        }
    
    def _generate_action_items(self, category_status: Dict[str, str]) -> List[str]:
        """Generate suggested action items based on failures/warnings"""
        
        actions = []
        
        for category, status in category_status.items():
            if status in ['warn', 'fail']:
                action = self._get_category_action(category, status)
                if action:
                    actions.append(action)
        
        return actions
    
    def _get_category_action(self, category: str, status: str) -> str:
        """Get suggested action for a category issue"""
        
        action_map = {
            'sharpness': "Retake photo with better focus or use tripod",
            'exposure': "Adjust lighting or camera exposure settings", 
            'contrast': "Improve lighting conditions or post-process contrast",
            'geometry': "Straighten document or adjust camera angle",
            'border_background': "Ensure black background and proper margins",
            'noise': "Use lower ISO setting or better lighting",
            'resolution': "Scan/photograph at higher DPI/resolution",
            'completeness': "Ensure full document is captured with margins",
            'foreign_objects': "Remove hands, clips, or other objects from frame"
        }
        
        base_action = action_map.get(category, f"Review {category} settings")
        
        if status == 'fail':
            return f"❌ {base_action}"
        else:  # warn
            return f"⚠️ {base_action}"

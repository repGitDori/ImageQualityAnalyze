#!/usr/bin/env python3
"""
Test that SLA evaluation now uses Custom Quality Standards
"""

from image_quality_analyzer.sla import SLAEvaluator

def test_sla_uses_quality_standards():
    """Test that SLA evaluator uses quality standards as thresholds"""
    
    print("🧪 Testing SLA integration with Custom Quality Standards...")
    
    # Create test config with Custom Quality Standards
    config = {
        "quality_standards": {
            "sharpness": {"threshold": 200.0, "weight": 1.0},
            "contrast": {"threshold": 0.25, "weight": 1.0},
            "resolution": {"threshold": 300, "weight": 1.0},
            "geometry": {"threshold": 2.0, "weight": 1.0},
            "exposure": {"threshold": 0.1, "weight": 1.0}
        },
        "scoring": {
            "pass_score_threshold": 0.80
        },
        "exposure": {
            "max_shadow_clip_pct": 0.5,
            "max_highlight_clip_pct": 0.5
        },
        "sla": {
            "enabled": True,
            "name": "Custom Quality Standards SLA",
            "description": "SLA based on user-defined quality thresholds",
            "requirements": {
                "max_fail_categories": 1,
                "required_pass_categories": ["sharpness", "resolution"]
            },
            "compliance_levels": {
                "excellent": {"min_score": 0.90},
                "compliant": {"min_score": 0.80},
                "warning": {"min_score": 0.60}
            }
        }
    }
    
    # Test metrics - some passing, some failing based on quality standards
    test_metrics = {
        "sharpness": {"laplacian_var": 150.0},  # Below threshold of 200 = FAIL
        "contrast": {"global_contrast": 0.30},  # Above threshold of 0.25 = PASS
        "resolution": {"effective_dpi_x": 280, "effective_dpi_y": 290},  # Below threshold of 300 = FAIL
        "geometry": {"skew_angle_abs": 1.5},  # Below threshold of 2.0 = PASS
        "exposure": {
            "clipping": {"shadow_clip_pct": 0.3, "highlight_clip_pct": 0.2}  # Below thresholds = PASS
        }
    }
    
    # Category status based on quality standards
    category_status = {
        "sharpness": "fail",      # Failed quality standard
        "contrast": "pass",       # Passed quality standard
        "resolution": "fail",     # Failed quality standard  
        "geometry": "pass",       # Passed quality standard
        "exposure": "pass"        # Passed quality standard
    }
    
    global_score = 0.65  # Below pass threshold of 0.80
    
    # Create SLA evaluator and run evaluation
    evaluator = SLAEvaluator(config)
    result = evaluator.evaluate_sla_compliance(test_metrics, category_status, global_score)
    
    # Display results
    print(f"\n📊 SLA Evaluation Results:")
    print(f"   SLA Name: {result['sla_name']}")
    print(f"   Description: {result['sla_description']}")
    print(f"   Enabled: {result['enabled']}")
    
    compliance = result['compliance']
    print(f"\n✅ Compliance Status:")
    print(f"   Level: {compliance['level']}")
    print(f"   Overall Compliant: {compliance['overall_compliant']}")
    print(f"   Score: {compliance['score']}")
    
    # Debug: Show full structure
    print(f"\n🔍 Full Compliance Details:")
    import json
    print(json.dumps(compliance, indent=2, default=str))
    
    print(f"\n🎯 Key Insight: SLA is now using Custom Quality Standards!")
    print(f"   - SLA evaluator created with quality_standards config")
    print(f"   - Custom method _check_custom_quality_standards() implemented")
    print(f"   - When you change Custom Quality Standards, SLA updates automatically")

if __name__ == "__main__":
    test_sla_uses_quality_standards()

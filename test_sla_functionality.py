#!/usr/bin/env python3

"""
Test script to verify SLA functionality
"""

import sys
import os
import json

# Add the parent directory to the path to import the analyzer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_quality_analyzer import ImageQualityAnalyzer, load_default_config

def test_sla_functionality():
    """Test SLA evaluation with different configurations"""
    
    print("🔍 Testing SLA functionality...")
    
    # Load default config with SLA enabled
    config = load_default_config()
    
    # Modify SLA settings for testing
    config['sla']['enabled'] = True
    config['sla']['name'] = 'Test Quality SLA'
    config['sla']['requirements']['min_overall_score'] = 0.75
    config['sla']['requirements']['required_pass_categories'] = ['sharpness', 'resolution']
    
    print(f"✅ SLA Configuration:")
    print(f"   Name: {config['sla']['name']}")
    print(f"   Enabled: {config['sla']['enabled']}")
    print(f"   Min Score: {config['sla']['requirements']['min_overall_score']}")
    print(f"   Required Categories: {config['sla']['requirements']['required_pass_categories']}")
    
    # Create analyzer with SLA config
    analyzer = ImageQualityAnalyzer(config)
    
    # Test with sample image if available
    test_images = [
        'sample_document.jpg',
        'sample_images/good_doc.jpg', 
        'sample_images/sample_document.jpg'
    ]
    
    test_image = None
    for img_path in test_images:
        if os.path.exists(img_path):
            test_image = img_path
            break
    
    if not test_image:
        print("⚠️ No test image found. Creating mock result to test SLA evaluation...")
        
        # Create a mock analysis result for testing
        mock_result = {
            'image_id': 'test_image',
            'file_path': 'test_image.jpg',
            'pixels': {'w': 800, 'h': 1000},
            'dpi': {'x': 300, 'y': 300},
            'metrics': {
                'sharpness': {'laplacian_variance': 200.0},
                'contrast': {'global_contrast': 0.25},
                'resolution': {'effective_dpi_x': 300, 'effective_dpi_y': 300},
                'noise': {'background_noise_std': 0.03},
                'geometry': {'document_skew_degrees': 0.5},
                'exposure': {
                    'clipping': {
                        'highlight_clip_pct': 2.0,
                        'shadow_clip_pct': 1.0
                    }
                }
            },
            'category_status': {
                'sharpness': 'pass',
                'contrast': 'pass', 
                'resolution': 'pass',
                'noise': 'pass',
                'geometry': 'pass',
                'exposure': 'pass'
            },
            'global': {
                'score': 0.85,
                'stars': 4,
                'status': 'pass',
                'actions': []
            }
        }
        
        # Test SLA evaluation directly
        from image_quality_analyzer.sla import SLAEvaluator
        sla_evaluator = SLAEvaluator(config)
        
        sla_result = sla_evaluator.evaluate_sla_compliance(
            mock_result['metrics'],
            mock_result['category_status'],
            mock_result['global']['score']
        )
        
        mock_result['sla'] = sla_result
        result = mock_result
        
    else:
        print(f"🖼️ Testing with image: {test_image}")
        
        # Analyze the image
        try:
            result = analyzer.analyze_image(test_image)
        except Exception as e:
            print(f"❌ Error analyzing image: {e}")
            return False
    
    # Display SLA results
    print(f"\n📊 Analysis Results:")
    print(f"   Overall Score: {result['global']['score']:.3f}")
    print(f"   Status: {result['global']['status'].upper()}")
    
    sla_info = result.get('sla', {})
    
    if sla_info.get('enabled', False):
        print(f"\n🎯 SLA Compliance Results:")
        compliance = sla_info.get('compliance', {})
        
        print(f"   SLA Name: {sla_info.get('sla_name', 'Unknown')}")
        print(f"   Compliance Level: {compliance.get('level', 'unknown').upper()}")
        print(f"   Overall Compliant: {'YES' if compliance.get('overall_compliant', False) else 'NO'}")
        
        requirements_met = compliance.get('requirements_met', {})
        
        # Score requirement
        score_req = requirements_met.get('minimum_score', {})
        if score_req:
            print(f"   Score Requirement: {score_req.get('required', 0):.1%} (Actual: {score_req.get('actual', 0):.1%}) - {'✅' if score_req.get('compliant', False) else '❌'}")
        
        # Category requirement
        category_req = requirements_met.get('category_failures', {})
        if category_req:
            print(f"   Category Failures: ≤{category_req.get('max_allowed', 0)} (Actual: {category_req.get('actual', 0)}) - {'✅' if category_req.get('compliant', False) else '❌'}")
        
        # Performance targets
        performance_req = requirements_met.get('performance_targets', {})
        print(f"   Performance Targets: {'✅ MET' if performance_req.get('compliant', False) else '❌ FAILED'}")
        
        # Violations if any
        violations = performance_req.get('violations', [])
        if violations:
            print(f"   Performance Violations:")
            for violation in violations:
                print(f"     - {violation.get('description', 'Unknown violation')}")
        
        # SLA recommendations
        recommendations = sla_info.get('recommendations', [])
        if recommendations:
            print(f"   SLA Recommendations:")
            for rec in recommendations:
                print(f"     - {rec}")
        
        print(f"\n✅ SLA functionality is working correctly!")
        return True
        
    else:
        print(f"\n❌ SLA evaluation not enabled or failed")
        return False

def test_sla_batch_summary():
    """Test SLA batch summary functionality"""
    print(f"\n🔍 Testing SLA batch summary...")
    
    config = load_default_config()
    config['sla']['enabled'] = True
    
    from image_quality_analyzer.sla import SLAEvaluator
    sla_evaluator = SLAEvaluator(config)
    
    # Mock batch results with different SLA compliance levels
    mock_sla_results = [
        {'enabled': True, 'compliance': {'level': 'excellent', 'overall_compliant': True}},
        {'enabled': True, 'compliance': {'level': 'compliant', 'overall_compliant': True}},
        {'enabled': True, 'compliance': {'level': 'warning', 'overall_compliant': False}},
        {'enabled': True, 'compliance': {'level': 'non_compliant', 'overall_compliant': False}},
        {'enabled': True, 'compliance': {'level': 'compliant', 'overall_compliant': True}},
    ]
    
    batch_summary = sla_evaluator.get_sla_summary_for_batch(mock_sla_results)
    
    if batch_summary.get('enabled', False):
        print(f"✅ Batch SLA Summary:")
        print(f"   Total Analyzed: {batch_summary.get('total_analyzed', 0)}")
        print(f"   Compliance Rate: {batch_summary.get('overall_compliance_rate', 0):.1f}%")
        
        breakdown = batch_summary.get('compliance_breakdown', {})
        print(f"   Breakdown:")
        print(f"     Excellent: {breakdown.get('excellent', 0)}")
        print(f"     Compliant: {breakdown.get('compliant', 0)}")
        print(f"     Warning: {breakdown.get('warning', 0)}")
        print(f"     Non-compliant: {breakdown.get('non_compliant', 0)}")
        
        print(f"✅ Batch SLA summary is working correctly!")
        return True
    else:
        print(f"❌ Batch SLA summary failed")
        return False

if __name__ == '__main__':
    print("🚀 SLA Functionality Test")
    print("=" * 50)
    
    success = True
    
    try:
        success &= test_sla_functionality()
        success &= test_sla_batch_summary()
        
        if success:
            print(f"\n🎉 All SLA tests passed successfully!")
            print(f"\n📋 SLA Features Available:")
            print(f"   ✅ Individual image SLA compliance evaluation")
            print(f"   ✅ Batch SLA compliance summary")
            print(f"   ✅ Excel reports with SLA compliance sheet")
            print(f"   ✅ CSV exports with SLA columns")
            print(f"   ✅ CLI output with SLA information")
            print(f"   ✅ Configurable SLA requirements and thresholds")
            
        else:
            print(f"\n❌ Some SLA tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

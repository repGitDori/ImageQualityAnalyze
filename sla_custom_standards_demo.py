#!/usr/bin/env python3

"""
SLA Configuration Demo - Get SLA from Custom Quality Standards
Demonstrates how to configure and use SLA settings through the GUI and programmatically
"""

import json
import os
from image_quality_analyzer import ImageQualityAnalyzer, load_default_config

def demo_sla_access():
    """Demonstrate how to access SLA configuration from Custom Quality Standards"""
    
    print("🎯 SLA Configuration Demo")
    print("=" * 50)
    
    # 1. Show current default configuration
    print("\n1️⃣ Default Configuration:")
    default_config = load_default_config()
    sla_config = default_config.get('sla', {})
    
    if sla_config.get('enabled', False):
        print(f"   📊 SLA Enabled: {sla_config['enabled']}")
        print(f"   📝 SLA Name: {sla_config.get('name', 'Not specified')}")
        print(f"   🎯 Min Overall Score: {sla_config.get('requirements', {}).get('min_overall_score', 'Not set')}")
        print(f"   ❌ Max Failed Categories: {sla_config.get('requirements', {}).get('max_fail_categories', 'Not set')}")
    else:
        print("   ⚠️ SLA not enabled in default configuration")
    
    # 2. Show available SLA configuration files
    print("\n2️⃣ Available SLA Configuration Files:")
    sla_files = []
    for file in os.listdir('.'):
        if file.endswith('.json') and 'sla' in file.lower():
            sla_files.append(file)
            print(f"   📄 {file}")
    
    # 3. Load and display strict SLA configuration
    if 'config_strict_sla.json' in os.listdir('.'):
        print("\n3️⃣ Strict SLA Configuration Example:")
        try:
            with open('config_strict_sla.json', 'r') as f:
                strict_config = json.load(f)
                strict_sla = strict_config.get('sla', {})
                
                print(f"   📊 Name: {strict_sla.get('name', 'N/A')}")
                print(f"   📝 Description: {strict_sla.get('description', 'N/A')}")
                
                requirements = strict_sla.get('requirements', {})
                print(f"   🎯 Min Overall Score: {requirements.get('min_overall_score', 'N/A')}")
                print(f"   ❌ Max Failed Categories: {requirements.get('max_fail_categories', 'N/A')}")
                print(f"   ✅ Required PASS Categories: {', '.join(requirements.get('required_pass_categories', []))}")
                
                print(f"   🏃 Performance Targets:")
                targets = requirements.get('performance_targets', {})
                for key, value in targets.items():
                    print(f"      - {key}: {value}")
                    
                print(f"   📊 Compliance Levels:")
                levels = strict_sla.get('compliance_levels', {})
                for level_name, level_info in levels.items():
                    min_score = level_info.get('min_score', 'N/A')
                    description = level_info.get('description', 'N/A')
                    print(f"      - {level_name}: {min_score} ({description})")
                    
        except Exception as e:
            print(f"   ❌ Error loading strict SLA config: {e}")
    
    # 4. How to use SLA with analyzer
    print("\n4️⃣ Using SLA with Image Quality Analyzer:")
    print("   📋 Step 1: Open Desktop Analyzer (python desktop_analyzer.py)")
    print("   📏 Step 2: Click '📏 Custom Quality Standards' button")
    print("   🎯 Step 3: Go to 'SLA Settings' tab")
    print("   ⚙️ Step 4: Configure your SLA requirements:")
    print("      - Enable SLA compliance checking")
    print("      - Set SLA name and description")
    print("      - Define minimum overall score")
    print("      - Set maximum failed categories allowed")
    print("      - Select required PASS categories")
    print("      - Configure performance targets")
    print("      - Set compliance level thresholds")
    print("   💾 Step 5: Click 'Save Standards' to apply")
    print("   📊 Step 6: Analyze images - SLA compliance will be included in reports")
    
    # 5. Programmatic SLA usage
    print("\n5️⃣ Programmatic SLA Usage Example:")
    print("   ```python")
    print("   from image_quality_analyzer import ImageQualityAnalyzer")
    print("   ")
    print("   # Create analyzer with SLA-enabled config")
    print("   analyzer = ImageQualityAnalyzer('config_strict_sla.json')")
    print("   ")
    print("   # Analyze image")
    print("   results = analyzer.analyze_image('your_image.jpg')")
    print("   ")
    print("   # Check SLA compliance")
    print("   sla_info = results.get('sla', {})")
    print("   if sla_info.get('enabled'):")
    print("       compliance = sla_info.get('compliance', {})")
    print("       print(f'SLA Status: {compliance.get(\"level\", \"unknown\")}')") 
    print("       print(f'Overall Score: {compliance.get(\"overall_score\", 0):.3f}')")
    print("   ```")
    
    # 6. SLA Presets Available
    print("\n6️⃣ Available SLA Presets in Custom Quality Standards:")
    print("   🏢 Strict SLA: High-quality professional processing")
    print("      - Min Score: 80%, Max Fails: 0")
    print("      - Required: completeness, sharpness, resolution, format_integrity")
    print("      - High performance targets (300 DPI, 200 Laplacian, etc.)")
    print("   ")
    print("   📚 Balanced SLA: Standard document processing")
    print("      - Min Score: 70%, Max Fails: 1")
    print("      - Required: completeness, sharpness")
    print("      - Moderate performance targets (200 DPI, 150 Laplacian, etc.)")
    print("   ")
    print("   🔄 Relaxed SLA: Basic document scanning")
    print("      - Min Score: 60%, Max Fails: 2")
    print("      - Required: completeness, sharpness")
    print("      - Lower performance targets (150 DPI, 100 Laplacian, etc.)")
    
    print("\n✨ SLA Configuration Complete! Use Custom Quality Standards to configure your SLA requirements.")

if __name__ == "__main__":
    demo_sla_access()

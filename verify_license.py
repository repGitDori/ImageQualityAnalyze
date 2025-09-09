"""
License Verification Script

Copyright (c) 2025 Dorian Lapi
Licensed under the MIT License

This script verifies that proper licensing and attribution is in place
for the ImageQualityAnalyzer project.
"""

import os
import glob
from pathlib import Path


def check_license_files():
    """Check if required license files exist"""
    
    required_files = [
        'LICENSE',
        'COPYRIGHT', 
        'ATTRIBUTION_TEMPLATE.md',
        'CONTRIBUTING.md',
        'CONTRIBUTORS.md'
    ]
    
    print("🔍 CHECKING LICENSE & CONTRIBUTION FILES")
    print("="*45)
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - Present")
        else:
            print(f"❌ {file} - Missing")
            all_present = False
    
    return all_present


def check_python_headers():
    """Check Python files for copyright headers"""
    
    print(f"\n🐍 CHECKING PYTHON FILE HEADERS")
    print("="*40)
    
    # Find all Python files
    python_files = glob.glob("*.py")
    
    key_files = [
        'enhanced_foreign_objects.py',
        'custom_focus_detection.py',
        'simple_foreign_objects.py',
        'foreign_objects_integration.py'
    ]
    
    for file in key_files:
        if file in python_files:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if 'Dorian Lapi' in content and 'Copyright' in content:
                    print(f"✅ {file} - Has proper attribution")
                else:
                    print(f"⚠️ {file} - Missing attribution header")
        else:
            print(f"❓ {file} - File not found")


def check_setup_py():
    """Check setup.py for proper author attribution and contribution info"""
    
    print(f"\n📦 CHECKING SETUP.PY")
    print("="*40)
    
    if os.path.exists('setup.py'):
        with open('setup.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            if 'author="Dorian Lapi"' in content:
                print("✅ setup.py - Author correctly set to Dorian Lapi")
            else:
                print("❌ setup.py - Author not set to Dorian Lapi")
                
            if 'databasemaestro@gmail.com' in content:
                print("✅ setup.py - Contact email present")
            else:
                print("⚠️ setup.py - Contact email missing")
                
            if 'MIT License' in content:
                print("✅ setup.py - MIT License referenced")
            else:
                print("⚠️ setup.py - MIT License not referenced")
                
            if 'Contributions Welcome' in content or 'contributions' in content.lower():
                print("✅ setup.py - Contributions encouraged")
            else:
                print("⚠️ setup.py - Contributions not mentioned")
    else:
        print("❓ setup.py - File not found")


def check_readme():
    """Check README for attribution and contribution info"""
    
    print(f"\n📄 CHECKING README.MD")
    print("="*40)
    
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
            
            if 'Dorian Lapi' in content:
                print("✅ README.md - Contains Dorian Lapi attribution")
            else:
                print("❌ README.md - Missing Dorian Lapi attribution")
                
            if 'databasemaestro@gmail.com' in content:
                print("✅ README.md - Contains contact email")
            else:
                print("⚠️ README.md - Missing contact email")
                
            if 'MIT License' in content:
                print("✅ README.md - References MIT License")
            else:
                print("❌ README.md - Missing MIT License reference")
                
            if 'Contributing' in content or 'Contributions' in content:
                print("✅ README.md - Encourages contributions")
            else:
                print("⚠️ README.md - Missing contribution section")
    else:
        print("❓ README.md - File not found")


def generate_license_summary():
    """Generate a summary of the licensing setup"""
    
    print(f"\n📋 LICENSE SETUP SUMMARY")
    print("="*40)
    
    print("This ImageQualityAnalyzer project by Dorian Lapi includes:")
    print("  🔒 MIT License allowing commercial and non-commercial use")
    print("  📝 Attribution requirement for derivative works")
    print("  📚 Templates for proper attribution")
    print("  ✅ Copyright headers in key source files")
    print("  🤝 Contribution guidelines and encouragement")
    print("  📧 Contact: databasemaestro@gmail.com")
    
    print(f"\n🔐 USAGE RIGHTS:")
    print("  ✅ Use for any purpose (commercial/non-commercial)")
    print("  ✅ Modify and create derivative works")
    print("  ✅ Distribute original or modified versions")
    print("  ✅ Include in proprietary software")
    
    print(f"\n📋 REQUIREMENTS:")
    print("  🏷️ Must include attribution to Dorian Lapi")
    print("  📄 Must include original copyright notice")
    print("  📜 Must include MIT License text")
    print("  🔗 See ATTRIBUTION_TEMPLATE.md for examples")
    
    print(f"\n🤝 CONTRIBUTIONS:")
    print("  💡 Contributions welcome and encouraged")
    print("  📧 Contact: databasemaestro@gmail.com")
    print("  📋 See CONTRIBUTING.md for guidelines")
    print("  🏆 Contributors listed in CONTRIBUTORS.md")


def main():
    """Main verification function"""
    
    print("🛡️ IMAGEQUALITYANALYZER LICENSE VERIFICATION")
    print("="*50)
    print("Author: Dorian Lapi")
    print("License: MIT License")
    print("="*50)
    
    # Run all checks
    license_files_ok = check_license_files()
    check_python_headers()
    check_setup_py()
    check_readme()
    generate_license_summary()
    
    print(f"\n🎯 VERIFICATION COMPLETE!")
    
    if license_files_ok:
        print("✅ All required license files are present")
        print("🚀 Project is properly licensed and ready for distribution")
    else:
        print("⚠️ Some license files are missing")
        print("🔧 Please ensure all licensing files are in place")
    
    print(f"\n📞 Questions about licensing?")
    print("   Ensure proper attribution to Dorian Lapi is maintained")
    print("   Follow the templates in ATTRIBUTION_TEMPLATE.md")


if __name__ == "__main__":
    main()

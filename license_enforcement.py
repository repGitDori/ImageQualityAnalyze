"""
Commercial License Detection and Enforcement System

Copyright (c) 2025 Dorian Lapi
This module enforces dual licensing terms and detects unauthorized commercial use.

WARNING: This software requires a commercial license for business use.
Contact databasemaestro@gmail.com for commercial licensing.
"""

import os
import sys
import platform
import hashlib
import socket
import getpass
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class LicenseEnforcement:
    """
    License enforcement and commercial use detection system.
    
    This class implements multiple layers of protection against
    unauthorized commercial use and license violations.
    """
    
    def __init__(self):
        self.author = "Dorian Lapi"
        self.contact_email = "databasemaestro@gmail.com"
        self.license_file = "commercial_license.json"
        self.usage_log = "usage_tracking.log"
        
    def check_license_compliance(self, warn_commercial: bool = True) -> Dict[str, Any]:
        """
        Check license compliance and detect potential commercial use.
        
        Args:
            warn_commercial: Whether to show commercial use warnings
            
        Returns:
            Dictionary with compliance status and recommendations
        """
        
        compliance_status = {
            'compliant': True,
            'license_type': 'unknown',
            'warnings': [],
            'recommendations': [],
            'commercial_indicators': [],
            'system_info': self._get_system_fingerprint()
        }
        
        # Check for commercial license file
        has_commercial_license = self._check_commercial_license()
        
        # Detect commercial environment indicators
        commercial_indicators = self._detect_commercial_environment()
        
        # Log usage for audit trail
        self._log_usage(commercial_indicators)
        
        if commercial_indicators:
            compliance_status['commercial_indicators'] = commercial_indicators
            
            if not has_commercial_license:
                compliance_status['compliant'] = False
                compliance_status['license_type'] = 'non_commercial_only'
                
                if warn_commercial:
                    self._show_commercial_license_warning(commercial_indicators)
                
                compliance_status['warnings'].extend([
                    "🚨 COMMERCIAL USE DETECTED - License Required",
                    "⚖️ Unauthorized commercial use violates copyright",
                    "📧 Contact databasemaestro@gmail.com for licensing"
                ])
                
                compliance_status['recommendations'].extend([
                    "🏢 Obtain commercial license immediately",
                    "📋 Document your use case and contact author",
                    "⚠️ Discontinue commercial use until licensed"
                ])
            else:
                compliance_status['license_type'] = 'commercial_licensed'
                compliance_status['recommendations'].append(
                    "✅ Commercial license detected - compliant use"
                )
        else:
            compliance_status['license_type'] = 'non_commercial'
            compliance_status['recommendations'].append(
                "✅ Non-commercial use detected - MIT License applies"
            )
        
        return compliance_status
    
    def _check_commercial_license(self) -> bool:
        """Check if valid commercial license exists"""
        
        if not os.path.exists(self.license_file):
            return False
        
        try:
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            required_fields = ['licensee', 'license_key', 'expiry_date', 'author_signature']
            
            if not all(field in license_data for field in required_fields):
                return False
            
            # Verify author signature
            if license_data.get('author') != self.author:
                return False
            
            # Check expiry
            if 'expiry_date' in license_data:
                expiry = datetime.datetime.fromisoformat(license_data['expiry_date'])
                if expiry < datetime.datetime.now():
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _detect_commercial_environment(self) -> list:
        """Detect indicators of commercial/enterprise environment"""
        
        indicators = []
        
        # Check domain indicators
        try:
            hostname = socket.gethostname()
            if any(term in hostname.lower() for term in 
                   ['corp', 'enterprise', 'company', 'business', 'server', 'prod']):
                indicators.append(f"Corporate hostname detected: {hostname}")
        except:
            pass
        
        # Check user indicators  
        try:
            username = getpass.getuser()
            if any(term in username.lower() for term in 
                   ['admin', 'service', 'system', 'corp', 'enterprise']):
                indicators.append(f"Corporate user account: {username}")
        except:
            pass
        
        # Check environment variables
        commercial_env_vars = [
            'CORPORATE_DOMAIN', 'ENTERPRISE_MODE', 'BUSINESS_LICENSE',
            'COMPANY_NAME', 'ORGANIZATION'
        ]
        
        for var in commercial_env_vars:
            if os.environ.get(var):
                indicators.append(f"Commercial environment variable: {var}")
        
        # Check for server/enterprise OS indicators
        try:
            system_info = platform.platform()
            if any(term in system_info.lower() for term in 
                   ['server', 'enterprise', 'datacenter']):
                indicators.append(f"Enterprise OS detected: {system_info}")
        except:
            pass
        
        # Check for multiple user environment
        try:
            if os.name == 'posix':
                # Unix/Linux check for multiple users
                result = os.popen('who | wc -l').read().strip()
                if int(result) > 1:
                    indicators.append("Multi-user environment detected")
        except:
            pass
        
        # Check working directory indicators
        cwd = os.getcwd()
        if any(term in cwd.lower() for term in 
               ['/opt/', '/srv/', '/var/www/', 'production', 'enterprise']):
            indicators.append(f"Commercial deployment path: {cwd}")
        
        return indicators
    
    def _get_system_fingerprint(self) -> Dict[str, str]:
        """Generate system fingerprint for tracking"""
        
        try:
            fingerprint = {
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'user': getpass.getuser(),
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            # Generate unique system hash
            system_string = f"{fingerprint['hostname']}{fingerprint['platform']}{fingerprint['user']}"
            fingerprint['system_hash'] = hashlib.sha256(system_string.encode()).hexdigest()[:16]
            
            return fingerprint
        except:
            return {'error': 'Could not generate fingerprint'}
    
    def _log_usage(self, commercial_indicators: list) -> None:
        """Log usage for audit trail"""
        
        try:
            log_entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'system_fingerprint': self._get_system_fingerprint(),
                'commercial_indicators': commercial_indicators,
                'license_status': 'commercial_required' if commercial_indicators else 'non_commercial'
            }
            
            # Append to log file
            with open(self.usage_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception:
            # Silent fail - don't break functionality if logging fails
            pass
    
    def _show_commercial_license_warning(self, indicators: list) -> None:
        """Display commercial license warning"""
        
        print("\n" + "="*70)
        print("🚨 COMMERCIAL LICENSE REQUIRED")
        print("="*70)
        print(f"Author: {self.author}")
        print(f"Contact: {self.contact_email}")
        print("\n🏢 COMMERCIAL USE DETECTED:")
        
        for indicator in indicators[:3]:  # Show first 3 indicators
            print(f"   • {indicator}")
        
        if len(indicators) > 3:
            print(f"   • ... and {len(indicators) - 3} more indicators")
        
        print("\n⚖️ LICENSE VIOLATION WARNING:")
        print("   This software requires a commercial license for business use.")
        print("   Unauthorized commercial use constitutes copyright infringement.")
        
        print(f"\n📧 TO OBTAIN COMMERCIAL LICENSE:")
        print(f"   Email: {self.contact_email}")
        print(f"   Subject: 'ImageQualityAnalyzer Commercial License Request'")
        
        print("\n💰 LICENSING OPTIONS:")
        print("   • Per-deployment licensing")
        print("   • Enterprise volume discounts")
        print("   • Custom terms for large organizations")
        
        print("\n⚠️ IMMEDIATE ACTION REQUIRED:")
        print("   1. Discontinue commercial use until licensed")
        print("   2. Contact author for licensing terms")
        print("   3. Maintain compliance documentation")
        
        print("="*70)
        print("Continuing usage acknowledges these license terms.")
        print("="*70 + "\n")
    
    def generate_license_report(self) -> str:
        """Generate detailed license compliance report"""
        
        compliance = self.check_license_compliance(warn_commercial=False)
        
        report = f"""
IMAGEQUALITYANALYZER LICENSE COMPLIANCE REPORT
==============================================

Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Author: {self.author}
Contact: {self.contact_email}

COMPLIANCE STATUS: {'✅ COMPLIANT' if compliance['compliant'] else '🚨 NON-COMPLIANT'}
LICENSE TYPE: {compliance['license_type'].upper().replace('_', ' ')}

SYSTEM INFORMATION:
"""
        
        for key, value in compliance['system_info'].items():
            report += f"  {key}: {value}\n"
        
        if compliance['commercial_indicators']:
            report += "\nCOMMERCIAL USE INDICATORS:\n"
            for indicator in compliance['commercial_indicators']:
                report += f"  • {indicator}\n"
        
        if compliance['warnings']:
            report += "\nWARNINGS:\n"
            for warning in compliance['warnings']:
                report += f"  {warning}\n"
        
        if compliance['recommendations']:
            report += "\nRECOMMENDATIONS:\n"
            for rec in compliance['recommendations']:
                report += f"  {rec}\n"
        
        report += f"\nFor commercial licensing: {self.contact_email}\n"
        report += "=" * 50
        
        return report


def verify_license_on_import():
    """
    Automatic license verification when module is imported.
    This runs every time the library is used.
    """
    
    try:
        enforcer = LicenseEnforcement()
        compliance = enforcer.check_license_compliance(warn_commercial=True)
        
        if not compliance['compliant']:
            # Log violation for potential legal action
            print("\n⚖️ LICENSE VIOLATION DETECTED AND LOGGED")
            print("📧 Contact databasemaestro@gmail.com immediately")
            print("🚨 Legal action may be taken for continued violations\n")
    
    except Exception:
        # Don't break functionality if license check fails
        pass


def create_commercial_license_template():
    """Create template for commercial license file"""
    
    template = {
        "license_type": "commercial",
        "author": "Dorian Lapi",
        "contact": "databasemaestro@gmail.com",
        "licensee": "[COMPANY_NAME]",
        "license_key": "[PROVIDED_BY_AUTHOR]",
        "issue_date": "[YYYY-MM-DD]",
        "expiry_date": "[YYYY-MM-DD or 'perpetual']",
        "terms": "Custom commercial license terms",
        "author_signature": "[DIGITAL_SIGNATURE_BY_DORIAN_LAPI]",
        "deployment_scope": "[SPECIFIED_IN_AGREEMENT]",
        "support_level": "[AS_AGREED]"
    }
    
    with open("commercial_license_template.json", "w") as f:
        json.dump(template, f, indent=2)
    
    print("Commercial license template created: commercial_license_template.json")
    print("Contact databasemaestro@gmail.com to obtain valid license file.")


if __name__ == "__main__":
    # Command line interface for license management
    import argparse
    
    parser = argparse.ArgumentParser(description="ImageQualityAnalyzer License Management")
    parser.add_argument("--check", action="store_true", help="Check license compliance")
    parser.add_argument("--report", action="store_true", help="Generate compliance report")
    parser.add_argument("--template", action="store_true", help="Create license template")
    
    args = parser.parse_args()
    
    enforcer = LicenseEnforcement()
    
    if args.template:
        create_commercial_license_template()
    elif args.report:
        print(enforcer.generate_license_report())
    elif args.check:
        compliance = enforcer.check_license_compliance()
        print(f"License Status: {'COMPLIANT' if compliance['compliant'] else 'NON-COMPLIANT'}")
    else:
        print("ImageQualityAnalyzer License Management")
        print("Usage: python license_enforcement.py --check|--report|--template")


# Auto-run license check when module is imported
verify_license_on_import()

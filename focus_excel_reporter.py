"""
Enhanced Excel Report Generator with Focus-Specific Features

This module generates Excel reports with enhanced focus detection information,
including specific "out of focus" flags and detailed focus quality analysis.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime


class FocusEnhancedExcelReporter:
    """Excel reporter with enhanced focus detection features"""
    
    def __init__(self):
        """Initialize the reporter"""
        self.focus_thresholds = {
            'excellent': 300.0,
            'good': 200.0, 
            'acceptable': 120.0,
            'poor': 80.0,
            'unusable': 0.0
        }
    
    def generate_focus_report(self, analysis_results: List[Dict[str, Any]], 
                            output_file: str = None) -> str:
        """
        Generate Excel report with focus-specific analysis
        
        Args:
            analysis_results: List of analysis results from enhanced focus detector
            output_file: Output Excel file path
            
        Returns:
            Path to generated Excel file
        """
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"focus_analysis_report_{timestamp}.xlsx"
        
        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # 1. Executive Summary with Focus Overview
            self._create_executive_summary(analysis_results, writer)
            
            # 2. Focus Quality Details
            self._create_focus_details_sheet(analysis_results, writer)
            
            # 3. Failed Images (Out of Focus)
            self._create_failed_images_sheet(analysis_results, writer)
            
            # 4. Focus Recommendations
            self._create_recommendations_sheet(analysis_results, writer)
            
            # 5. Raw Focus Metrics
            self._create_raw_metrics_sheet(analysis_results, writer)
        
        print(f"📊 Focus analysis report generated: {output_file}")
        return output_file
    
    def _create_executive_summary(self, results: List[Dict[str, Any]], writer):
        """Create executive summary sheet with focus statistics"""
        
        # Calculate focus statistics
        total_images = len(results)
        focus_distribution = {
            'excellent': 0, 'good': 0, 'acceptable': 0, 'poor': 0, 'unusable': 0
        }
        
        overall_scores = []
        focus_scores = []
        failed_for_focus = 0
        
        for result in results:
            # Get focus analysis
            focus_analysis = result.get('focus_analysis', {})
            focus_level = focus_analysis.get('focus_level', 'unknown')
            
            if focus_level in focus_distribution:
                focus_distribution[focus_level] += 1
            
            # Count failures specifically for focus
            if focus_level in ['poor', 'unusable']:
                failed_for_focus += 1
            
            # Collect scores
            overall_scores.append(result.get('overall_score', 0.0))
            focus_scores.append(focus_analysis.get('focus_score', 0.0))
        
        # Create summary data
        summary_data = [
            ['FOCUS ANALYSIS SUMMARY', ''],
            ['', ''],
            ['Total Images Analyzed', total_images],
            ['', ''],
            ['FOCUS QUALITY DISTRIBUTION', ''],
            ['🟢 Excellent Focus', focus_distribution['excellent']],
            ['🟢 Good Focus', focus_distribution['good']],
            ['🟡 Acceptable Focus', focus_distribution['acceptable']],
            ['🔴 Poor Focus (Out of Focus)', focus_distribution['poor']],
            ['🔴 Unusable (Severely Out of Focus)', focus_distribution['unusable']],
            ['', ''],
            ['KEY STATISTICS', ''],
            [f'Images Failed for OUT OF FOCUS', failed_for_focus],
            [f'Failure Rate', f'{failed_for_focus/total_images*100:.1f}%' if total_images > 0 else '0%'],
            [f'Usable Images', total_images - failed_for_focus],
            [f'Success Rate', f'{(total_images-failed_for_focus)/total_images*100:.1f}%' if total_images > 0 else '0%'],
            ['', ''],
            ['AVERAGE SCORES', ''],
            ['Average Overall Score', f'{sum(overall_scores)/len(overall_scores):.3f}' if overall_scores else '0.000'],
            ['Average Focus Score', f'{sum(focus_scores)/len(focus_scores):.1f}' if focus_scores else '0.0'],
            ['', ''],
            ['FOCUS QUALITY THRESHOLDS', ''],
            ['Excellent Focus (≥300)', 'Professional quality'],
            ['Good Focus (≥200)', 'Suitable for most uses'],
            ['Acceptable Focus (≥120)', 'Usable with minor issues'],
            ['Poor Focus (≥80)', 'Out of focus - noticeable blur'],
            ['Unusable Focus (<80)', 'Severely out of focus']
        ]
        
        df_summary = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
        df_summary.to_excel(writer, sheet_name='Executive Summary', index=False)
        
        # Format the sheet
        worksheet = writer.sheets['Executive Summary']
        worksheet.column_dimensions['A'].width = 35
        worksheet.column_dimensions['B'].width = 25
    
    def _create_focus_details_sheet(self, results: List[Dict[str, Any]], writer):
        """Create detailed focus analysis sheet"""
        
        focus_data = []
        
        for result in results:
            filename = Path(result.get('image_path', '')).name
            focus_analysis = result.get('focus_analysis', {})
            
            # Basic info
            focus_level = focus_analysis.get('focus_level', 'unknown')
            focus_score = focus_analysis.get('focus_score', 0.0)
            confidence = focus_analysis.get('confidence', 0.0)
            
            # Overall status
            overall_score = result.get('overall_score', 0.0)
            overall_status = result.get('overall_status', 'unknown')
            
            # Focus metrics breakdown
            metrics = focus_analysis.get('metrics_breakdown', {})
            
            # Issues and recommendations
            focus_issues = focus_analysis.get('focus_issues', [])
            main_issue = focus_issues[0] if focus_issues else 'No issues detected'
            
            # Determine status display
            if focus_level in ['poor', 'unusable']:
                focus_status = '🔴 FAILED - OUT OF FOCUS'
                action_needed = 'RETAKE REQUIRED'
            elif focus_level == 'acceptable':
                focus_status = '🟡 SOFT - Minor Issues'
                action_needed = 'Consider retaking'
            else:
                focus_status = '🟢 GOOD - Acceptable'
                action_needed = 'Ready for use'
            
            focus_data.append({
                'Filename': filename,
                'Focus Status': focus_status,
                'Focus Level': focus_level.upper(),
                'Focus Score': f'{focus_score:.1f}',
                'Confidence': f'{confidence:.1%}',
                'Overall Score': f'{overall_score:.3f}',
                'Overall Status': overall_status.upper(),
                'Primary Sharpness': f"{metrics.get('primary_sharpness', 0):.1f}",
                'Edge Content': f"{metrics.get('edge_content', 0):.4f}",
                'High Freq Energy': f"{metrics.get('high_freq_energy', 0):.6f}",
                'Gradient Strength': f"{metrics.get('gradient_strength', 0):.1f}",
                'Main Issue': main_issue,
                'Action Needed': action_needed
            })
        
        df_focus = pd.DataFrame(focus_data)
        df_focus.to_excel(writer, sheet_name='Focus Details', index=False)
        
        # Format the sheet
        worksheet = writer.sheets['Focus Details']
        for col in worksheet.columns:
            max_length = max(len(str(cell.value)) for cell in col)
            worksheet.column_dimensions[col[0].column_letter].width = min(max_length + 2, 50)
    
    def _create_failed_images_sheet(self, results: List[Dict[str, Any]], writer):
        """Create sheet specifically for out-of-focus images"""
        
        failed_data = []
        
        for result in results:
            focus_analysis = result.get('focus_analysis', {})
            focus_level = focus_analysis.get('focus_level', 'unknown')
            
            # Only include images that failed for focus
            if focus_level in ['poor', 'unusable']:
                filename = Path(result.get('image_path', '')).name
                focus_score = focus_analysis.get('focus_score', 0.0)
                
                # Get focus issues
                focus_issues = focus_analysis.get('focus_issues', [])
                
                # Get recommendations
                recommendations = result.get('focus_recommendations', [])
                critical_recs = [rec for rec in recommendations if 'CRITICAL' in rec]
                
                failed_data.append({
                    'Filename': filename,
                    'Failure Reason': 'OUT OF FOCUS',
                    'Focus Level': focus_level.upper(),
                    'Focus Score': f'{focus_score:.1f}',
                    'Threshold': '≥120 required',
                    'Primary Issue': focus_issues[0] if focus_issues else 'Focus quality below threshold',
                    'Secondary Issues': '; '.join(focus_issues[1:3]) if len(focus_issues) > 1 else 'None',
                    'Critical Recommendations': critical_recs[0] if critical_recs else 'Retake with better focus',
                    'Additional Recommendations': '; '.join([rec for rec in recommendations[1:3] if 'CRITICAL' not in rec])
                })
        
        if failed_data:
            df_failed = pd.DataFrame(failed_data)
            df_failed.to_excel(writer, sheet_name='Failed - Out of Focus', index=False)
            
            # Format the sheet
            worksheet = writer.sheets['Failed - Out of Focus']
            for col in worksheet.columns:
                max_length = max(len(str(cell.value)) for cell in col)
                worksheet.column_dimensions[col[0].column_letter].width = min(max_length + 2, 60)
        else:
            # Create empty sheet with message
            df_empty = pd.DataFrame([['No images failed for out of focus issues']], 
                                  columns=['Message'])
            df_empty.to_excel(writer, sheet_name='Failed - Out of Focus', index=False)
    
    def _create_recommendations_sheet(self, results: List[Dict[str, Any]], writer):
        """Create recommendations sheet focused on focus improvements"""
        
        rec_data = []
        
        for result in results:
            filename = Path(result.get('image_path', '')).name
            focus_analysis = result.get('focus_analysis', {})
            focus_level = focus_analysis.get('focus_level', 'unknown')
            
            # Only include images that need improvement
            if focus_level in ['acceptable', 'poor', 'unusable']:
                recommendations = result.get('focus_recommendations', [])
                
                # Categorize recommendations
                critical_recs = [rec for rec in recommendations if '🔴' in rec or 'CRITICAL' in rec]
                warning_recs = [rec for rec in recommendations if '🟡' in rec or 'WARNING' in rec]
                general_recs = [rec for rec in recommendations if rec not in critical_recs + warning_recs]
                
                # Priority level
                if focus_level in ['poor', 'unusable']:
                    priority = 'CRITICAL - RETAKE REQUIRED'
                else:
                    priority = 'WARNING - CONSIDER IMPROVEMENT'
                
                rec_data.append({
                    'Filename': filename,
                    'Focus Level': focus_level.upper(),
                    'Priority': priority,
                    'Primary Recommendation': critical_recs[0] if critical_recs else warning_recs[0] if warning_recs else general_recs[0] if general_recs else 'No specific recommendations',
                    'Secondary Recommendation': critical_recs[1] if len(critical_recs) > 1 else warning_recs[1] if len(warning_recs) > 1 else general_recs[1] if len(general_recs) > 1 else '',
                    'Additional Actions': '; '.join(general_recs[:2]) if general_recs else 'Review focus settings',
                    'Expected Improvement': 'Better focus quality' if focus_level in ['poor', 'unusable'] else 'Optimal focus quality'
                })
        
        if rec_data:
            df_rec = pd.DataFrame(rec_data)
            df_rec.to_excel(writer, sheet_name='Focus Recommendations', index=False)
            
            # Format the sheet
            worksheet = writer.sheets['Focus Recommendations']
            for col in worksheet.columns:
                max_length = max(len(str(cell.value)) for cell in col)
                worksheet.column_dimensions[col[0].column_letter].width = min(max_length + 2, 80)
        else:
            # Create empty sheet with message
            df_empty = pd.DataFrame([['All images have acceptable focus quality']], 
                                  columns=['Message'])
            df_empty.to_excel(writer, sheet_name='Focus Recommendations', index=False)
    
    def _create_raw_metrics_sheet(self, results: List[Dict[str, Any]], writer):
        """Create sheet with raw focus metrics data"""
        
        raw_data = []
        
        for result in results:
            filename = Path(result.get('image_path', '')).name
            focus_analysis = result.get('focus_analysis', {})
            metrics = focus_analysis.get('metrics_breakdown', {})
            
            raw_data.append({
                'Filename': filename,
                'Focus_Level': focus_analysis.get('focus_level', 'unknown'),
                'Primary_Sharpness_Laplacian': metrics.get('primary_sharpness', 0.0),
                'Edge_Content_Density': metrics.get('edge_content', 0.0),
                'High_Frequency_Energy': metrics.get('high_freq_energy', 0.0),
                'Local_Variation_Std': metrics.get('local_variation', 0.0),
                'Gradient_Strength_Mean': metrics.get('gradient_strength', 0.0),
                'Focus_Confidence_Score': focus_analysis.get('confidence', 0.0),
                'Overall_Quality_Score': result.get('overall_score', 0.0),
                'Overall_Status': result.get('overall_status', 'unknown'),
                'Image_Path': result.get('image_path', '')
            })
        
        df_raw = pd.DataFrame(raw_data)
        df_raw.to_excel(writer, sheet_name='Raw Focus Metrics', index=False)
        
        # Format the sheet
        worksheet = writer.sheets['Raw Focus Metrics']
        for col in worksheet.columns:
            max_length = max(len(str(cell.value)) for cell in col)
            worksheet.column_dimensions[col[0].column_letter].width = min(max_length + 2, 30)


def generate_sample_focus_report():
    """Generate a sample focus report for demonstration"""
    
    print("📊 GENERATING SAMPLE FOCUS REPORT")
    print("="*50)
    
    # Sample data simulating different focus quality levels
    sample_results = [
        {
            'image_path': 'sample_sharp_document.jpg',
            'overall_score': 0.92,
            'overall_status': 'pass',
            'focus_analysis': {
                'focus_level': 'excellent',
                'focus_score': 350.5,
                'confidence': 0.95,
                'focus_issues': [],
                'metrics_breakdown': {
                    'primary_sharpness': 350.5,
                    'edge_content': 0.025,
                    'high_freq_energy': 0.003,
                    'local_variation': 1200.0,
                    'gradient_strength': 18.5
                }
            },
            'focus_recommendations': []
        },
        {
            'image_path': 'sample_blurry_document.jpg',
            'overall_score': 0.45,
            'overall_status': 'fail',
            'focus_analysis': {
                'focus_level': 'poor',
                'focus_score': 75.2,
                'confidence': 0.88,
                'focus_issues': ['Out of focus - noticeable blur', 'Low edge content - soft focus'],
                'metrics_breakdown': {
                    'primary_sharpness': 75.2,
                    'edge_content': 0.008,
                    'high_freq_energy': 0.0005,
                    'local_variation': 150.0,
                    'gradient_strength': 8.2
                }
            },
            'focus_recommendations': [
                '🔴 CRITICAL: Image failed for OUT OF FOCUS - retake required',
                '📸 Use auto-focus or tap screen to focus on document',
                '🎯 Ensure proper distance - too close causes focus issues'
            ]
        },
        {
            'image_path': 'sample_soft_document.jpg',
            'overall_score': 0.68,
            'overall_status': 'warn',
            'focus_analysis': {
                'focus_level': 'acceptable',
                'focus_score': 135.8,
                'confidence': 0.82,
                'focus_issues': ['Slightly soft focus - minor blur'],
                'metrics_breakdown': {
                    'primary_sharpness': 135.8,
                    'edge_content': 0.013,
                    'high_freq_energy': 0.0012,
                    'local_variation': 450.0,
                    'gradient_strength': 12.1
                }
            },
            'focus_recommendations': [
                '🟡 WARNING: Image is slightly soft - consider retaking for better quality',
                '🔧 Fine-tune focus or move slightly closer/further'
            ]
        }
    ]
    
    # Generate the report
    reporter = FocusEnhancedExcelReporter()
    output_file = reporter.generate_focus_report(sample_results, "sample_focus_analysis_report.xlsx")
    
    print(f"\n✅ Sample focus report generated: {output_file}")
    print("\nThe report includes:")
    print("- 📋 Executive Summary with focus statistics")
    print("- 🔍 Detailed focus quality analysis")
    print("- 🔴 Failed images (out of focus) with reasons")
    print("- 💡 Focus improvement recommendations")
    print("- 📊 Raw focus metrics for technical analysis")
    
    return output_file


if __name__ == "__main__":
    generate_sample_focus_report()

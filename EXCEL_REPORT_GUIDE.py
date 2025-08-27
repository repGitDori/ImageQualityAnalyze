"""
📊 COMPLETE GUIDE TO EXCEL ANALYSIS REPORTS
===========================================

This guide explains each sheet in your Excel export and what to look for.
"""

def create_analysis_guide():
    guide = """
🔍 EXCEL REPORT STRUCTURE EXPLAINED
===================================

Your image quality analysis generates a comprehensive Excel report with 4 main sheets:
1. Executive Summary
2. Detailed Quality Metrics  
3. Improvement Recommendations
4. Visual Analysis Charts

Let's break down what each sheet tells you and what to look for:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 SHEET 1: EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 PURPOSE: High-level overview for decision makers

📊 KEY METRICS TO EXAMINE:

┌─────────────────────┬─────────────────┬────────────────────────────────────┐
│ FIELD               │ WHAT IT MEANS   │ WHAT TO LOOK FOR                   │
├─────────────────────┼─────────────────┼────────────────────────────────────┤
│ Overall Score       │ 0.0 to 1.0      │ • 0.8+ = Excellent quality        │
│                     │ quality rating  │ • 0.6-0.8 = Good quality          │
│                     │                 │ • 0.4-0.6 = Fair quality          │
│                     │                 │ • Below 0.4 = Poor quality        │
├─────────────────────┼─────────────────┼────────────────────────────────────┤
│ Quality Rating      │ 1-4 star system│ • 4 stars = Professional grade    │
│ (Stars)             │                 │ • 3 stars = Good for most uses    │
│                     │                 │ • 2 stars = Acceptable            │
│                     │                 │ • 1 star = Needs improvement      │
├─────────────────────┼─────────────────┼────────────────────────────────────┤
│ Status              │ Overall verdict │ • EXCELLENT = Ready to use        │
│                     │                 │ • GOOD = Minor improvements        │
│                     │                 │ • FAIR = Some issues to address   │
│                     │                 │ • FAIL = Major problems           │
├─────────────────────┼─────────────────┼────────────────────────────────────┤
│ Quality Gauge       │ Visual bar      │ • Length shows quality level      │
│                     │                 │ • Quick visual assessment         │
└─────────────────────┴─────────────────┴────────────────────────────────────┘

🚨 RED FLAGS TO WATCH FOR:
• Overall Score below 0.4
• Status showing "FAIL"
• Only 1 star rating
• Short quality gauge bar

✅ GOOD SIGNS:
• Overall Score above 0.7
• Status showing "EXCELLENT" or "GOOD"
• 3-4 star rating
• Long quality gauge bar

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SHEET 2: DETAILED QUALITY METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 PURPOSE: Technical breakdown of each quality aspect

📊 METRICS EXPLAINED:

┌─────────────────────┬─────────────────────────────────────────────────────┐
│ METRIC              │ WHAT IT MEASURES & WHAT TO LOOK FOR                │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 📄 COMPLETENESS     │ • Is the full document captured?                   │
│                     │ • Look for: Score 0.8+ means full doc visible      │
│                     │ • Red flag: Score below 0.5 = missing content      │
│                     │ • Details show: coverage percentage, edge touching  │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 🔍 SHARPNESS        │ • How clear and crisp is the text/image?           │
│                     │ • Look for: Score 0.7+ for readable text           │
│                     │ • Red flag: Score below 0.5 = blurry/out of focus  │
│                     │ • Details show: edge sharpness, blur measurements  │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 💡 EXPOSURE         │ • Is the lighting appropriate?                     │
│                     │ • Look for: Score 0.6+ for good visibility         │
│                     │ • Red flag: Score below 0.4 = too dark/bright      │
│                     │ • Details show: shadow/highlight clipping %        │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ ⚖️ CONTRAST         │ • Can you distinguish text from background?        │
│                     │ • Look for: Score 0.7+ for easy reading            │
│                     │ • Red flag: Score below 0.5 = poor readability     │
│                     │ • Details show: contrast ratios, luminance         │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 🎨 COLOR            │ • Are colors natural and balanced?                 │
│                     │ • Look for: Score 0.6+ for good color reproduction │
│                     │ • Red flag: Score below 0.4 = color cast issues    │
│                     │ • Details show: hue shifts, color balance          │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 📐 GEOMETRY         │ • Is the document straight and properly aligned?   │
│                     │ • Look for: Score 0.8+ for minimal distortion      │
│                     │ • Red flag: Score below 0.6 = skewed/warped        │
│                     │ • Details show: skew angle, perspective distortion │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 🏞️ BORDER/BACKGROUND│ • Is the background clean and uniform?             │
│                     │ • Look for: Score 0.7+ for clean background        │
│                     │ • Red flag: Score below 0.5 = busy/distracting BG  │
│                     │ • Details show: background uniformity, margins     │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 🔇 NOISE            │ • How much grain/digital noise is present?         │
│                     │ • Look for: Score 0.7+ for clean image             │
│                     │ • Red flag: Score below 0.5 = excessive noise      │
│                     │ • Details show: noise levels, grain measurements   │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 📱 FORMAT INTEGRITY │ • Is the file format appropriate and uncorrupted?  │
│                     │ • Look for: Score 0.8+ for reliable file           │
│                     │ • Red flag: Score below 0.6 = format issues        │
│                     │ • Details show: format type, compression quality   │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 🔬 RESOLUTION       │ • Is the image resolution sufficient for purpose?  │
│                     │ • Look for: Score 0.7+ for good detail capture     │
│                     │ • Red flag: Score below 0.5 = insufficient quality │
│                     │ • Details show: DPI values, pixel dimensions       │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 🚫 FOREIGN OBJECTS  │ • Are there unwanted items in the image?           │
│                     │ • Look for: Score 0.9+ for clean document          │
│                     │ • Red flag: Score below 0.7 = fingers/shadows/etc  │
│                     │ • Details show: object detection, obstruction %    │
└─────────────────────┴─────────────────────────────────────────────────────┘

📊 SCORE INTERPRETATION:
• 0.85+ (EXCELLENT) = Professional quality, meets all standards
• 0.70-0.84 (GOOD) = Acceptable quality, minor improvements possible  
• 0.30-0.69 (FAIR) = Usable but has noticeable issues
• Below 0.30 (POOR) = Significant problems, retake recommended

📊 STATUS COLOR CODING:
• 🟢 Green = EXCELLENT (ready to use)
• 🟡 Orange = FAIR (acceptable with caveats)  
• 🔴 Red = POOR (needs improvement)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 SHEET 3: IMPROVEMENT RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 PURPOSE: Actionable advice to improve image quality

📋 RECOMMENDATION TYPES:

┌─────────────────┬─────────────────────────────────────────────────────────┐
│ PRIORITY LEVEL  │ WHAT IT MEANS & WHEN TO ACT                             │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ 🚨 CRITICAL     │ • Must be addressed for acceptable quality              │
│                 │ • Image unusable for intended purpose                   │
│                 │ • Immediate action required                             │
│                 │ • Examples: "Document partially cut off"               │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ ⚠️ WARNING      │ • Should be addressed for optimal quality               │
│                 │ • Image usable but could be better                     │
│                 │ • Action recommended                                    │
│                 │ • Examples: "Consider better lighting"                 │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ ℹ️ INFO         │ • Optional improvements for perfect quality             │
│                 │ • Image already acceptable                              │
│                 │ • Action optional                                       │
│                 │ • Examples: "Excellent quality maintained"             │
└─────────────────┴─────────────────────────────────────────────────────────┘

📋 COMMON RECOMMENDATIONS & SOLUTIONS:

• "Ensure full document is captured with margins"
  → Move camera back or adjust framing

• "Adjust lighting or camera exposure settings"  
  → Use more even lighting, avoid shadows

• "Straighten document or adjust camera angle"
  → Use document scanner app or manual alignment

• "Use lower ISO setting or better lighting"
  → Reduce camera ISO, add more light

• "Scan/photograph at higher DPI/resolution"
  → Use higher quality camera settings

• "Remove foreign objects from frame"
  → Clear fingers, shadows, or other obstructions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 SHEET 4: VISUAL ANALYSIS CHARTS  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 PURPOSE: Graphical overview for quick assessment

📊 CHART ELEMENTS:

┌─────────────────┬─────────────────────────────────────────────────────────┐
│ VISUAL ELEMENT  │ HOW TO INTERPRET                                        │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ 📊 Bar Chart    │ • Each bar = one quality metric                         │
│                 │ • Height = score (0-1 scale)                           │
│                 │ • Look for: Consistently high bars = good quality       │
│                 │ • Red flag: Short bars = problem areas                  │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ 📋 Data Table   │ • Metric names and exact scores                         │
│                 │ • Use to identify specific problem metrics              │
│                 │ • Cross-reference with detailed metrics sheet           │
└─────────────────┴─────────────────────────────────────────────────────────┘

🎯 QUICK VISUAL ASSESSMENT:
• All bars above 0.7 = Excellent overall quality
• Mixed heights = Some good, some problem areas  
• Most bars below 0.5 = Multiple quality issues
• One very short bar = Specific problem to address

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 PRACTICAL USAGE GUIDE
━━━━━━━━━━━━━━━━━━━━━━━

📋 FOR DOCUMENT SCANNING:
✅ ACCEPTABLE: Overall score 0.6+, Sharpness 0.7+, Completeness 0.8+
❌ RESHOOT IF: Any score below 0.3, or Overall below 0.4

📋 FOR ARCHIVAL PURPOSES:  
✅ ACCEPTABLE: Overall score 0.8+, Resolution 0.8+, Format Integrity 0.9+
❌ RESHOOT IF: Any score below 0.6, or Overall below 0.7

📋 FOR PROFESSIONAL USE:
✅ ACCEPTABLE: Overall score 0.9+, All metrics 0.7+
❌ RESHOOT IF: Any metric below 0.5, or Overall below 0.8

📋 FOR QUICK SHARING:
✅ ACCEPTABLE: Overall score 0.5+, Sharpness 0.6+, Exposure 0.5+  
❌ RESHOOT IF: Overall below 0.3, or completely unreadable

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 TROUBLESHOOTING COMMON ISSUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ LOW SHARPNESS SCORE:
• Camera shake → Use tripod or steadier hold
• Wrong focus → Tap screen to focus on document  
• Motion blur → Use faster shutter speed
• Lens dirt → Clean camera lens

❓ LOW EXPOSURE SCORE:  
• Too dark → Add more light, increase exposure
• Too bright → Reduce light, decrease exposure
• Uneven lighting → Use diffused, even light sources
• Strong shadows → Reposition light sources

❓ LOW COMPLETENESS SCORE:
• Document cut off → Move camera back, adjust framing
• Missing corners → Ensure full document visible
• Poor margins → Leave space around document edges

❓ LOW GEOMETRY SCORE:
• Document tilted → Align document with camera
• Perspective distortion → Shoot straight-on, not angled
• Warped/curved → Flatten document completely

❓ LOW CONTRAST SCORE:
• Text too faint → Increase contrast in camera settings
• Poor separation → Improve lighting contrast
• Washed out → Reduce overexposure

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ SUMMARY: WHAT TO FOCUS ON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 📋 START WITH EXECUTIVE SUMMARY
   • Check overall score and status
   • Determine if image meets your needs

2. 📊 DIVE INTO DETAILED METRICS  
   • Identify specific problem areas
   • Focus on metrics with poor scores

3. 💡 FOLLOW RECOMMENDATIONS
   • Address critical issues first
   • Use specific guidance provided

4. 📈 USE CHARTS FOR QUICK OVERVIEW
   • Spot problem areas visually
   • Track improvements over time

Remember: The goal is to capture images that serve your specific purpose.
Not every image needs to be perfect - just good enough for its intended use!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    return guide

if __name__ == "__main__":
    print(create_analysis_guide())

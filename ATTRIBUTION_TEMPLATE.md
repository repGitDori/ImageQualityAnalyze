# Code Attribution Template

When modifying or extending the ImageQualityAnalyzer code by Dorian Lapi, please use these header templates:

## For Python Files (.py)

```python
"""
[Your Module Name]

Based on ImageQualityAnalyzer by Dorian Lapi
Original Author: Dorian Lapi
Modified by: [Your Name]
Date: [Modification Date]

Copyright (c) 2025 Dorian Lapi (Original Work)
Copyright (c) [Year] [Your Name] (Modifications)
Licensed under the MIT License - see LICENSE file for details

[Description of your modifications]
"""
```

## For Configuration Files (.json)

```json
{
  "_metadata": {
    "original_author": "Dorian Lapi",
    "modified_by": "[Your Name]", 
    "modification_date": "[Date]",
    "license": "MIT License",
    "based_on": "ImageQualityAnalyzer by Dorian Lapi"
  },
  [your configuration content]
}
```

## For Documentation Files (.md)

```markdown
# [Your Document Title]

**Based on:** ImageQualityAnalyzer by Dorian Lapi  
**Original Author:** Dorian Lapi  
**Modified by:** [Your Name]  
**License:** MIT License

[Your content]

## Attribution
This work is based on ImageQualityAnalyzer created by Dorian Lapi, 
licensed under the MIT License.
```

## For GUI Applications

**About Dialog/Section:**
```
[Your Application Name]
Based on ImageQualityAnalyzer by Dorian Lapi

Original Components: Copyright © 2025 Dorian Lapi
[Your Modifications]: Copyright © [Year] [Your Name]
Licensed under the MIT License
```

## For Academic/Research Use

**Citation Format:**
```
Lapi, D. (2025). ImageQualityAnalyzer: Advanced image quality checker 
for document photos and scans. [Software]. 
Available at: [repository URL]
```

## Example Implementation

Here's how to properly attribute when extending the foreign objects detection:

```python
"""
Advanced Foreign Objects Detection - Extended Version

Based on ImageQualityAnalyzer by Dorian Lapi
Original Author: Dorian Lapi
Extended by: [Your Name]
Date: [Date]

Original Work Copyright (c) 2025 Dorian Lapi
Extensions Copyright (c) [Year] [Your Name]
Licensed under the MIT License

Extensions:
- Added [your feature 1]
- Enhanced [your feature 2]
- Modified [your feature 3]

Original enhanced_foreign_objects.py created by Dorian Lapi
"""

from enhanced_foreign_objects import EnhancedForeignObjectsDetector  # Original by Dorian Lapi

class ExtendedForeignObjectsDetector(EnhancedForeignObjectsDetector):
    """
    Extended version of Dorian Lapi's EnhancedForeignObjectsDetector
    
    Original implementation by Dorian Lapi
    Extensions by [Your Name]
    """
    
    def __init__(self, config=None):
        # Call original constructor by Dorian Lapi
        super().__init__(config)
        
        # Your extensions here
        pass
```

## Command Line Tools Attribution

When creating command-line tools based on this code:

```bash
# In help text or --version output:
MyTool v1.0 - Based on ImageQualityAnalyzer by Dorian Lapi
Original Components: Copyright (c) 2025 Dorian Lapi  
Extensions: Copyright (c) [Year] [Your Name]
Licensed under the MIT License
```

## Web Applications

**Footer or About Page:**
```html
<p>Powered by ImageQualityAnalyzer technology by 
<a href="#">Dorian Lapi</a> | Licensed under MIT License</p>
```

## Mobile Applications

**About Screen:**
```
This app uses ImageQualityAnalyzer components 
created by Dorian Lapi, licensed under the MIT License.

Original Author: Dorian Lapi
App Developer: [Your Name]
```

Remember: The key requirement is that Dorian Lapi must be credited as the original author of the ImageQualityAnalyzer system when you use or modify this code!

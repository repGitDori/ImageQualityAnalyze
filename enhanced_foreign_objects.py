"""
Enhanced Foreign Objects Detection for Document Analysis

This enhanced system detects two main types of foreign objects:
1. Tools/clips holding pages - create pixelated backgrounds with non-black borders
2. Black foreign objects - go deep into document area (hands, shadows, etc.)

Based on real-world document scanning scenarios where foreign objects 
interfere with proper document capture.
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path


class EnhancedForeignObjectsDetector:
    """Enhanced detection for foreign objects in document captures"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with configuration parameters"""
        
        self.config = config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for foreign object detection"""
        
        return {
            "foreign_objects": {
                # Clip/tool detection (pixelated background, non-black borders)
                "clip_detection": {
                    "min_contour_area": 1000,           # Minimum size for clip detection
                    "max_border_luminance": 0.15,       # Black border threshold
                    "pixelation_threshold": 0.3,        # Background pixelation indicator
                    "aspect_ratio_range": [0.1, 10.0],  # Valid aspect ratios
                    "edge_proximity": 50                 # Pixels from image edge
                },
                
                # Black object detection (objects in document area)
                "black_object_detection": {
                    "min_darkness_threshold": 0.1,      # Maximum luminance for "black"
                    "min_object_area": 500,              # Minimum size for detection
                    "document_penetration": 0.05,       # How deep into document (5%)
                    "contrast_ratio": 2.0,               # Contrast with surrounding area
                    "shadow_detection": True             # Detect accompanying shadows
                },
                
                # General settings
                "failure_thresholds": {
                    "clip_area_pct": 2.0,               # % of image covered by clips
                    "black_object_area_pct": 1.0,       # % of document covered by black objects
                    "combined_area_pct": 3.0             # Total foreign object coverage
                }
            }
        }
    
    def analyze_foreign_objects(self, image: np.ndarray, doc_mask: np.ndarray) -> Dict[str, Any]:
        """
        Comprehensive foreign object analysis
        
        Args:
            image: Input image array
            doc_mask: Document area mask
            
        Returns:
            Dictionary with foreign object analysis results
        """
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 1. Detect clips/tools (background objects with non-black borders)
        clip_results = self._detect_clips_and_tools(image, gray, doc_mask)
        
        # 2. Detect black objects penetrating document area
        black_object_results = self._detect_black_objects_in_document(image, gray, doc_mask)
        
        # 3. Additional analysis for shadows and reflections
        shadow_results = self._detect_shadows_and_reflections(image, gray, doc_mask)
        
        # 4. Combine results and determine overall foreign object status
        combined_results = self._combine_detection_results(
            clip_results, black_object_results, shadow_results, image.shape
        )
        
        return combined_results
    
    def _detect_clips_and_tools(self, image: np.ndarray, gray: np.ndarray, 
                               doc_mask: np.ndarray) -> Dict[str, Any]:
        """Detect clips, tools, and other objects holding the document"""
        
        config = self.config["foreign_objects"]["clip_detection"]
        
        # Create background mask (areas outside document)
        bg_mask = (1 - doc_mask).astype(np.uint8)
        
        # Look for non-black objects in background
        # Clips/tools usually have metallic or colored surfaces
        bg_gray = gray * bg_mask
        
        # Threshold to find non-black objects in background
        max_black_luminance = int(config["max_border_luminance"] * 255)
        _, non_black_mask = cv2.threshold(bg_gray, max_black_luminance, 255, cv2.THRESH_BINARY)
        
        # Find contours of potential clips/tools
        contours, _ = cv2.findContours(non_black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_clips = []
        total_clip_area = 0
        
        h, w = image.shape[:2]
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by minimum size
            if area < config["min_contour_area"]:
                continue
            
            # Get bounding rectangle
            x, y, cw, ch = cv2.boundingRect(contour)
            
            # Check if near image edges (clips usually are)
            edge_proximity = config["edge_proximity"]
            near_edge = (x < edge_proximity or y < edge_proximity or 
                        x + cw > w - edge_proximity or y + ch > h - edge_proximity)
            
            # Calculate aspect ratio
            aspect_ratio = cw / ch if ch > 0 else 0
            valid_aspect = (config["aspect_ratio_range"][0] <= aspect_ratio <= 
                          config["aspect_ratio_range"][1])
            
            # Check for pixelation in surrounding area (indicates tools/clips)
            pixelation_score = self._calculate_pixelation_score(gray, x, y, cw, ch)
            
            if near_edge and valid_aspect and pixelation_score > config["pixelation_threshold"]:
                clip_info = {
                    'bbox': (x, y, cw, ch),
                    'area': area,
                    'aspect_ratio': aspect_ratio,
                    'pixelation_score': pixelation_score,
                    'position': self._get_edge_position(x, y, cw, ch, w, h),
                    'type': 'clip_or_tool'
                }
                detected_clips.append(clip_info)
                total_clip_area += area
        
        # Calculate percentage of image covered by clips
        total_image_area = h * w
        clip_area_pct = (total_clip_area / total_image_area) * 100
        
        return {
            'detected_clips': detected_clips,
            'clip_count': len(detected_clips),
            'total_clip_area': total_clip_area,
            'clip_area_percentage': clip_area_pct,
            'clip_flag': clip_area_pct > config.get('failure_threshold', 2.0)
        }
    
    def _detect_black_objects_in_document(self, image: np.ndarray, gray: np.ndarray,
                                        doc_mask: np.ndarray) -> Dict[str, Any]:
        """Detect black foreign objects that penetrate into the document area"""
        
        config = self.config["foreign_objects"]["black_object_detection"]
        
        # Focus on document area only
        doc_gray = gray * doc_mask
        
        # Create mask for very dark objects
        darkness_threshold = int(config["min_darkness_threshold"] * 255)
        _, dark_mask = cv2.threshold(doc_gray, darkness_threshold, 255, cv2.THRESH_BINARY_INV)
        
        # Remove areas that are naturally dark (text, etc.)
        # Use morphological operations to focus on larger dark areas
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours of dark objects
        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_black_objects = []
        total_black_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by minimum size
            if area < config["min_object_area"]:
                continue
            
            # Get bounding rectangle
            x, y, cw, ch = cv2.boundingRect(contour)
            
            # Check if object penetrates significantly into document
            penetration_depth = self._calculate_document_penetration(
                contour, doc_mask, config["document_penetration"]
            )
            
            # Check contrast with surrounding document area
            contrast_ratio = self._calculate_local_contrast(gray, contour)
            
            if (penetration_depth > config["document_penetration"] and 
                contrast_ratio > config["contrast_ratio"]):
                
                # Classify object type
                object_type = self._classify_black_object(image, contour, x, y, cw, ch)
                
                object_info = {
                    'bbox': (x, y, cw, ch),
                    'area': area,
                    'penetration_depth': penetration_depth,
                    'contrast_ratio': contrast_ratio,
                    'type': object_type,
                    'centroid': self._get_contour_centroid(contour)
                }
                detected_black_objects.append(object_info)
                total_black_area += area
        
        # Calculate percentage of document covered by black objects
        doc_area = np.sum(doc_mask)
        black_area_pct = (total_black_area / doc_area) * 100 if doc_area > 0 else 0
        
        return {
            'detected_black_objects': detected_black_objects,
            'black_object_count': len(detected_black_objects),
            'total_black_area': total_black_area,
            'black_area_percentage': black_area_pct,
            'black_object_flag': black_area_pct > config.get('failure_threshold', 1.0)
        }
    
    def _detect_shadows_and_reflections(self, image: np.ndarray, gray: np.ndarray,
                                      doc_mask: np.ndarray) -> Dict[str, Any]:
        """Detect shadows and reflections caused by foreign objects"""
        
        # Convert to LAB color space for better shadow detection
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]
        else:
            l_channel = gray
        
        # Focus on document area
        doc_l = l_channel * doc_mask
        
        # Calculate average luminance in document
        doc_pixels = doc_l[doc_mask > 0]
        if len(doc_pixels) == 0:
            return {'shadow_flag': False, 'reflection_flag': False}
        
        avg_luminance = np.mean(doc_pixels)
        std_luminance = np.std(doc_pixels)
        
        # Detect shadows (significantly darker than average)
        shadow_threshold = avg_luminance - (2 * std_luminance)
        shadow_mask = (doc_l < shadow_threshold) & (doc_mask > 0)
        
        # Detect reflections (significantly brighter than average)
        reflection_threshold = avg_luminance + (2 * std_luminance)
        reflection_mask = (doc_l > reflection_threshold) & (doc_mask > 0)
        
        # Calculate areas
        shadow_area = np.sum(shadow_mask)
        reflection_area = np.sum(reflection_mask)
        doc_area = np.sum(doc_mask)
        
        shadow_pct = (shadow_area / doc_area) * 100 if doc_area > 0 else 0
        reflection_pct = (reflection_area / doc_area) * 100 if doc_area > 0 else 0
        
        return {
            'shadow_area': shadow_area,
            'shadow_percentage': shadow_pct,
            'shadow_flag': shadow_pct > 3.0,  # More than 3% of document in shadow
            'reflection_area': reflection_area,
            'reflection_percentage': reflection_pct,
            'reflection_flag': reflection_pct > 2.0,  # More than 2% reflection
            'luminance_stats': {
                'average': avg_luminance,
                'std_dev': std_luminance,
                'shadow_threshold': shadow_threshold,
                'reflection_threshold': reflection_threshold
            }
        }
    
    def _calculate_pixelation_score(self, gray: np.ndarray, x: int, y: int, 
                                  w: int, h: int) -> float:
        """Calculate pixelation score in area around detected object"""
        
        # Expand area around object
        margin = 20
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(gray.shape[1], x + w + margin)
        y2 = min(gray.shape[0], y + h + margin)
        
        region = gray[y1:y2, x1:x2]
        
        if region.size == 0:
            return 0.0
        
        # Calculate gradient magnitude to detect pixelation
        grad_x = cv2.Sobel(region, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(region, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # High gradient variance indicates pixelation
        gradient_variance = np.var(gradient_magnitude)
        
        # Normalize score
        return min(gradient_variance / 1000.0, 1.0)
    
    def _calculate_document_penetration(self, contour: np.ndarray, doc_mask: np.ndarray,
                                      min_penetration: float) -> float:
        """Calculate how deep an object penetrates into the document"""
        
        # Create mask for the contour
        mask = np.zeros(doc_mask.shape, dtype=np.uint8)
        cv2.fillPoly(mask, [contour], 255)
        
        # Calculate overlap with document
        overlap_area = np.sum((mask > 0) & (doc_mask > 0))
        contour_area = cv2.contourArea(contour)
        
        if contour_area == 0:
            return 0.0
        
        return overlap_area / contour_area
    
    def _calculate_local_contrast(self, gray: np.ndarray, contour: np.ndarray) -> float:
        """Calculate contrast of object with its surrounding area"""
        
        # Create masks
        object_mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.fillPoly(object_mask, [contour], 255)
        
        # Dilate to get surrounding area
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        surrounding_mask = cv2.dilate(object_mask, kernel) - object_mask
        
        # Calculate mean intensities
        object_pixels = gray[object_mask > 0]
        surrounding_pixels = gray[surrounding_mask > 0]
        
        if len(object_pixels) == 0 or len(surrounding_pixels) == 0:
            return 0.0
        
        object_mean = np.mean(object_pixels)
        surrounding_mean = np.mean(surrounding_pixels)
        
        if surrounding_mean == 0:
            return 0.0
        
        return surrounding_mean / (object_mean + 1e-6)
    
    def _classify_black_object(self, image: np.ndarray, contour: np.ndarray,
                              x: int, y: int, w: int, h: int) -> str:
        """Classify the type of black object detected"""
        
        # Calculate shape properties
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            return 'unknown'
        
        # Circularity
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Aspect ratio
        aspect_ratio = w / h if h > 0 else 0
        
        # Classify based on shape characteristics
        if circularity > 0.7:
            return 'round_object'  # Possible finger, round tool
        elif aspect_ratio > 3.0:
            return 'linear_object'  # Possible ruler, pen, etc.
        elif aspect_ratio < 0.3:
            return 'linear_object'
        elif area > 5000:
            return 'large_object'  # Hand, large tool
        else:
            return 'small_object'  # Small tool, clip part
    
    def _get_edge_position(self, x: int, y: int, w: int, h: int, 
                          img_w: int, img_h: int) -> str:
        """Determine which edge the object is near"""
        
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Determine primary edge
        distances = {
            'top': center_y,
            'bottom': img_h - center_y,
            'left': center_x,
            'right': img_w - center_x
        }
        
        return min(distances, key=distances.get)
    
    def _get_contour_centroid(self, contour: np.ndarray) -> Tuple[int, int]:
        """Calculate centroid of contour"""
        
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            return (cx, cy)
        else:
            return (0, 0)
    
    def _combine_detection_results(self, clip_results: Dict[str, Any],
                                 black_results: Dict[str, Any],
                                 shadow_results: Dict[str, Any],
                                 image_shape: Tuple[int, ...]) -> Dict[str, Any]:
        """Combine all detection results into final assessment"""
        
        config = self.config["foreign_objects"]["failure_thresholds"]
        
        # Calculate total foreign object coverage
        total_area_pct = (clip_results['clip_area_percentage'] + 
                         black_results['black_area_percentage'])
        
        # Determine overall foreign object flag
        foreign_object_flag = (
            clip_results['clip_flag'] or
            black_results['black_object_flag'] or
            total_area_pct > config['combined_area_pct']
        )
        
        # Generate specific failure reasons
        failure_reasons = []
        if clip_results['clip_flag']:
            failure_reasons.append(f"Tools/clips detected covering {clip_results['clip_area_percentage']:.1f}% of image")
        if black_results['black_object_flag']:
            failure_reasons.append(f"Black objects penetrating {black_results['black_area_percentage']:.1f}% of document")
        if shadow_results['shadow_flag']:
            failure_reasons.append(f"Shadows covering {shadow_results['shadow_percentage']:.1f}% of document")
        if shadow_results['reflection_flag']:
            failure_reasons.append(f"Reflections affecting {shadow_results['reflection_percentage']:.1f}% of document")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            clip_results, black_results, shadow_results
        )
        
        return {
            'foreign_object_flag': foreign_object_flag,
            'foreign_object_area_pct': total_area_pct,
            'failure_reasons': failure_reasons,
            'recommendations': recommendations,
            'detailed_results': {
                'clips_and_tools': clip_results,
                'black_objects': black_results,
                'shadows_reflections': shadow_results
            },
            'summary': {
                'total_objects_detected': (clip_results['clip_count'] + 
                                         black_results['black_object_count']),
                'image_quality_impact': self._assess_quality_impact(
                    clip_results, black_results, shadow_results
                )
            }
        }
    
    def _generate_recommendations(self, clip_results: Dict[str, Any],
                                black_results: Dict[str, Any],
                                shadow_results: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on detected objects"""
        
        recommendations = []
        
        if clip_results['clip_flag']:
            recommendations.extend([
                "🔴 CRITICAL: Remove clips, tools, or holders from document area",
                "📎 Use document scanner without physical restraints",
                "📱 Consider using scanner apps that handle document edges automatically"
            ])
        
        if black_results['black_object_flag']:
            recommendations.extend([
                "🔴 CRITICAL: Remove hands, fingers, or objects from document area",
                "👋 Keep hands away from document during capture",
                "📸 Use timer mode or remote shutter to avoid hand interference"
            ])
        
        if shadow_results['shadow_flag']:
            recommendations.extend([
                "🌞 Improve lighting to eliminate shadows on document",
                "💡 Use diffused lighting from multiple angles",
                "📱 Position camera directly above document to minimize shadows"
            ])
        
        if shadow_results['reflection_flag']:
            recommendations.extend([
                "✨ Reduce reflections from document surface",
                "📐 Adjust camera angle to avoid direct light reflection",
                "🔆 Use polarizing filter if available"
            ])
        
        return recommendations
    
    def _assess_quality_impact(self, clip_results: Dict[str, Any],
                             black_results: Dict[str, Any],
                             shadow_results: Dict[str, Any]) -> str:
        """Assess overall quality impact of foreign objects"""
        
        total_coverage = (clip_results['clip_area_percentage'] + 
                         black_results['black_area_percentage'] +
                         shadow_results['shadow_percentage'])
        
        if total_coverage > 10.0:
            return 'SEVERE - Document unusable'
        elif total_coverage > 5.0:
            return 'HIGH - Significant quality degradation'
        elif total_coverage > 2.0:
            return 'MODERATE - Some quality loss'
        else:
            return 'LOW - Minor impact on quality'


def analyze_document_with_foreign_objects(image_path: str, 
                                        output_file: str = None) -> Dict[str, Any]:
    """
    Analyze document for foreign objects with enhanced detection
    
    Args:
        image_path: Path to image file
        output_file: Optional JSON output file
        
    Returns:
        Dictionary with foreign object analysis results
    """
    
    print(f"🔍 ANALYZING FOREIGN OBJECTS: {Path(image_path).name}")
    print("="*60)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Create simple document mask (this would normally come from document detection)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, doc_mask = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Initialize detector
    detector = EnhancedForeignObjectsDetector()
    
    # Analyze foreign objects
    results = detector.analyze_foreign_objects(image, doc_mask)
    
    # Print results
    print_foreign_objects_analysis(results)
    
    # Save results if requested
    if output_file:
        import json
        with open(output_file, 'w') as f:
            # Convert numpy arrays to lists for JSON serialization
            json_results = convert_results_for_json(results)
            json.dump(json_results, f, indent=2)
        print(f"\n📁 Results saved to: {output_file}")
    
    return results


def print_foreign_objects_analysis(results: Dict[str, Any]) -> None:
    """Print detailed foreign objects analysis"""
    
    print(f"\n🚨 FOREIGN OBJECTS DETECTED: {'YES' if results['foreign_object_flag'] else 'NO'}")
    print(f"📊 Total Coverage: {results['foreign_object_area_pct']:.2f}% of image")
    print(f"🔢 Objects Found: {results['summary']['total_objects_detected']}")
    print(f"💥 Quality Impact: {results['summary']['image_quality_impact']}")
    
    # Failure reasons
    if results['failure_reasons']:
        print(f"\n🔴 FAILURE REASONS:")
        for i, reason in enumerate(results['failure_reasons'], 1):
            print(f"   {i}. {reason}")
    
    # Detailed breakdown
    clip_results = results['detailed_results']['clips_and_tools']
    black_results = results['detailed_results']['black_objects']
    shadow_results = results['detailed_results']['shadows_reflections']
    
    print(f"\n📎 CLIPS/TOOLS DETECTED:")
    print(f"   Count: {clip_results['clip_count']}")
    print(f"   Coverage: {clip_results['clip_area_percentage']:.2f}%")
    print(f"   Flag: {'FAIL' if clip_results['clip_flag'] else 'PASS'}")
    
    print(f"\n⚫ BLACK OBJECTS DETECTED:")
    print(f"   Count: {black_results['black_object_count']}")
    print(f"   Coverage: {black_results['black_area_percentage']:.2f}%")
    print(f"   Flag: {'FAIL' if black_results['black_object_flag'] else 'PASS'}")
    
    print(f"\n🌑 SHADOWS/REFLECTIONS:")
    print(f"   Shadow Coverage: {shadow_results['shadow_percentage']:.2f}%")
    print(f"   Reflection Coverage: {shadow_results['reflection_percentage']:.2f}%")
    print(f"   Shadow Flag: {'FAIL' if shadow_results['shadow_flag'] else 'PASS'}")
    print(f"   Reflection Flag: {'FAIL' if shadow_results['reflection_flag'] else 'PASS'}")
    
    # Recommendations
    if results['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    print("="*60)


def convert_results_for_json(results: Dict[str, Any]) -> Dict[str, Any]:
    """Convert numpy arrays to lists for JSON serialization"""
    
    import json
    import numpy as np
    
    def convert_item(item):
        if isinstance(item, np.ndarray):
            return item.tolist()
        elif isinstance(item, np.integer):
            return int(item)
        elif isinstance(item, np.floating):
            return float(item)
        elif isinstance(item, np.bool_):
            return bool(item)
        elif isinstance(item, bool):
            return item
        elif isinstance(item, dict):
            return {k: convert_item(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [convert_item(i) for i in item]
        elif isinstance(item, tuple):
            return [convert_item(i) for i in item]
        else:
            return item
    
    return convert_item(results)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "foreign_objects_analysis.json"
        
        try:
            results = analyze_document_with_foreign_objects(image_path, output_file)
            
            if results['foreign_object_flag']:
                print(f"\n🔴 DOCUMENT FAILED: Foreign objects detected")
            else:
                print(f"\n🟢 DOCUMENT PASSED: No significant foreign objects")
                
        except Exception as e:
            print(f"❌ Error analyzing image: {e}")
    else:
        print("Usage: python enhanced_foreign_objects.py <image_path> [output_file]")
        print("Example: python enhanced_foreign_objects.py document.jpg analysis.json")

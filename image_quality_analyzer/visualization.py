"""
Graph and visualization generation for quality analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import cv2
from typing import Dict, Any, Optional, Tuple
import os


class GraphGenerator:
    """Generates graphs and visualizations for image quality analysis"""
    
    def __init__(self, style: str = 'default'):
        """
        Initialize graph generator
        
        Args:
            style: Matplotlib style to use
        """
        try:
            plt.style.use(style)
        except OSError:
            # Fallback to default style if requested style is not available
            plt.style.use('default')
        
        self.figure_size = (12, 8)
        self.dpi = 100
    
    def generate_all_graphs(self, image_path: str, analysis_result: Dict[str, Any], 
                           output_dir: str) -> Dict[str, str]:
        """
        Generate all graphs for an analysis result
        
        Returns dictionary mapping graph names to output file paths
        """
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Load image for visualization
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Create document mask
        from .metrics.base import DocumentMaskGenerator
        mask_generator = DocumentMaskGenerator()
        doc_mask = mask_generator.create_document_mask(image)
        
        graph_files = {}
        metrics = analysis_result.get('metrics', {})
        image_id = analysis_result.get('image_id', 'image')
        
        # Generate each graph type from the spec
        graph_files.update(self._generate_histogram_graphs(
            image, doc_mask, metrics, output_dir, image_id))
        
        graph_files.update(self._generate_heatmap_graphs(
            image, doc_mask, metrics, output_dir, image_id))
        
        graph_files.update(self._generate_bar_charts(
            metrics, output_dir, image_id))
        
        graph_files.update(self._generate_dial_charts(
            metrics, output_dir, image_id))
        
        graph_files.update(self._generate_overlay_visualizations(
            image, doc_mask, metrics, output_dir, image_id))
        
        return graph_files
    
    def _generate_histogram_graphs(self, image: np.ndarray, doc_mask: np.ndarray,
                                  metrics: Dict[str, Any], output_dir: str, 
                                  image_id: str) -> Dict[str, str]:
        """Generate luminance histograms"""
        
        files = {}
        
        # Luminance histogram
        from .metrics.base import DocumentMaskGenerator
        mask_generator = DocumentMaskGenerator()
        luminance = mask_generator.convert_to_luminance(image)
        valid_pixels = luminance[doc_mask > 0]
        
        if len(valid_pixels) > 0:
            # Regular histogram
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figure_size)
            
            # Histogram with clipping zones
            ax1.hist(valid_pixels, bins=50, alpha=0.7, color='blue', density=True)
            ax1.axvline(0.05, color='red', linestyle='--', label='Shadow clip (5%)')
            ax1.axvline(0.95, color='red', linestyle='--', label='Highlight clip (95%)')
            ax1.set_xlabel('Luminance (0-1)')
            ax1.set_ylabel('Density')
            ax1.set_title(f'Luminance Histogram - {image_id}')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Cumulative histogram
            sorted_pixels = np.sort(valid_pixels)
            y_vals = np.arange(1, len(sorted_pixels) + 1) / len(sorted_pixels)
            ax2.plot(sorted_pixels, y_vals, color='blue', linewidth=2)
            ax2.axvline(np.percentile(valid_pixels, 5), color='red', linestyle='--', label='P5')
            ax2.axvline(np.percentile(valid_pixels, 95), color='red', linestyle='--', label='P95')
            ax2.set_xlabel('Luminance (0-1)')
            ax2.set_ylabel('Cumulative Probability')
            ax2.set_title(f'Cumulative Histogram - {image_id}')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            hist_file = os.path.join(output_dir, f'{image_id}_histograms.png')
            plt.savefig(hist_file, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            files['histograms'] = hist_file
        
        return files
    
    def _generate_heatmap_graphs(self, image: np.ndarray, doc_mask: np.ndarray,
                                metrics: Dict[str, Any], output_dir: str,
                                image_id: str) -> Dict[str, str]:
        """Generate illumination and sharpness heatmaps"""
        
        files = {}
        
        # Illumination heatmap
        if 'exposure' in metrics:
            from .metrics.exposure import ExposureMetrics
            from .metrics.base import DocumentMaskGenerator
            
            mask_generator = DocumentMaskGenerator()
            exposure_metrics = ExposureMetrics()
            luminance = mask_generator.convert_to_luminance(image)
            
            illum_map = exposure_metrics.create_illumination_map(luminance, doc_mask)
            
            if illum_map.size > 0:
                fig, ax = plt.subplots(figsize=(8, 6))
                im = ax.imshow(illum_map, cmap='hot', interpolation='bilinear')
                ax.set_title(f'Illumination Uniformity - {image_id}')
                ax.set_xlabel('Tile X')
                ax.set_ylabel('Tile Y')
                
                # Add colorbar
                cbar = plt.colorbar(im, ax=ax)
                cbar.set_label('Mean Luminance')
                
                # Add uniformity ratio text
                uniformity = metrics.get('exposure', {}).get('illumination_uniformity', {})
                ratio = uniformity.get('uniformity_ratio', 0.0)
                ax.text(0.02, 0.98, f'Uniformity Ratio: {ratio:.3f}', 
                       transform=ax.transAxes, bbox=dict(boxstyle="round", 
                       facecolor='white', alpha=0.8), verticalalignment='top')
                
                plt.tight_layout()
                illum_file = os.path.join(output_dir, f'{image_id}_illumination.png')
                plt.savefig(illum_file, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                
                files['illumination_heatmap'] = illum_file
        
        # Sharpness heatmap (simplified version)
        if 'sharpness' in metrics:
            # Create a simple grid visualization for sharpness
            h, w = image.shape[:2]
            tile_size = 64
            sharpness_grid = np.zeros((h // tile_size + 1, w // tile_size + 1))
            
            # This would normally use the tile statistics from sharpness metrics
            # For now, create a placeholder visualization
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            for i in range(sharpness_grid.shape[0]):
                for j in range(sharpness_grid.shape[1]):
                    y1, x1 = i * tile_size, j * tile_size
                    y2, x2 = min(y1 + tile_size, h), min(x1 + tile_size, w)
                    
                    if np.sum(doc_mask[y1:y2, x1:x2]) > 0:
                        tile = gray[y1:y2, x1:x2]
                        laplacian_var = np.var(cv2.Laplacian(tile, cv2.CV_64F))
                        sharpness_grid[i, j] = laplacian_var
            
            if np.max(sharpness_grid) > 0:
                fig, ax = plt.subplots(figsize=(8, 6))
                im = ax.imshow(sharpness_grid, cmap='viridis', interpolation='bilinear')
                ax.set_title(f'Sharpness Map - {image_id}')
                ax.set_xlabel('Tile X')
                ax.set_ylabel('Tile Y')
                
                cbar = plt.colorbar(im, ax=ax)
                cbar.set_label('Laplacian Variance')
                
                # Add overall sharpness text
                overall_sharpness = metrics.get('sharpness', {}).get('laplacian_var', 0.0)
                ax.text(0.02, 0.98, f'Overall Sharpness: {overall_sharpness:.1f}',
                       transform=ax.transAxes, bbox=dict(boxstyle="round",
                       facecolor='white', alpha=0.8), verticalalignment='top')
                
                plt.tight_layout()
                sharp_file = os.path.join(output_dir, f'{image_id}_sharpness.png')
                plt.savefig(sharp_file, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                
                files['sharpness_heatmap'] = sharp_file
        
        return files
    
    def _generate_bar_charts(self, metrics: Dict[str, Any], output_dir: str,
                            image_id: str) -> Dict[str, str]:
        """Generate margin bar chart and other bar visualizations"""
        
        files = {}
        
        # Margin bar chart
        if 'border_background' in metrics:
            border_metrics = metrics['border_background']
            
            margins = {
                'Left': border_metrics.get('left_margin_ratio', 0.0),
                'Right': border_metrics.get('right_margin_ratio', 0.0), 
                'Top': border_metrics.get('top_margin_ratio', 0.0),
                'Bottom': border_metrics.get('bottom_margin_ratio', 0.0)
            }
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            bars = ax.bar(margins.keys(), margins.values(), 
                         color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow'])
            
            # Add threshold lines (example thresholds)
            ax.axhline(y=0.10, color='orange', linestyle='--', label='Pass Threshold')
            ax.axhline(y=0.12, color='red', linestyle='--', label='Warn Threshold')
            
            # Color bars based on thresholds
            for bar, (_, value) in zip(bars, margins.items()):
                if value > 0.12:
                    bar.set_color('red')
                elif value > 0.10:
                    bar.set_color('orange')
                else:
                    bar.set_color('green')
            
            ax.set_ylabel('Margin Ratio')
            ax.set_title(f'Document Margins - {image_id}')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            margin_file = os.path.join(output_dir, f'{image_id}_margins.png')
            plt.savefig(margin_file, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            files['margin_bars'] = margin_file
        
        return files
    
    def _generate_dial_charts(self, metrics: Dict[str, Any], output_dir: str,
                             image_id: str) -> Dict[str, str]:
        """Generate skew dial and other circular visualizations"""
        
        files = {}
        
        # Skew dial
        if 'geometry' in metrics:
            skew_angle = metrics['geometry'].get('skew_angle_abs', 0.0)
            
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
            
            # Create dial background
            angles = np.linspace(0, 2*np.pi, 100)
            
            # Color zones: green (pass), yellow (warn), red (fail)
            pass_angle = np.radians(1.0 * 360 / 45)  # 1 degree in polar coords
            warn_angle = np.radians(3.0 * 360 / 45)  # 3 degrees 
            
            # Plot zones
            ax.fill_between(angles, 0, 1, where=(np.abs(angles) <= pass_angle), 
                           color='green', alpha=0.3, label='Pass')
            ax.fill_between(angles, 0, 1, where=((np.abs(angles) > pass_angle) & 
                           (np.abs(angles) <= warn_angle)), color='yellow', alpha=0.3, label='Warn')
            ax.fill_between(angles, 0, 1, where=(np.abs(angles) > warn_angle), 
                           color='red', alpha=0.3, label='Fail')
            
            # Plot skew angle
            skew_radians = np.radians(skew_angle * 360 / 45)
            ax.arrow(0, 0, skew_radians, 0.8, head_width=0.05, head_length=0.1, 
                    fc='black', ec='black', linewidth=2)
            
            ax.set_ylim(0, 1)
            ax.set_title(f'Skew Angle: {skew_angle:.2f}°\n{image_id}', pad=20)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
            
            plt.tight_layout()
            skew_file = os.path.join(output_dir, f'{image_id}_skew_dial.png')
            plt.savefig(skew_file, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            files['skew_dial'] = skew_file
        
        return files
    
    def _generate_overlay_visualizations(self, image: np.ndarray, doc_mask: np.ndarray,
                                       metrics: Dict[str, Any], output_dir: str,
                                       image_id: str) -> Dict[str, str]:
        """Generate document mask overlay and other overlay visualizations"""
        
        files = {}
        
        # Document mask overlay
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Original image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        ax1.imshow(image_rgb)
        ax1.set_title('Original Image')
        ax1.axis('off')
        
        # Overlay with document mask and bounding box
        overlay = image_rgb.copy()
        
        # Add semi-transparent mask
        mask_overlay = np.zeros_like(overlay)
        mask_overlay[doc_mask > 0] = [0, 255, 0]  # Green for document area
        overlay = cv2.addWeighted(overlay, 0.7, mask_overlay, 0.3, 0)
        
        # Add bounding box
        from .metrics.base import DocumentMaskGenerator
        mask_generator = DocumentMaskGenerator()
        x_min, y_min, x_max, y_max = mask_generator.get_document_bbox(doc_mask)
        
        # Draw bounding box
        cv2.rectangle(overlay, (x_min, y_min), (x_max, y_max), (255, 0, 0), 3)
        
        ax2.imshow(overlay)
        ax2.set_title('Document Detection Overlay')
        ax2.axis('off')
        
        plt.tight_layout()
        overlay_file = os.path.join(output_dir, f'{image_id}_overlay.png')
        plt.savefig(overlay_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        files['document_overlay'] = overlay_file
        
        return files
    
    def create_summary_dashboard(self, analysis_result: Dict[str, Any], 
                                output_path: str) -> None:
        """Create a summary dashboard with key metrics"""
        
        fig = plt.figure(figsize=(16, 10))
        
        # Overall score and stars
        global_info = analysis_result.get('global', {})
        score = global_info.get('score', 0.0)
        stars = global_info.get('stars', 0)
        
        # Title with score
        star_str = '★' * stars + '☆' * (4 - stars)
        fig.suptitle(f'{analysis_result.get("image_id", "Image")} - Quality Score: {score:.2f} ({star_str})',
                    fontsize=16, fontweight='bold')
        
        # Category status grid
        ax_status = plt.subplot(2, 3, 1)
        self._plot_category_status(analysis_result.get('category_status', {}), ax_status)
        
        # Key metrics summary
        ax_metrics = plt.subplot(2, 3, 2)
        self._plot_key_metrics(analysis_result.get('metrics', {}), ax_metrics)
        
        # Action items
        ax_actions = plt.subplot(2, 3, 3)
        self._plot_action_items(global_info.get('actions', []), ax_actions)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
    
    def _plot_category_status(self, category_status: Dict[str, str], ax) -> None:
        """Plot category status as colored grid"""
        
        categories = list(category_status.keys())
        statuses = [category_status[cat] for cat in categories]
        
        # Color mapping
        color_map = {'pass': 'green', 'warn': 'orange', 'fail': 'red'}
        colors = [color_map.get(status, 'gray') for status in statuses]
        
        y_pos = np.arange(len(categories))
        bars = ax.barh(y_pos, [1] * len(categories), color=colors)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels([cat.replace('_', ' ').title() for cat in categories])
        ax.set_xlim(0, 1)
        ax.set_title('Category Status')
        ax.set_xticks([])
        
        # Add status text
        for i, (status, bar) in enumerate(zip(statuses, bars)):
            ax.text(0.5, i, status.upper(), ha='center', va='center', 
                   fontweight='bold', color='white')
    
    def _plot_key_metrics(self, metrics: Dict[str, Any], ax) -> None:
        """Plot key metrics as text summary"""
        
        ax.axis('off')
        
        key_values = []
        
        # Extract key metrics
        if 'sharpness' in metrics:
            key_values.append(f"Sharpness: {metrics['sharpness'].get('laplacian_var', 0):.1f}")
        
        if 'contrast' in metrics:
            key_values.append(f"Contrast: {metrics['contrast'].get('global_contrast', 0):.2f}")
        
        if 'geometry' in metrics:
            key_values.append(f"Skew: {metrics['geometry'].get('skew_angle_abs', 0):.2f}°")
        
        if 'exposure' in metrics:
            uniformity = metrics['exposure'].get('illumination_uniformity', {}).get('uniformity_ratio', 0)
            key_values.append(f"Uniformity: {uniformity:.3f}")
        
        # Display as text
        ax.text(0.1, 0.9, 'Key Metrics:', fontsize=12, fontweight='bold', 
               transform=ax.transAxes)
        
        for i, value in enumerate(key_values[:6]):  # Limit to 6 metrics
            ax.text(0.1, 0.8 - i*0.12, value, fontsize=10, transform=ax.transAxes)
    
    def _plot_action_items(self, actions: list, ax) -> None:
        """Plot action items as text list"""
        
        ax.axis('off')
        
        ax.text(0.1, 0.9, 'Recommended Actions:', fontsize=12, fontweight='bold',
               transform=ax.transAxes)
        
        if not actions:
            ax.text(0.1, 0.7, 'No issues found!', fontsize=10, color='green',
                   transform=ax.transAxes)
        else:
            for i, action in enumerate(actions[:5]):  # Limit to 5 actions
                ax.text(0.1, 0.8 - i*0.12, action, fontsize=9, transform=ax.transAxes,
                       wrap=True)

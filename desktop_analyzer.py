#!/usr/bin/env python3
"""
Professional Desktop Image Quality Analyzer
A secure, offline desktop application for document image quality analysis
with customizable quality standards and modern professional interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import os
import sys
import threading
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from datetime import datetime
import copy

# Add the current directory to Python path to import our analyzer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from image_quality_analyzer import ImageQualityAnalyzer, load_default_config, load_profile
    from image_quality_analyzer.config import list_profiles
    from image_quality_analyzer.visualization import GraphGenerator
    
    # Fix matplotlib backend for GUI
    import matplotlib
    matplotlib.use('TkAgg')
    
except ImportError as e:
    print(f"Error importing ImageQualityAnalyzer: {e}")
    sys.exit(1)

class QualityStandardsEditor:
    def __init__(self, parent, current_config=None):
        self.parent = parent
        self.config = current_config or load_default_config()
        self.result = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Quality Standards Editor")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.center_window()
        
        # Create interface
        self.create_widgets()
        self.setup_layout()
        self.load_config_values()
        
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
    def create_widgets(self):
        """Create all widgets for the standards editor"""
        
        # Main container with padding
        self.main_frame = ttk.Frame(self.window, padding="15")
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.title_label = ttk.Label(
            self.header_frame, 
            text="📏 Custom Quality Standards", 
            font=("Segoe UI", 16, "bold")
        )
        self.subtitle_label = ttk.Label(
            self.header_frame, 
            text="Define your own quality thresholds for precise document analysis",
            font=("Segoe UI", 10)
        )
        
        # Standards notebook
        self.standards_notebook = ttk.Notebook(self.main_frame)
        
        # Create tabs for different metric categories
        self.create_resolution_tab()
        self.create_exposure_tab()
        self.create_sharpness_tab()
        self.create_geometry_tab()
        self.create_completeness_tab()
        self.create_scoring_tab()
        
        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.save_button = ttk.Button(
            self.button_frame, 
            text="💾 Save Standards", 
            command=self.save_standards,
            style="Accent.TButton"
        )
        self.reset_button = ttk.Button(
            self.button_frame, 
            text="🔄 Reset to Defaults", 
            command=self.reset_to_defaults
        )
        self.cancel_button = ttk.Button(
            self.button_frame, 
            text="❌ Cancel", 
            command=self.cancel
        )
        self.preview_button = ttk.Button(
            self.button_frame, 
            text="👁️ Preview JSON", 
            command=self.preview_config
        )
        
    def create_resolution_tab(self):
        """Create resolution standards tab"""
        frame = ttk.Frame(self.standards_notebook, padding="20")
        self.standards_notebook.add(frame, text="🖼️ Resolution")
        
        # Resolution settings
        resolution_frame = ttk.LabelFrame(frame, text="Resolution Requirements", padding="15")
        resolution_frame.pack(fill="x", pady=(0, 20))
        
        # Text DPI minimum
        ttk.Label(resolution_frame, text="Minimum DPI for Text Documents:").grid(row=0, column=0, sticky="w", pady=5)
        self.min_dpi_text = ttk.Spinbox(resolution_frame, from_=50, to=1200, width=15)
        self.min_dpi_text.grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(resolution_frame, text="DPI", foreground="gray").grid(row=0, column=2, sticky="w", padx=(5, 0))
        
        # Archival DPI minimum
        ttk.Label(resolution_frame, text="Minimum DPI for Archival Quality:").grid(row=1, column=0, sticky="w", pady=5)
        self.min_dpi_archival = ttk.Spinbox(resolution_frame, from_=50, to=1200, width=15)
        self.min_dpi_archival.grid(row=1, column=1, sticky="w", padx=(10, 0))
        ttk.Label(resolution_frame, text="DPI", foreground="gray").grid(row=1, column=2, sticky="w", padx=(5, 0))
        
        # Help text
        help_text = """📖 Resolution Guidelines:
• 150 DPI: Basic quality for digital viewing
• 300 DPI: Standard for professional documents
• 400+ DPI: Archival quality for long-term preservation
• 600+ DPI: High-quality scanning for detailed documents"""
        
        help_frame = ttk.LabelFrame(frame, text="Guidelines", padding="15")
        help_frame.pack(fill="both", expand=True)
        help_label = ttk.Label(help_frame, text=help_text, justify="left", foreground="#666")
        help_label.pack(anchor="w")
        
    def create_exposure_tab(self):
        """Create exposure standards tab"""
        frame = ttk.Frame(self.standards_notebook, padding="20")
        self.standards_notebook.add(frame, text="☀️ Exposure")
        
        # Shadow clipping
        shadow_frame = ttk.LabelFrame(frame, text="Shadow Clipping", padding="15")
        shadow_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(shadow_frame, text="Maximum Shadow Clipping %:").grid(row=0, column=0, sticky="w", pady=5)
        self.max_shadow_clip = ttk.Scale(shadow_frame, from_=0.0, to=5.0, orient="horizontal", length=200)
        self.max_shadow_clip.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.shadow_value_label = ttk.Label(shadow_frame, text="0.5%")
        self.shadow_value_label.grid(row=0, column=2, sticky="w", padx=(10, 0))
        
        # Highlight clipping
        highlight_frame = ttk.LabelFrame(frame, text="Highlight Clipping", padding="15")
        highlight_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(highlight_frame, text="Maximum Highlight Clipping %:").grid(row=0, column=0, sticky="w", pady=5)
        self.max_highlight_clip = ttk.Scale(highlight_frame, from_=0.0, to=5.0, orient="horizontal", length=200)
        self.max_highlight_clip.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.highlight_value_label = ttk.Label(highlight_frame, text="0.5%")
        self.highlight_value_label.grid(row=0, column=2, sticky="w", padx=(10, 0))
        
        # Illumination uniformity
        illum_frame = ttk.LabelFrame(frame, text="Illumination Uniformity", padding="15")
        illum_frame.pack(fill="x")
        
        ttk.Label(illum_frame, text="Warning Threshold:").grid(row=0, column=0, sticky="w", pady=5)
        self.illum_warn = ttk.Scale(illum_frame, from_=0.05, to=0.5, orient="horizontal", length=150)
        self.illum_warn.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.illum_warn_label = ttk.Label(illum_frame, text="0.15")
        self.illum_warn_label.grid(row=0, column=2, sticky="w", padx=(10, 0))
        
        ttk.Label(illum_frame, text="Fail Threshold:").grid(row=1, column=0, sticky="w", pady=5)
        self.illum_fail = ttk.Scale(illum_frame, from_=0.1, to=0.8, orient="horizontal", length=150)
        self.illum_fail.grid(row=1, column=1, sticky="w", padx=(10, 0))
        self.illum_fail_label = ttk.Label(illum_frame, text="0.25")
        self.illum_fail_label.grid(row=1, column=2, sticky="w", padx=(10, 0))
        
        # Bind scale updates
        self.max_shadow_clip.bind("<Motion>", lambda e: self.update_scale_label(self.max_shadow_clip, self.shadow_value_label, "%"))
        self.max_highlight_clip.bind("<Motion>", lambda e: self.update_scale_label(self.max_highlight_clip, self.highlight_value_label, "%"))
        self.illum_warn.bind("<Motion>", lambda e: self.update_scale_label(self.illum_warn, self.illum_warn_label, ""))
        self.illum_fail.bind("<Motion>", lambda e: self.update_scale_label(self.illum_fail, self.illum_fail_label, ""))
        
    def create_sharpness_tab(self):
        """Create sharpness standards tab"""
        frame = ttk.Frame(self.standards_notebook, padding="20")
        self.standards_notebook.add(frame, text="🔍 Sharpness")
        
        # Sharpness settings
        sharp_frame = ttk.LabelFrame(frame, text="Laplacian Variance Thresholds", padding="15")
        sharp_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(sharp_frame, text="Minimum for Pass:").grid(row=0, column=0, sticky="w", pady=5)
        self.min_laplacian = ttk.Spinbox(sharp_frame, from_=50, to=500, width=15)
        self.min_laplacian.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(sharp_frame, text="Warning Threshold:").grid(row=1, column=0, sticky="w", pady=5)
        self.warn_laplacian = ttk.Spinbox(sharp_frame, from_=30, to=400, width=15)
        self.warn_laplacian.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        # Help text
        help_text = """📖 Sharpness Guidelines:
• 100-150: Acceptable for most documents
• 150-200: Good quality
• 200+: Excellent sharpness
• Below 100: Likely blurry, may need refocus"""
        
        help_frame = ttk.LabelFrame(frame, text="Guidelines", padding="15")
        help_frame.pack(fill="both", expand=True)
        help_label = ttk.Label(help_frame, text=help_text, justify="left", foreground="#666")
        help_label.pack(anchor="w")
        
    def create_geometry_tab(self):
        """Create geometry standards tab"""
        frame = ttk.Frame(self.standards_notebook, padding="20")
        self.standards_notebook.add(frame, text="📐 Geometry")
        
        # Skew settings
        skew_frame = ttk.LabelFrame(frame, text="Skew Tolerance", padding="15")
        skew_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(skew_frame, text="Maximum Skew for Pass (degrees):").grid(row=0, column=0, sticky="w", pady=5)
        self.max_skew_pass = ttk.Scale(skew_frame, from_=0.1, to=10.0, orient="horizontal", length=200)
        self.max_skew_pass.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.skew_pass_label = ttk.Label(skew_frame, text="1.0°")
        self.skew_pass_label.grid(row=0, column=2, sticky="w", padx=(10, 0))
        
        ttk.Label(skew_frame, text="Maximum Skew for Warning (degrees):").grid(row=1, column=0, sticky="w", pady=5)
        self.max_skew_warn = ttk.Scale(skew_frame, from_=1.0, to=15.0, orient="horizontal", length=200)
        self.max_skew_warn.grid(row=1, column=1, sticky="w", padx=(10, 0))
        self.skew_warn_label = ttk.Label(skew_frame, text="3.0°")
        self.skew_warn_label.grid(row=1, column=2, sticky="w", padx=(10, 0))
        
        # Bind scale updates
        self.max_skew_pass.bind("<Motion>", lambda e: self.update_scale_label(self.max_skew_pass, self.skew_pass_label, "°"))
        self.max_skew_warn.bind("<Motion>", lambda e: self.update_scale_label(self.max_skew_warn, self.skew_warn_label, "°"))
        
    def create_completeness_tab(self):
        """Create completeness standards tab"""
        frame = ttk.Frame(self.standards_notebook, padding="20")
        self.standards_notebook.add(frame, text="📄 Completeness")
        
        # Margin settings
        margin_frame = ttk.LabelFrame(frame, text="Margin Requirements", padding="15")
        margin_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(margin_frame, text="Minimum Margin (pixels):").grid(row=0, column=0, sticky="w", pady=5)
        self.min_margin_px = ttk.Spinbox(margin_frame, from_=0, to=50, width=15)
        self.min_margin_px.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(margin_frame, text="Minimum Content Coverage:").grid(row=1, column=0, sticky="w", pady=5)
        self.min_coverage = ttk.Scale(margin_frame, from_=0.5, to=1.0, orient="horizontal", length=200)
        self.min_coverage.grid(row=1, column=1, sticky="w", padx=(10, 0))
        self.coverage_label = ttk.Label(margin_frame, text="90%")
        self.coverage_label.grid(row=1, column=2, sticky="w", padx=(10, 0))
        
        # Bind scale updates
        self.min_coverage.bind("<Motion>", lambda e: self.update_scale_label(self.min_coverage, self.coverage_label, "%", 100))
        
    def create_scoring_tab(self):
        """Create scoring standards tab"""
        frame = ttk.Frame(self.standards_notebook, padding="20")
        self.standards_notebook.add(frame, text="🎯 Scoring")
        
        # Scoring thresholds
        score_frame = ttk.LabelFrame(frame, text="Quality Score Thresholds", padding="15")
        score_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(score_frame, text="Pass Score Threshold:").grid(row=0, column=0, sticky="w", pady=5)
        self.pass_threshold = ttk.Scale(score_frame, from_=0.5, to=1.0, orient="horizontal", length=200)
        self.pass_threshold.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.pass_threshold_label = ttk.Label(score_frame, text="80%")
        self.pass_threshold_label.grid(row=0, column=2, sticky="w", padx=(10, 0))
        
        ttk.Label(score_frame, text="Warning Score Threshold:").grid(row=1, column=0, sticky="w", pady=5)
        self.warn_threshold = ttk.Scale(score_frame, from_=0.3, to=0.9, orient="horizontal", length=200)
        self.warn_threshold.grid(row=1, column=1, sticky="w", padx=(10, 0))
        self.warn_threshold_label = ttk.Label(score_frame, text="65%")
        self.warn_threshold_label.grid(row=1, column=2, sticky="w", padx=(10, 0))
        
        # Bind scale updates
        self.pass_threshold.bind("<Motion>", lambda e: self.update_scale_label(self.pass_threshold, self.pass_threshold_label, "%", 100))
        self.warn_threshold.bind("<Motion>", lambda e: self.update_scale_label(self.warn_threshold, self.warn_threshold_label, "%", 100))
        
        # Preset buttons
        preset_frame = ttk.LabelFrame(frame, text="Quality Presets", padding="15")
        preset_frame.pack(fill="x")
        
        ttk.Button(preset_frame, text="🏢 Enterprise", command=lambda: self.apply_preset("enterprise")).pack(side="left", padx=(0, 10))
        ttk.Button(preset_frame, text="📚 Archival", command=lambda: self.apply_preset("archival")).pack(side="left", padx=(0, 10))
        ttk.Button(preset_frame, text="📄 Standard", command=lambda: self.apply_preset("standard")).pack(side="left", padx=(0, 10))
        ttk.Button(preset_frame, text="🔄 Lenient", command=lambda: self.apply_preset("lenient")).pack(side="left")
        
    def update_scale_label(self, scale, label, suffix, multiplier=1):
        """Update scale label with current value"""
        value = scale.get()
        if multiplier != 1:
            display_value = value * multiplier
            label.config(text=f"{display_value:.0f}{suffix}")
        else:
            label.config(text=f"{value:.2f}{suffix}")
            
    def apply_preset(self, preset_type):
        """Apply preset quality standards"""
        presets = {
            "enterprise": {
                "pass_threshold": 0.85,
                "warn_threshold": 0.70,
                "min_dpi_text": 300,
                "min_dpi_archival": 600,
                "max_shadow_clip": 0.3,
                "max_highlight_clip": 0.3,
                "min_laplacian": 180,
                "warn_laplacian": 150,
                "max_skew_pass": 0.5,
                "max_skew_warn": 1.5
            },
            "archival": {
                "pass_threshold": 0.90,
                "warn_threshold": 0.80,
                "min_dpi_text": 400,
                "min_dpi_archival": 800,
                "max_shadow_clip": 0.2,
                "max_highlight_clip": 0.2,
                "min_laplacian": 200,
                "warn_laplacian": 170,
                "max_skew_pass": 0.3,
                "max_skew_warn": 1.0
            },
            "standard": {
                "pass_threshold": 0.75,
                "warn_threshold": 0.60,
                "min_dpi_text": 200,
                "min_dpi_archival": 400,
                "max_shadow_clip": 0.5,
                "max_highlight_clip": 0.5,
                "min_laplacian": 150,
                "warn_laplacian": 120,
                "max_skew_pass": 1.0,
                "max_skew_warn": 3.0
            },
            "lenient": {
                "pass_threshold": 0.65,
                "warn_threshold": 0.45,
                "min_dpi_text": 150,
                "min_dpi_archival": 300,
                "max_shadow_clip": 1.0,
                "max_highlight_clip": 1.0,
                "min_laplacian": 100,
                "warn_laplacian": 80,
                "max_skew_pass": 2.0,
                "max_skew_warn": 5.0
            }
        }
        
        if preset_type in presets:
            preset = presets[preset_type]
            
            # Apply values
            self.pass_threshold.set(preset["pass_threshold"])
            self.warn_threshold.set(preset["warn_threshold"])
            self.min_dpi_text.delete(0, tk.END)
            self.min_dpi_text.insert(0, str(preset["min_dpi_text"]))
            self.min_dpi_archival.delete(0, tk.END)
            self.min_dpi_archival.insert(0, str(preset["min_dpi_archival"]))
            self.max_shadow_clip.set(preset["max_shadow_clip"])
            self.max_highlight_clip.set(preset["max_highlight_clip"])
            self.min_laplacian.delete(0, tk.END)
            self.min_laplacian.insert(0, str(preset["min_laplacian"]))
            self.warn_laplacian.delete(0, tk.END)
            self.warn_laplacian.insert(0, str(preset["warn_laplacian"]))
            self.max_skew_pass.set(preset["max_skew_pass"])
            self.max_skew_warn.set(preset["max_skew_warn"])
            
            # Update labels
            self.update_all_labels()
            
            messagebox.showinfo("Preset Applied", f"Applied {preset_type.title()} quality standards.")
            
    def update_all_labels(self):
        """Update all scale labels"""
        self.update_scale_label(self.max_shadow_clip, self.shadow_value_label, "%")
        self.update_scale_label(self.max_highlight_clip, self.highlight_value_label, "%")
        self.update_scale_label(self.illum_warn, self.illum_warn_label, "")
        self.update_scale_label(self.illum_fail, self.illum_fail_label, "")
        self.update_scale_label(self.max_skew_pass, self.skew_pass_label, "°")
        self.update_scale_label(self.max_skew_warn, self.skew_warn_label, "°")
        self.update_scale_label(self.min_coverage, self.coverage_label, "%", 100)
        self.update_scale_label(self.pass_threshold, self.pass_threshold_label, "%", 100)
        self.update_scale_label(self.warn_threshold, self.warn_threshold_label, "%", 100)
        
    def setup_layout(self):
        """Setup the layout of all widgets"""
        self.main_frame.pack(fill="both", expand=True)
        
        # Header
        self.header_frame.pack(fill="x", pady=(0, 20))
        self.title_label.pack(anchor="w")
        self.subtitle_label.pack(anchor="w")
        
        # Standards notebook
        self.standards_notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # Buttons
        self.button_frame.pack(fill="x")
        self.save_button.pack(side="right", padx=(10, 0))
        self.cancel_button.pack(side="right", padx=(10, 0))
        self.reset_button.pack(side="right", padx=(10, 0))
        self.preview_button.pack(side="left")
        
    def load_config_values(self):
        """Load current config values into the interface"""
        try:
            # Resolution
            self.min_dpi_text.delete(0, tk.END)
            self.min_dpi_text.insert(0, str(self.config.get('resolution', {}).get('min_dpi_text', 300)))
            self.min_dpi_archival.delete(0, tk.END)
            self.min_dpi_archival.insert(0, str(self.config.get('resolution', {}).get('min_dpi_archival', 400)))
            
            # Exposure
            self.max_shadow_clip.set(self.config.get('exposure', {}).get('max_shadow_clip_pct', 0.5))
            self.max_highlight_clip.set(self.config.get('exposure', {}).get('max_highlight_clip_pct', 0.5))
            self.illum_warn.set(self.config.get('exposure', {}).get('illumination_uniformity_warn', 0.15))
            self.illum_fail.set(self.config.get('exposure', {}).get('illumination_uniformity_fail', 0.25))
            
            # Sharpness
            self.min_laplacian.delete(0, tk.END)
            self.min_laplacian.insert(0, str(self.config.get('sharpness', {}).get('min_laplacian_variance', 150.0)))
            self.warn_laplacian.delete(0, tk.END)
            self.warn_laplacian.insert(0, str(self.config.get('sharpness', {}).get('warn_laplacian_variance', 120.0)))
            
            # Geometry
            self.max_skew_pass.set(self.config.get('geometry', {}).get('max_skew_deg_pass', 1.0))
            self.max_skew_warn.set(self.config.get('geometry', {}).get('max_skew_deg_warn', 3.0))
            
            # Completeness
            self.min_margin_px.delete(0, tk.END)
            self.min_margin_px.insert(0, str(self.config.get('completeness', {}).get('min_margin_px', 8)))
            self.min_coverage.set(self.config.get('completeness', {}).get('min_content_bbox_coverage', 0.9))
            
            # Scoring
            self.pass_threshold.set(self.config.get('scoring', {}).get('pass_score_threshold', 0.8))
            self.warn_threshold.set(self.config.get('scoring', {}).get('warn_score_threshold', 0.65))
            
            # Update all labels
            self.update_all_labels()
            
        except Exception as e:
            print(f"Error loading config values: {e}")
            
    def preview_config(self):
        """Preview the current configuration as JSON"""
        config = self.build_config()
        
        preview_window = tk.Toplevel(self.window)
        preview_window.title("Configuration Preview")
        preview_window.geometry("600x500")
        preview_window.transient(self.window)
        
        # JSON display
        text_widget = scrolledtext.ScrolledText(preview_window, font=("Consolas", 10))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        try:
            formatted_json = json.dumps(config, indent=2, sort_keys=True)
            text_widget.insert(1.0, formatted_json)
        except Exception as e:
            text_widget.insert(1.0, f"Error formatting config: {e}")
            
        # Close button
        close_button = ttk.Button(preview_window, text="Close", command=preview_window.destroy)
        close_button.pack(pady=10)
        
    def build_config(self):
        """Build configuration dictionary from current values"""
        try:
            config = copy.deepcopy(self.config)
            
            # Update with current values
            config['resolution'] = {
                'min_dpi_text': int(self.min_dpi_text.get()),
                'min_dpi_archival': int(self.min_dpi_archival.get())
            }
            
            config['exposure'] = config.get('exposure', {})
            config['exposure'].update({
                'max_shadow_clip_pct': self.max_shadow_clip.get(),
                'max_highlight_clip_pct': self.max_highlight_clip.get(),
                'illumination_uniformity_warn': self.illum_warn.get(),
                'illumination_uniformity_fail': self.illum_fail.get()
            })
            
            config['sharpness'] = config.get('sharpness', {})
            config['sharpness'].update({
                'min_laplacian_variance': float(self.min_laplacian.get()),
                'warn_laplacian_variance': float(self.warn_laplacian.get())
            })
            
            config['geometry'] = config.get('geometry', {})
            config['geometry'].update({
                'max_skew_deg_pass': self.max_skew_pass.get(),
                'max_skew_deg_warn': self.max_skew_warn.get()
            })
            
            config['completeness'] = config.get('completeness', {})
            config['completeness'].update({
                'min_margin_px': int(self.min_margin_px.get()),
                'min_content_bbox_coverage': self.min_coverage.get()
            })
            
            config['scoring'] = config.get('scoring', {})
            config['scoring'].update({
                'pass_score_threshold': self.pass_threshold.get(),
                'warn_score_threshold': self.warn_threshold.get()
            })
            
            return config
            
        except Exception as e:
            messagebox.showerror("Error", f"Error building configuration: {e}")
            return self.config
            
    def save_standards(self):
        """Save the current standards"""
        try:
            self.result = self.build_config()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving standards: {e}")
            
    def reset_to_defaults(self):
        """Reset all values to defaults"""
        if messagebox.askyesno("Reset to Defaults", "This will reset all values to their defaults. Continue?"):
            self.config = load_default_config()
            self.load_config_values()
            
    def cancel(self):
        """Cancel without saving"""
        self.result = None
        self.window.destroy()


class ProfessionalDesktopImageQualityAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Image Quality Analyzer")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Configure modern styling
        self.setup_modern_styling()
        
        # Initialize analyzer
        self.analyzer = ImageQualityAnalyzer()
        self.graph_generator = GraphGenerator()
        self.current_image_path = None
        self.current_results = None
        self.current_config = load_default_config()
        
        # Create main interface
        self.create_widgets()
        self.setup_layout()
        
        # Load available profiles
        self.load_profiles()
        
    def setup_modern_styling(self):
        """Configure modern professional styling"""
        style = ttk.Style()
        
        # Use modern theme
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        
        # Custom styles
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 11), foreground='#7f8c8d')
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#34495e')
        style.configure('Metric.TLabel', font=('Segoe UI', 10), foreground='#2c3e50')
        
        # Accent button (primary action)
        style.configure('Accent.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       foreground='white',
                       focuscolor='none')
        style.map('Accent.TButton', 
                 background=[('active', '#3498db'), ('!active', '#2980b9')],
                 foreground=[('active', 'white'), ('!active', 'white')])
        
        # Success button
        style.configure('Success.TButton',
                       font=('Segoe UI', 10),
                       foreground='white',
                       focuscolor='none')
        style.map('Success.TButton',
                 background=[('active', '#27ae60'), ('!active', '#2ecc71')],
                 foreground=[('active', 'white'), ('!active', 'white')])
        
        # Warning button
        style.configure('Warning.TButton',
                       font=('Segoe UI', 10),
                       foreground='white',
                       focuscolor='none')
        style.map('Warning.TButton',
                 background=[('active', '#f39c12'), ('!active', '#e67e22')],
                 foreground=[('active', 'white'), ('!active', 'white')])
        
        # Configure notebook tabs
        style.configure('TNotebook.Tab', padding=[15, 8])
        
        # Configure frames
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        
    def create_widgets(self):
        """Create all GUI widgets with modern professional design"""
        
        # Main container with modern padding
        self.main_frame = ttk.Frame(self.root, padding="20")
        
        # === HEADER SECTION ===
        self.header_frame = ttk.Frame(self.main_frame)
        
        # Logo and title area
        self.title_container = ttk.Frame(self.header_frame)
        self.title_label = ttk.Label(
            self.title_container,
            text="🏢 Professional Image Quality Analyzer",
            style='Title.TLabel'
        )
        self.subtitle_label = ttk.Label(
            self.title_container,
            text="Enterprise-grade document analysis • Complete offline security • Customizable standards",
            style='Subtitle.TLabel'
        )
        
        # Status indicator
        self.status_frame = ttk.Frame(self.header_frame)
        self.security_label = ttk.Label(
            self.status_frame,
            text="🔒 SECURE MODE",
            font=('Segoe UI', 9, 'bold'),
            foreground='#27ae60'
        )
        self.version_label = ttk.Label(
            self.status_frame,
            text="v2.0 Professional",
            font=('Segoe UI', 9),
            foreground='#7f8c8d'
        )
        
        # === CONTROL PANEL ===
        self.control_panel = ttk.LabelFrame(self.main_frame, text="🎛️ Analysis Control Panel", padding="20")
        
        # File selection with drag-drop area
        self.file_section = ttk.Frame(self.control_panel)
        self.file_label = ttk.Label(self.file_section, text="📁 Document Image:", style='Header.TLabel')
        
        self.file_container = ttk.Frame(self.file_section)
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(
            self.file_container, 
            textvariable=self.file_path_var, 
            font=('Segoe UI', 10),
            width=60
        )
        self.browse_button = ttk.Button(
            self.file_container, 
            text="📂 Browse Files", 
            command=self.browse_file,
            style='Accent.TButton'
        )
        
        # Configuration section
        self.config_section = ttk.Frame(self.control_panel)
        self.config_label = ttk.Label(self.config_section, text="⚙️ Quality Standards:", style='Header.TLabel')
        
        self.config_container = ttk.Frame(self.config_section)
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(
            self.config_container, 
            textvariable=self.profile_var, 
            width=25,
            font=('Segoe UI', 10),
            state="readonly"
        )
        
        self.custom_button = ttk.Button(
            self.config_container,
            text="🔧 Custom Standards",
            command=self.open_custom_standards,
            style='Warning.TButton'
        )
        
        self.save_profile_button = ttk.Button(
            self.config_container,
            text="💾 Save Profile",
            command=self.save_current_profile
        )
        
        # Options
        self.options_section = ttk.Frame(self.control_panel)
        self.options_label = ttk.Label(self.options_section, text="🎯 Analysis Options:", style='Header.TLabel')
        
        self.options_container = ttk.Frame(self.options_section)
        self.viz_var = tk.BooleanVar(value=False)  # Disabled by default due to threading issues
        self.viz_check = ttk.Checkbutton(
            self.options_container, 
            text="📊 Generate Visualizations (Beta)", 
            variable=self.viz_var
        )
        
        self.verbose_var = tk.BooleanVar(value=True)
        self.verbose_check = ttk.Checkbutton(
            self.options_container,
            text="📝 Detailed Analysis Report",
            variable=self.verbose_var
        )
        
        # Action buttons
        self.action_section = ttk.Frame(self.control_panel)
        self.analyze_button = ttk.Button(
            self.action_section,
            text="🚀 Analyze Quality",
            command=self.start_analysis,
            style="Accent.TButton"
        )
        self.export_button = ttk.Button(
            self.action_section,
            text="📋 Export Report",
            command=self.export_report,
            state="disabled"
        )
        self.batch_button = ttk.Button(
            self.action_section,
            text="📦 Batch Analysis",
            command=self.batch_analysis
        )
        
        # === PROGRESS SECTION ===
        self.progress_section = ttk.LabelFrame(self.main_frame, text="📊 Analysis Progress", padding="15")
        self.progress_container = ttk.Frame(self.progress_section)
        
        self.progress_var = tk.StringVar(value="Ready for analysis")
        self.progress_label = ttk.Label(
            self.progress_container, 
            textvariable=self.progress_var,
            font=('Segoe UI', 10)
        )
        self.progress_bar = ttk.Progressbar(
            self.progress_container, 
            mode='determinate',
            length=400
        )
        
        # === RESULTS SECTION ===
        self.results_section = ttk.LabelFrame(self.main_frame, text="📋 Analysis Results", padding="15")
        
        # Results notebook with modern tabs
        self.results_notebook = ttk.Notebook(self.results_section)
        
        # Tab 1: Executive Summary
        self.summary_frame = ttk.Frame(self.results_notebook, padding="20")
        self.results_notebook.add(self.summary_frame, text="📊 Executive Summary")
        
        # Tab 2: Quality Metrics
        self.metrics_frame = ttk.Frame(self.results_notebook, padding="20")
        self.results_notebook.add(self.metrics_frame, text="🔍 Quality Metrics")
        
        # Tab 3: Recommendations
        self.recommendations_frame = ttk.Frame(self.results_notebook, padding="20")
        self.results_notebook.add(self.recommendations_frame, text="💡 Recommendations")
        
        # Tab 4: Technical Data
        self.raw_frame = ttk.Frame(self.results_notebook, padding="20")
        self.results_notebook.add(self.raw_frame, text="🔧 Technical Data")
        
        # Create content for each tab
        self.create_summary_widgets()
        self.create_metrics_widgets()
        self.create_recommendations_widgets()
        self.create_technical_widgets()
        
    def create_summary_widgets(self):
        """Create executive summary widgets"""
        # Score display area
        self.score_display = ttk.Frame(self.summary_frame)
        
        # Main score card
        self.score_card = ttk.Frame(self.score_display, style='Card.TFrame')
        self.overall_score_label = ttk.Label(
            self.score_card,
            text="Overall Quality Score",
            font=('Segoe UI', 12, 'bold')
        )
        self.score_value_label = ttk.Label(
            self.score_card,
            text="--",
            font=('Segoe UI', 36, 'bold'),
            foreground='#3498db'
        )
        self.stars_label = ttk.Label(
            self.score_card,
            text="☆☆☆☆",
            font=('Segoe UI', 20)
        )
        
        # Status indicators
        self.status_indicators = ttk.Frame(self.score_display)
        
        self.pass_count_frame = ttk.Frame(self.status_indicators, style='Card.TFrame')
        self.pass_count_label = ttk.Label(self.pass_count_frame, text="PASSED", font=('Segoe UI', 10, 'bold'))
        self.pass_count_value = ttk.Label(self.pass_count_frame, text="--", font=('Segoe UI', 24, 'bold'), foreground='#27ae60')
        
        self.warn_count_frame = ttk.Frame(self.status_indicators, style='Card.TFrame')
        self.warn_count_label = ttk.Label(self.warn_count_frame, text="WARNINGS", font=('Segoe UI', 10, 'bold'))
        self.warn_count_value = ttk.Label(self.warn_count_frame, text="--", font=('Segoe UI', 24, 'bold'), foreground='#f39c12')
        
        self.fail_count_frame = ttk.Frame(self.status_indicators, style='Card.TFrame')
        self.fail_count_label = ttk.Label(self.fail_count_frame, text="FAILED", font=('Segoe UI', 10, 'bold'))
        self.fail_count_value = ttk.Label(self.fail_count_frame, text="--", font=('Segoe UI', 24, 'bold'), foreground='#e74c3c')
        
        # Quality assessment
        self.quality_assessment = ttk.LabelFrame(self.summary_frame, text="Quality Assessment", padding="15")
        self.assessment_text = scrolledtext.ScrolledText(
            self.quality_assessment,
            height=6,
            width=70,
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        
    def create_metrics_widgets(self):
        """Create quality metrics widgets"""
        # Metrics table with modern styling
        self.metrics_tree = ttk.Treeview(
            self.metrics_frame,
            columns=('metric', 'score', 'status', 'threshold', 'details'),
            show='headings',
            height=15
        )
        
        # Configure columns
        self.metrics_tree.heading('metric', text='Quality Metric')
        self.metrics_tree.heading('score', text='Score')
        self.metrics_tree.heading('status', text='Status')
        self.metrics_tree.heading('threshold', text='Threshold')
        self.metrics_tree.heading('details', text='Technical Details')
        
        self.metrics_tree.column('metric', width=200, anchor='w')
        self.metrics_tree.column('score', width=100, anchor='center')
        self.metrics_tree.column('status', width=100, anchor='center')
        self.metrics_tree.column('threshold', width=100, anchor='center')
        self.metrics_tree.column('details', width=300, anchor='w')
        
        # Scrollbar for metrics
        self.metrics_scrollbar = ttk.Scrollbar(self.metrics_frame, orient="vertical", command=self.metrics_tree.yview)
        self.metrics_tree.configure(yscrollcommand=self.metrics_scrollbar.set)
        
        # Metrics summary
        self.metrics_summary = ttk.LabelFrame(self.metrics_frame, text="Metrics Summary", padding="10")
        self.metrics_summary_text = tk.Text(
            self.metrics_summary,
            height=4,
            width=70,
            font=('Segoe UI', 9),
            state='disabled'
        )
        
    def create_recommendations_widgets(self):
        """Create recommendations widgets"""
        # Priority recommendations
        self.priority_frame = ttk.LabelFrame(self.recommendations_frame, text="🔥 Priority Actions", padding="15")
        self.priority_text = scrolledtext.ScrolledText(
            self.priority_frame,
            height=8,
            width=70,
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        
        # Improvement suggestions
        self.improvements_frame = ttk.LabelFrame(self.recommendations_frame, text="💡 Improvement Suggestions", padding="15")
        self.improvements_text = scrolledtext.ScrolledText(
            self.improvements_frame,
            height=8,
            width=70,
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        
        # Best practices
        self.best_practices_frame = ttk.LabelFrame(self.recommendations_frame, text="📚 Best Practices", padding="15")
        self.best_practices_text = scrolledtext.ScrolledText(
            self.best_practices_frame,
            height=6,
            width=70,
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        
    def create_technical_widgets(self):
        """Create technical data widgets"""
        # JSON display with syntax highlighting (simplified)
        self.raw_text = scrolledtext.ScrolledText(
            self.raw_frame,
            height=25,
            width=90,
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        
        # Technical details summary
        self.tech_summary_frame = ttk.Frame(self.raw_frame)
        self.copy_button = ttk.Button(
            self.tech_summary_frame,
            text="📋 Copy to Clipboard",
            command=self.copy_technical_data
        )
        self.save_json_button = ttk.Button(
            self.tech_summary_frame,
            text="💾 Save JSON",
            command=self.save_json_data
        )
        
    def open_custom_standards(self):
        """Open the custom quality standards editor"""
        editor = QualityStandardsEditor(self.root, self.current_config)
        self.root.wait_window(editor.window)
        
        if editor.result:
            self.current_config = editor.result
            messagebox.showinfo("Standards Updated", "Custom quality standards have been applied.")
            
    def save_current_profile(self):
        """Save current configuration as a new profile"""
        profile_name = tk.simpledialog.askstring(
            "Save Profile",
            "Enter a name for this quality profile:",
            parent=self.root
        )
        
        if profile_name:
            try:
                # Save to a custom profiles directory
                profiles_dir = os.path.join(os.path.dirname(__file__), "custom_profiles")
                os.makedirs(profiles_dir, exist_ok=True)
                
                profile_path = os.path.join(profiles_dir, f"{profile_name}.json")
                with open(profile_path, 'w') as f:
                    json.dump(self.current_config, f, indent=2)
                
                messagebox.showinfo("Profile Saved", f"Profile '{profile_name}' saved successfully!")
                self.load_profiles()  # Refresh the dropdown
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save profile: {e}")
                
    def batch_analysis(self):
        """Run batch analysis on multiple images"""
        folder_path = filedialog.askdirectory(title="Select folder containing images")
        if not folder_path:
            return
            
        # Find all image files
        image_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')
        image_files = []
        
        for file in os.listdir(folder_path):
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(folder_path, file))
        
        if not image_files:
            messagebox.showwarning("No Images", "No image files found in the selected folder.")
            return
            
        # Confirm batch analysis
        if not messagebox.askyesno("Batch Analysis", 
                                  f"Found {len(image_files)} images. Start batch analysis?\n"
                                  f"This may take several minutes."):
            return
            
        # Run batch analysis in background
        self.run_batch_analysis(image_files, folder_path)
        
    def run_batch_analysis(self, image_files, output_folder):
        """Run batch analysis in background thread"""
        def batch_worker():
            try:
                results = []
                total_files = len(image_files)
                
                for i, image_path in enumerate(image_files):
                    self.root.after(0, lambda p=i/total_files: self.progress_bar.configure(value=p*100))
                    self.root.after(0, lambda: self.progress_var.set(f"Processing {os.path.basename(image_path)}..."))
                    
                    try:
                        result = self.analyzer.analyze_image(image_path, self.current_config)
                        results.append({
                            'file': os.path.basename(image_path),
                            'path': image_path,
                            'results': result
                        })
                    except Exception as e:
                        results.append({
                            'file': os.path.basename(image_path),
                            'path': image_path,
                            'error': str(e)
                        })
                
                # Save batch results
                batch_report_path = os.path.join(output_folder, "batch_analysis_report.json")
                with open(batch_report_path, 'w') as f:
                    json.dump({
                        'timestamp': datetime.now().isoformat(),
                        'total_images': total_files,
                        'results': results
                    }, f, indent=2, default=str)
                
                self.root.after(0, lambda: self.batch_analysis_complete(batch_report_path, len(results)))
                
            except Exception as e:
                self.root.after(0, lambda: self.analysis_error(f"Batch analysis failed: {e}"))
        
        # Start batch analysis
        self.progress_bar.configure(mode='determinate', maximum=100, value=0)
        self.progress_var.set("Starting batch analysis...")
        
        thread = threading.Thread(target=batch_worker, daemon=True)
        thread.start()
        
    def batch_analysis_complete(self, report_path, total_analyzed):
        """Handle batch analysis completion"""
        self.progress_bar.configure(value=100)
        self.progress_var.set("Batch analysis complete!")
        
        messagebox.showinfo(
            "Batch Analysis Complete",
            f"Successfully analyzed {total_analyzed} images.\n"
            f"Report saved to: {report_path}"
        )
        
        # Reset progress
        self.progress_bar.configure(mode='indeterminate', value=0)
        self.progress_var.set("Ready for analysis")
        
    def copy_technical_data(self):
        """Copy technical data to clipboard"""
        if self.current_results:
            try:
                formatted_json = json.dumps(self.current_results, indent=2, sort_keys=True, default=str)
                self.root.clipboard_clear()
                self.root.clipboard_append(formatted_json)
                messagebox.showinfo("Copied", "Technical data copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy data: {e}")
        else:
            messagebox.showwarning("No Data", "No analysis results to copy.")
            
    def save_json_data(self):
        """Save technical data as JSON file"""
        if not self.current_results:
            messagebox.showwarning("No Data", "No analysis results to save.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Technical Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_results, f, indent=2, sort_keys=True, default=str)
                messagebox.showinfo("Saved", f"Technical data saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {e}")
        
    def setup_layout(self):
        """Setup the modern professional layout"""
        # Configure main window grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main frame
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Header section
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title container
        self.title_container.grid(row=0, column=0, sticky="w")
        self.title_label.pack(anchor="w")
        self.subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Status container
        self.status_frame.grid(row=0, column=1, sticky="e")
        self.security_label.pack(anchor="e")
        self.version_label.pack(anchor="e")
        
        # Control panel
        self.control_panel.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.control_panel.grid_columnconfigure(0, weight=1)
        
        # File section
        self.file_section.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.file_section.grid_columnconfigure(0, weight=1)
        self.file_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.file_container.grid(row=1, column=0, sticky="ew")
        self.file_container.grid_columnconfigure(0, weight=1)
        self.file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.browse_button.grid(row=0, column=1, sticky="e")
        
        # Config section
        self.config_section.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.config_section.grid_columnconfigure(0, weight=1)
        self.config_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.config_container.grid(row=1, column=0, sticky="ew")
        self.profile_combo.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.custom_button.grid(row=0, column=1, sticky="w", padx=(0, 10))
        self.save_profile_button.grid(row=0, column=2, sticky="w")
        
        # Options section
        self.options_section.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.options_section.grid_columnconfigure(0, weight=1)
        self.options_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.options_container.grid(row=1, column=0, sticky="ew")
        self.verbose_check.grid(row=0, column=0, sticky="w", padx=(0, 20))
        self.viz_check.grid(row=0, column=1, sticky="w")
        
        # Action section
        self.action_section.grid(row=3, column=0, sticky="ew")
        self.analyze_button.grid(row=0, column=0, padx=(0, 10), pady=10)
        self.export_button.grid(row=0, column=1, padx=(0, 10), pady=10)
        self.batch_button.grid(row=0, column=2, pady=10)
        
        # Progress section
        self.progress_section.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        self.progress_section.grid_columnconfigure(0, weight=1)
        self.progress_container.grid(row=0, column=0, sticky="ew")
        self.progress_container.grid_columnconfigure(1, weight=1)
        self.progress_label.grid(row=0, column=0, sticky="w", padx=(0, 15))
        self.progress_bar.grid(row=0, column=1, sticky="ew")
        
        # Results section
        self.results_section.grid(row=3, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.results_section.grid_columnconfigure(0, weight=1)
        self.results_section.grid_rowconfigure(0, weight=1)
        self.results_notebook.grid(row=0, column=0, sticky="nsew")
        
        # Layout for each tab
        self.layout_summary_tab()
        self.layout_metrics_tab()
        self.layout_recommendations_tab()
        self.layout_technical_tab()
        
    def layout_summary_tab(self):
        """Layout the summary tab"""
        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.summary_frame.grid_rowconfigure(1, weight=1)
        
        # Score display
        self.score_display.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.score_display.grid_columnconfigure(0, weight=1)
        self.score_display.grid_columnconfigure(1, weight=1)
        self.score_display.grid_columnconfigure(2, weight=1)
        self.score_display.grid_columnconfigure(3, weight=1)
        
        # Score card
        self.score_card.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.score_card.grid_columnconfigure(0, weight=1)
        self.overall_score_label.pack(pady=(10, 0))
        self.score_value_label.pack()
        self.stars_label.pack(pady=(0, 10))
        
        # Status indicators
        self.status_indicators.grid(row=0, column=1, columnspan=3, sticky="ew")
        
        self.pass_count_frame.grid(row=0, column=0, sticky="ew", padx=5)
        self.pass_count_frame.grid_columnconfigure(0, weight=1)
        self.pass_count_label.pack(pady=(10, 0))
        self.pass_count_value.pack(pady=(0, 10))
        
        self.warn_count_frame.grid(row=0, column=1, sticky="ew", padx=5)
        self.warn_count_frame.grid_columnconfigure(0, weight=1)
        self.warn_count_label.pack(pady=(10, 0))
        self.warn_count_value.pack(pady=(0, 10))
        
        self.fail_count_frame.grid(row=0, column=2, sticky="ew", padx=5)
        self.fail_count_frame.grid_columnconfigure(0, weight=1)
        self.fail_count_label.pack(pady=(10, 0))
        self.fail_count_value.pack(pady=(0, 10))
        
        # Quality assessment
        self.quality_assessment.grid(row=1, column=0, sticky="nsew")
        self.quality_assessment.grid_columnconfigure(0, weight=1)
        self.quality_assessment.grid_rowconfigure(0, weight=1)
        self.assessment_text.grid(row=0, column=0, sticky="nsew")
        
    def layout_metrics_tab(self):
        """Layout the metrics tab"""
        self.metrics_frame.grid_columnconfigure(0, weight=1)
        self.metrics_frame.grid_rowconfigure(0, weight=1)
        
        # Metrics tree
        self.metrics_tree.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        self.metrics_scrollbar.grid(row=0, column=1, sticky="ns", pady=(0, 15))
        
        # Metrics summary
        self.metrics_summary.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.metrics_summary.grid_columnconfigure(0, weight=1)
        self.metrics_summary_text.grid(row=0, column=0, sticky="ew")
        
    def layout_recommendations_tab(self):
        """Layout the recommendations tab"""
        self.recommendations_frame.grid_columnconfigure(0, weight=1)
        self.recommendations_frame.grid_rowconfigure(0, weight=1)
        self.recommendations_frame.grid_rowconfigure(1, weight=1)
        self.recommendations_frame.grid_rowconfigure(2, weight=1)
        
        # Priority frame
        self.priority_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.priority_frame.grid_columnconfigure(0, weight=1)
        self.priority_frame.grid_rowconfigure(0, weight=1)
        self.priority_text.grid(row=0, column=0, sticky="nsew")
        
        # Improvements frame
        self.improvements_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.improvements_frame.grid_columnconfigure(0, weight=1)
        self.improvements_frame.grid_rowconfigure(0, weight=1)
        self.improvements_text.grid(row=0, column=0, sticky="nsew")
        
        # Best practices frame
        self.best_practices_frame.grid(row=2, column=0, sticky="nsew")
        self.best_practices_frame.grid_columnconfigure(0, weight=1)
        self.best_practices_frame.grid_rowconfigure(0, weight=1)
        self.best_practices_text.grid(row=0, column=0, sticky="nsew")
        
    def layout_technical_tab(self):
        """Layout the technical tab"""
        self.raw_frame.grid_columnconfigure(0, weight=1)
        self.raw_frame.grid_rowconfigure(0, weight=1)
        
        # Technical summary
        self.tech_summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.copy_button.pack(side="left", padx=(0, 10))
        self.save_json_button.pack(side="left")
        
        # Raw text
        self.raw_text.grid(row=1, column=0, sticky="nsew")
        
    def load_profiles(self):
        """Load available configuration profiles"""
        try:
            profiles = list_profiles()
            profile_names = ['default'] + list(profiles.keys())
            
            # Add custom profiles if they exist
            custom_dir = os.path.join(os.path.dirname(__file__), "custom_profiles")
            if os.path.exists(custom_dir):
                for file in os.listdir(custom_dir):
                    if file.endswith('.json'):
                        profile_name = f"custom_{file[:-5]}"
                        profile_names.append(profile_name)
            
            self.profile_combo['values'] = profile_names
            self.profile_combo.set('default')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profiles: {e}")
            self.profile_combo['values'] = ['default']
            self.profile_combo.set('default')
    
    def browse_file(self):
        """Open file browser to select image with modern file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Document Image for Quality Analysis",
            filetypes=[
                ("All Supported Images", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp"),
                ("JPEG Images", "*.jpg *.jpeg"),
                ("PNG Images", "*.png"),
                ("TIFF Images", "*.tiff *.tif"),
                ("Bitmap Images", "*.bmp"),
                ("All Files", "*.*")
            ],
            parent=self.root
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.current_image_path = file_path
            self.progress_var.set(f"Ready to analyze: {os.path.basename(file_path)}")
    
    def start_analysis(self):
        """Start the image analysis with modern progress tracking"""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            messagebox.showerror("File Required", "Please select a valid image file first.")
            return
        
        # Disable controls during analysis
        self.analyze_button.config(state="disabled")
        self.export_button.config(state="disabled")
        self.batch_button.config(state="disabled")
        
        # Configure progress
        self.progress_bar.configure(mode='determinate', maximum=100, value=0)
        self.progress_var.set("Initializing analysis...")
        
        # Run analysis in background thread
        analysis_thread = threading.Thread(target=self.run_analysis, daemon=True)
        analysis_thread.start()
    
    def run_analysis(self):
        """Run the actual analysis with progress updates"""
        try:
            # Step 1: Load configuration (10%)
            self.root.after(0, lambda: self.progress_bar.configure(value=10))
            self.root.after(0, lambda: self.progress_var.set("Loading quality standards..."))
            
            profile_name = self.profile_var.get()
            if profile_name == 'default':
                config = self.current_config or load_default_config()
            elif profile_name.startswith('custom_'):
                custom_name = profile_name[7:]  # Remove 'custom_' prefix
                custom_dir = os.path.join(os.path.dirname(__file__), "custom_profiles")
                custom_path = os.path.join(custom_dir, f"{custom_name}.json")
                with open(custom_path, 'r') as f:
                    config = json.load(f)
            else:
                config = load_profile(profile_name)
            
            # Step 2: Start analysis (30%)
            self.root.after(0, lambda: self.progress_bar.configure(value=30))
            self.root.after(0, lambda: self.progress_var.set("Analyzing image quality..."))
            
            # Run analysis
            results = self.analyzer.analyze_image(self.current_image_path, config)
            
            # Step 3: Process results (70%)
            self.root.after(0, lambda: self.progress_bar.configure(value=70))
            self.root.after(0, lambda: self.progress_var.set("Processing results..."))
            
            # Generate visualizations if requested (disabled for now)
            viz_data = None
            if self.viz_var.get():
                self.root.after(0, lambda: self.progress_var.set("Generating visualizations..."))
                viz_data = self.generate_visualizations(results)
            
            # Step 4: Complete (100%)
            self.root.after(0, lambda: self.progress_bar.configure(value=100))
            self.root.after(0, lambda: self.display_results(results, viz_data))
            
        except Exception as e:
            self.root.after(0, lambda: self.analysis_error(str(e)))
        
    def load_profiles(self):
        """Load available configuration profiles"""
        try:
            profiles = list_profiles()
            profile_names = ['default'] + list(profiles.keys())
            self.profile_combo['values'] = profile_names
            self.profile_combo.set('default')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profiles: {e}")
            self.profile_combo['values'] = ['default']
            self.profile_combo.set('default')
    
    def browse_file(self):
        """Open file browser to select image"""
        file_path = filedialog.askopenfilename(
            title="Select Image for Analysis",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("TIFF files", "*.tiff *.tif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.current_image_path = file_path
    
    def start_analysis(self):
        """Start the image analysis in a background thread"""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            messagebox.showerror("Error", "Please select a valid image file first.")
            return
        
        # Disable controls during analysis
        self.analyze_button.config(state="disabled")
        self.export_button.config(state="disabled")
        
        # Start progress animation
        self.progress_bar.start()
        self.progress_var.set("Starting analysis...")
        
        # Run analysis in background thread
        analysis_thread = threading.Thread(target=self.run_analysis, daemon=True)
        analysis_thread.start()
    
    def run_analysis(self):
        """Run the actual analysis (in background thread)"""
        try:
            # Update progress
            self.root.after(0, lambda: self.progress_var.set("Loading configuration..."))
            
            # Load configuration
            profile_name = self.profile_var.get()
            if profile_name == 'default':
                config = load_default_config()
            else:
                config = load_profile(profile_name)
            
            # Update progress
            self.root.after(0, lambda: self.progress_var.set("Analyzing image quality..."))
            
            # Run analysis
            results = self.analyzer.analyze_image(self.current_image_path, config)
            
            # Generate visualizations if requested
            viz_data = None
            if self.viz_var.get():
                self.root.after(0, lambda: self.progress_var.set("Generating visualizations..."))
                viz_data = self.generate_visualizations(results)
            
            # Update UI with results
            self.root.after(0, lambda: self.display_results(results, viz_data))
            
        except Exception as e:
            self.root.after(0, lambda: self.analysis_error(str(e)))
    
    def generate_visualizations(self, results):
        """Generate visualization plots"""
        try:
            # For now, disable visualizations due to matplotlib threading issues
            # This will be fixed in the next version
            print("Visualization generation temporarily disabled for GUI stability")
            return None
            
            # # Create temporary directory for visualizations
            # import tempfile
            # temp_dir = tempfile.mkdtemp()
            
            # # Generate all visualizations
            # viz_files = self.graph_generator.generate_all_graphs(
            #     self.current_image_path, 
            #     results, 
            #     temp_dir
            # )
            
            # return viz_files
        except Exception as e:
            print(f"Visualization generation error: {e}")
            return None
    
    def display_results(self, results, viz_data=None):
        """Display analysis results in the GUI"""
        try:
            self.current_results = results
            
            # Stop progress animation
            self.progress_bar.stop()
            self.progress_var.set("Analysis complete!")
            
            # Enable controls
            self.analyze_button.config(state="normal")
            self.export_button.config(state="normal")
            
            # Update tabs with error handling
            try:
                self.update_summary_tab(results)
            except Exception as e:
                print(f"Error updating summary tab: {e}")
                self.progress_var.set("Error displaying summary")
            
            try:
                self.update_metrics_tab(results)
            except Exception as e:
                print(f"Error updating metrics tab: {e}")
                self.progress_var.set("Error displaying metrics")
            
            # Update visualizations tab (currently disabled)
            # if viz_data:
            #     try:
            #         self.update_visualizations_tab(viz_data)
            #     except Exception as e:
            #         print(f"Error updating visualizations tab: {e}")
            
            try:
                self.update_raw_data_tab(results)
            except Exception as e:
                print(f"Error updating raw data tab: {e}")
                self.progress_var.set("Error displaying raw data")
            
            # Switch to summary tab
            self.results_notebook.select(0)
            
            print("✅ Analysis results displayed successfully!")
            
        except Exception as e:
            self.analysis_error(f"Error displaying results: {e}")
    
    def update_summary_tab(self, results):
        """Update the executive summary tab with results"""
        try:
            global_results = results['global']
            
            # Update main score display
            score = global_results['score']
            stars = global_results['stars']
            status = global_results['status'].upper()
            
            # Update score value
            self.score_value_label.config(text=f"{score:.3f}")
            
            # Generate star display
            star_display = "★" * stars + "☆" * (4 - stars)
            self.stars_label.config(text=star_display)
            
            # Set star color based on rating
            if stars >= 3:
                star_color = '#f1c40f'  # Gold
            elif stars >= 2:
                star_color = '#f39c12'  # Orange
            else:
                star_color = '#e74c3c'  # Red
            self.stars_label.config(foreground=star_color)
            
            # Update status indicators
            category_status = results.get('category_status', {})
            pass_count = sum(1 for status in category_status.values() if status.lower() == 'pass')
            warn_count = sum(1 for status in category_status.values() if status.lower() == 'warn')
            fail_count = sum(1 for status in category_status.values() if status.lower() == 'fail')
            
            self.pass_count_value.config(text=str(pass_count))
            self.warn_count_value.config(text=str(warn_count))
            self.fail_count_value.config(text=str(fail_count))
            
            # Update quality assessment text
            self.assessment_text.delete(1.0, tk.END)
            
            # Create professional assessment report
            assessment_report = f"""QUALITY ANALYSIS REPORT
{'=' * 50}

Overall Assessment: {status}
Quality Score: {score:.3f} ({score*100:.1f}%)
Star Rating: {star_display} ({stars}/4 stars)

CATEGORY BREAKDOWN:
{'-' * 30}
"""
            
            for metric_name, metric_status in category_status.items():
                status_icon = "✅" if metric_status.lower() == "pass" else "⚠️" if metric_status.lower() == "warn" else "❌"
                display_name = metric_name.replace('_', ' ').title()
                assessment_report += f"{status_icon} {display_name}: {metric_status.upper()}\n"
            
            # Add recommendations
            assessment_report += f"\nRECOMMENDATIONS:\n{'-' * 30}\n"
            actions = global_results.get('actions', [])
            if actions:
                for i, action in enumerate(actions, 1):
                    clean_action = action.replace('\u274c', '❌').replace('\u26a0\ufe0f', '⚠️')
                    assessment_report += f"{i}. {clean_action}\n"
            else:
                assessment_report += "✅ No issues found - image quality meets all standards!\n"
            
            # Add file information
            assessment_report += f"\nFILE INFORMATION:\n{'-' * 30}\n"
            assessment_report += f"File: {os.path.basename(self.current_image_path)}\n"
            assessment_report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if 'pixels' in results:
                pixels = results['pixels']
                assessment_report += f"Dimensions: {pixels['w']} × {pixels['h']} pixels\n"
            
            if 'dpi' in results:
                dpi = results['dpi']
                assessment_report += f"Resolution: {dpi['x']} × {dpi['y']} DPI\n"
            
            self.assessment_text.insert(1.0, assessment_report)
            
        except Exception as e:
            print(f"Error in update_summary_tab: {e}")
            # Fallback simple display
            try:
                self.score_value_label.config(text="ERROR")
                self.assessment_text.delete(1.0, tk.END)
                self.assessment_text.insert(1.0, f"Error displaying results: {e}")
            except:
                pass
    
    def update_metrics_tab(self, results):
        """Update the detailed metrics tab"""
        try:
            # Clear existing items
            for item in self.metrics_tree.get_children():
                self.metrics_tree.delete(item)
            
            # Add metrics data
            metrics = results.get('metrics', {})
            category_status = results.get('category_status', {})
            
            for metric_name, metric_data in metrics.items():
                display_name = metric_name.replace('_', ' ').title()
                
                # Get score if available
                score = "N/A"
                if isinstance(metric_data, dict) and 'score' in metric_data:
                    score = f"{metric_data['score']:.3f}"
                elif isinstance(metric_data, (int, float)):
                    score = f"{metric_data:.3f}"
                
                # Get status from category_status
                status = category_status.get(metric_name, 'unknown').upper()
                
                # Get threshold information if available
                threshold = "N/A"
                # This would need to be extracted from the config, for now just show N/A
                
                # Create details string from metric data
                details = []
                if isinstance(metric_data, dict):
                    for key, value in metric_data.items():
                        if key not in ['status', 'score'] and not key.startswith('_'):
                            if isinstance(value, (int, float)):
                                if abs(value) < 0.001:  # Very small numbers
                                    details.append(f"{key}: {value:.6f}")
                                else:
                                    details.append(f"{key}: {value:.3f}")
                            elif isinstance(value, bool):
                                details.append(f"{key}: {'Yes' if value else 'No'}")
                            elif isinstance(value, str):
                                details.append(f"{key}: {value}")
                            elif isinstance(value, dict) and len(str(value)) < 50:
                                details.append(f"{key}: {value}")
                
                details_text = " | ".join(details[:2])  # Limit to first 2 details to fit
                
                # Add to tree
                item = self.metrics_tree.insert('', 'end', values=(display_name, score, status, threshold, details_text))
            
            # Update metrics summary
            self.metrics_summary_text.config(state='normal')
            self.metrics_summary_text.delete(1.0, tk.END)
            
            summary_text = f"""Metrics Analysis Summary:
• Total Metrics Evaluated: {len(metrics)}
• Passed: {sum(1 for s in category_status.values() if s.lower() == 'pass')}
• Warnings: {sum(1 for s in category_status.values() if s.lower() == 'warn')}  
• Failed: {sum(1 for s in category_status.values() if s.lower() == 'fail')}"""
            
            self.metrics_summary_text.insert(1.0, summary_text)
            self.metrics_summary_text.config(state='disabled')
            
        except Exception as e:
            print(f"Error in update_metrics_tab: {e}")
            # Add error message to tree
            try:
                self.metrics_tree.insert('', 'end', values=("Error", "N/A", "ERROR", "N/A", f"Error loading metrics: {e}"))
            except:
                pass
    
    def update_visualizations_tab(self, viz_data):
        """Update the visualizations tab with generated charts"""
        # Clear existing visualizations
        for widget in self.viz_inner_frame.winfo_children():
            widget.destroy()
        
        if not viz_data:
            no_viz_label = ttk.Label(self.viz_inner_frame, text="No visualizations generated")
            no_viz_label.pack(pady=20)
            return
        
        # Display each visualization
        row = 0
        for viz_type, viz_path in viz_data.items():
            if viz_path and os.path.exists(viz_path):
                try:
                    # Load and display image
                    img = Image.open(viz_path)
                    
                    # Resize if too large
                    max_width = 800
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(img)
                    
                    # Create label frame for each visualization
                    viz_frame = ttk.LabelFrame(self.viz_inner_frame, text=viz_type.replace('_', ' ').title(), padding="10")
                    viz_frame.pack(fill='x', padx=10, pady=5)
                    
                    viz_label = ttk.Label(viz_frame, image=photo)
                    viz_label.image = photo  # Keep a reference
                    viz_label.pack()
                    
                    row += 1
                    
                except Exception as e:
                    print(f"Error displaying visualization {viz_type}: {e}")
        
        # Configure canvas scrolling
        self.viz_inner_frame.update_idletasks()
        self.viz_canvas.create_window(0, 0, anchor="nw", window=self.viz_inner_frame)
        self.viz_canvas.configure(scrollregion=self.viz_canvas.bbox("all"))
    
    def update_raw_data_tab(self, results):
        """Update the raw data tab with JSON results"""
        self.raw_text.delete(1.0, tk.END)
        
        try:
            # Format JSON nicely
            formatted_json = json.dumps(results, indent=2, sort_keys=True, default=str)
            self.raw_text.insert(1.0, formatted_json)
        except Exception as e:
            self.raw_text.insert(1.0, f"Error formatting results: {e}\n\n{results}")
    
    def export_report(self):
        """Export analysis results to file"""
        if not self.current_results:
            messagebox.showwarning("Warning", "No analysis results to export.")
            return
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Export Analysis Report",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Add metadata
                export_data = {
                    'metadata': {
                        'image_path': self.current_image_path,
                        'analysis_timestamp': datetime.now().isoformat(),
                        'profile_used': self.profile_var.get(),
                        'analyzer_version': '1.0.0'
                    },
                    'results': self.current_results
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                messagebox.showinfo("Success", f"Report exported successfully to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report:\n{e}")
    
    def analysis_error(self, error_message):
        """Handle analysis errors"""
        self.progress_bar.stop()
        self.progress_var.set("Analysis failed!")
        self.analyze_button.config(state="normal")
        
        messagebox.showerror("Analysis Error", f"Analysis failed:\n\n{error_message}")

def main():
    """Main application entry point"""
    print("🔒 Starting Secure Desktop Image Quality Analyzer...")
    print("📊 All processing happens locally on your machine")
    print("🛡️ No data is transmitted or stored externally")
    print("⚡ Complete offline operation for maximum security")
    
    root = tk.Tk()
    
    # Set up styling
    style = ttk.Style()
    style.theme_use('clam')  # Use a modern theme
    
    # Configure accent button style
    style.configure('Accent.TButton', foreground='white', background='#0078d4')
    style.map('Accent.TButton', background=[('active', '#106ebe')])
    
    app = ProfessionalDesktopImageQualityAnalyzer(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Application error: {e}")

if __name__ == "__main__":
    main()

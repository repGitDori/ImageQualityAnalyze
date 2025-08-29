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
        self.create_sla_tab()  # Add SLA configuration tab
        
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
            
            # SLA Configuration (if SLA tab exists)
            if hasattr(self, 'sla_enabled'):
                sla_config = self.config.get('sla', {})
                self.sla_enabled.set(sla_config.get('enabled', False))
                
                self.sla_name.delete(0, tk.END)
                self.sla_name.insert(0, sla_config.get('name', 'Default Document Quality SLA'))
                
                self.sla_description.delete(1.0, tk.END)
                self.sla_description.insert(1.0, sla_config.get('description', 'Standard quality requirements for document processing'))
                
                requirements = sla_config.get('requirements', {})
                self.sla_min_score.set(requirements.get('min_overall_score', 0.80))
                
                self.sla_max_fails.delete(0, tk.END)
                self.sla_max_fails.insert(0, str(requirements.get('max_fail_categories', 1)))
                
                # Required categories
                required_cats = requirements.get('required_pass_categories', [])
                for cat, var in self.sla_req_categories.items():
                    var.set(cat in required_cats)
                
                # Performance targets
                targets = requirements.get('performance_targets', {})
                for key, entry in self.sla_targets.items():
                    if key in targets:
                        entry.delete(0, tk.END)
                        entry.insert(0, str(targets[key]))
                
                # Compliance levels
                compliance_levels = sla_config.get('compliance_levels', {})
                
                excellent = compliance_levels.get('excellent', {}).get('min_score', 0.95)
                self.sla_excellent_score.delete(0, tk.END)
                self.sla_excellent_score.insert(0, str(excellent))
                
                compliant = compliance_levels.get('compliant', {}).get('min_score', 0.80)
                self.sla_compliant_score.delete(0, tk.END)
                self.sla_compliant_score.insert(0, str(compliant))
                
                warning = compliance_levels.get('warning', {}).get('min_score', 0.65)
                self.sla_warning_score.delete(0, tk.END)
                self.sla_warning_score.insert(0, str(warning))
            
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
            
            # SLA Configuration (if SLA tab exists)
            if hasattr(self, 'sla_enabled'):
                # Get required categories
                required_categories = [cat for cat, var in self.sla_req_categories.items() if var.get()]
                
                # Get performance targets
                performance_targets = {}
                for key, entry in self.sla_targets.items():
                    try:
                        value = float(entry.get())
                        performance_targets[key] = value
                    except ValueError:
                        pass  # Skip invalid values
                
                # Build SLA config
                config['sla'] = {
                    'enabled': self.sla_enabled.get(),
                    'name': self.sla_name.get(),
                    'description': self.sla_description.get(1.0, tk.END).strip(),
                    'requirements': {
                        'min_overall_score': self.sla_min_score.get(),
                        'max_fail_categories': int(self.sla_max_fails.get() or 1),
                        'required_pass_categories': required_categories,
                        'performance_targets': performance_targets
                    },
                    'compliance_levels': {
                        'excellent': {
                            'min_score': float(self.sla_excellent_score.get() or 0.95),
                            'description': 'Exceeds all SLA requirements - professional quality'
                        },
                        'compliant': {
                            'min_score': float(self.sla_compliant_score.get() or 0.80),
                            'description': 'Meets all SLA requirements - ready for processing'
                        },
                        'warning': {
                            'min_score': float(self.sla_warning_score.get() or 0.65),
                            'description': 'Below SLA but usable - review recommended'
                        },
                        'non_compliant': {
                            'min_score': 0.0,
                            'description': 'Does not meet SLA requirements - reject or reprocess'
                        }
                    }
                }
            
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
            
    def create_sla_tab(self):
        """Create SLA configuration tab"""
        frame = ttk.Frame(self.standards_notebook, padding="20")
        self.standards_notebook.add(frame, text="🎯 SLA Settings")
        
        # SLA Enable/Disable
        sla_enable_frame = ttk.LabelFrame(frame, text="SLA Configuration", padding="15")
        sla_enable_frame.pack(fill="x", pady=(0, 20))
        
        self.sla_enabled = tk.BooleanVar()
        sla_check = ttk.Checkbutton(sla_enable_frame, text="Enable SLA Compliance Checking", variable=self.sla_enabled)
        sla_check.pack(anchor="w", pady=5)
        
        # SLA Basic Info
        info_frame = ttk.Frame(sla_enable_frame)
        info_frame.pack(fill="x", pady=10)
        
        ttk.Label(info_frame, text="SLA Name:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.sla_name = ttk.Entry(info_frame, width=40)
        self.sla_name.grid(row=0, column=1, sticky="w")
        
        ttk.Label(info_frame, text="Description:").grid(row=1, column=0, sticky="nw", padx=(0, 10), pady=(10, 0))
        self.sla_description = tk.Text(info_frame, height=3, width=40)
        self.sla_description.grid(row=1, column=1, sticky="w", pady=(10, 0))
        
        # SLA Requirements Frame
        req_frame = ttk.LabelFrame(frame, text="SLA Requirements", padding="15")
        req_frame.pack(fill="x", pady=(0, 20))
        
        # Minimum overall score
        ttk.Label(req_frame, text="Minimum Overall Score:").grid(row=0, column=0, sticky="w", pady=5)
        self.sla_min_score = ttk.Scale(req_frame, from_=0.5, to=1.0, orient="horizontal", length=200)
        self.sla_min_score.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.sla_min_score_label = ttk.Label(req_frame, text="80%")
        self.sla_min_score_label.grid(row=0, column=2, sticky="w", padx=(10, 0))
        
        # Maximum fail categories
        ttk.Label(req_frame, text="Max Failed Categories:").grid(row=1, column=0, sticky="w", pady=5)
        self.sla_max_fails = ttk.Spinbox(req_frame, from_=0, to=10, width=10)
        self.sla_max_fails.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        # Required pass categories
        ttk.Label(req_frame, text="Required PASS Categories:").grid(row=2, column=0, sticky="nw", pady=(10, 0))
        req_cat_frame = ttk.Frame(req_frame)
        req_cat_frame.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=(10, 0))
        
        self.sla_req_categories = {}
        categories = ['completeness', 'sharpness', 'resolution', 'format_integrity', 'contrast', 'exposure']
        for i, cat in enumerate(categories):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(req_cat_frame, text=cat.replace('_', ' ').title(), variable=var)
            cb.grid(row=i//2, column=i%2, sticky="w", padx=(0, 20))
            self.sla_req_categories[cat] = var
        
        # Performance Targets Frame
        perf_frame = ttk.LabelFrame(frame, text="Performance Targets", padding="15")
        perf_frame.pack(fill="x", pady=(0, 20))
        
        # Create entry fields for performance targets
        targets = [
            ('Sharpness Min (Laplacian):', 'sharpness_min_laplacian', 150.0),
            ('Contrast Min (Global):', 'contrast_min_global', 0.20),
            ('Resolution Min (DPI):', 'resolution_min_dpi', 300),
            ('Noise Max (Std Dev):', 'noise_max_std', 0.05),
            ('Geometry Max Skew:', 'geometry_max_skew', 1.0),
            ('Max Highlight Clip:', 'exposure_max_highlight_clip', 0.50),
            ('Max Shadow Clip:', 'exposure_max_shadow_clip', 0.50)
        ]
        
        self.sla_targets = {}
        for i, (label, key, default) in enumerate(targets):
            ttk.Label(perf_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            entry = ttk.Entry(perf_frame, width=15)
            entry.grid(row=i, column=1, sticky="w", padx=(10, 0), pady=2)
            entry.insert(0, str(default))
            self.sla_targets[key] = entry
        
        # Compliance Levels Frame
        comp_frame = ttk.LabelFrame(frame, text="Compliance Levels", padding="15")
        comp_frame.pack(fill="x", pady=(0, 20))
        
        # Excellent level
        ttk.Label(comp_frame, text="Excellent (Min Score):").grid(row=0, column=0, sticky="w", pady=2)
        self.sla_excellent_score = ttk.Entry(comp_frame, width=10)
        self.sla_excellent_score.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        self.sla_excellent_score.insert(0, "0.95")
        
        # Compliant level  
        ttk.Label(comp_frame, text="Compliant (Min Score):").grid(row=1, column=0, sticky="w", pady=2)
        self.sla_compliant_score = ttk.Entry(comp_frame, width=10)
        self.sla_compliant_score.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        self.sla_compliant_score.insert(0, "0.80")
        
        # Warning level
        ttk.Label(comp_frame, text="Warning (Min Score):").grid(row=2, column=0, sticky="w", pady=2)
        self.sla_warning_score = ttk.Entry(comp_frame, width=10)
        self.sla_warning_score.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)
        self.sla_warning_score.insert(0, "0.65")
        
        # Bind scale updates
        self.sla_min_score.bind("<Motion>", lambda e: self.update_scale_label(self.sla_min_score, self.sla_min_score_label, "%", 100))
        
        # SLA Presets
        preset_sla_frame = ttk.LabelFrame(frame, text="SLA Presets", padding="15")
        preset_sla_frame.pack(fill="x")
        
        ttk.Button(preset_sla_frame, text="🏢 Strict SLA", command=lambda: self.apply_sla_preset("strict")).pack(side="left", padx=(0, 10))
        ttk.Button(preset_sla_frame, text="📚 Balanced SLA", command=lambda: self.apply_sla_preset("balanced")).pack(side="left", padx=(0, 10))
        ttk.Button(preset_sla_frame, text="🔄 Relaxed SLA", command=lambda: self.apply_sla_preset("relaxed")).pack(side="left")
        
    def apply_sla_preset(self, preset_type):
        """Apply SLA preset configurations"""
        presets = {
            "strict": {
                "enabled": True,
                "name": "High-Quality Document Processing SLA",
                "description": "Strict quality requirements for professional document processing and archival",
                "min_overall_score": 0.80,
                "max_fail_categories": 0,
                "required_categories": ['completeness', 'sharpness', 'resolution', 'format_integrity'],
                "targets": {
                    "sharpness_min_laplacian": 200.0,
                    "contrast_min_global": 0.25,
                    "resolution_min_dpi": 300,
                    "noise_max_std": 0.03,
                    "geometry_max_skew": 0.5,
                    "exposure_max_highlight_clip": 0.1,
                    "exposure_max_shadow_clip": 0.1
                },
                "levels": {
                    "excellent": 0.95,
                    "compliant": 0.80,
                    "warning": 0.65
                }
            },
            "balanced": {
                "enabled": True,
                "name": "Standard Document Quality SLA",
                "description": "Balanced quality requirements for general document processing",
                "min_overall_score": 0.70,
                "max_fail_categories": 1,
                "required_categories": ['completeness', 'sharpness'],
                "targets": {
                    "sharpness_min_laplacian": 150.0,
                    "contrast_min_global": 0.20,
                    "resolution_min_dpi": 200,
                    "noise_max_std": 0.05,
                    "geometry_max_skew": 1.0,
                    "exposure_max_highlight_clip": 0.50,
                    "exposure_max_shadow_clip": 0.50
                },
                "levels": {
                    "excellent": 0.90,
                    "compliant": 0.70,
                    "warning": 0.55
                }
            },
            "relaxed": {
                "enabled": True,
                "name": "Basic Document Quality SLA", 
                "description": "Relaxed quality requirements for general document scanning and processing",
                "min_overall_score": 0.60,
                "max_fail_categories": 2,
                "required_categories": ['completeness', 'sharpness'],
                "targets": {
                    "sharpness_min_laplacian": 100.0,
                    "contrast_min_global": 0.15,
                    "resolution_min_dpi": 150,
                    "noise_max_std": 0.06,
                    "geometry_max_skew": 2.0,
                    "exposure_max_highlight_clip": 1.0,
                    "exposure_max_shadow_clip": 1.0
                },
                "levels": {
                    "excellent": 0.85,
                    "compliant": 0.60,
                    "warning": 0.45
                }
            }
        }
        
        if preset_type in presets:
            preset = presets[preset_type]
            
            # Apply basic settings
            self.sla_enabled.set(preset["enabled"])
            self.sla_name.delete(0, tk.END)
            self.sla_name.insert(0, preset["name"])
            self.sla_description.delete(1.0, tk.END)
            self.sla_description.insert(1.0, preset["description"])
            
            # Apply requirements
            self.sla_min_score.set(preset["min_overall_score"])
            self.sla_max_fails.delete(0, tk.END)
            self.sla_max_fails.insert(0, str(preset["max_fail_categories"]))
            
            # Apply required categories
            for cat, var in self.sla_req_categories.items():
                var.set(cat in preset["required_categories"])
            
            # Apply performance targets
            for key, value in preset["targets"].items():
                if key in self.sla_targets:
                    self.sla_targets[key].delete(0, tk.END)
                    self.sla_targets[key].insert(0, str(value))
            
            # Apply compliance levels
            self.sla_excellent_score.delete(0, tk.END)
            self.sla_excellent_score.insert(0, str(preset["levels"]["excellent"]))
            self.sla_compliant_score.delete(0, tk.END)
            self.sla_compliant_score.insert(0, str(preset["levels"]["compliant"]))
            self.sla_warning_score.delete(0, tk.END)
            self.sla_warning_score.insert(0, str(preset["levels"]["warning"]))
            
            # Update labels
            self.update_scale_label(self.sla_min_score, self.sla_min_score_label, "%", 100)
            
            messagebox.showinfo("SLA Preset Applied", f"Applied {preset_type.title()} SLA configuration.")
    
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
                       foreground='#2c3e50',
                       focuscolor='none')
        style.map('Accent.TButton', 
                 background=[('active', '#3498db'), ('!active', '#2980b9')],
                 foreground=[('active', '#2c3e50'), ('!active', '#2c3e50')])
        
        # Success button
        style.configure('Success.TButton',
                       font=('Segoe UI', 10),
                       foreground='#2c3e50',
                       focuscolor='none')
        style.map('Success.TButton',
                 background=[('active', '#27ae60'), ('!active', '#2ecc71')],
                 foreground=[('active', '#2c3e50'), ('!active', '#2c3e50')])
        
        # Warning button
        style.configure('Warning.TButton',
                       font=('Segoe UI', 10),
                       foreground='#2c3e50',
                       focuscolor='none')
        style.map('Warning.TButton',
                 background=[('active', '#f39c12'), ('!active', '#e67e22')],
                 foreground=[('active', '#2c3e50'), ('!active', '#2c3e50')])
        
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
        
        # Help button
        self.help_button = ttk.Button(
            self.status_frame,
            text="❓",
            command=self.show_help,
            width=3
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
        """Run batch analysis in background thread with detailed error tracking"""
        def batch_worker():
            try:
                successful_results = []
                failed_results = []
                total_files = len(image_files)
                
                for i, image_path in enumerate(image_files):
                    progress = (i / total_files) * 100
                    filename = os.path.basename(image_path)
                    
                    self.root.after(0, lambda p=progress: self.progress_bar.configure(value=p))
                    self.root.after(0, lambda f=filename: self.progress_var.set(f"Processing {f}..."))
                    
                    try:
                        # Try to analyze the image
                        result = self.analyzer.analyze_image(image_path, self.current_config)
                        successful_results.append({
                            'filename': filename,
                            'filepath': image_path,
                            'results': result
                        })
                        print(f"✅ Successfully analyzed: {filename}")
                        
                    except Exception as e:
                        # Detailed error categorization
                        error_type = type(e).__name__
                        error_message = str(e)
                        
                        # Categorize common errors
                        if "could not load" in error_message.lower() or "cannot identify image file" in error_message.lower():
                            analysis_type = "Image Loading"
                            error_reason = "File format not supported or corrupted"
                        elif "permission" in error_message.lower():
                            analysis_type = "File Access"
                            error_reason = "Permission denied or file in use"
                        elif "memory" in error_message.lower():
                            analysis_type = "Memory"
                            error_reason = "Insufficient memory to process large image"
                        elif "cv2" in error_message.lower():
                            analysis_type = "Image Processing"
                            error_reason = "OpenCV processing error"
                        elif "shape" in error_message.lower():
                            analysis_type = "Image Dimensions"
                            error_reason = "Invalid or unexpected image dimensions"
                        else:
                            analysis_type = "General Analysis"
                            error_reason = f"{error_type}: {error_message}"
                        
                        failed_results.append({
                            'filename': filename,
                            'filepath': image_path,
                            'analysis_type': analysis_type,
                            'error_type': error_type,
                            'error_message': error_message,
                            'error_reason': error_reason,
                            'timestamp': datetime.now().isoformat()
                        })
                        print(f"❌ Failed to analyze: {filename} - {error_reason}")
                
                # Generate comprehensive Excel report with error tracking
                self.root.after(0, lambda: self.progress_var.set("Generating Excel report..."))
                excel_path = self.create_batch_excel_report(successful_results, failed_results, output_folder)
                
                # Also save JSON backup
                batch_report_path = os.path.join(output_folder, "batch_analysis_report.json")
                with open(batch_report_path, 'w') as f:
                    json.dump({
                        'timestamp': datetime.now().isoformat(),
                        'total_images': total_files,
                        'successful_count': len(successful_results),
                        'failed_count': len(failed_results),
                        'successful_results': successful_results,
                        'failed_results': failed_results
                    }, f, indent=2, default=str)
                
                self.root.after(0, lambda: self.batch_analysis_complete(excel_path, len(successful_results), len(failed_results)))
                
            except Exception as e:
                self.root.after(0, lambda: self.analysis_error(f"Batch analysis failed: {e}"))
        
        # Start batch analysis
        self.progress_bar.configure(mode='determinate', maximum=100, value=0)
        self.progress_var.set("Starting batch analysis...")
        
        thread = threading.Thread(target=batch_worker, daemon=True)
        thread.start()
        
    def batch_analysis_complete(self, excel_path, successful_count, failed_count):
        """Handle batch analysis completion with detailed statistics"""
        self.progress_bar.configure(value=100)
        self.progress_var.set("Batch analysis complete!")
        
        total_count = successful_count + failed_count
        success_rate = (successful_count / total_count) * 100 if total_count > 0 else 0
        
        # Detailed completion message
        message = f"Batch Analysis Complete!\n\n"
        message += f"📊 Total Images: {total_count}\n"
        message += f"✅ Successfully Analyzed: {successful_count}\n"
        message += f"❌ Failed Analysis: {failed_count}\n"
        message += f"📈 Success Rate: {success_rate:.1f}%\n\n"
        message += f"📋 Excel Report: {os.path.basename(excel_path)}"
        
        if failed_count > 0:
            message += f"\n\n⚠️ Check the 'Failed Files' tab in the Excel report for details on failures."
        
        messagebox.showinfo("Batch Analysis Complete", message)
        
        # Open the Excel report
        try:
            if os.path.exists(excel_path):
                os.startfile(excel_path)
                print(f"📊 Opened batch Excel report: {excel_path}")
        except Exception as e:
            print(f"Could not open Excel file: {e}")
        
        # Reset progress
        self.progress_bar.configure(mode='indeterminate', value=0)
        self.progress_var.set("Ready for analysis")
    
    def create_batch_excel_report(self, successful_results, failed_results, output_folder):
        """Create comprehensive Excel report for batch analysis with error tracking"""
        try:
            import pandas as pd
            import xlsxwriter
            
            # Generate filename for batch report
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            folder_name = os.path.basename(output_folder)
            excel_filename = f"{folder_name}_BatchAnalysis_{timestamp}.xlsx"
            excel_filepath = os.path.join(output_folder, excel_filename)
            
            print(f"📊 Creating batch Excel report: {excel_filename}")
            
            # Create Excel writer
            with pd.ExcelWriter(excel_filepath, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Define professional formats
                header_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14,
                    'bg_color': '#2c5aa0',
                    'font_color': 'white',
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1
                })
                
                title_format = workbook.add_format({
                    'bold': True,
                    'font_size': 16,
                    'bg_color': '#1a252f',
                    'font_color': 'white',
                    'align': 'center',
                    'valign': 'vcenter'
                })
                
                success_format = workbook.add_format({
                    'bg_color': '#d4edda',
                    'font_color': '#155724',
                    'align': 'center'
                })
                
                fail_format = workbook.add_format({
                    'bg_color': '#f8d7da',
                    'font_color': '#721c24',
                    'align': 'center'
                })
                
                warning_format = workbook.add_format({
                    'bg_color': '#fff3cd',
                    'font_color': '#856404',
                    'align': 'center'
                })
                
                # Universal status color coding function
                def apply_status_color_coding(worksheet, df, start_row=2):
                    """Apply color coding to all status columns in a worksheet"""
                    status_columns = []
                    
                    # Find all columns that contain 'Status' in their name
                    for col_num, col_name in enumerate(df.columns):
                        if 'Status' in str(col_name) or col_name == 'Status':
                            status_columns.append((col_num, col_name))
                    
                    # Apply conditional formatting to each status column
                    for col_num, col_name in status_columns:
                        col_letter = chr(65 + col_num)  # Convert to Excel column letter
                        
                        # Define the range for conditional formatting (data rows only)
                        last_row = start_row + len(df) - 1
                        range_str = f"{col_letter}{start_row}:{col_letter}{last_row}"
                        
                        # PASS/EXCELLENT = Green
                        worksheet.conditional_format(range_str, {
                            'type': 'text',
                            'criteria': 'containing',
                            'value': 'PASS',
                            'format': success_format
                        })
                        worksheet.conditional_format(range_str, {
                            'type': 'text', 
                            'criteria': 'containing',
                            'value': 'EXCELLENT',
                            'format': success_format
                        })
                        
                        # WARN/WARNING = Yellow
                        worksheet.conditional_format(range_str, {
                            'type': 'text',
                            'criteria': 'containing', 
                            'value': 'WARN',
                            'format': warning_format
                        })
                        
                        # FAIL/POOR = Red
                        worksheet.conditional_format(range_str, {
                            'type': 'text',
                            'criteria': 'containing',
                            'value': 'FAIL',
                            'format': fail_format
                        })
                        worksheet.conditional_format(range_str, {
                            'type': 'text',
                            'criteria': 'containing',
                            'value': 'POOR',
                            'format': fail_format
                        })
                        
                        print(f"   🎨 Applied color coding to '{col_name}' column")
                
                # 1. BATCH SUMMARY SHEET
                self.create_batch_summary_sheet(writer, workbook, successful_results, failed_results, 
                                              title_format, header_format, success_format, fail_format)
                
                # 2. SUCCESSFUL ANALYSIS SHEET
                if successful_results:
                    self.create_batch_success_sheet(writer, workbook, successful_results, 
                                                  title_format, header_format, success_format, warning_format, fail_format)
                
                # 4. DETAILED METRICS SHEET - Raw numerical data
                if successful_results:
                    self.create_detailed_metrics_sheet(writer, workbook, successful_results, 
                                                     title_format, header_format, success_format, warning_format, fail_format)
                
                # 5. SLA COMPLIANCE SHEET - Service Level Agreement comparison
                if successful_results:
                    self.create_sla_compliance_sheet(writer, workbook, successful_results,
                                                    title_format, header_format, success_format, warning_format, fail_format)
                
                # 6. RAW MEASUREMENTS SHEET - All raw values
                if successful_results:
                    self.create_raw_measurements_sheet(writer, workbook, successful_results, 
                                                     title_format, header_format)
                
                # 7. TECHNICAL ANALYSIS SHEET - Advanced metrics
                if successful_results:
                    self.create_technical_analysis_sheet(writer, workbook, successful_results, 
                                                        title_format, header_format)
                
                # 8. QUALITY BREAKDOWN SHEET - Category deep dive
                if successful_results:
                    self.create_quality_breakdown_sheet(writer, workbook, successful_results, 
                                                       title_format, header_format, success_format, warning_format, fail_format)
                
                # NEW: Color coding explanation sheet
                self.create_color_coding_guide_sheet(writer, workbook, title_format, header_format, 
                                                   success_format, warning_format, fail_format)
                
                # 7. FAILED FILES SHEET (The key feature you requested!)
                if failed_results:
                    self.create_batch_failed_sheet(writer, workbook, failed_results, 
                                                 title_format, header_format, fail_format)
                
                # 8. STATISTICS SHEET
                self.create_batch_statistics_sheet(writer, workbook, successful_results, failed_results,
                                                 title_format, header_format, success_format, fail_format)
            
            return excel_filepath
            
        except ImportError:
            print("⚠️ Installing required packages for batch Excel export...")
            self.install_batch_excel_packages()
            return self.create_batch_excel_report(successful_results, failed_results, output_folder)
        except Exception as e:
            print(f"Error creating batch Excel report: {e}")
            return None
    
    def create_batch_failed_sheet(self, writer, workbook, failed_results, title_format, header_format, fail_format):
        """Create Failed Files sheet with detailed error information"""
        import pandas as pd
        
        if not failed_results:
            return
        
        # Prepare failed files data
        failed_data = []
        for failure in failed_results:
            failed_data.append({
                'File Name': failure['filename'],
                'Analysis Type': failure['analysis_type'],
                'Error Type': failure['error_type'],
                'Error Reason': failure['error_reason'],
                'Full Path': failure['filepath'],
                'Timestamp': failure['timestamp']
            })
        
        # Create DataFrame
        failed_df = pd.DataFrame(failed_data)
        
        # Write to Excel (data starts at row 3, pandas startrow=2)
        failed_df.to_excel(writer, sheet_name='Failed Files', index=False, startrow=2, header=False)
        
        # Get worksheet
        worksheet = writer.sheets['Failed Files']
        
        # Add title
        worksheet.merge_range('A1:F1', '❌ FAILED FILES - DETAILED ERROR REPORT', title_format)
        
        # Write column headers manually at row 2 (Excel row 2, index 1)
        headers = ['File Name', 'Analysis Type', 'Error Type', 'Error Reason', 'Full Path', 'Timestamp']
        for col_num, header in enumerate(headers):
            worksheet.write(1, col_num, header, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 25)  # File Name
        worksheet.set_column('B:B', 20)  # Analysis Type
        worksheet.set_column('C:C', 15)  # Error Type
        worksheet.set_column('D:D', 40)  # Error Reason
        worksheet.set_column('E:E', 50)  # Full Path
        worksheet.set_column('F:F', 20)  # Timestamp
        
        # Apply formatting to all data rows (data starts at row 3, Excel 1-based)
        for row_idx, row_data in enumerate(failed_data):
            excel_row = row_idx + 2  # Row 3, 4, 5, etc. (0-based indexing: 2, 3, 4, etc.)
            worksheet.write(excel_row, 0, row_data['File Name'], fail_format)
            worksheet.write(excel_row, 1, row_data['Analysis Type'], fail_format)
            worksheet.write(excel_row, 2, row_data['Error Type'], fail_format)
            worksheet.write(excel_row, 3, row_data['Error Reason'], fail_format)
            worksheet.write(excel_row, 4, row_data['Full Path'], fail_format)
            worksheet.write(excel_row, 5, row_data['Timestamp'], fail_format)
        
        print(f"📊 Created Failed Files sheet with {len(failed_data)} entries")
    
    def create_batch_summary_sheet(self, writer, workbook, successful_results, failed_results, 
                                  title_format, header_format, success_format, fail_format):
        """Create batch analysis summary sheet"""
        import pandas as pd
        
        total_count = len(successful_results) + len(failed_results)
        success_rate = (len(successful_results) / total_count) * 100 if total_count > 0 else 0
        
        summary_data = {
            'Metric': [
                'Total Images Processed',
                'Successfully Analyzed',
                'Failed Analysis',
                'Success Rate',
                'Analysis Date',
                'Analysis Time'
            ],
            'Value': [
                total_count,
                len(successful_results),
                len(failed_results),
                f"{success_rate:.1f}%",
                datetime.now().strftime("%Y-%m-%d"),
                datetime.now().strftime("%H:%M:%S")
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        # Write data starting at row 3 (Excel row 3, pandas startrow=2)
        summary_df.to_excel(writer, sheet_name='Batch Summary', index=False, startrow=2, header=False)
        
        worksheet = writer.sheets['Batch Summary']
        worksheet.merge_range('A1:B1', '📊 BATCH ANALYSIS SUMMARY', title_format)
        
        # Write column headers manually at row 2 (Excel row 2, index 1)
        headers = ['Metric', 'Value']
        for col_num, header in enumerate(headers):
            worksheet.write(1, col_num, header, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 20)
        
        # Apply conditional formatting (data starts at row 3, Excel 1-based)
        for row_idx, metric in enumerate(summary_data['Metric']):
            excel_row = row_idx + 2  # Row 3, 4, 5, etc. (0-based indexing: 2, 3, 4, etc.)
            value = summary_data['Value'][row_idx]
            
            # Write the data first
            worksheet.write(excel_row, 0, metric)
            
            # Apply conditional formatting to the value column
            if 'Success' in metric:
                worksheet.write(excel_row, 1, value, success_format)
            elif 'Failed' in metric:
                worksheet.write(excel_row, 1, value, fail_format)
            else:
                worksheet.write(excel_row, 1, value)  # Default formatting
    
    def create_batch_success_sheet(self, writer, workbook, successful_results, title_format, 
                                  header_format, success_format, warning_format, fail_format):
        """Create successful analysis summary sheet"""
        import pandas as pd
        
        success_data = []
        
        for result in successful_results:
            filename = result['filename']
            analysis = result['results']
            global_info = analysis.get('global', {})
            
            success_data.append({
                'File Name': filename,
                'Overall Score': f"{global_info.get('score', 0):.3f}",
                'Status': global_info.get('status', 'Unknown').upper(),
                'Stars': f"{global_info.get('stars', 0)} out of 4",
                'Critical Issues': 'Yes' if global_info.get('critical_fail', False) else 'No',
                'Recommendations': len(global_info.get('actions', []))
            })
        
        success_df = pd.DataFrame(success_data)
        # Write data starting at row 3 (Excel row 3, pandas startrow=2)
        success_df.to_excel(writer, sheet_name='Successful Analysis', index=False, startrow=2, header=False)
        
        worksheet = writer.sheets['Successful Analysis']
        worksheet.merge_range('A1:F1', '✅ SUCCESSFUL ANALYSIS RESULTS', title_format)
        
        # Write column headers manually at row 2 (Excel row 2, index 1)
        headers = ['File Name', 'Overall Score', 'Status', 'Stars', 'Critical Issues', 'Recommendations']
        for col_num, header in enumerate(headers):
            worksheet.write(1, col_num, header, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 25)  # File Name
        worksheet.set_column('B:B', 15)  # Overall Score
        worksheet.set_column('C:C', 15)  # Status
        worksheet.set_column('D:D', 15)  # Stars
        worksheet.set_column('E:E', 15)  # Critical Issues
        worksheet.set_column('F:F', 15)  # Recommendations
        
        # Apply conditional formatting based on status (data starts at row 3, Excel 1-based)
        for row_idx, row_data in enumerate(success_data):
            excel_row = row_idx + 2  # Row 3, 4, 5, etc. (0-based indexing: 2, 3, 4, etc.)
            status = row_data['Status']
            critical = row_data['Critical Issues']
            
            if status == 'EXCELLENT':
                format_to_use = success_format
            elif status in ['FAIL', 'POOR'] or critical == 'Yes':
                format_to_use = fail_format
            else:
                format_to_use = warning_format
            
            # Write the entire row with formatting
            worksheet.write(excel_row, 0, row_data['File Name'], format_to_use)
            worksheet.write(excel_row, 1, row_data['Overall Score'], format_to_use)
            worksheet.write(excel_row, 2, row_data['Status'], format_to_use)
            worksheet.write(excel_row, 3, row_data['Stars'], format_to_use)
            worksheet.write(excel_row, 4, row_data['Critical Issues'], format_to_use)
            worksheet.write(excel_row, 5, row_data['Recommendations'], format_to_use)
    
    def create_batch_statistics_sheet(self, writer, workbook, successful_results, failed_results,
                                     title_format, header_format, success_format, fail_format):
        """Create statistics and trends sheet"""
        import pandas as pd
        
        # Error type statistics
        error_types = {}
        analysis_types = {}
        
        for failure in failed_results:
            error_type = failure['error_type']
            analysis_type = failure['analysis_type']
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
            analysis_types[analysis_type] = analysis_types.get(analysis_type, 0) + 1
        
        # Create error statistics table
        if failed_results:
            error_stats_data = []
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(failed_results)) * 100
                error_stats_data.append({
                    'Error Type': error_type,
                    'Count': count,
                    'Percentage': f"{percentage:.1f}%"
                })
            
            error_df = pd.DataFrame(error_stats_data)
            # Write data starting at row 3 (Excel row 3, pandas startrow=2)
            error_df.to_excel(writer, sheet_name='Statistics', index=False, startrow=2, header=False)
            
            worksheet = writer.sheets['Statistics']
            worksheet.merge_range('A1:C1', '📈 ERROR STATISTICS', title_format)
            
            # Write column headers manually at row 2 (Excel row 2, index 1)
            headers = ['Error Type', 'Count', 'Percentage']
            for col_num, header in enumerate(headers):
                worksheet.write(1, col_num, header, header_format)
            
            # Analysis type breakdown
            if len(analysis_types) > 1:
                analysis_stats_data = []
                for analysis_type, count in sorted(analysis_types.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(failed_results)) * 100
                    analysis_stats_data.append({
                        'Analysis Type': analysis_type,
                        'Failure Count': count,
                        'Failure Rate': f"{percentage:.1f}%"
                    })
                
                analysis_df = pd.DataFrame(analysis_stats_data)
                start_row = len(error_stats_data) + 4
                # Write data starting at calculated row (no header since we'll write manually)
                analysis_df.to_excel(writer, sheet_name='Statistics', index=False, startrow=start_row, header=False)
                
                worksheet.merge_range(f'A{start_row}:C{start_row}', '🔍 ANALYSIS TYPE BREAKDOWN', title_format)
                
                # Write analysis headers manually at start_row + 1
                analysis_headers = ['Analysis Type', 'Failure Count', 'Failure Rate']
                for col_num, header in enumerate(analysis_headers):
                    worksheet.write(start_row, col_num, header, header_format)
        
        print(f"📊 Created Statistics sheet with error analysis")
    
    def create_detailed_metrics_sheet(self, writer, workbook, successful_results, title_format, 
                                     header_format, success_format, warning_format, fail_format):
        """Create detailed metrics sheet with comprehensive numerical data"""
        import pandas as pd
        
        detailed_data = []
        
        for result in successful_results:
            filename = result['filename']
            analysis = result['results']
            metrics = analysis.get('metrics', {})
            global_info = analysis.get('global', {})
            category_status = analysis.get('category_status', {})
            
            # Build comprehensive row with all key metrics
            row_data = {
                'File Name': filename,
                'Overall Score': global_info.get('score', 0),
                'Quality Stars': global_info.get('stars', 0),
                'Status': global_info.get('status', 'Unknown').upper(),
                'Critical Issues': 'Yes' if global_info.get('critical_fail', False) else 'No',
                
                # Sharpness metrics
                'Laplacian Variance': metrics.get('sharpness', {}).get('laplacian_var', 0),
                'Gradient Magnitude': metrics.get('sharpness', {}).get('gradient_magnitude_mean', 0),
                'Edge Density': metrics.get('sharpness', {}).get('edge_density', 0),
                'High Freq Energy': metrics.get('sharpness', {}).get('frequency_metrics', {}).get('high_freq_energy', 0),
                'Sharpness Status': category_status.get('sharpness', 'Unknown').upper(),
                
                # Exposure metrics
                'Shadow Clip %': metrics.get('exposure', {}).get('clipping', {}).get('shadow_clip_pct', 0),
                'Highlight Clip %': metrics.get('exposure', {}).get('clipping', {}).get('highlight_clip_pct', 0),
                'Brightness Mean': metrics.get('exposure', {}).get('brightness', {}).get('mean', 0),
                'Brightness Std': metrics.get('exposure', {}).get('brightness', {}).get('std', 0),
                'Dynamic Range': metrics.get('exposure', {}).get('dynamic_range', {}).get('effective_range', 0),
                'Illumination Uniformity': metrics.get('exposure', {}).get('illumination_uniformity', {}).get('uniformity_ratio', 0),
                'Background Median': metrics.get('exposure', {}).get('background', {}).get('median', 0),
                'Exposure Status': category_status.get('exposure', 'Unknown').upper(),
                
                # Contrast metrics
                'Global Contrast': metrics.get('contrast', {}).get('global_contrast', 0),
                'RMS Contrast': metrics.get('contrast', {}).get('rms_contrast', 0),
                'Local Contrast Mean': metrics.get('contrast', {}).get('local_contrast', {}).get('mean', 0),
                'Local Contrast Std': metrics.get('contrast', {}).get('local_contrast', {}).get('std', 0),
                'Contrast Status': category_status.get('contrast', 'Unknown').upper(),
                
                # Geometry metrics
                'Skew Angle (abs)': metrics.get('geometry', {}).get('skew_angle_abs', 0),
                'Warp Index': metrics.get('geometry', {}).get('warp_index', 0),
                'Aspect Ratio': metrics.get('geometry', {}).get('orientation', {}).get('aspect_ratio', 0),
                'Line Angle Std': metrics.get('geometry', {}).get('line_angles', {}).get('angle_std', 0),
                'Geometry Status': category_status.get('geometry', 'Unknown').upper(),
                
                # Resolution metrics
                'DPI X': metrics.get('resolution', {}).get('effective_dpi_x', 0),
                'DPI Y': metrics.get('resolution', {}).get('effective_dpi_y', 0),
                'Width (px)': metrics.get('resolution', {}).get('pixel_width', 0),
                'Height (px)': metrics.get('resolution', {}).get('pixel_height', 0),
                'Megapixels': metrics.get('resolution', {}).get('megapixels', 0),
                'Resolution Status': category_status.get('resolution', 'Unknown').upper(),
                
                # Border/Background metrics
                'Left Margin %': metrics.get('border_background', {}).get('left_margin_ratio', 0) * 100,
                'Right Margin %': metrics.get('border_background', {}).get('right_margin_ratio', 0) * 100,
                'Top Margin %': metrics.get('border_background', {}).get('top_margin_ratio', 0) * 100,
                'Bottom Margin %': metrics.get('border_background', {}).get('bottom_margin_ratio', 0) * 100,
                'BG Luminance': metrics.get('border_background', {}).get('bg_median_lum', 0),
                'BG Noise Std': metrics.get('noise', {}).get('bg_noise_std', 0),
                'Border Status': category_status.get('border_background', 'Unknown').upper(),
                
                # Completeness metrics
                'Content Coverage': metrics.get('completeness', {}).get('content_bbox_coverage', 0),
                'Edge Touch': 'Yes' if metrics.get('completeness', {}).get('edge_touch_flag', False) else 'No',
                'Left Margin (px)': metrics.get('completeness', {}).get('margins', {}).get('left_px', 0),
                'Right Margin (px)': metrics.get('completeness', {}).get('margins', {}).get('right_px', 0),
                'Top Margin (px)': metrics.get('completeness', {}).get('margins', {}).get('top_px', 0),
                'Bottom Margin (px)': metrics.get('completeness', {}).get('margins', {}).get('bottom_px', 0),
                'Completeness Status': category_status.get('completeness', 'Unknown').upper(),
                
                # Color metrics
                'Hue Cast (degrees)': metrics.get('color', {}).get('hue_cast_degrees', 0),
                'Gray Delta E': metrics.get('color', {}).get('gray_deltaE', 0) if metrics.get('color', {}).get('gray_deltaE') is not None else 0,
                'Color Status': category_status.get('color', 'Unknown').upper(),
                
                # Format metrics
                'Format': metrics.get('format_integrity', {}).get('format_name', 'Unknown'),
                'Bit Depth': metrics.get('format_integrity', {}).get('bit_depth', 0),
                'JPEG Quality': metrics.get('format_integrity', {}).get('jpeg_quality', 0) if metrics.get('format_integrity', {}).get('jpeg_quality') is not None else 'N/A',
                'Format Status': category_status.get('format_integrity', 'Unknown').upper(),
                
                # Foreign objects
                'Foreign Objects': 'Yes' if metrics.get('foreign_objects', {}).get('foreign_object_flag', False) else 'No',
                'Foreign Area %': metrics.get('foreign_objects', {}).get('foreign_object_area_pct', 0),
            }
            
            detailed_data.append(row_data)
        
        # Create DataFrame and write to Excel
        detailed_df = pd.DataFrame(detailed_data)
        # Write data starting at row 3 (Excel row 3, pandas startrow=2)
        detailed_df.to_excel(writer, sheet_name='Detailed Metrics', index=False, startrow=2, header=False)
        
        worksheet = writer.sheets['Detailed Metrics']
        
        # Calculate the end column letter properly for merge range  
        end_col_index = len(detailed_df.columns) - 1
        if end_col_index > 25:
            # For very wide tables, use a safe range
            worksheet.merge_range('A1:Z1', '📊 DETAILED METRICS & MEASUREMENTS', title_format)
        else:
            end_col_letter = chr(65 + end_col_index)
            worksheet.merge_range(f'A1:{end_col_letter}1', '📊 DETAILED METRICS & MEASUREMENTS', title_format)
        
        # Write column headers manually at row 2 (Excel row 2, index 1)
        for col_num, column_title in enumerate(detailed_df.columns):
            worksheet.write(1, col_num, column_title, header_format)
        
        # Apply conditional formatting based on status columns (data starts at row 3, Excel 1-based)
        for row_idx, row_data in enumerate(detailed_data):
            excel_row = row_idx + 2  # Row 3, 4, 5, etc. (0-based indexing: 2, 3, 4, etc.)
            overall_status = row_data['Status']
            critical = row_data['Critical Issues']
            
            if overall_status == 'EXCELLENT':
                format_to_use = success_format
            elif overall_status in ['FAIL', 'POOR'] or critical == 'Yes':
                format_to_use = fail_format
            else:
                format_to_use = warning_format
            
            # Apply format to the entire row
            for col_num, column_name in enumerate(detailed_df.columns):
                value = row_data[column_name]
                worksheet.write(excel_row, col_num, value, format_to_use)
        
        # Set column widths
        for i, col in enumerate(detailed_df.columns):
            worksheet.set_column(i, i, 15)
            
        # Apply status color coding to all Status columns
        status_columns = []
        for col_num, col_name in enumerate(detailed_df.columns):
            if 'Status' in str(col_name) or col_name == 'Status':
                status_columns.append((col_num, col_name))
        
        for col_num, col_name in status_columns:
            col_letter = chr(65 + col_num)
            last_row = 3 + len(detailed_df) - 1
            range_str = f"{col_letter}3:{col_letter}{last_row}"
            
            # PASS/EXCELLENT = Green
            worksheet.conditional_format(range_str, {
                'type': 'text', 'criteria': 'containing', 'value': 'PASS', 'format': success_format
            })
            worksheet.conditional_format(range_str, {
                'type': 'text', 'criteria': 'containing', 'value': 'EXCELLENT', 'format': success_format
            })
            
            # WARN/WARNING = Yellow
            worksheet.conditional_format(range_str, {
                'type': 'text', 'criteria': 'containing', 'value': 'WARN', 'format': warning_format
            })
            
            # FAIL/POOR = Red
            worksheet.conditional_format(range_str, {
                'type': 'text', 'criteria': 'containing', 'value': 'FAIL', 'format': fail_format
            })
            worksheet.conditional_format(range_str, {
                'type': 'text', 'criteria': 'containing', 'value': 'POOR', 'format': fail_format
            })
            
            print(f"   🎨 Applied color coding to '{col_name}' column")
        
        print(f"📊 Created Detailed Metrics sheet with {len(detailed_data)} files and {len(detailed_df.columns)} metrics")
    
    def create_raw_measurements_sheet(self, writer, workbook, successful_results, title_format, header_format):
        """Create raw measurements sheet with all numerical values"""
        import pandas as pd
        
        raw_data = []
        
        for result in successful_results:
            filename = result['filename']
            analysis = result['results']
            metrics = analysis.get('metrics', {})
            
            # Extract all raw numerical measurements
            row_data = {'File Name': filename}
            
            # Sharpness raw data
            sharpness = metrics.get('sharpness', {})
            row_data.update({
                'Sharp_Laplacian_Var': sharpness.get('laplacian_var', 0),
                'Sharp_Gradient_Mean': sharpness.get('gradient_magnitude_mean', 0),
                'Sharp_Edge_Density': sharpness.get('edge_density', 0),
                'Sharp_Local_Mean': sharpness.get('local_sharpness', {}).get('mean', 0),
                'Sharp_Local_Std': sharpness.get('local_sharpness', {}).get('std', 0),
                'Sharp_Local_Min': sharpness.get('local_sharpness', {}).get('min', 0),
                'Sharp_Local_Max': sharpness.get('local_sharpness', {}).get('max', 0),
                'Sharp_P10': sharpness.get('local_sharpness', {}).get('percentiles', {}).get('p10', 0),
                'Sharp_P25': sharpness.get('local_sharpness', {}).get('percentiles', {}).get('p25', 0),
                'Sharp_P50': sharpness.get('local_sharpness', {}).get('percentiles', {}).get('p50', 0),
                'Sharp_P75': sharpness.get('local_sharpness', {}).get('percentiles', {}).get('p75', 0),
                'Sharp_P90': sharpness.get('local_sharpness', {}).get('percentiles', {}).get('p90', 0),
                'Sharp_High_Freq': sharpness.get('frequency_metrics', {}).get('high_freq_energy', 0),
                'Sharp_Mid_Freq': sharpness.get('frequency_metrics', {}).get('mid_freq_energy', 0),
                'Sharp_Low_Freq': sharpness.get('frequency_metrics', {}).get('low_freq_energy', 0),
                'Sharp_Spectral_Centroid': sharpness.get('frequency_metrics', {}).get('spectral_centroid', 0),
            })
            
            # Exposure raw data
            exposure = metrics.get('exposure', {})
            row_data.update({
                'Exp_Shadow_Clip_Pct': exposure.get('clipping', {}).get('shadow_clip_pct', 0),
                'Exp_Highlight_Clip_Pct': exposure.get('clipping', {}).get('highlight_clip_pct', 0),
                'Exp_Shadow_Pixels': exposure.get('clipping', {}).get('shadow_clipped_pixels', 0),
                'Exp_Highlight_Pixels': exposure.get('clipping', {}).get('highlight_clipped_pixels', 0),
                'Exp_Total_Pixels': exposure.get('clipping', {}).get('total_pixels', 0),
                'Exp_Uniformity_Ratio': exposure.get('illumination_uniformity', {}).get('uniformity_ratio', 0),
                'Exp_Local_Std': exposure.get('illumination_uniformity', {}).get('local_std', 0),
                'Exp_Local_Mean': exposure.get('illumination_uniformity', {}).get('local_mean', 0),
                'Exp_Coeff_Variation': exposure.get('illumination_uniformity', {}).get('coefficient_of_variation', 0),
                'Exp_Tiles_Analyzed': exposure.get('illumination_uniformity', {}).get('num_tiles_analyzed', 0),
                'Exp_Bright_Mean': exposure.get('brightness', {}).get('mean', 0),
                'Exp_Bright_Median': exposure.get('brightness', {}).get('median', 0),
                'Exp_Bright_Std': exposure.get('brightness', {}).get('std', 0),
                'Exp_Bright_Min': exposure.get('brightness', {}).get('min', 0),
                'Exp_Bright_Max': exposure.get('brightness', {}).get('max', 0),
                'Exp_Bright_P5': exposure.get('brightness', {}).get('percentiles', {}).get('p5', 0),
                'Exp_Bright_P10': exposure.get('brightness', {}).get('percentiles', {}).get('p10', 0),
                'Exp_Bright_P25': exposure.get('brightness', {}).get('percentiles', {}).get('p25', 0),
                'Exp_Bright_P75': exposure.get('brightness', {}).get('percentiles', {}).get('p75', 0),
                'Exp_Bright_P90': exposure.get('brightness', {}).get('percentiles', {}).get('p90', 0),
                'Exp_Bright_P95': exposure.get('brightness', {}).get('percentiles', {}).get('p95', 0),
                'Exp_Dynamic_Effective': exposure.get('dynamic_range', {}).get('effective_range', 0),
                'Exp_Dynamic_Full': exposure.get('dynamic_range', {}).get('full_range', 0),
                'Exp_Dynamic_Utilization': exposure.get('dynamic_range', {}).get('utilization', 0),
                'Exp_BG_Median': exposure.get('background', {}).get('median', 0),
                'Exp_BG_Mean': exposure.get('background', {}).get('mean', 0),
                'Exp_BG_Std': exposure.get('background', {}).get('std', 0),
                'Exp_BG_Max': exposure.get('background', {}).get('max', 0),
                'Exp_BG_Pixel_Count': exposure.get('background', {}).get('pixel_count', 0),
            })
            
            # Contrast raw data
            contrast = metrics.get('contrast', {})
            row_data.update({
                'Con_Global': contrast.get('global_contrast', 0),
                'Con_RMS': contrast.get('rms_contrast', 0),
                'Con_P5': contrast.get('percentiles', {}).get('p5', 0),
                'Con_P95': contrast.get('percentiles', {}).get('p95', 0),
                'Con_Mean_Luminance': contrast.get('mean_luminance', 0),
                'Con_Local_Mean': contrast.get('local_contrast', {}).get('mean', 0),
                'Con_Local_Std': contrast.get('local_contrast', {}).get('std', 0),
                'Con_Local_Min': contrast.get('local_contrast', {}).get('min', 0),
                'Con_Local_Max': contrast.get('local_contrast', {}).get('max', 0),
                'Con_Local_Tiles': contrast.get('local_contrast', {}).get('num_tiles', 0),
            })
            
            # Geometry raw data
            geometry = metrics.get('geometry', {})
            row_data.update({
                'Geo_Skew_Deg': geometry.get('skew_angle_deg', 0),
                'Geo_Skew_Abs': geometry.get('skew_angle_abs', 0),
                'Geo_Lines_Detected': geometry.get('line_angles', {}).get('detected_lines', 0),
                'Geo_Angle_Std': geometry.get('line_angles', {}).get('angle_std', 0),
                'Geo_Angle_Range': geometry.get('line_angles', {}).get('angle_range', 0),
                'Geo_Warp_Index': geometry.get('warp_index', 0),
                'Geo_Aspect_Ratio': geometry.get('orientation', {}).get('aspect_ratio', 0),
                'Geo_Doc_Width': geometry.get('orientation', {}).get('doc_width_px', 0),
                'Geo_Doc_Height': geometry.get('orientation', {}).get('doc_height_px', 0),
            })
            
            # Border/Background raw data
            border = metrics.get('border_background', {})
            margins_px = border.get('margins_px', {})
            row_data.update({
                'Border_BG_Median': border.get('bg_median_lum', 0),
                'Border_BG_Mean': border.get('bg_mean_lum', 0),
                'Border_BG_Std': border.get('bg_std', 0),
                'Border_Left_Ratio': border.get('left_margin_ratio', 0),
                'Border_Right_Ratio': border.get('right_margin_ratio', 0),
                'Border_Top_Ratio': border.get('top_margin_ratio', 0),
                'Border_Bottom_Ratio': border.get('bottom_margin_ratio', 0),
                'Border_Left_Px': margins_px.get('left', 0),
                'Border_Right_Px': margins_px.get('right', 0),
                'Border_Top_Px': margins_px.get('top', 0),
                'Border_Bottom_Px': margins_px.get('bottom', 0),
            })
            
            # Noise raw data
            noise = metrics.get('noise', {})
            row_data.update({
                'Noise_BG_Std': noise.get('bg_noise_std', 0),
                'Noise_Blockiness': noise.get('blockiness_index', 0),
            })
            
            # Completeness raw data
            completeness = metrics.get('completeness', {})
            margins = completeness.get('margins', {})
            bbox = completeness.get('document_bbox', {})
            violations = completeness.get('edge_violations', {})
            row_data.update({
                'Comp_Coverage': completeness.get('content_bbox_coverage', 0),
                'Comp_Edge_Touch': 1 if completeness.get('edge_touch_flag', False) else 0,
                'Comp_Left_Px': margins.get('left_px', 0),
                'Comp_Right_Px': margins.get('right_px', 0),
                'Comp_Top_Px': margins.get('top_px', 0),
                'Comp_Bottom_Px': margins.get('bottom_px', 0),
                'Comp_Left_Violation': 1 if violations.get('left_violation', False) else 0,
                'Comp_Right_Violation': 1 if violations.get('right_violation', False) else 0,
                'Comp_Top_Violation': 1 if violations.get('top_violation', False) else 0,
                'Comp_Bottom_Violation': 1 if violations.get('bottom_violation', False) else 0,
                'Comp_BBox_X_Min': bbox.get('x_min', 0),
                'Comp_BBox_Y_Min': bbox.get('y_min', 0),
                'Comp_BBox_X_Max': bbox.get('x_max', 0),
                'Comp_BBox_Y_Max': bbox.get('y_max', 0),
                'Comp_BBox_Width': bbox.get('width', 0),
                'Comp_BBox_Height': bbox.get('height', 0),
                'Comp_BBox_Aspect': bbox.get('aspect_ratio', 0),
            })
            
            # Resolution raw data
            resolution = metrics.get('resolution', {})
            row_data.update({
                'Res_DPI_X': resolution.get('effective_dpi_x', 0),
                'Res_DPI_Y': resolution.get('effective_dpi_y', 0),
                'Res_Width_Px': resolution.get('pixel_width', 0),
                'Res_Height_Px': resolution.get('pixel_height', 0),
                'Res_Megapixels': resolution.get('megapixels', 0),
            })
            
            # Color raw data
            color = metrics.get('color', {})
            row_data.update({
                'Color_Hue_Cast': color.get('hue_cast_degrees', 0),
                'Color_Gray_DeltaE': color.get('gray_deltaE', 0) if color.get('gray_deltaE') is not None else 0,
                'Color_Enabled': 1 if color.get('enabled', False) else 0,
            })
            
            # Format raw data
            format_info = metrics.get('format_integrity', {})
            row_data.update({
                'Format_Bit_Depth': format_info.get('bit_depth', 0),
                'Format_JPEG_Quality': format_info.get('jpeg_quality', 0) if format_info.get('jpeg_quality') is not None else 0,
                'Format_Allowed': 1 if format_info.get('format_allowed', False) else 0,
            })
            
            # Foreign objects raw data
            foreign = metrics.get('foreign_objects', {})
            row_data.update({
                'Foreign_Flag': 1 if foreign.get('foreign_object_flag', False) else 0,
                'Foreign_Area_Pct': foreign.get('foreign_object_area_pct', 0),
            })
            
            raw_data.append(row_data)
        
        # Create DataFrame and write to Excel - headers=False to avoid duplication
        raw_df = pd.DataFrame(raw_data)
        raw_df.to_excel(writer, sheet_name='Raw Measurements', index=False, startrow=2, header=False)
        
        worksheet = writer.sheets['Raw Measurements']
        
        # Calculate the end column letter properly for merge range
        end_col_index = len(raw_df.columns) - 1
        if end_col_index > 25:
            # For very wide tables, use a safe range
            worksheet.merge_range('A1:Z1', '🔬 RAW MEASUREMENTS & TECHNICAL DATA', title_format)
        else:
            end_col_letter = chr(65 + end_col_index)
            worksheet.merge_range(f'A1:{end_col_letter}1', '🔬 RAW MEASUREMENTS & TECHNICAL DATA', title_format)
        
        # Add proper headers with formatting at row 2 (index 1)
        for col_num, column_title in enumerate(raw_df.columns):
            worksheet.write(1, col_num, column_title, header_format)
        
        # Set column widths
        for i, col in enumerate(raw_df.columns):
            if 'File' in col:
                worksheet.set_column(i, i, 25)
            else:
                worksheet.set_column(i, i, 12)
        
        print(f"📊 Created Raw Measurements sheet with {len(raw_data)} files and {len(raw_df.columns)} raw measurements")
    
    def create_technical_analysis_sheet(self, writer, workbook, successful_results, title_format, header_format):
        """Create technical analysis sheet with advanced computed metrics"""
        import pandas as pd
        
        tech_data = []
        
        for result in successful_results:
            filename = result['filename']
            analysis = result['results']
            metrics = analysis.get('metrics', {})
            
            # Compute advanced derived metrics
            sharpness = metrics.get('sharpness', {})
            exposure = metrics.get('exposure', {})
            contrast = metrics.get('contrast', {})
            geometry = metrics.get('geometry', {})
            resolution = metrics.get('resolution', {})
            
            # Advanced calculations
            laplacian = sharpness.get('laplacian_var', 0)
            gradient = sharpness.get('gradient_magnitude_mean', 0)
            sharpness_score = (laplacian / 1000) * (gradient / 100) if laplacian > 0 and gradient > 0 else 0
            
            dynamic_range = exposure.get('dynamic_range', {}).get('effective_range', 0)
            brightness_std = exposure.get('brightness', {}).get('std', 0)
            exposure_quality = dynamic_range * (1 - brightness_std) if brightness_std < 1 else 0
            
            global_contrast = contrast.get('global_contrast', 0)
            local_contrast_mean = contrast.get('local_contrast', {}).get('mean', 0)
            contrast_balance = abs(global_contrast - local_contrast_mean) if global_contrast > 0 and local_contrast_mean > 0 else 1
            
            skew_abs = geometry.get('skew_angle_abs', 0)
            warp_index = geometry.get('warp_index', 0)
            geometry_score = max(0, 1 - (skew_abs / 10) - (warp_index / 2))
            
            dpi_x = resolution.get('effective_dpi_x', 0)
            dpi_y = resolution.get('effective_dpi_y', 0)
            megapixels = resolution.get('megapixels', 0)
            resolution_quality = min(dpi_x, dpi_y) / 300 * min(1, megapixels / 3) if dpi_x > 0 and dpi_y > 0 else 0
            
            row_data = {
                'File Name': filename,
                'Sharpness Score': round(sharpness_score, 4),
                'Exposure Quality': round(exposure_quality, 4),
                'Contrast Balance': round(contrast_balance, 4),
                'Geometry Score': round(geometry_score, 4),
                'Resolution Quality': round(resolution_quality, 4),
                'Sharpness Category': 'Excellent' if laplacian > 500 else 'Good' if laplacian > 200 else 'Poor',
                'Exposure Category': 'Excellent' if dynamic_range > 0.3 else 'Good' if dynamic_range > 0.15 else 'Poor',
                'Contrast Category': 'Excellent' if global_contrast > 0.25 else 'Good' if global_contrast > 0.15 else 'Poor',
                'Geometry Category': 'Excellent' if skew_abs < 1 else 'Good' if skew_abs < 3 else 'Poor',
                'Resolution Category': 'Excellent' if min(dpi_x, dpi_y) >= 300 else 'Good' if min(dpi_x, dpi_y) >= 200 else 'Poor',
                
                # Technical ratios
                'Freq High/Mid Ratio': round(sharpness.get('frequency_metrics', {}).get('high_freq_energy', 0) / 
                                           max(sharpness.get('frequency_metrics', {}).get('mid_freq_energy', 0.001), 0.001), 4),
                'Shadow/Highlight Ratio': round(exposure.get('clipping', {}).get('shadow_clip_pct', 0) / 
                                               max(exposure.get('clipping', {}).get('highlight_clip_pct', 0.001), 0.001), 4),
                'DPI Consistency': round(abs(dpi_x - dpi_y) / max(dpi_x, dpi_y, 1), 4),
                'Aspect Stability': round(abs(geometry.get('orientation', {}).get('aspect_ratio', 1) - 1.414), 4),  # Distance from A4 ratio
                
                # Quality indicators
                'Detail Preservation': 'High' if laplacian > 300 and gradient > 40 else 'Medium' if laplacian > 150 else 'Low',
                'Illumination Quality': 'Uniform' if exposure.get('illumination_uniformity', {}).get('uniformity_ratio', 1) < 0.1 else 'Variable',
                'Document Alignment': 'Aligned' if skew_abs < 1 else 'Slightly Skewed' if skew_abs < 3 else 'Skewed',
                'Capture Completeness': 'Complete' if metrics.get('completeness', {}).get('content_bbox_coverage', 0) > 0.9 else 'Partial',
                
                # File characteristics
                'File Size Category': 'Large' if megapixels > 5 else 'Medium' if megapixels > 2 else 'Small',
                'Processing Complexity': 'High' if megapixels > 8 else 'Medium' if megapixels > 3 else 'Low',
            }
            
            tech_data.append(row_data)
        
        # Create DataFrame and write to Excel - headers=False to avoid duplication
        tech_df = pd.DataFrame(tech_data)
        tech_df.to_excel(writer, sheet_name='Technical Analysis', index=False, startrow=2, header=False)
        
        worksheet = writer.sheets['Technical Analysis']
        
        # Calculate the end column letter properly for merge range
        end_col_index = len(tech_df.columns) - 1
        if end_col_index > 25:
            worksheet.merge_range('A1:Z1', '⚙️ TECHNICAL ANALYSIS & COMPUTED METRICS', title_format)
        else:
            end_col_letter = chr(65 + end_col_index)
            worksheet.merge_range(f'A1:{end_col_letter}1', '⚙️ TECHNICAL ANALYSIS & COMPUTED METRICS', title_format)
        
        # Add proper headers with formatting at row 2 (index 1)
        for col_num, column_title in enumerate(tech_df.columns):
            worksheet.write(1, col_num, column_title, header_format)
        
        # Set column widths
        for i, col in enumerate(tech_df.columns):
            if 'File' in col:
                worksheet.set_column(i, i, 25)
            elif 'Category' in col or 'Quality' in col:
                worksheet.set_column(i, i, 18)
            else:
                worksheet.set_column(i, i, 15)
        
        print(f"📊 Created Technical Analysis sheet with {len(tech_data)} files and advanced metrics")
    
    def create_quality_breakdown_sheet(self, writer, workbook, successful_results, title_format, 
                                      header_format, success_format, warning_format, fail_format):
        """Create quality breakdown sheet with category-by-category analysis"""
        import pandas as pd
        
        breakdown_data = []
        
        for result in successful_results:
            filename = result['filename']
            analysis = result['results']
            category_status = analysis.get('category_status', {})
            metrics = analysis.get('metrics', {})
            global_info = analysis.get('global', {})
            
            # Convert category status to scores for detailed breakdown
            status_to_score = {'pass': 0.85, 'warn': 0.70, 'fail': 0.30, 'unknown': 0.50}
            
            row_data = {
                'File Name': filename,
                'Overall Score': global_info.get('score', 0),
                'Overall Status': global_info.get('status', 'Unknown').upper(),
                'Total Issues': len(global_info.get('actions', [])),
                
                # Individual category scores
                'Completeness Score': status_to_score.get(category_status.get('completeness', 'unknown'), 0.5),
                'Completeness Status': category_status.get('completeness', 'Unknown').upper(),
                'Completeness Detail': f"Coverage: {metrics.get('completeness', {}).get('content_bbox_coverage', 0):.1%}",
                
                'Sharpness Score': status_to_score.get(category_status.get('sharpness', 'unknown'), 0.5),
                'Sharpness Status': category_status.get('sharpness', 'Unknown').upper(),
                'Sharpness Detail': f"Laplacian: {metrics.get('sharpness', {}).get('laplacian_var', 0):.1f}",
                
                'Exposure Score': status_to_score.get(category_status.get('exposure', 'unknown'), 0.5),
                'Exposure Status': category_status.get('exposure', 'Unknown').upper(),
                'Exposure Detail': f"Range: {metrics.get('exposure', {}).get('dynamic_range', {}).get('effective_range', 0):.3f}",
                
                'Contrast Score': status_to_score.get(category_status.get('contrast', 'unknown'), 0.5),
                'Contrast Status': category_status.get('contrast', 'Unknown').upper(),
                'Contrast Detail': f"Global: {metrics.get('contrast', {}).get('global_contrast', 0):.3f}",
                
                'Color Score': status_to_score.get(category_status.get('color', 'unknown'), 0.5),
                'Color Status': category_status.get('color', 'Unknown').upper(),
                'Color Detail': f"Hue Cast: {metrics.get('color', {}).get('hue_cast_degrees', 0):.1f}°",
                
                'Geometry Score': status_to_score.get(category_status.get('geometry', 'unknown'), 0.5),
                'Geometry Status': category_status.get('geometry', 'Unknown').upper(),
                'Geometry Detail': f"Skew: {metrics.get('geometry', {}).get('skew_angle_abs', 0):.1f}°",
                
                'Border Score': status_to_score.get(category_status.get('border_background', 'unknown'), 0.5),
                'Border Status': category_status.get('border_background', 'Unknown').upper(),
                'Border Detail': f"BG Lum: {metrics.get('border_background', {}).get('bg_median_lum', 0):.3f}",
                
                'Noise Score': status_to_score.get(category_status.get('noise', 'unknown'), 0.5),
                'Noise Status': category_status.get('noise', 'Unknown').upper(),
                'Noise Detail': f"BG Std: {metrics.get('noise', {}).get('bg_noise_std', 0):.4f}",
                
                'Format Score': status_to_score.get(category_status.get('format_integrity', 'unknown'), 0.5),
                'Format Status': category_status.get('format_integrity', 'Unknown').upper(),
                'Format Detail': f"{metrics.get('format_integrity', {}).get('format_name', 'Unknown')} - {metrics.get('format_integrity', {}).get('bit_depth', 0)}bit",
                
                'Resolution Score': status_to_score.get(category_status.get('resolution', 'unknown'), 0.5),
                'Resolution Status': category_status.get('resolution', 'Unknown').upper(),
                'Resolution Detail': f"{metrics.get('resolution', {}).get('effective_dpi_x', 0):.0f} DPI",
                
                # Problem indicators
                'Critical Issues': 'Yes' if global_info.get('critical_fail', False) else 'No',
                'Worst Category': min(category_status.keys(), key=lambda k: status_to_score.get(category_status.get(k, 'unknown'), 0.5)) if category_status else 'Unknown',
                'Best Category': max(category_status.keys(), key=lambda k: status_to_score.get(category_status.get(k, 'unknown'), 0.5)) if category_status else 'Unknown',
                'Pass Count': sum(1 for status in category_status.values() if status == 'pass'),
                'Warn Count': sum(1 for status in category_status.values() if status == 'warn'),
                'Fail Count': sum(1 for status in category_status.values() if status == 'fail'),
            }
            
            breakdown_data.append(row_data)
        
        # Create DataFrame and write to Excel
        breakdown_df = pd.DataFrame(breakdown_data)
        # Write data starting at row 3 (Excel row 3, pandas startrow=2)
        breakdown_df.to_excel(writer, sheet_name='Quality Breakdown', index=False, startrow=2, header=False)
        
        worksheet = writer.sheets['Quality Breakdown']
        
        # Calculate the end column letter properly for merge range
        end_col_index = len(breakdown_df.columns) - 1
        if end_col_index > 25:
            worksheet.merge_range('A1:Z1', '🎯 QUALITY BREAKDOWN BY CATEGORY', title_format)
        else:
            end_col_letter = chr(65 + end_col_index)
            worksheet.merge_range(f'A1:{end_col_letter}1', '🎯 QUALITY BREAKDOWN BY CATEGORY', title_format)
        
        # Write column headers manually at row 2 (Excel row 2, index 1)
        for col_num, column_title in enumerate(breakdown_df.columns):
            worksheet.write(1, col_num, column_title, header_format)
        
        # Apply conditional formatting for status columns (data starts at row 3, Excel 1-based)
        for row_idx, row_data in enumerate(breakdown_data):
            excel_row = row_idx + 2  # Row 3, 4, 5, etc. (0-based indexing: 2, 3, 4, etc.)
            
            for col_name in breakdown_df.columns:
                if 'Status' in col_name:
                    status_value = row_data[col_name]
                    col_idx = list(breakdown_df.columns).index(col_name)
                    
                    if status_value == 'PASS':
                        format_to_use = success_format
                    elif status_value == 'WARN':
                        format_to_use = warning_format
                    elif status_value == 'FAIL':
                        format_to_use = fail_format
                    else:
                        format_to_use = None
                    
                    if format_to_use:
                        worksheet.write(excel_row, col_idx, status_value, format_to_use)
        
        # Set column widths
        for i, col in enumerate(breakdown_df.columns):
            if 'File' in col:
                worksheet.set_column(i, i, 25)
            elif 'Detail' in col:
                worksheet.set_column(i, i, 20)
            else:
                worksheet.set_column(i, i, 15)
        
        # Add comprehensive status color coding to Quality Breakdown sheet
        status_columns = []
        for col_num, col_name in enumerate(breakdown_df.columns):
            # Look for any status-related columns (including category status columns)
            if any(keyword in str(col_name).upper() for keyword in ['STATUS', 'COMPLIANT', 'COMPLIANCE']) and 'File' not in str(col_name):
                status_columns.append((col_num, col_name))
        
        print(f"   🎨 Found {len(status_columns)} status columns in Quality Breakdown sheet")
        
        for col_num, col_name in status_columns:
            col_letter = chr(65 + col_num)
            last_row = 3 + len(breakdown_df) - 1
            range_str = f"{col_letter}3:{col_letter}{last_row}"
            
            # Green for positive statuses
            for positive_status in ['PASS', 'EXCELLENT', 'GOOD', 'COMPLIANT', 'YES']:
                worksheet.conditional_format(range_str, {
                    'type': 'text', 'criteria': 'containing', 'value': positive_status, 'format': success_format
                })
            
            # Yellow for warning statuses
            for warning_status in ['WARN', 'WARNING', 'ACCEPTABLE']:
                worksheet.conditional_format(range_str, {
                    'type': 'text', 'criteria': 'containing', 'value': warning_status, 'format': warning_format
                })
            
            # Red for failure statuses
            for failure_status in ['FAIL', 'POOR', 'BAD', 'NON_COMPLIANT', 'NO']:
                worksheet.conditional_format(range_str, {
                    'type': 'text', 'criteria': 'containing', 'value': failure_status, 'format': fail_format
                })
                
            print(f"      • Applied color coding to '{col_name}' column")
        
        print(f"📊 Created Quality Breakdown sheet with {len(breakdown_data)} files and detailed category analysis")
    
    def create_sla_compliance_sheet(self, writer, workbook, successful_results, title_format, 
                                   header_format, success_format, warning_format, fail_format):
        """Create SLA Compliance sheet showing Service Level Agreement comparison"""
        import pandas as pd
        
        sla_data = []
        
        for result in successful_results:
            sla_info = result.get('sla', {})
            
            if not sla_info.get('enabled', False):
                # If SLA not enabled, show basic info
                sla_data.append({
                    'File Name': os.path.basename(result.get('file_path', '')),
                    'Quality Score': result.get('global', {}).get('score', 0),
                    'SLA Status': 'Not Configured',
                    'Compliance Level': 'N/A',
                    'Overall Compliant': 'N/A',
                    'Score Requirement': 'N/A',
                    'Category Failures': 'N/A',
                    'Performance Targets': 'N/A',
                    'SLA Recommendations': 'Configure SLA settings to enable compliance checking'
                })
                continue
            
            compliance = sla_info.get('compliance', {})
            requirements_met = compliance.get('requirements_met', {})
            
            # Get requirement details
            score_req = requirements_met.get('minimum_score', {})
            category_req = requirements_met.get('category_failures', {})
            performance_req = requirements_met.get('performance_targets', {})
            
            # Format SLA recommendations 
            recommendations = sla_info.get('recommendations', [])
            recommendations_text = '; '.join(recommendations[:2]) if recommendations else 'All requirements met'
            
            sla_data.append({
                'File Name': os.path.basename(result.get('file_path', '')),
                'Quality Score': result.get('global', {}).get('score', 0),
                'SLA Name': sla_info.get('sla_name', ''),
                'Compliance Level': compliance.get('level', '').upper(),
                'Overall Compliant': 'YES' if compliance.get('overall_compliant', False) else 'NO',
                'Score Requirement': f"≥{score_req.get('required', 0):.1%} (Actual: {score_req.get('actual', 0):.1%})",
                'Score Met': 'YES' if score_req.get('compliant', False) else 'NO',
                'Category Failures': f"≤{category_req.get('max_allowed', 0)} (Actual: {category_req.get('actual', 0)})",
                'Category Met': 'YES' if category_req.get('compliant', False) else 'NO',
                'Performance Targets': 'MET' if performance_req.get('compliant', False) else 'FAILED',
                'SLA Recommendations': recommendations_text
            })
        
        if not sla_data:
            return
        
        # Create DataFrame
        sla_df = pd.DataFrame(sla_data)
        
        # Create worksheet
        worksheet = workbook.add_worksheet('SLA Compliance')
        
        # Add title
        worksheet.merge_range('A1:K1', '🎯 SERVICE LEVEL AGREEMENT (SLA) COMPLIANCE REPORT', title_format)
        
        # Create DataFrame and write to Excel
        sla_df.to_excel(writer, sheet_name='SLA Compliance', index=False, startrow=2)
        
        # Get the xlsxwriter workbook and worksheet objects.
        worksheet = writer.sheets['SLA Compliance']
        
        # Apply conditional formatting
        for idx, row in sla_df.iterrows():
            row_num = idx + 3  # Account for title and headers
            
            # Format compliance level
            compliance_level = row.get('Compliance Level', '').lower()
            if compliance_level in ['excellent', 'compliant']:
                format_to_use = success_format
            elif compliance_level == 'warning':
                format_to_use = warning_format
            elif compliance_level == 'non_compliant':
                format_to_use = fail_format
            else:
                format_to_use = None
            
            if format_to_use and 'Compliance Level' in sla_df.columns:
                col_idx = list(sla_df.columns).index('Compliance Level')
                worksheet.write(row_num, col_idx, row['Compliance Level'], format_to_use)
            
            # Format overall compliant status
            overall_compliant = row.get('Overall Compliant', '')
            if overall_compliant == 'YES':
                format_to_use = success_format
            elif overall_compliant == 'NO':
                format_to_use = fail_format
            else:
                format_to_use = None
            
            if format_to_use and 'Overall Compliant' in sla_df.columns:
                col_idx = list(sla_df.columns).index('Overall Compliant')
                worksheet.write(row_num, col_idx, overall_compliant, format_to_use)
            
            # Format individual requirement statuses
            for col_name in ['Score Met', 'Category Met']:
                if col_name in sla_df.columns and col_name in row:
                    status = row[col_name]
                    if status == 'YES':
                        format_to_use = success_format
                    elif status == 'NO':
                        format_to_use = fail_format
                    else:
                        format_to_use = None
                    
                    if format_to_use:
                        col_idx = list(sla_df.columns).index(col_name)
                        worksheet.write(row_num, col_idx, status, format_to_use)
            
            # Format performance targets
            if 'Performance Targets' in sla_df.columns and 'Performance Targets' in row:
                status = row['Performance Targets']
                if status == 'MET':
                    format_to_use = success_format
                elif status == 'FAILED':
                    format_to_use = fail_format
                else:
                    format_to_use = None
                
                if format_to_use:
                    col_idx = list(sla_df.columns).index('Performance Targets')
                    worksheet.write(row_num, col_idx, status, format_to_use)
        
        # Set column widths
        for i, col in enumerate(sla_df.columns):
            if 'File' in col:
                worksheet.set_column(i, i, 25)
            elif 'Recommendations' in col:
                worksheet.set_column(i, i, 40)
            elif 'Requirement' in col:
                worksheet.set_column(i, i, 20)
            elif 'SLA Name' in col:
                worksheet.set_column(i, i, 25)
            else:
                worksheet.set_column(i, i, 15)
        
        # Add SLA summary information
        if sla_data and sla_data[0].get('SLA Name') != '':
            summary_start_row = len(sla_data) + 5
            
            # Calculate summary statistics
            compliant_count = sum(1 for row in sla_data if row.get('Overall Compliant') == 'YES')
            total_count = len(sla_data)
            compliance_rate = (compliant_count / total_count * 100) if total_count > 0 else 0
            
            # Add summary section
            worksheet.merge_range(f'A{summary_start_row}:K{summary_start_row}', 
                                '📊 SLA COMPLIANCE SUMMARY', title_format)
            
            summary_start_row += 2
            worksheet.write(f'A{summary_start_row}', 'Total Files Analyzed:', header_format)
            worksheet.write(f'B{summary_start_row}', total_count)
            
            summary_start_row += 1
            worksheet.write(f'A{summary_start_row}', 'SLA Compliant Files:', header_format)
            worksheet.write(f'B{summary_start_row}', compliant_count, success_format if compliant_count > 0 else fail_format)
            
            summary_start_row += 1
            worksheet.write(f'A{summary_start_row}', 'Overall Compliance Rate:', header_format)
            worksheet.write(f'B{summary_start_row}', f'{compliance_rate:.1f}%', 
                          success_format if compliance_rate >= 80 else warning_format if compliance_rate >= 60 else fail_format)
        
        print(f"📊 Created SLA Compliance sheet with {len(sla_data)} files and service level agreement analysis")
    
    def create_color_coding_guide_sheet(self, writer, workbook, title_format, header_format, 
                                       success_format, warning_format, fail_format):
        """Create comprehensive color coding guide sheet"""
        import pandas as pd
        
        # Color coding explanation data
        guide_sections = [
            {
                'section': '🎨 COLOR CODING SYSTEM',
                'description': 'Understanding the colors used throughout all Excel sheets',
                'items': []
            },
            {
                'section': '✅ GREEN (PASS/SUCCESS)',
                'description': 'Indicates excellent performance and meeting quality standards',
                'items': [
                    ['Status Values', 'PASS, EXCELLENT, GOOD', 'Quality meets or exceeds standards'],
                    ['Score Range', '0.80 - 1.00 (80% - 100%)', 'High quality measurements'],
                    ['Examples', 'Sharp images, proper exposure, correct geometry', 'These images meet professional standards'],
                    ['Action', 'No changes needed', 'Images are ready for use'],
                    ['Background', 'Light green (#D4EDDA)', 'Easy visual identification of success']
                ]
            },
            {
                'section': '⚠️ YELLOW/ORANGE (WARN/CAUTION)',
                'description': 'Indicates acceptable but improvable quality - attention recommended',
                'items': [
                    ['Status Values', 'WARN, FAIR, MEDIUM', 'Quality is acceptable but could be better'],
                    ['Score Range', '0.65 - 0.79 (65% - 79%)', 'Moderate quality measurements'],
                    ['Examples', 'Slight blur, minor exposure issues, small geometry problems', 'Usable but not optimal'],
                    ['Action', 'Consider improvement if possible', 'Review capture settings or processing'],
                    ['Background', 'Light yellow (#FFF3CD)', 'Caution indicator for attention']
                ]
            },
            {
                'section': '❌ RED (FAIL/CRITICAL)',
                'description': 'Indicates poor quality requiring attention or re-capture',
                'items': [
                    ['Status Values', 'FAIL, POOR, CRITICAL', 'Quality falls below acceptable standards'],
                    ['Score Range', '0.00 - 0.64 (0% - 64%)', 'Low quality measurements'],
                    ['Examples', 'Blurry images, poor exposure, significant skew', 'Images need improvement'],
                    ['Action', 'Re-capture recommended', 'Address underlying capture/processing issues'],
                    ['Background', 'Light red (#F8D7DA)', 'Alert indicator for problems']
                ]
            },
            {
                'section': '📊 SCORE INTERPRETATION',
                'description': 'How numerical scores translate to quality ratings',
                'items': [
                    ['0.85 Score', 'PASS Status', 'Excellent quality - meets all requirements'],
                    ['0.70 Score', 'WARN Status', 'Good quality - minor improvements possible'],
                    ['0.30 Score', 'FAIL Status', 'Poor quality - significant improvements needed'],
                    ['0.50 Score', 'UNKNOWN Status', 'Unable to determine - check raw data'],
                    ['Critical Flag', 'Yes/No Indicator', 'Immediate attention required regardless of score']
                ]
            },
            {
                'section': '🎯 CATEGORY STATUS MEANINGS',
                'description': 'What each quality category status indicates',
                'items': [
                    ['Sharpness PASS', 'Image is sharp and clear', 'Good focus, minimal blur'],
                    ['Exposure PASS', 'Proper lighting and brightness', 'No clipping, good dynamic range'],
                    ['Contrast PASS', 'Good tonal separation', 'Clear distinction between light/dark areas'],
                    ['Geometry PASS', 'Document properly aligned', 'Minimal skew, correct orientation'],
                    ['Resolution PASS', 'Sufficient detail capture', 'Adequate DPI for intended use'],
                    ['Border PASS', 'Proper margins and background', 'Clean borders, dark background'],
                    ['Completeness PASS', 'Full document captured', 'No content cut off at edges'],
                    ['Color PASS', 'Natural color reproduction', 'Minimal color cast or distortion'],
                    ['Format PASS', 'Appropriate file format', 'Correct compression and bit depth'],
                    ['Noise PASS', 'Clean image quality', 'Minimal digital noise or artifacts']
                ]
            },
            {
                'section': '📈 USING THE COLOR SYSTEM',
                'description': 'How to effectively use color coding for analysis',
                'items': [
                    ['Quick Scanning', 'Identify problems at a glance', 'Red areas need immediate attention'],
                    ['Batch Overview', 'Assess overall quality trends', 'Proportion of green/yellow/red'],
                    ['Priority Setting', 'Focus on red items first', 'Address critical issues before minor ones'],
                    ['Quality Control', 'Track improvements over time', 'Monitor color distribution changes'],
                    ['Reporting', 'Communicate status clearly', 'Colors provide instant understanding']
                ]
            }
        ]
        
        # Create the guide sheet
        all_rows = []
        current_row = 0
        
        for section in guide_sections:
            # Section header
            all_rows.append({
                'A': section['section'],
                'B': section['description'],
                'C': '',
                'row_type': 'section_header'
            })
            current_row += 1
            
            # Add space
            all_rows.append({'A': '', 'B': '', 'C': '', 'row_type': 'spacer'})
            current_row += 1
            
            # Section items
            for item in section['items']:
                all_rows.append({
                    'A': item[0],
                    'B': item[1],
                    'C': item[2] if len(item) > 2 else '',
                    'row_type': 'content'
                })
                current_row += 1
            
            # Add space after section
            all_rows.append({'A': '', 'B': '', 'C': '', 'row_type': 'spacer'})
            current_row += 1
        
        # Create worksheet
        worksheet = workbook.add_worksheet('Color Coding Guide')
        
        # Title
        worksheet.merge_range('A1:C1', '🎨 COLOR CODING & STATUS INTERPRETATION GUIDE', title_format)
        
        # Headers
        worksheet.write('A2', 'Element', header_format)
        worksheet.write('B2', 'Meaning', header_format)
        worksheet.write('C2', 'Description', header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 35)
        worksheet.set_column('C:C', 50)
        
        # Write content with appropriate formatting
        row_num = 2
        for row_data in all_rows:
            row_num += 1
            
            if row_data['row_type'] == 'section_header':
                # Section headers get title formatting
                worksheet.merge_range(f'A{row_num}:C{row_num}', row_data['A'], title_format)
                if row_data['B']:
                    row_num += 1
                    worksheet.merge_range(f'A{row_num}:C{row_num}', row_data['B'], header_format)
                    
            elif row_data['row_type'] == 'content':
                # Determine formatting based on content
                if 'PASS' in row_data['A'] or 'GREEN' in row_data['A'] or 'SUCCESS' in row_data['A']:
                    format_to_use = success_format
                elif 'WARN' in row_data['A'] or 'YELLOW' in row_data['A'] or 'CAUTION' in row_data['A']:
                    format_to_use = warning_format
                elif 'FAIL' in row_data['A'] or 'RED' in row_data['A'] or 'CRITICAL' in row_data['A']:
                    format_to_use = fail_format
                else:
                    format_to_use = None
                
                if format_to_use:
                    worksheet.write(f'A{row_num}', row_data['A'], format_to_use)
                    worksheet.write(f'B{row_num}', row_data['B'], format_to_use)
                    worksheet.write(f'C{row_num}', row_data['C'], format_to_use)
                else:
                    worksheet.write(f'A{row_num}', row_data['A'])
                    worksheet.write(f'B{row_num}', row_data['B'])
                    worksheet.write(f'C{row_num}', row_data['C'])
        
        # Add a legend at the bottom
        legend_start = row_num + 3
        worksheet.merge_range(f'A{legend_start}:C{legend_start}', '🎨 COLOR LEGEND', title_format)
        
        legend_start += 2
        worksheet.write(f'A{legend_start}', 'GREEN BACKGROUND', success_format)
        worksheet.write(f'B{legend_start}', 'PASS/SUCCESS/EXCELLENT', success_format) 
        worksheet.write(f'C{legend_start}', 'Quality meets standards - no action needed', success_format)
        
        legend_start += 1
        worksheet.write(f'A{legend_start}', 'YELLOW BACKGROUND', warning_format)
        worksheet.write(f'B{legend_start}', 'WARN/FAIR/MEDIUM', warning_format)
        worksheet.write(f'C{legend_start}', 'Acceptable quality - consider improvement', warning_format)
        
        legend_start += 1
        worksheet.write(f'A{legend_start}', 'RED BACKGROUND', fail_format)
        worksheet.write(f'B{legend_start}', 'FAIL/POOR/CRITICAL', fail_format)
        worksheet.write(f'C{legend_start}', 'Quality issues - attention required', fail_format)
        
        print(f"📊 Created Color Coding Guide sheet with comprehensive explanations")
    
    def safe_merge_range(self, worksheet, range_str, text, format_obj):
        """Safely merge range with error handling"""
        try:
            worksheet.merge_range(range_str, text, format_obj)
        except Exception as e:
            print(f"⚠️ Merge range warning for {range_str}: {e}")
            # Fall back to writing to first cell if merge fails
            try:
                first_cell = range_str.split(':')[0]
                worksheet.write(first_cell, text, format_obj)
            except Exception as e2:
                print(f"❌ Failed to write header: {e2}")
    
    def install_batch_excel_packages(self):
        """Install required packages for batch Excel export"""
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "xlsxwriter"])
            print("✅ Successfully installed batch Excel export packages")
        except Exception as e:
            print(f"❌ Failed to install packages: {e}")
        
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
        self.help_button.pack(anchor="e", pady=(5, 0))
        
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
    
    def show_help(self):
        """Show help popup with user guide from local text file"""
        help_window = tk.Toplevel(self.root)
        help_window.title("❓ Help - Professional Image Quality Analyzer")
        help_window.geometry("800x600")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center the help window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
        y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")
        
        # Create main frame with padding
        main_frame = ttk.Frame(help_window, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Create scrollable text widget
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True)
        
        # Text widget with scrollbar
        help_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            padx=10,
            pady=10,
            relief='flat',
            bg='#ffffff',
            fg='#2c3e50'
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=help_text.yview)
        help_text.configure(yscrollcommand=scrollbar.set)
        
        help_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load help content from local file
        try:
            help_file_path = os.path.join(os.path.dirname(__file__), 'help_guide.txt')
            if os.path.exists(help_file_path):
                with open(help_file_path, 'r', encoding='utf-8') as f:
                    help_content = f.read()
            else:
                help_content = """# 🏢 Professional Image Quality Analyzer - Help

## 🚀 Quick Start Guide

1. **📁 Select Image** - Click "Browse Files" to choose your document image
2. **⚙️ Choose Standards** - Select quality standards from dropdown
3. **🚀 Analyze** - Click "Analyze Quality" to start analysis
4. **📋 Export** - Save results as JSON or view detailed reports

## 🛡️ Security & Privacy
- ✅ 100% Offline - No internet connection required
- ✅ Local Processing - Images never leave your computer
- ✅ Complete Privacy Protection

For more detailed help, please refer to the documentation files in the application folder.
"""
        except Exception as e:
            help_content = f"""# Help Content Error

Sorry, there was an error loading the help file: {str(e)}

## Basic Usage:
1. Select an image file using the Browse button
2. Choose your quality standards
3. Click Analyze Quality to start analysis
4. View results in the tabs below
5. Export reports as needed

The application works completely offline for your security and privacy.
"""
        
        # Insert help content
        help_text.insert("1.0", help_content)
        help_text.configure(state='disabled')  # Make it read-only
        
        # Configure text styling for headers and sections
        help_text.tag_configure("header", font=('Segoe UI', 12, 'bold'), foreground='#2980b9')
        help_text.tag_configure("subheader", font=('Segoe UI', 11, 'bold'), foreground='#34495e')
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Close button
        close_button = ttk.Button(
            button_frame,
            text="✓ Close Help",
            command=help_window.destroy,
            style="Accent.TButton"
        )
        close_button.pack(side="right")
        
        # Focus the help window
        help_window.focus_set()

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
            
            try:
                self.update_recommendations_tab(results)
            except Exception as e:
                print(f"Error updating recommendations tab: {e}")
                self.progress_var.set("Error displaying recommendations")
            
            # Switch to summary tab
            self.results_notebook.select(0)
            
            print("✅ Analysis results displayed successfully!")
            
            # Automatically export results to Excel with visuals
            self.auto_export_excel_with_visuals(results)
            
        except Exception as e:
            self.analysis_error(f"Error displaying results: {e}")
    
    def auto_export_excel_with_visuals(self, results):
        """Automatically export analysis results to Excel with charts and visual formatting"""
        try:
            # Try importing pandas first
            try:
                import pandas as pd
            except ImportError:
                print("⚠️ Installing pandas for Excel export...")
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
                import pandas as pd
            
            import xlsxwriter
            import io
            import matplotlib.pyplot as plt
            from matplotlib.patches import Circle
            import numpy as np
            
            # Create output directory
            base_dir = os.path.dirname(self.current_image_path) if self.current_image_path else os.getcwd()
            output_dir = os.path.join(base_dir, "analysis_results")
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate professional Excel filename
            excel_filename, excel_filepath = self.generate_excel_filename(output_dir)
            
            # Create Excel writer with xlsxwriter engine for better formatting
            try:
                with pd.ExcelWriter(excel_filepath, engine='xlsxwriter') as writer:
                    
                    # Get the workbook and add formats
                    workbook = writer.book
                
                    # Define professional formats
                    header_format = workbook.add_format({
                        'bold': True,
                        'font_size': 14,
                        'bg_color': '#2c5aa0',
                        'font_color': 'white',
                        'align': 'center',
                        'valign': 'vcenter',
                        'border': 1
                    })
                    
                    title_format = workbook.add_format({
                        'bold': True,
                        'font_size': 16,
                        'bg_color': '#1a252f',
                        'font_color': 'white',
                        'align': 'center',
                        'valign': 'vcenter'
                    })
                    
                    metric_header_format = workbook.add_format({
                        'bold': True,
                        'font_size': 12,
                        'bg_color': '#f8f9fa',
                        'font_color': '#212529',
                        'align': 'center',
                        'border': 1
                    })
                    
                    good_format = workbook.add_format({
                        'bg_color': '#d4edda',
                        'font_color': '#155724',
                        'border': 1,
                        'align': 'center'
                    })
                    
                    warning_format = workbook.add_format({
                        'bg_color': '#fff3cd',
                        'font_color': '#856404',
                        'border': 1,
                        'align': 'center'
                    })
                    
                    poor_format = workbook.add_format({
                        'bg_color': '#f8d7da',
                        'font_color': '#721c24',
                        'border': 1,
                        'align': 'center'
                    })
                    
                    # Format for unknown status - white background
                    unknown_format = workbook.add_format({
                        'bg_color': '#ffffff',
                        'font_color': '#6c757d',
                        'border': 1,
                        'align': 'center'
                    })
                    
                    # Create Summary Sheet
                    print(f"📊 ===== COMPREHENSIVE EXCEL DEBUG =====")
                    print(f"📊 Creating Excel sheets with results data...")
                    print(f"📊 Results type: {type(results)}")
                    print(f"📊 Full results structure:")
                    if isinstance(results, dict):
                        for main_key, main_value in results.items():
                            print(f"📊   MAIN: '{main_key}' = {type(main_value)}")
                            if isinstance(main_value, dict):
                                for sub_key, sub_value in main_value.items():
                                    if isinstance(sub_value, dict):
                                        print(f"📊     SUB-DICT: '{sub_key}' contains {len(sub_value)} items")
                                        for detail_key, detail_value in sub_value.items():
                                            print(f"📊       DETAIL: '{detail_key}' = {detail_value}")
                                    else:
                                        print(f"📊     SUB: '{sub_key}' = {sub_value}")
                            elif isinstance(main_value, list):
                                print(f"📊     LIST: {len(main_value)} items = {main_value}")
                            else:
                                print(f"📊     DIRECT: {main_value}")
                    print(f"📊 ===== END DEBUG =====")
                    print(f"📊 Global results keys: {list(results.get('global', {}).keys())}")
                    print(f"📊 Metrics keys: {list(results.get('metrics', {}).keys())}")
                    
                    self.create_summary_sheet(writer, workbook, results, title_format, header_format, metric_header_format)
                    
                    # Create Detailed Metrics Sheet
                    self.create_metrics_sheet(writer, workbook, results, header_format, metric_header_format, good_format, warning_format, poor_format, unknown_format)
                    
                    # Create Recommendations Sheet
                    self.create_recommendations_sheet(writer, workbook, results, header_format, metric_header_format)
                    
                    # Create Charts Sheet
                    self.create_charts_sheet(writer, workbook, results, header_format)
                
                print(f"✅ Excel report exported: {excel_filename}")
                
                # Update status and show notification
                self.progress_var.set("✅ Excel report exported successfully!")
                
                # Auto-open the Excel file
                self.open_excel_file(excel_filepath, output_dir)
                
            except Exception as e:
                print(f"❌ Error creating Excel report: {e}")
                self.progress_var.set("Analysis complete (Excel export error)")
                messagebox.showwarning(
                    "Export Warning",
                    f"Analysis completed successfully, but Excel export failed:\n\n{e}\n\n"
                    f"You can still view results in the application."
                )
        
        except Exception as e:
            print(f"❌ Excel export error: {e}")
            self.progress_var.set("Analysis complete (Excel export error)")
    
    def create_summary_sheet(self, writer, workbook, results, title_format, header_format, metric_header_format):
        """Create the executive summary sheet"""
        import pandas as pd  # Import here for scope
        
        global_results = results.get('global', {})
        print(f"📊 Global results data: {global_results}")  # Debug print
        
        # Extract actual values with proper fallbacks
        overall_score = global_results.get('overall_score', global_results.get('score', 0))
        stars = global_results.get('stars', 0)
        status = global_results.get('status', 'Unknown')
        
        # Handle different time formats
        analysis_time = global_results.get('analysis_time', 
                                          global_results.get('processing_time', 
                                                            global_results.get('time', 0)))
        
        # Create summary data with actual values
        summary_data = {
            'Analysis Summary': [
                'Overall Score',
                'Quality Rating (Stars)',
                'Status',
                'Image File',
                'Analysis Date',
                'Processing Time'
            ],
            'Value': [
                f"{overall_score:.3f}",
                f"{stars} out of 4 stars",
                status.upper(),
                os.path.basename(self.current_image_path) if self.current_image_path else 'N/A',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                f"{analysis_time:.2f} seconds" if isinstance(analysis_time, (int, float)) else str(analysis_time)
            ]
        }
        
        print(f"📊 Summary data being written: {summary_data}")  # Debug print
        
        # Convert to DataFrame
        summary_df = pd.DataFrame(summary_data)
        
        # Write to Excel
        summary_df.to_excel(writer, sheet_name='Executive Summary', index=False, startrow=2)
        
        # Get the worksheet
        worksheet = writer.sheets['Executive Summary']
        
        # Add title
        worksheet.merge_range('A1:B1', '🔍 IMAGE QUALITY ANALYSIS REPORT', title_format)
        
        # Format columns
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 30)
        
        # Format headers
        worksheet.write('A3', 'Analysis Summary', header_format)
        worksheet.write('B3', 'Value', header_format)
        
        # Add score visualization (text-based gauge)
        score = global_results.get('score', 0)
        gauge_text = self.create_text_gauge(score)
        worksheet.write('A10', 'Quality Gauge:', metric_header_format)
        worksheet.write('B10', gauge_text)
        
    def create_metrics_sheet(self, writer, workbook, results, header_format, metric_header_format, good_format, warning_format, poor_format, unknown_format):
        """Create detailed metrics sheet with conditional formatting"""
        import pandas as pd  # Import here for scope
        
        metrics_data = results.get('metrics', {})
        category_status = results.get('category_status', {})
        print(f"📊 Metrics data: {list(metrics_data.keys())}")  # Debug print
        print(f"📊 Category status: {category_status}")  # Debug print
        
        # Prepare metrics data for DataFrame
        metrics_rows = []
        for metric_name, metric_data in metrics_data.items():
            
            # Get status from category_status
            status_text = category_status.get(metric_name, 'unknown')
            
            # Use actual status values and appropriate scores
            if status_text == 'pass':
                score = 0.85  # Good passing score
                status = 'PASS'  # Use actual status
            elif status_text == 'warn':
                score = 0.70  # Warning score
                status = 'WARN'  # Use actual status
            elif status_text == 'fail':
                score = 0.30  # Failing score
                status = 'FAIL'  # Use actual status
            else:
                score = 0.50  # Default/unknown
                status = 'UNKNOWN'
            
            # Try to extract meaningful details from the complex metric data
            details = self.extract_metric_details(metric_name, metric_data)
            threshold = 'Varies by metric'
            
            # Create readable metric name
            readable_name = metric_name.replace('_', ' ').title()
            
            metrics_rows.append({
                'Metric': readable_name,
                'Score': f"{score:.3f}",
                'Percentage': f"{score:.1%}",
                'Status': status,
                'Threshold': threshold,
                'Details': details
            })
            
            print(f"📊 Added metric: {readable_name} = {score:.3f} ({status}) from category '{status_text}'")  # Debug print
        
        if not metrics_rows:
            # Add a placeholder if no metrics found
            metrics_rows.append({
                'Metric': 'No Metrics Available',
                'Score': '0.000',
                'Percentage': '0.0%',
                'Status': 'N/A',
                'Threshold': 'N/A',
                'Details': 'No detailed metrics were found in the analysis results'
            })
        
        print(f"📊 Total metrics rows: {len(metrics_rows)}")  # Debug print
        
        # Convert to DataFrame
        metrics_df = pd.DataFrame(metrics_rows)
        
        # Write to Excel (data starts at row 4, startrow=3 in pandas means Excel row 4)
        metrics_df.to_excel(writer, sheet_name='Detailed Metrics', index=False, startrow=3, header=False)
        
        # Get the worksheet
        worksheet = writer.sheets['Detailed Metrics']
        
        # Add title
        worksheet.merge_range('A1:F1', '📊 DETAILED QUALITY METRICS', header_format)
        
        # Write column headers manually at row 3 (Excel row 3, index 2)
        headers = ['Metric', 'Score', 'Percentage', 'Status', 'Threshold', 'Details']
        for col_num, header in enumerate(headers):
            worksheet.write(2, col_num, header, metric_header_format)  # Row 3 in Excel (index 2)
        
        # Format columns
        worksheet.set_column('A:A', 20)  # Metric
        worksheet.set_column('B:B', 12)  # Score
        worksheet.set_column('C:C', 15)  # Percentage
        worksheet.set_column('D:D', 15)  # Status
        worksheet.set_column('E:E', 15)  # Threshold
        worksheet.set_column('F:F', 40)  # Details
        
        # Apply conditional formatting based on status
        for row_num, row_data in enumerate(metrics_rows, start=4):  # Start from row 4 (data starts at row 4, 1-based)
            status = row_data['Status']
            if status == 'PASS':
                format_to_use = good_format
            elif status == 'WARN':
                format_to_use = warning_format
            elif status == 'FAIL':
                format_to_use = poor_format
            else:  # UNKNOWN or any other status - use white background
                format_to_use = unknown_format
            
            worksheet.write(f'D{row_num}', status, format_to_use)
            
    def create_recommendations_sheet(self, writer, workbook, results, header_format, metric_header_format):
        """Create recommendations sheet"""
        import pandas as pd  # Import here for scope
        
        global_results = results.get('global', {})
        actions = global_results.get('actions', global_results.get('recommendations', []))
        
        print(f"📊 Found {len(actions)} recommendations")  # Debug print
        
        # Categorize recommendations
        critical_actions = []
        warning_actions = []
        general_actions = []
        
        for action in actions:
            clean_action = str(action).replace('❌', '').replace('⚠️', '').strip()
            if '❌' in str(action) or 'critical' in clean_action.lower() or 'urgent' in clean_action.lower():
                critical_actions.append(clean_action)
            elif '⚠️' in str(action) or 'warning' in clean_action.lower() or 'improve' in clean_action.lower():
                warning_actions.append(clean_action)
            else:
                general_actions.append(clean_action)
        
        # Create recommendations data
        all_recommendations = []
        
        for action in critical_actions:
            all_recommendations.append({
                'Priority': 'CRITICAL',
                'Category': 'Immediate Action Required',
                'Recommendation': action
            })
            
        for action in warning_actions:
            all_recommendations.append({
                'Priority': 'WARNING',
                'Category': 'Improvement Suggested',
                'Recommendation': action
            })
            
        for action in general_actions:
            all_recommendations.append({
                'Priority': 'INFO',
                'Category': 'General Guidance',
                'Recommendation': action
            })
        
        # If no recommendations found, add default message
        if not all_recommendations:
            all_recommendations.append({
                'Priority': 'INFO',
                'Category': 'Status',
                'Recommendation': 'No specific recommendations found. Image quality appears to meet standards.'
            })
        
        print(f"📊 Created {len(all_recommendations)} recommendation rows")  # Debug print
        
        if all_recommendations:
            rec_df = pd.DataFrame(all_recommendations)
            rec_df.to_excel(writer, sheet_name='Recommendations', index=False, startrow=2)
            
            # Get the worksheet
            worksheet = writer.sheets['Recommendations']
            
            # Add title safely
            self.safe_merge_range(worksheet, 'A1:C1', '💡 QUALITY IMPROVEMENT RECOMMENDATIONS', header_format)
            
            # Format the column headers that pandas already created
            for col_num, column_title in enumerate(rec_df.columns):
                worksheet.write(2, col_num, column_title, metric_header_format)
            
            # Format columns
            worksheet.set_column('A:A', 15)  # Priority
            worksheet.set_column('B:B', 25)  # Category
            worksheet.set_column('C:C', 60)  # Recommendation
        
    def create_charts_sheet(self, writer, workbook, results, header_format):
        """Create charts and visual representations"""
        worksheet = workbook.add_worksheet('Visual Charts')
        
        # Add title
        worksheet.merge_range('A1:H1', '📈 VISUAL ANALYSIS CHARTS', header_format)
        
        # Create a simple metrics chart using Excel's chart feature
        metrics_data = results.get('metrics', {})
        
        print(f"📊 Creating charts with {len(metrics_data)} metrics")  # Debug print
        
        if metrics_data:
            # Prepare data for chart
            row = 3
            worksheet.write('A2', 'Metric', header_format)
            worksheet.write('B2', 'Score', header_format)
            
            chart_data = []
            category_status = results.get('category_status', {})
            
            for metric_name, metric_data in metrics_data.items():
                readable_name = metric_name.replace('_', ' ').title()
                
                # Use same scoring logic as metrics sheet
                status_text = category_status.get(metric_name, 'unknown')
                
                if status_text == 'pass':
                    score = 0.85
                elif status_text == 'warn':
                    score = 0.70
                elif status_text == 'fail':
                    score = 0.30
                else:
                    score = 0.50
                
                worksheet.write(row, 0, readable_name)
                worksheet.write(row, 1, score)
                chart_data.append((readable_name, score))
                row += 1
                print(f"📊 Chart data: {readable_name} = {score}")  # Debug print
            
            # Create a column chart
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'name': 'Quality Scores',
                'categories': f'=\'Visual Charts\'!$A$3:$A${row-1}',
                'values': f'=\'Visual Charts\'!$B$3:$B${row-1}',
                'fill': {'color': '#2c5aa0'},
            })
            
            chart.set_title({'name': 'Quality Metrics Overview'})
            chart.set_x_axis({'name': 'Quality Metrics'})
            chart.set_y_axis({'name': 'Score (0-1)', 'max': 1})
            chart.set_size({'width': 600, 'height': 400})
            
            worksheet.insert_chart('D3', chart)
            
            print(f"📊 Chart created with {len(chart_data)} data points")  # Debug print
        else:
            # No metrics data available
            worksheet.write('A3', 'No metrics data available for chart creation')
            print("📊 No metrics data available for charts")  # Debug print
    
    def get_status_from_score(self, score):
        """Convert numeric score to status text"""
        if score >= 0.8:
            return 'EXCELLENT'
        elif score >= 0.6:
            return 'GOOD'
        elif score >= 0.4:
            return 'FAIR'
        else:
            return 'POOR'
    
    def extract_metric_details(self, metric_name, metric_data):
        """Extract meaningful details from complex metric data structure"""
        if not isinstance(metric_data, dict):
            return str(metric_data)
        
        # Define key metrics to extract for each category
        detail_mappings = {
            'completeness': ['content_bbox_coverage', 'edge_touch_flag'],
            'foreign_objects': ['foreign_object_flag', 'foreign_object_area_pct'],
            'sharpness': ['laplacian_var', 'gradient_magnitude_mean'],
            'exposure': ['shadow_clip_pct', 'highlight_clip_pct'],
            'contrast': ['global_contrast', 'rms_contrast'],
            'color': ['hue_cast_degrees', 'gray_deltaE'],
            'geometry': ['skew_angle_deg', 'warp_index'],
            'border_background': ['bg_median_lum', 'left_margin_ratio'],
            'noise': ['bg_noise_std', 'blockiness_index'],
            'format_integrity': ['format_name', 'bit_depth'],
            'resolution': ['effective_dpi_x', 'effective_dpi_y']
        }
        
        key_metrics = detail_mappings.get(metric_name, [])
        details = []
        
        for key in key_metrics:
            if key in metric_data:
                value = metric_data[key]
                if isinstance(value, float):
                    details.append(f"{key}: {value:.3f}")
                else:
                    details.append(f"{key}: {value}")
        
        # If no specific keys found, try to extract first few meaningful values
        if not details:
            count = 0
            for key, value in metric_data.items():
                if count >= 2:  # Limit to 2 details
                    break
                if not key.startswith('_') and not isinstance(value, dict):
                    if isinstance(value, float):
                        details.append(f"{key}: {value:.3f}")
                    else:
                        details.append(f"{key}: {value}")
                    count += 1
        
        return "; ".join(details) if details else "Complex metric data"
    
    def clean_filename(self, filename):
        """Clean filename for safe file system use"""
        import re
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # Replace invalid chars
        filename = re.sub(r'[^\w\s\-_.]', '', filename)    # Keep only alphanumeric, spaces, hyphens, underscores, dots
        filename = re.sub(r'\s+', '_', filename)           # Replace spaces with underscores
        filename = re.sub(r'_+', '_', filename)            # Replace multiple underscores with single
        filename = filename.strip('_')                     # Remove leading/trailing underscores
        return filename
    
    def generate_excel_filename(self, output_dir):
        """Generate professional Excel filename with multiple naming strategies"""
        from datetime import datetime
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        short_timestamp = datetime.now().strftime("%m%d_%H%M")
        
        if not self.current_image_path:
            filename = f"ImageQuality_Analysis_{timestamp}.xlsx"
            return filename, os.path.join(output_dir, filename)
        
        # Get image and folder information
        image_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
        folder_name = os.path.basename(os.path.dirname(self.current_image_path))
        
        # Clean names for file system safety
        image_name = self.clean_filename(image_name)
        folder_name = self.clean_filename(folder_name)
        
        # Determine naming strategy
        generic_names = ['image', 'img', 'photo', 'picture', 'document', 'doc', 'scan', 
                        'untitled', 'new', 'temp', 'screenshot', 'capture']
        system_folders = ['desktop', 'downloads', 'documents', 'pictures', 'photos', 
                         'onedrive', 'dropbox', 'google drive', 'icloud']
        
        is_generic_image = any(generic in image_name.lower() for generic in generic_names)
        is_system_folder = folder_name.lower() in system_folders
        
        # Strategy 1: Use meaningful folder name if image name is generic
        if is_generic_image and not is_system_folder and folder_name:
            base_name = f"{folder_name}_Analysis"
        
        # Strategy 2: Use image name if it's descriptive (not too long/short)
        elif not is_generic_image and 5 <= len(image_name) <= 40:
            base_name = image_name
        
        # Strategy 3: Combine folder + short image name for very long names
        elif len(image_name) > 40 and not is_system_folder and folder_name:
            short_image = image_name[:20]
            base_name = f"{folder_name}_{short_image}"
        
        # Strategy 4: Use truncated image name
        elif len(image_name) > 40:
            base_name = image_name[:40]
        
        # Strategy 5: Default fallback
        else:
            if not is_system_folder and folder_name:
                base_name = f"{folder_name}_Analysis"
            else:
                base_name = "Quality_Analysis"
        
        # Create final filename with timestamp
        # For very long base names, use short timestamp
        if len(base_name) > 30:
            filename = f"{base_name}_{short_timestamp}.xlsx"
        else:
            filename = f"{base_name}_{timestamp}.xlsx"
        
        # Ensure filename isn't too long (Windows has 260 char limit)
        max_filename_length = 100  # Conservative limit
        if len(filename) > max_filename_length:
            base_truncated = base_name[:max_filename_length-20]  # Leave room for timestamp + extension
            filename = f"{base_truncated}_{short_timestamp}.xlsx"
        
        filepath = os.path.join(output_dir, filename)
        
        # Log the filename choice for user reference
        print(f"📊 Excel report: {filename}")
        print(f"📂 Source: {os.path.basename(self.current_image_path)} from {folder_name}/")
        
        return filename, filepath
    
    def create_text_gauge(self, score):
        """Create a text-based gauge visualization"""
        filled_blocks = int(score * 10)
        empty_blocks = 10 - filled_blocks
        gauge = '█' * filled_blocks + '░' * empty_blocks
        return f"{gauge} {score:.1%}"
    
    def install_and_retry_excel_export(self, results):
        """Install pandas and retry Excel export"""
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
            print("✅ Pandas installed, retrying Excel export...")
            self.auto_export_excel_with_visuals(results)
        except Exception as e:
            print(f"❌ Failed to install pandas: {e}")
            self.progress_var.set("Analysis complete (Excel export unavailable)")
    
    def open_excel_file(self, excel_filepath, output_dir):
        """Open the Excel file automatically"""
        try:
            import subprocess
            import platform
            
            # Show success notification
            messagebox.showinfo(
                "Excel Report Ready!",
                f"✅ Professional Excel report created!\n\n"
                f"📊 File: {os.path.basename(excel_filepath)}\n"
                f"📂 Location: {output_dir}\n\n"
                f"The report includes:\n"
                f"• Executive summary with scores\n"
                f"• Detailed metrics with color coding\n"
                f"• Actionable recommendations\n"
                f"• Visual charts and graphs\n\n"
                f"Opening Excel file now..."
            )
            
            # Open the Excel file
            if platform.system() == 'Windows':
                os.startfile(excel_filepath)
                # Also open the folder
                subprocess.run(['explorer', output_dir])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', excel_filepath])
                subprocess.run(['open', output_dir])
            else:  # Linux
                subprocess.run(['xdg-open', excel_filepath])
                subprocess.run(['xdg-open', output_dir])
            
            print(f"📊 Opened Excel report: {excel_filepath}")
            print(f"📂 Opened results folder: {output_dir}")
            
        except Exception as e:
            print(f"Error opening Excel file: {e}")
            messagebox.showinfo(
                "Report Created",
                f"✅ Excel report created successfully!\n\n"
                f"📂 Location: {output_dir}\n"
                f"📄 File: {os.path.basename(excel_filepath)}\n\n"
                f"Please open the file manually to view the report."
            )
    
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
    
    def update_recommendations_tab(self, results):
        """Update the recommendations tab with structured recommendations"""
        try:
            global_results = results['global']
            actions = global_results.get('actions', [])
            
            # Clear existing content
            self.priority_text.delete(1.0, tk.END)
            self.improvements_text.delete(1.0, tk.END)
            self.best_practices_text.delete(1.0, tk.END)
            
            # Categorize recommendations
            priority_actions = []
            improvement_suggestions = []
            
            for action in actions:
                clean_action = action.replace('\u274c', '❌').replace('\u26a0\ufe0f', '⚠️')
                if '❌' in clean_action:
                    priority_actions.append(clean_action)
                else:
                    improvement_suggestions.append(clean_action)
            
            # Priority Actions
            if priority_actions:
                priority_text = "CRITICAL ISSUES - IMMEDIATE ACTION REQUIRED:\n\n"
                for i, action in enumerate(priority_actions, 1):
                    priority_text += f"{i}. {action}\n\n"
            else:
                priority_text = "✅ No critical issues found!\n\nYour image quality meets the required standards."
            
            self.priority_text.insert(1.0, priority_text)
            
            # Improvement Suggestions
            if improvement_suggestions:
                improvements_text = "SUGGESTED IMPROVEMENTS:\n\n"
                for i, action in enumerate(improvement_suggestions, 1):
                    improvements_text += f"{i}. {action}\n\n"
            else:
                improvements_text = "✅ No specific improvements needed.\n\nYour image quality is excellent!"
            
            self.improvements_text.insert(1.0, improvements_text)
            
            # Best Practices
            best_practices_text = """DOCUMENT IMAGING BEST PRACTICES:

📸 CAPTURING:
• Use good lighting - avoid shadows and glare
• Keep the camera steady - use a tripod if possible
• Ensure the document is flat and fully visible
• Maintain consistent distance from the document

🖼️ QUALITY SETTINGS:
• Use at least 300 DPI for text documents
• Save in uncompressed format (TIFF/PNG) when possible
• Avoid heavy JPEG compression
• Capture in color even for black and white documents

📐 POSITIONING:
• Align document edges with image borders
• Include small margins around the document
• Avoid skewed or rotated captures
• Ensure all text is clearly legible

💡 POST-PROCESSING:
• Adjust exposure if too dark or too bright
• Correct any rotation or skew
• Crop to remove unnecessary background
• Enhance contrast if text is faint"""
            
            self.best_practices_text.insert(1.0, best_practices_text)
            
        except Exception as e:
            print(f"Error in update_recommendations_tab: {e}")
            # Fallback error display
            try:
                self.priority_text.delete(1.0, tk.END)
                self.priority_text.insert(1.0, f"Error loading recommendations: {e}")
            except:
                pass
    
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
    style.configure('Accent.TButton', foreground='#2c3e50', background='#0078d4')
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

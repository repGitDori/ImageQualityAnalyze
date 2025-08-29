#!/usr/bin/env python3
"""
Professional Tabbed Image Quality Analyzer
A clean 3-tab interface: Upload → Config → Analysis
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
from pathlib import Path
from PIL import Image, ImageTk

# Add the current directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from image_quality_analyzer import ImageQualityAnalyzer
    from image_quality_analyzer.config import load_default_config, load_profile, list_profiles
except ImportError as e:
    print(f"Error importing ImageQualityAnalyzer: {e}")
    print("Please ensure all dependencies are installed.")
    sys.exit(1)


class TabbedImageQualityAnalyzer:
    """Professional 3-tab image quality analyzer"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Image Quality Analyzer")
        self.root.geometry("1000x750")
        self.root.configure(bg='#f8f9fa')
        
        # Initialize variables
        self.current_image_path = None
        self.current_image_preview = None
        self.selected_config = None
        self.analysis_results = None
        self.analyzer = ImageQualityAnalyzer()
        
        # Configure styles
        self.setup_styles()
        
        # Create main interface
        self.create_interface()
    
    def setup_styles(self):
        """Setup professional styling with dark text only"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors - ALL TEXT IS DARK
        bg_color = '#f8f9fa'
        card_bg = 'white'
        text_dark = '#1a1a1a'
        text_medium = '#2c3e50'
        text_light = '#34495e'
        primary_blue = '#2c3e50'
        success_green = '#27ae60'
        
        # Main title - DARK TEXT
        style.configure('MainTitle.TLabel',
                       font=('Segoe UI', 20, 'bold'),
                       foreground=text_dark,
                       background=bg_color)
        
        # Tab titles - DARK TEXT
        style.configure('TabTitle.TLabel',
                       font=('Segoe UI', 14, 'bold'),
                       foreground=text_medium,
                       background=card_bg)
        
        # Subtitles - DARK TEXT
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 11),
                       foreground=text_light,
                       background=card_bg)
        
        # Info text - DARK TEXT
        style.configure('Info.TLabel',
                       font=('Segoe UI', 10),
                       foreground=text_medium,
                       background=card_bg)
        
        # Status text - DARK TEXT
        style.configure('Status.TLabel',
                       font=('Segoe UI', 10, 'bold'),
                       foreground=text_dark,
                       background=card_bg)
        
        # Primary buttons - White text on dark background
        style.configure('Primary.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       foreground='white',
                       background=primary_blue,
                       focuscolor='none',
                       padding=(20, 12))
        style.map('Primary.TButton',
                 background=[('active', '#34495e')])
        
        # Secondary buttons - Dark text on light background
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10),
                       foreground=text_medium,
                       background='#ecf0f1',
                       focuscolor='none',
                       padding=(15, 8))
        style.map('Secondary.TButton',
                 background=[('active', '#d5dbdb')])
        
        # Success buttons - White text on green background
        style.configure('Success.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       foreground='white',
                       background=success_green,
                       focuscolor='none',
                       padding=(20, 12))
        style.map('Success.TButton',
                 background=[('active', '#2ecc71')])
        
        # Card frames
        style.configure('Card.TFrame',
                       background=card_bg,
                       relief='solid',
                       borderwidth=1)
        
        # Configure notebook tabs
        style.configure('TNotebook.Tab',
                       padding=[20, 12],
                       font=('Segoe UI', 11, 'bold'))
        
        # Progress bar
        style.configure('Custom.Horizontal.TProgressbar',
                       background='#3498db',
                       troughcolor='#ecf0f1')
    
    def create_interface(self):
        """Create the main tabbed interface"""
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title section (left side)
        title_section = ttk.Frame(header_frame)
        title_section.pack(side='left', fill='x', expand=True)
        
        title_label = ttk.Label(
            title_section,
            text="🔍 Professional Image Quality Analyzer",
            style='MainTitle.TLabel'
        )
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(
            title_section,
            text="🛡️ Secure • Offline • Professional Analysis",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Help button section (right side)
        help_section = ttk.Frame(header_frame)
        help_section.pack(side='right')
        
        self.help_button = ttk.Button(
            help_section,
            text="❓",
            command=self.show_help,
            width=3
        )
        self.help_button.pack()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_upload_tab()
        self.create_config_tab()
        self.create_analysis_tab()
        
        # Bind tab change events
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def create_upload_tab(self):
        """Create the Upload tab"""
        # Create tab frame
        upload_frame = ttk.Frame(self.notebook)
        self.notebook.add(upload_frame, text='📁 Upload Image')
        
        # Main content with padding
        content_frame = ttk.Frame(upload_frame, style='Card.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Inner content with padding
        inner_frame = ttk.Frame(content_frame)
        inner_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Tab title
        title_label = ttk.Label(
            inner_frame,
            text="Select Your Image",
            style='TabTitle.TLabel'
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            inner_frame,
            text="Choose the document image you want to analyze for quality assessment",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # File selection section
        file_section = ttk.Frame(inner_frame)
        file_section.pack(fill='both', expand=True)
        
        # Browse button
        browse_frame = ttk.Frame(file_section)
        browse_frame.pack(pady=(0, 20))
        
        self.browse_button = ttk.Button(
            browse_frame,
            text="📁 Browse for Image File",
            style='Primary.TButton',
            command=self.browse_image
        )
        self.browse_button.pack()
        
        # File info display
        self.file_info_frame = ttk.Frame(file_section, style='Card.TFrame')
        self.file_info_frame.pack(fill='x', pady=10)
        
        self.file_status_label = ttk.Label(
            self.file_info_frame,
            text="No image selected",
            style='Info.TLabel'
        )
        self.file_status_label.pack(pady=20)
        
        # Image preview area
        preview_frame = ttk.LabelFrame(file_section, text="Image Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        self.preview_label = ttk.Label(
            preview_frame,
            text="Image preview will appear here",
            style='Info.TLabel'
        )
        self.preview_label.pack(expand=True)
        
        # Supported formats info
        formats_label = ttk.Label(
            inner_frame,
            text="Supported formats: JPEG, PNG, TIFF, BMP",
            style='Info.TLabel'
        )
        formats_label.pack(side='bottom', pady=(20, 0))
    
    def create_config_tab(self):
        """Create the Configuration tab"""
        # Create tab frame
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text='⚙️ Configuration')
        
        # Main content with padding
        content_frame = ttk.Frame(config_frame, style='Card.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Inner content with padding
        inner_frame = ttk.Frame(content_frame)
        inner_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Tab title
        title_label = ttk.Label(
            inner_frame,
            text="Configure Quality Standards",
            style='TabTitle.TLabel'
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            inner_frame,
            text="Set the quality standards and analysis options for your image assessment",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Quality Standards Section
        standards_section = ttk.LabelFrame(inner_frame, text="Quality Standards", padding=20)
        standards_section.pack(fill='x', pady=(0, 20))
        
        self.standards_var = tk.StringVar(value="default")
        
        # Default standards radio
        default_frame = ttk.Frame(standards_section)
        default_frame.pack(fill='x', pady=5)
        
        default_radio = ttk.Radiobutton(
            default_frame,
            text="Default Standards",
            variable=self.standards_var,
            value="default"
        )
        default_radio.pack(anchor='w')
        
        default_desc = ttk.Label(
            default_frame,
            text="Standard quality requirements suitable for most document types",
            style='Info.TLabel'
        )
        default_desc.pack(anchor='w', padx=(25, 0), pady=(2, 0))
        
        # Professional standards radio
        professional_frame = ttk.Frame(standards_section)
        professional_frame.pack(fill='x', pady=10)
        
        professional_radio = ttk.Radiobutton(
            professional_frame,
            text="Professional Standards",
            variable=self.standards_var,
            value="professional"
        )
        professional_radio.pack(anchor='w')
        
        professional_desc = ttk.Label(
            professional_frame,
            text="Higher quality requirements for professional document processing",
            style='Info.TLabel'
        )
        professional_desc.pack(anchor='w', padx=(25, 0), pady=(2, 0))
        
        # Custom standards radio
        custom_frame = ttk.Frame(standards_section)
        custom_frame.pack(fill='x', pady=5)
        
        custom_radio = ttk.Radiobutton(
            custom_frame,
            text="Custom Standards",
            variable=self.standards_var,
            value="custom"
        )
        custom_radio.pack(anchor='w')
        
        custom_desc = ttk.Label(
            custom_frame,
            text="Define your own quality standards",
            style='Info.TLabel'
        )
        custom_desc.pack(anchor='w', padx=(25, 0), pady=(2, 0))
        
        # Analysis Options Section
        options_section = ttk.LabelFrame(inner_frame, text="Analysis Options", padding=20)
        options_section.pack(fill='x', pady=(0, 20))
        
        # Visualizations checkbox
        self.viz_var = tk.BooleanVar(value=True)
        viz_check = ttk.Checkbutton(
            options_section,
            text="Generate Visualization Charts",
            variable=self.viz_var
        )
        viz_check.pack(anchor='w', pady=5)
        
        viz_desc = ttk.Label(
            options_section,
            text="Create visual charts and graphs showing quality metrics",
            style='Info.TLabel'
        )
        viz_desc.pack(anchor='w', padx=(25, 0), pady=(0, 10))
        
        # Detailed report checkbox
        self.detailed_var = tk.BooleanVar(value=True)
        detailed_check = ttk.Checkbutton(
            options_section,
            text="Generate Detailed Report",
            variable=self.detailed_var
        )
        detailed_check.pack(anchor='w', pady=5)
        
        detailed_desc = ttk.Label(
            options_section,
            text="Include comprehensive analysis with actionable recommendations",
            style='Info.TLabel'
        )
        detailed_desc.pack(anchor='w', padx=(25, 0), pady=(0, 10))
        
        # Export Options Section
        export_section = ttk.LabelFrame(inner_frame, text="Export Options", padding=20)
        export_section.pack(fill='x')
        
        self.export_json_var = tk.BooleanVar(value=True)
        json_check = ttk.Checkbutton(
            export_section,
            text="Export as JSON",
            variable=self.export_json_var
        )
        json_check.pack(anchor='w', pady=5)
        
        self.export_summary_var = tk.BooleanVar(value=True)
        summary_check = ttk.Checkbutton(
            export_section,
            text="Export Summary Report",
            variable=self.export_summary_var
        )
        summary_check.pack(anchor='w', pady=5)
    
    def create_analysis_tab(self):
        """Create the Analysis tab"""
        # Create tab frame
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text='📊 Analysis')
        
        # Main content with padding
        content_frame = ttk.Frame(analysis_frame, style='Card.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Inner content with padding
        inner_frame = ttk.Frame(content_frame)
        inner_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Tab title
        title_label = ttk.Label(
            inner_frame,
            text="Image Quality Analysis",
            style='TabTitle.TLabel'
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            inner_frame,
            text="Run the analysis and view detailed quality assessment results",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Status section
        status_section = ttk.Frame(inner_frame, style='Card.TFrame')
        status_section.pack(fill='x', pady=(0, 20))
        
        # Analysis status
        self.status_label = ttk.Label(
            status_section,
            text="Ready to analyze",
            style='Status.TLabel'
        )
        self.status_label.pack(pady=20)
        
        # Start Analysis button
        self.analyze_button = ttk.Button(
            inner_frame,
            text="🔍 Start Analysis",
            style='Success.TButton',
            command=self.start_analysis
        )
        self.analyze_button.pack(pady=(0, 20))
        
        # Progress bar
        self.progress_var = tk.StringVar(value="")
        self.progress_bar = ttk.Progressbar(
            inner_frame,
            style='Custom.Horizontal.TProgressbar',
            length=400,
            mode='indeterminate'
        )
        
        self.progress_text = ttk.Label(
            inner_frame,
            textvariable=self.progress_var,
            style='Info.TLabel'
        )
        
        # Results area
        self.results_frame = ttk.LabelFrame(inner_frame, text="Analysis Results", padding=20)
        self.results_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Results content (initially empty)
        self.results_content = ttk.Frame(self.results_frame)
        self.results_content.pack(fill='both', expand=True)
        
        # Placeholder
        self.results_placeholder = ttk.Label(
            self.results_content,
            text="Analysis results will appear here after processing",
            style='Info.TLabel'
        )
        self.results_placeholder.pack(expand=True)
        
        # Export buttons (initially hidden)
        self.export_frame = ttk.Frame(inner_frame)
        
        self.export_json_button = ttk.Button(
            self.export_frame,
            text="💾 Export JSON",
            style='Secondary.TButton',
            command=self.export_json_results
        )
        self.export_json_button.pack(side='left', padx=(0, 10))
        
        self.view_details_button = ttk.Button(
            self.export_frame,
            text="📋 View Details",
            style='Primary.TButton',
            command=self.view_detailed_results
        )
        self.view_details_button.pack(side='left')
    
    def browse_image(self):
        """Browse for image file"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("TIFF files", "*.tiff *.tif"),
            ("BMP files", "*.bmp"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Image File for Analysis",
            filetypes=file_types
        )
        
        if file_path:
            self.current_image_path = file_path
            self.load_image_preview(file_path)
            self.update_file_status(file_path)
    
    def load_image_preview(self, file_path):
        """Load and display image preview"""
        try:
            # Load image
            pil_image = Image.open(file_path)
            
            # Calculate preview size (maintain aspect ratio)
            max_size = (300, 300)
            pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.current_image_preview = ImageTk.PhotoImage(pil_image)
            
            # Update preview label
            self.preview_label.configure(image=self.current_image_preview, text="")
            
        except Exception as e:
            self.preview_label.configure(image="", text=f"Error loading preview: {e}")
            print(f"Preview error: {e}")
    
    def update_file_status(self, file_path):
        """Update file status display"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        
        try:
            # Get image dimensions
            with Image.open(file_path) as img:
                width, height = img.size
            
            status_text = f"✅ {filename}\n📊 Size: {file_size:.2f} MB • Dimensions: {width}×{height}px"
        except:
            status_text = f"✅ {filename}\n📊 Size: {file_size:.2f} MB"
        
        self.file_status_label.config(text=status_text)
    
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
            help_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'help_guide.txt')
            if os.path.exists(help_file_path):
                with open(help_file_path, 'r', encoding='utf-8') as f:
                    help_content = f.read()
            else:
                help_content = """# 🔍 Professional Image Quality Analyzer - Help

## 🚀 Quick Start Guide

### Tab 1: Upload
1. **📁 Select Image** - Click "Browse Files" to choose your document image
2. **👁️ Preview** - View your selected image before analysis

### Tab 2: Config  
1. **⚙️ Choose Standards** - Select quality standards from dropdown
2. **🎯 Set Options** - Enable visualizations and detailed reports

### Tab 3: Analysis
1. **🚀 Analyze** - Click "Analyze Quality" to start analysis
2. **📋 Results** - View comprehensive analysis results
3. **📋 Export** - Save results as JSON reports

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
1. Upload Tab: Select an image file using the Browse button
2. Config Tab: Choose your quality standards and options
3. Analysis Tab: Click Analyze Quality to start analysis and view results

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
            command=help_window.destroy
        )
        close_button.pack(side="right")
        
        # Focus the help window
        help_window.focus_set()

    def on_tab_changed(self, event):
        """Handle tab change events"""
        selected_tab = self.notebook.select()
        tab_index = self.notebook.index(selected_tab)
        
        # Validate prerequisites for each tab
        if tab_index == 1:  # Config tab
            if not self.current_image_path:
                messagebox.showwarning(
                    "Image Required",
                    "Please select an image file in the Upload tab first."
                )
                self.notebook.select(0)  # Switch back to upload tab
        elif tab_index == 2:  # Analysis tab
            if not self.current_image_path:
                messagebox.showwarning(
                    "Image Required",
                    "Please select an image file in the Upload tab first."
                )
                self.notebook.select(0)  # Switch back to upload tab
    
    def start_analysis(self):
        """Start the image analysis process"""
        if not self.current_image_path:
            messagebox.showerror("Error", "Please select an image file first.")
            return
        
        # Update UI
        self.analyze_button.config(state='disabled')
        self.status_label.config(text="⏳ Analyzing image...")
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()
        self.progress_text.pack()
        self.progress_var.set("Initializing analysis engine...")
        
        # Start analysis in background thread
        analysis_thread = threading.Thread(target=self.run_analysis, daemon=True)
        analysis_thread.start()
    
    def run_analysis(self):
        """Run the actual analysis"""
        try:
            # Update progress
            self.root.after(0, lambda: self.progress_var.set("Loading quality standards..."))
            
            # Load configuration based on selection
            standards = self.standards_var.get()
            if standards == "professional":
                # Create professional config (stricter standards)
                config = load_default_config()
                # Make standards more strict
                for metric in config.get('metrics', {}):
                    if 'thresholds' in config['metrics'][metric]:
                        thresholds = config['metrics'][metric]['thresholds']
                        if 'min_acceptable' in thresholds:
                            thresholds['min_acceptable'] *= 1.2  # 20% stricter
            elif standards == "custom":
                # For now, use default (custom editor would go here)
                config = load_default_config()
            else:
                config = load_default_config()
            
            # Update progress
            self.root.after(0, lambda: self.progress_var.set("Analyzing image quality..."))
            
            # Run analysis
            results = self.analyzer.analyze_image(self.current_image_path, config)
            self.analysis_results = results
            
            # Update progress
            self.root.after(0, lambda: self.progress_var.set("Preparing results..."))
            
            # Update UI with results
            self.root.after(0, self.display_analysis_results)
            
        except Exception as e:
            self.root.after(0, lambda: self.analysis_error(str(e)))
    
    def display_analysis_results(self):
        """Display analysis results in the UI"""
        # Stop progress
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_text.pack_forget()
        
        # Update status
        self.status_label.config(text="✅ Analysis completed successfully!")
        
        # Enable analyze button
        self.analyze_button.config(state='normal')
        
        # Clear results area
        for widget in self.results_content.winfo_children():
            widget.destroy()
        
        # Display results summary
        if self.analysis_results:
            global_results = self.analysis_results.get('global', {})
            overall_score = global_results.get('overall_score', 0)
            
            # Overall score
            score_frame = ttk.Frame(self.results_content)
            score_frame.pack(fill='x', pady=(0, 20))
            
            score_label = ttk.Label(
                score_frame,
                text=f"Overall Quality Score: {overall_score:.1%}",
                style='TabTitle.TLabel'
            )
            score_label.pack()
            
            # Quality status
            if overall_score >= 0.8:
                status_text = "🟢 EXCELLENT - Image quality exceeds standards"
                status_color = '#27ae60'
            elif overall_score >= 0.6:
                status_text = "🟡 GOOD - Image quality meets basic standards"
                status_color = '#f39c12'
            else:
                status_text = "🔴 NEEDS IMPROVEMENT - Image quality below standards"
                status_color = '#e74c3c'
            
            status_label = ttk.Label(
                score_frame,
                text=status_text,
                style='Info.TLabel'
            )
            status_label.pack(pady=(5, 0))
            
            # Key metrics summary
            metrics_frame = ttk.LabelFrame(self.results_content, text="Key Metrics", padding=15)
            metrics_frame.pack(fill='x', pady=(0, 20))
            
            # Show top metrics
            metrics_data = self.analysis_results.get('metrics', {})
            key_metrics = ['sharpness', 'exposure', 'contrast', 'geometry']
            
            for metric in key_metrics:
                if metric in metrics_data:
                    metric_data = metrics_data[metric]
                    score = metric_data.get('score', 0)
                    
                    metric_frame = ttk.Frame(metrics_frame)
                    metric_frame.pack(fill='x', pady=2)
                    
                    metric_label = ttk.Label(
                        metric_frame,
                        text=f"{metric.title()}:",
                        style='Info.TLabel'
                    )
                    metric_label.pack(side='left')
                    
                    score_label = ttk.Label(
                        metric_frame,
                        text=f"{score:.1%}",
                        style='Info.TLabel'
                    )
                    score_label.pack(side='right')
            
            # Recommendations
            actions = global_results.get('actions', [])
            if actions:
                rec_frame = ttk.LabelFrame(self.results_content, text="Top Recommendations", padding=15)
                rec_frame.pack(fill='x', pady=(0, 20))
                
                for i, action in enumerate(actions[:3], 1):  # Show top 3
                    action_clean = action.replace('❌', '•').replace('⚠️', '•')
                    action_label = ttk.Label(
                        rec_frame,
                        text=f"{i}. {action_clean}",
                        style='Info.TLabel',
                        wraplength=600
                    )
                    action_label.pack(anchor='w', pady=2)
        
        # Show export buttons
        self.export_frame.pack(pady=(20, 0))
    
    def analysis_error(self, error_message):
        """Handle analysis error"""
        # Stop progress
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_text.pack_forget()
        
        # Update status
        self.status_label.config(text="❌ Analysis failed")
        
        # Enable analyze button
        self.analyze_button.config(state='normal')
        
        # Show error
        messagebox.showerror("Analysis Error", f"Failed to analyze image:\n\n{error_message}")
    
    def export_json_results(self):
        """Export results as JSON"""
        if not self.analysis_results:
            messagebox.showwarning("No Results", "No analysis results to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Analysis Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.analysis_results, f, indent=2, default=str)
                messagebox.showinfo("Export Complete", f"Results exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
    
    def view_detailed_results(self):
        """View detailed results in a new window"""
        if not self.analysis_results:
            return
        
        # Create detailed results window
        details_window = tk.Toplevel(self.root)
        details_window.title("Detailed Analysis Results")
        details_window.geometry("800x600")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(details_window)
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Insert results
        formatted_results = json.dumps(self.analysis_results, indent=2, default=str)
        text_widget.insert('1.0', formatted_results)
        text_widget.config(state='disabled')


def main():
    """Main application entry point"""
    print("🚀 Starting Professional Tabbed Image Quality Analyzer...")
    print("📁 Upload → ⚙️ Configure → 📊 Analyze")
    print("🔒 Secure • Offline • Professional")
    
    root = tk.Tk()
    app = TabbedImageQualityAnalyzer(root)
    
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

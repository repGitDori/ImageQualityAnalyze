#!/usr/bin/env python3
"""
Professional Multi-Step Image Quality Analyzer
A wizard-style interface that guides users through the analysis process step by step.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
from pathlib import Path

# Add the current directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from image_quality_analyzer import ImageQualityAnalyzer
    from image_quality_analyzer.config import load_default_config, load_profile, list_profiles
except ImportError as e:
    print(f"Error importing ImageQualityAnalyzer: {e}")
    print("Please ensure all dependencies are installed.")
    sys.exit(1)


class ImageQualityWizard:
    """Multi-step wizard for image quality analysis"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Image Quality Analyzer - Wizard")
        self.root.geometry("900x700")
        self.root.configure(bg='#f8f9fa')
        
        # Initialize variables
        self.current_step = 0
        self.total_steps = 5
        self.current_image_path = None
        self.selected_profile = None
        self.custom_config = None
        self.analysis_results = None
        self.analyzer = ImageQualityAnalyzer()
        
        # Configure styles
        self.setup_styles()
        
        # Create main interface
        self.create_wizard_interface()
        
        # Show first step
        self.show_step(0)
    
    def setup_styles(self):
        """Setup professional styling with dark text"""
        style = ttk.Style()
        
        # Configure main theme
        style.theme_use('clam')
        
        # Title styles - DARK TEXT ONLY
        style.configure('WizardTitle.TLabel',
                       font=('Segoe UI', 24, 'bold'),
                       foreground='#1a1a1a',  # Dark text
                       background='#f8f9fa')
        
        style.configure('StepTitle.TLabel',
                       font=('Segoe UI', 16, 'bold'),
                       foreground='#2c3e50',  # Dark blue-gray
                       background='#f8f9fa')
        
        style.configure('StepSubtitle.TLabel',
                       font=('Segoe UI', 11),
                       foreground='#34495e',  # Medium dark gray
                       background='#f8f9fa')
        
        style.configure('Info.TLabel',
                       font=('Segoe UI', 10),
                       foreground='#2c3e50',  # Dark text
                       background='#f8f9fa')
        
        # Button styles - Dark text on light backgrounds or white text on dark backgrounds
        style.configure('Primary.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       foreground='white',
                       background='#2c3e50',
                       focuscolor='none',
                       padding=(20, 12))
        style.map('Primary.TButton',
                 background=[('active', '#34495e')])
        
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10),
                       foreground='#2c3e50',  # Dark text
                       background='#ecf0f1',
                       focuscolor='none',
                       padding=(15, 8))
        style.map('Secondary.TButton',
                 background=[('active', '#d5dbdb')])
        
        style.configure('Success.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       foreground='white',
                       background='#27ae60',
                       focuscolor='none',
                       padding=(20, 12))
        style.map('Success.TButton',
                 background=[('active', '#2ecc71')])
        
        # Frame styles
        style.configure('Card.TFrame',
                       background='white',
                       relief='solid',
                       borderwidth=1)
        
        # Progress bar
        style.configure('Wizard.Horizontal.TProgressbar',
                       background='#3498db',
                       troughcolor='#ecf0f1',
                       borderwidth=0,
                       lightcolor='#3498db',
                       darkcolor='#3498db')
    
    def create_wizard_interface(self):
        """Create the main wizard interface"""
        
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header with progress
        self.create_header()
        
        # Content area
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Navigation buttons
        self.create_navigation()
        
        # Create all step frames
        self.create_step_frames()
    
    def create_header(self):
        """Create header with title and progress bar"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="🔍 Image Quality Analysis Wizard",
            style='WizardTitle.TLabel'
        )
        title_label.pack(pady=(0, 15))
        
        # Progress section
        progress_frame = ttk.Frame(header_frame)
        progress_frame.pack(fill='x')
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            style='Wizard.Horizontal.TProgressbar',
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Step indicator
        self.step_label = ttk.Label(
            progress_frame,
            text="Step 1 of 5: Select Image",
            style='Info.TLabel'
        )
        self.step_label.pack()
    
    def create_navigation(self):
        """Create navigation buttons"""
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(fill='x', pady=(20, 0))
        
        # Previous button
        self.prev_button = ttk.Button(
            nav_frame,
            text="← Previous",
            style='Secondary.TButton',
            command=self.previous_step,
            state='disabled'
        )
        self.prev_button.pack(side='left')
        
        # Next button
        self.next_button = ttk.Button(
            nav_frame,
            text="Next →",
            style='Primary.TButton',
            command=self.next_step
        )
        self.next_button.pack(side='right')
        
        # Cancel button
        self.cancel_button = ttk.Button(
            nav_frame,
            text="Cancel",
            style='Secondary.TButton',
            command=self.cancel_wizard
        )
        self.cancel_button.pack(side='right', padx=(0, 10))
    
    def create_step_frames(self):
        """Create all step frames"""
        self.step_frames = []
        
        # Step 1: Select Image
        self.step_frames.append(self.create_step1_frame())
        
        # Step 2: Choose Quality Standards
        self.step_frames.append(self.create_step2_frame())
        
        # Step 3: Configure Analysis Options
        self.step_frames.append(self.create_step3_frame())
        
        # Step 4: Run Analysis
        self.step_frames.append(self.create_step4_frame())
        
        # Step 5: View Results
        self.step_frames.append(self.create_step5_frame())
    
    def create_step1_frame(self):
        """Step 1: Select Image File"""
        frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Padding frame
        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Step title
        title = ttk.Label(
            content,
            text="Step 1: Select Your Image",
            style='StepTitle.TLabel'
        )
        title.pack(pady=(0, 10))
        
        # Subtitle
        subtitle = ttk.Label(
            content,
            text="Choose the document image you want to analyze for quality assessment",
            style='StepSubtitle.TLabel'
        )
        subtitle.pack(pady=(0, 30))
        
        # File selection area
        file_frame = ttk.Frame(content)
        file_frame.pack(fill='x', pady=20)
        
        # Current file display
        self.file_display_frame = ttk.Frame(file_frame, style='Card.TFrame')
        self.file_display_frame.pack(fill='x', pady=(0, 20))
        
        self.file_info_label = ttk.Label(
            self.file_display_frame,
            text="No file selected",
            style='Info.TLabel'
        )
        self.file_info_label.pack(pady=20)
        
        # Browse button
        browse_button = ttk.Button(
            file_frame,
            text="📁 Browse for Image File",
            style='Primary.TButton',
            command=self.browse_image_file
        )
        browse_button.pack(pady=10)
        
        # Supported formats info
        formats_label = ttk.Label(
            content,
            text="Supported formats: JPEG, PNG, TIFF, BMP",
            style='Info.TLabel'
        )
        formats_label.pack(pady=(30, 0))
        
        return frame
    
    def create_step2_frame(self):
        """Step 2: Choose Quality Standards"""
        frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Padding frame
        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Step title
        title = ttk.Label(
            content,
            text="Step 2: Select Quality Standards",
            style='StepTitle.TLabel'
        )
        title.pack(pady=(0, 10))
        
        # Subtitle
        subtitle = ttk.Label(
            content,
            text="Choose the quality standards that match your requirements",
            style='StepSubtitle.TLabel'
        )
        subtitle.pack(pady=(0, 30))
        
        # Standards selection
        self.standards_var = tk.StringVar(value="default")
        
        # Default standards
        default_frame = ttk.Frame(content, style='Card.TFrame')
        default_frame.pack(fill='x', pady=10)
        
        default_radio = ttk.Radiobutton(
            default_frame,
            text="Default Standards",
            variable=self.standards_var,
            value="default"
        )
        default_radio.pack(anchor='w', padx=20, pady=(15, 5))
        
        default_desc = ttk.Label(
            default_frame,
            text="Standard quality requirements suitable for most document types",
            style='Info.TLabel'
        )
        default_desc.pack(anchor='w', padx=40, pady=(0, 15))
        
        # Custom standards
        custom_frame = ttk.Frame(content, style='Card.TFrame')
        custom_frame.pack(fill='x', pady=10)
        
        custom_radio = ttk.Radiobutton(
            custom_frame,
            text="Custom Standards",
            variable=self.standards_var,
            value="custom"
        )
        custom_radio.pack(anchor='w', padx=20, pady=(15, 5))
        
        custom_desc = ttk.Label(
            custom_frame,
            text="Create your own quality standards tailored to your specific needs",
            style='Info.TLabel'
        )
        custom_desc.pack(anchor='w', padx=40, pady=(0, 10))
        
        custom_button = ttk.Button(
            custom_frame,
            text="⚙️ Configure Custom Standards",
            style='Secondary.TButton',
            command=self.configure_custom_standards
        )
        custom_button.pack(anchor='w', padx=40, pady=(0, 15))
        
        return frame
    
    def create_step3_frame(self):
        """Step 3: Configure Analysis Options"""
        frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Padding frame
        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Step title
        title = ttk.Label(
            content,
            text="Step 3: Analysis Options",
            style='StepTitle.TLabel'
        )
        title.pack(pady=(0, 10))
        
        # Subtitle
        subtitle = ttk.Label(
            content,
            text="Configure what type of analysis and output you want",
            style='StepSubtitle.TLabel'
        )
        subtitle.pack(pady=(0, 30))
        
        # Analysis options
        options_frame = ttk.Frame(content)
        options_frame.pack(fill='both', expand=True)
        
        # Generate visualizations
        self.viz_var = tk.BooleanVar(value=True)
        viz_check = ttk.Checkbutton(
            options_frame,
            text="Generate Visual Analysis Charts",
            variable=self.viz_var
        )
        viz_check.pack(anchor='w', pady=10)
        
        viz_desc = ttk.Label(
            options_frame,
            text="Creates graphs and charts to visualize quality metrics",
            style='Info.TLabel'
        )
        viz_desc.pack(anchor='w', padx=25, pady=(0, 20))
        
        # Detailed report
        self.detailed_var = tk.BooleanVar(value=True)
        detailed_check = ttk.Checkbutton(
            options_frame,
            text="Generate Detailed Report",
            variable=self.detailed_var
        )
        detailed_check.pack(anchor='w', pady=10)
        
        detailed_desc = ttk.Label(
            options_frame,
            text="Includes comprehensive analysis with recommendations",
            style='Info.TLabel'
        )
        detailed_desc.pack(anchor='w', padx=25, pady=(0, 20))
        
        # Export options
        export_frame = ttk.LabelFrame(options_frame, text="Export Options", padding=20)
        export_frame.pack(fill='x', pady=20)
        
        self.export_json_var = tk.BooleanVar(value=True)
        json_check = ttk.Checkbutton(
            export_frame,
            text="Export as JSON",
            variable=self.export_json_var
        )
        json_check.pack(anchor='w', pady=5)
        
        self.export_pdf_var = tk.BooleanVar(value=False)
        pdf_check = ttk.Checkbutton(
            export_frame,
            text="Export as PDF Report (Coming Soon)",
            variable=self.export_pdf_var,
            state='disabled'
        )
        pdf_check.pack(anchor='w', pady=5)
        
        return frame
    
    def create_step4_frame(self):
        """Step 4: Run Analysis"""
        frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Padding frame
        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Step title
        title = ttk.Label(
            content,
            text="Step 4: Running Analysis",
            style='StepTitle.TLabel'
        )
        title.pack(pady=(0, 10))
        
        # Subtitle
        subtitle = ttk.Label(
            content,
            text="Please wait while we analyze your image quality",
            style='StepSubtitle.TLabel'
        )
        subtitle.pack(pady=(0, 30))
        
        # Analysis progress
        self.analysis_progress_frame = ttk.Frame(content)
        self.analysis_progress_frame.pack(fill='both', expand=True)
        
        # Progress bar for analysis
        self.analysis_progress = ttk.Progressbar(
            self.analysis_progress_frame,
            style='Wizard.Horizontal.TProgressbar',
            length=500,
            mode='indeterminate'
        )
        self.analysis_progress.pack(pady=20)
        
        # Status label
        self.analysis_status = ttk.Label(
            self.analysis_progress_frame,
            text="Preparing to analyze...",
            style='Info.TLabel'
        )
        self.analysis_status.pack(pady=10)
        
        # Analysis details
        details_frame = ttk.Frame(content, style='Card.TFrame')
        details_frame.pack(fill='x', pady=30)
        
        details_title = ttk.Label(
            details_frame,
            text="🔍 What we're analyzing:",
            style='StepSubtitle.TLabel'
        )
        details_title.pack(pady=(20, 10))
        
        analysis_points = [
            "• Image sharpness and focus quality",
            "• Exposure and lighting conditions", 
            "• Document orientation and geometry",
            "• Color balance and contrast levels",
            "• Noise levels and image artifacts",
            "• Overall document completeness"
        ]
        
        for point in analysis_points:
            point_label = ttk.Label(
                details_frame,
                text=point,
                style='Info.TLabel'
            )
            point_label.pack(anchor='w', padx=30, pady=2)
        
        # Bottom padding
        ttk.Label(details_frame, text="").pack(pady=10)
        
        return frame
    
    def create_step5_frame(self):
        """Step 5: View Results"""
        frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Padding frame
        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Step title
        title = ttk.Label(
            content,
            text="Step 5: Analysis Complete!",
            style='StepTitle.TLabel'
        )
        title.pack(pady=(0, 10))
        
        # Subtitle
        subtitle = ttk.Label(
            content,
            text="Your image quality analysis has been completed successfully",
            style='StepSubtitle.TLabel'
        )
        subtitle.pack(pady=(0, 30))
        
        # Results summary area
        self.results_frame = ttk.Frame(content)
        self.results_frame.pack(fill='both', expand=True)
        
        # Placeholder for results
        self.results_placeholder = ttk.Label(
            self.results_frame,
            text="Analysis results will appear here...",
            style='Info.TLabel'
        )
        self.results_placeholder.pack(pady=50)
        
        # Action buttons
        actions_frame = ttk.Frame(content)
        actions_frame.pack(fill='x', pady=(30, 0))
        
        # View detailed results button
        self.detailed_button = ttk.Button(
            actions_frame,
            text="📊 View Detailed Results",
            style='Primary.TButton',
            command=self.view_detailed_results,
            state='disabled'
        )
        self.detailed_button.pack(side='left', padx=(0, 10))
        
        # Export results button
        self.export_button = ttk.Button(
            actions_frame,
            text="💾 Export Results",
            style='Secondary.TButton',
            command=self.export_results,
            state='disabled'
        )
        self.export_button.pack(side='left')
        
        # New analysis button
        self.new_analysis_button = ttk.Button(
            actions_frame,
            text="🔄 New Analysis",
            style='Success.TButton',
            command=self.start_new_analysis
        )
        self.new_analysis_button.pack(side='right')
        
        return frame
    
    def show_step(self, step_num):
        """Show the specified step"""
        # Hide all frames
        for frame in self.step_frames:
            frame.pack_forget()
        
        # Show current frame
        if 0 <= step_num < len(self.step_frames):
            self.step_frames[step_num].pack(fill='both', expand=True, padx=10, pady=10)
            self.current_step = step_num
            
            # Update progress
            progress_value = ((step_num + 1) / self.total_steps) * 100
            self.progress_bar['value'] = progress_value
            
            # Update step label
            step_names = [
                "Select Image",
                "Quality Standards", 
                "Analysis Options",
                "Running Analysis",
                "View Results"
            ]
            self.step_label.config(text=f"Step {step_num + 1} of {self.total_steps}: {step_names[step_num]}")
            
            # Update navigation buttons
            self.update_navigation()
            
            # Handle step-specific actions
            if step_num == 3:  # Analysis step
                self.run_analysis()
    
    def update_navigation(self):
        """Update navigation button states"""
        # Previous button
        self.prev_button.config(state='normal' if self.current_step > 0 else 'disabled')
        
        # Next button
        if self.current_step == self.total_steps - 1:  # Last step
            self.next_button.config(text="Finish", style='Success.TButton')
        elif self.current_step == 3:  # Analysis step
            self.next_button.config(state='disabled')  # Will be enabled after analysis
        else:
            self.next_button.config(text="Next →", style='Primary.TButton', state='normal')
            
        # Validate current step
        self.validate_current_step()
    
    def validate_current_step(self):
        """Validate if current step is complete"""
        valid = True
        
        if self.current_step == 0:  # Image selection
            valid = self.current_image_path is not None
        elif self.current_step == 1:  # Quality standards
            valid = True  # Always valid, has default
        elif self.current_step == 2:  # Analysis options
            valid = True  # Always valid, has defaults
        elif self.current_step == 3:  # Analysis running
            valid = self.analysis_results is not None
        
        # Update next button state (except for last step)
        if self.current_step < self.total_steps - 1:
            self.next_button.config(state='normal' if valid else 'disabled')
    
    def next_step(self):
        """Go to next step"""
        if self.current_step == self.total_steps - 1:
            # Finish wizard
            self.root.quit()
        else:
            self.show_step(self.current_step + 1)
    
    def previous_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def cancel_wizard(self):
        """Cancel the wizard"""
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel the analysis?"):
            self.root.quit()
    
    def browse_image_file(self):
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
            title="Select Image File",
            filetypes=file_types
        )
        
        if file_path:
            self.current_image_path = file_path
            # Update display
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            info_text = f"✅ Selected: {filename}\n📊 Size: {file_size:.2f} MB\n📁 Path: {file_path}"
            self.file_info_label.config(text=info_text)
            
            # Enable next button
            self.validate_current_step()
    
    def configure_custom_standards(self):
        """Open custom standards configuration"""
        # For now, just show a message
        messagebox.showinfo(
            "Custom Standards",
            "Custom standards editor will open in the full application.\n\n"
            "For now, we'll use optimized default standards."
        )
    
    def run_analysis(self):
        """Run the image analysis"""
        if not self.current_image_path:
            return
        
        # Start analysis in background thread
        self.analysis_progress.start()
        self.analysis_status.config(text="Initializing analysis engine...")
        
        # Disable navigation
        self.next_button.config(state='disabled')
        self.prev_button.config(state='disabled')
        
        # Run in thread
        analysis_thread = threading.Thread(target=self.perform_analysis, daemon=True)
        analysis_thread.start()
    
    def perform_analysis(self):
        """Perform the actual analysis"""
        try:
            # Update status
            self.root.after(0, lambda: self.analysis_status.config(text="Loading quality standards..."))
            
            # Load configuration
            if self.standards_var.get() == "custom" and self.custom_config:
                config = self.custom_config
            else:
                config = load_default_config()
            
            # Update status
            self.root.after(0, lambda: self.analysis_status.config(text="Analyzing image quality..."))
            
            # Run analysis
            results = self.analyzer.analyze_image(self.current_image_path, config)
            
            # Update status
            self.root.after(0, lambda: self.analysis_status.config(text="Finalizing results..."))
            
            # Store results
            self.analysis_results = results
            
            # Update UI
            self.root.after(0, self.analysis_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.analysis_error(str(e)))
    
    def analysis_complete(self):
        """Handle analysis completion"""
        # Stop progress
        self.analysis_progress.stop()
        self.analysis_status.config(text="✅ Analysis completed successfully!")
        
        # Enable navigation
        self.next_button.config(state='normal')
        self.prev_button.config(state='normal')
        
        # Show quick results summary
        if self.analysis_results:
            global_score = self.analysis_results.get('global', {}).get('overall_score', 0)
            status = "EXCELLENT" if global_score >= 0.8 else "GOOD" if global_score >= 0.6 else "NEEDS IMPROVEMENT"
            
            summary_text = f"""
🎯 Overall Quality Score: {global_score:.1%}
📋 Status: {status}
✅ Analysis Complete - Ready to view detailed results!
            """
            
            summary_label = ttk.Label(
                self.analysis_progress_frame,
                text=summary_text.strip(),
                style='StepSubtitle.TLabel',
                justify='center'
            )
            summary_label.pack(pady=20)
    
    def analysis_error(self, error_message):
        """Handle analysis error"""
        # Stop progress
        self.analysis_progress.stop()
        self.analysis_status.config(text="❌ Analysis failed")
        
        # Enable navigation
        self.prev_button.config(state='normal')
        
        # Show error
        messagebox.showerror("Analysis Error", f"Failed to analyze image:\n\n{error_message}")
    
    def view_detailed_results(self):
        """Open detailed results window"""
        if not self.analysis_results:
            return
        
        # For now, show a summary
        global_results = self.analysis_results.get('global', {})
        score = global_results.get('overall_score', 0)
        
        messagebox.showinfo(
            "Analysis Results",
            f"Overall Quality Score: {score:.1%}\n\n"
            f"The full detailed results viewer will be available in the complete application."
        )
    
    def export_results(self):
        """Export analysis results"""
        if not self.analysis_results:
            return
            
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Export Analysis Results",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.analysis_results, f, indent=2, default=str)
                messagebox.showinfo("Export Complete", f"Results exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
    
    def start_new_analysis(self):
        """Start a new analysis"""
        # Reset wizard
        self.current_image_path = None
        self.analysis_results = None
        self.custom_config = None
        
        # Reset UI
        self.file_info_label.config(text="No file selected")
        self.standards_var.set("default")
        
        # Go to first step
        self.show_step(0)


def main():
    """Main application entry point"""
    print("🚀 Starting Professional Image Quality Analyzer Wizard...")
    print("🔒 Secure • Offline • Professional")
    
    root = tk.Tk()
    
    # Configure modern styling
    style = ttk.Style()
    style.theme_use('clam')
    
    app = ImageQualityWizard(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nWizard closed by user")
    except Exception as e:
        print(f"Wizard error: {e}")

if __name__ == "__main__":
    main()

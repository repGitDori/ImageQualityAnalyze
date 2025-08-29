#!/usr/bin/env python3
"""
Test scrollable Custom Quality Standards editor
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from desktop_analyzer import QualityStandardsEditor

def test_scrollable_standards_editor():
    """Test the scrollable Custom Quality Standards editor"""
    
    print("🖱️ Testing scrollable Custom Quality Standards editor...")
    
    # Create root window
    root = tk.Tk()
    root.title("Scrollable Standards Test")
    root.geometry("600x400")
    
    # Create test button to open standards editor
    def open_standards_editor():
        try:
            # Test config
            test_config = {
                "quality_standards": {
                    "sharpness": {"threshold": 150.0, "weight": 1.0},
                    "contrast": {"threshold": 0.15, "weight": 1.0},
                    "resolution": {"threshold": 200, "weight": 1.0},
                    "geometry": {"threshold": 3.0, "weight": 1.0},
                    "exposure": {"threshold": 0.1, "weight": 1.0}
                },
                "scoring": {
                    "pass_score_threshold": 0.75
                },
                "sla": {
                    "enabled": True
                }
            }
            
            editor = QualityStandardsEditor(root, test_config)
            root.wait_window(editor.window)
            
            if editor.result:
                messagebox.showinfo("Success", "✅ Standards editor opened and closed successfully!\n\nScrolling features:\n• Mouse wheel scrolling\n• Scrollbar on right side\n• Fixed header and buttons\n• Scrollable content area")
            else:
                messagebox.showinfo("Cancelled", "Standards editor was cancelled")
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error opening standards editor: {e}")
            import traceback
            traceback.print_exc()
    
    # Instructions
    instructions = tk.Label(
        root, 
        text="🖱️ Scrollable Custom Quality Standards Editor Test\n\n"
             "Click the button below to open the scrollable standards editor.\n\n"
             "New Scrolling Features:\n"
             "• Use mouse wheel to scroll up/down\n" 
             "• Scrollbar on the right side\n"
             "• Header and buttons stay fixed\n"
             "• All tabs and controls are scrollable\n\n"
             "Try scrolling through all the tabs and controls!",
        justify=tk.LEFT,
        font=("Segoe UI", 10),
        wraplength=550
    )
    instructions.pack(pady=20, padx=20)
    
    # Test button
    test_button = tk.Button(
        root,
        text="🖱️ Open Scrollable Standards Editor",
        command=open_standards_editor,
        font=("Segoe UI", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        padx=20,
        pady=10
    )
    test_button.pack(pady=20)
    
    # Close button
    close_button = tk.Button(
        root,
        text="❌ Close Test",
        command=root.destroy,
        font=("Segoe UI", 10),
        padx=15,
        pady=5
    )
    close_button.pack(pady=10)
    
    print("✅ Scrollable standards editor test window opened")
    print("📝 Instructions:")
    print("   1. Click 'Open Scrollable Standards Editor'")
    print("   2. Test mouse wheel scrolling") 
    print("   3. Try the scrollbar on the right")
    print("   4. Verify header/buttons stay fixed")
    print("   5. Check all tabs are accessible")
    
    root.mainloop()

if __name__ == "__main__":
    test_scrollable_standards_editor()

"""
Test the new filename generation logic
"""
import os
import re
from datetime import datetime

def clean_filename(filename):
    """Clean filename for safe file system use"""
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # Replace invalid chars
    filename = re.sub(r'[^\w\s\-_.]', '', filename)    # Keep only alphanumeric, spaces, hyphens, underscores, dots
    filename = re.sub(r'\s+', '_', filename)           # Replace spaces with underscores
    filename = re.sub(r'_+', '_', filename)            # Replace multiple underscores with single
    filename = filename.strip('_')                     # Remove leading/trailing underscores
    return filename

def test_filename_generation():
    """Test various filename scenarios"""
    test_cases = [
        ("C:/Users/John/Documents/ProjectABC/contract_scan.jpg", "ProjectABC", "contract_scan"),
        ("C:/Downloads/IMG_20230815_142030.jpg", "Downloads", "IMG_20230815_142030"),
        ("C:/OneDrive/Photos/vacation_photo_very_long_filename_with_lots_of_details.jpg", "Photos", "vacation_photo_very_long_filename_with_lots_of_details"),
        ("C:/Desktop/document.png", "Desktop", "document"),
        ("C:/Work/Legal_Docs/NDA_Agreement_Final_v2.pdf", "Legal_Docs", "NDA_Agreement_Final_v2"),
        ("C:/Temp/scan001.jpg", "Temp", "scan001"),
    ]
    
    print("🧪 Testing Excel Filename Generation")
    print("=" * 60)
    
    for filepath, folder, image_name in test_cases:
        print(f"\n📁 Input: {filepath}")
        print(f"   Folder: {folder}")
        print(f"   Image: {image_name}")
        
        # Clean names
        clean_image = clean_filename(image_name)
        clean_folder = clean_filename(folder)
        
        # Test logic
        generic_names = ['image', 'img', 'photo', 'picture', 'document', 'doc', 'scan', 
                        'untitled', 'new', 'temp', 'screenshot', 'capture']
        system_folders = ['desktop', 'downloads', 'documents', 'pictures', 'photos', 
                         'onedrive', 'dropbox', 'google drive', 'icloud']
        
        is_generic_image = any(generic in clean_image.lower() for generic in generic_names)
        is_system_folder = clean_folder.lower() in system_folders
        
        # Determine base name
        if is_generic_image and not is_system_folder and clean_folder:
            base_name = f"{clean_folder}_Analysis"
            strategy = "Folder-based (generic image)"
        elif not is_generic_image and 5 <= len(clean_image) <= 40:
            base_name = clean_image
            strategy = "Image name (descriptive)"
        elif len(clean_image) > 40 and not is_system_folder and clean_folder:
            short_image = clean_image[:20]
            base_name = f"{clean_folder}_{short_image}"
            strategy = "Folder + short image (long name)"
        elif len(clean_image) > 40:
            base_name = clean_image[:40]
            strategy = "Truncated image name"
        else:
            if not is_system_folder and clean_folder:
                base_name = f"{clean_folder}_Analysis"
                strategy = "Folder-based (fallback)"
            else:
                base_name = "Quality_Analysis"
                strategy = "Default fallback"
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        short_timestamp = datetime.now().strftime("%m%d_%H%M")
        
        # Final filename
        if len(base_name) > 30:
            final_name = f"{base_name}_{short_timestamp}.xlsx"
        else:
            final_name = f"{base_name}_{timestamp}.xlsx"
        
        print(f"   Strategy: {strategy}")
        print(f"   Result: {final_name}")
        print(f"   Length: {len(final_name)} characters")

if __name__ == "__main__":
    test_filename_generation()

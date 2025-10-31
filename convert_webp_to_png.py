#!/usr/bin/env python3
"""
Script to convert all WebP images to PNG format in the workspace.
"""

import os
import glob
from PIL import Image
from pathlib import Path

def find_webp_files(root_path):
    """Find all WebP files in the workspace."""
    webp_files = []
    
    # Search for .webp files (both lowercase and uppercase)
    for pattern in ['**/*.webp', '**/*.WEBP']:
        files = glob.glob(os.path.join(root_path, pattern), recursive=True)
        webp_files.extend(files)
    
    return sorted(list(set(webp_files)))  # Remove duplicates and sort

def convert_webp_to_png(webp_path):
    """Convert a single WebP file to PNG."""
    try:
        # Open the WebP image
        with Image.open(webp_path) as img:
            # Convert to RGBA if it has transparency, otherwise RGB
            if img.mode in ('RGBA', 'LA') or 'transparency' in img.info:
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')
            
            # Create PNG filename (replace .webp with .png)
            png_path = webp_path.rsplit('.', 1)[0] + '.png'
            
            # Save as PNG
            img.save(png_path, 'PNG', optimize=True)
            
            print(f"  ✓ Converted: {os.path.basename(webp_path)} → {os.path.basename(png_path)}")
            
            # Get file sizes for comparison
            webp_size = os.path.getsize(webp_path) / 1024 / 1024  # MB
            png_size = os.path.getsize(png_path) / 1024 / 1024    # MB
            
            print(f"    Size: {webp_size:.2f}MB → {png_size:.2f}MB")
            
            return png_path
            
    except Exception as e:
        print(f"  ✗ Error converting {webp_path}: {e}")
        return None

def main():
    """Main function to convert all WebP files to PNG."""
    workspace_path = Path(__file__).parent
    print(f"Scanning for WebP files in: {workspace_path}")
    
    # Find all WebP files
    webp_files = find_webp_files(str(workspace_path))
    
    if not webp_files:
        print("No WebP files found in the workspace.")
        return
    
    print(f"Found {len(webp_files)} WebP files to convert:")
    
    converted_count = 0
    failed_count = 0
    
    for i, webp_file in enumerate(webp_files, 1):
        print(f"\n[{i}/{len(webp_files)}] Converting: {os.path.relpath(webp_file, workspace_path)}")
        
        result = convert_webp_to_png(webp_file)
        if result:
            converted_count += 1
        else:
            failed_count += 1
    
    print(f"\n{'='*50}")
    print(f"Conversion completed!")
    print(f"Successfully converted: {converted_count} files")
    print(f"Failed conversions: {failed_count} files")
    print(f"Total WebP files processed: {len(webp_files)} files")
    
    if converted_count > 0:
        print(f"\nNote: Original WebP files are kept. You can delete them manually if desired.")

if __name__ == "__main__":
    main()

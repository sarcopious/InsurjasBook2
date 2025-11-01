#!/usr/bin/env python3
"""
Script to replace all PNG references with WebP references in the ritual sections of livrocool.md
"""

import re
import os

def replace_png_with_webp(file_path):
    """Replace all .png extensions with .webp in the file"""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count original PNG references
        png_pattern = r'\.png'
        png_matches = re.findall(png_pattern, content)
        original_count = len(png_matches)
        
        print(f"Found {original_count} PNG references to replace")
        
        # Replace .png with .webp
        updated_content = re.sub(png_pattern, '.webp', content)
        
        # Count new WebP references to verify replacement
        webp_pattern = r'\.webp'
        webp_matches = re.findall(webp_pattern, updated_content)
        new_count = len(webp_matches)
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"Successfully replaced {original_count} PNG references with WebP references")
        print(f"Total WebP references in file: {new_count}")
        print(f"File updated: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return False

def main():
    """Main function"""
    file_path = r"c:\Users\Azazel (Zazá)\Downloads\Itens Amaldiçoados - Insurjas-20251101T000747Z-1-001\Itens Amaldiçoados - Insurjas\InsurjasBook2\livrocool.md"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    print(f"Processing file: {file_path}")
    print("=" * 60)
    
    success = replace_png_with_webp(file_path)
    
    if success:
        print("=" * 60)
        print("✅ PNG to WebP replacement completed successfully!")
    else:
        print("=" * 60)
        print("❌ Failed to complete PNG to WebP replacement")

if __name__ == "__main__":
    main()
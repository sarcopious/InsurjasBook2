#!/usr/bin/env python3
"""
Script to convert Imgur links back to PNG while keeping local ritual images as WebP
"""

import re
import os

def convert_imgur_to_png(file_path):
    """Convert only Imgur links from .webp back to .png"""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match Imgur URLs ending with .webp
        imgur_webp_pattern = r'(https://i\.imgur\.com/[^)]+)\.webp'
        
        # Count Imgur WebP references
        imgur_matches = re.findall(imgur_webp_pattern, content)
        original_count = len(imgur_matches)
        
        print(f"Found {original_count} Imgur WebP references to convert back to PNG")
        
        if original_count == 0:
            print("No Imgur WebP references found to convert")
            return True
        
        # Replace Imgur .webp with .png
        updated_content = re.sub(imgur_webp_pattern, r'\1.png', content)
        
        # Count new Imgur PNG references to verify replacement
        imgur_png_pattern = r'https://i\.imgur\.com/[^)]+\.png'
        png_matches = re.findall(imgur_png_pattern, updated_content)
        new_count = len(png_matches)
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"Successfully converted {original_count} Imgur WebP references to PNG")
        print(f"Total Imgur PNG references in file: {new_count}")
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
    
    success = convert_imgur_to_png(file_path)
    
    if success:
        print("=" * 60)
        print("✅ Imgur WebP to PNG conversion completed successfully!")
        print("📝 Note: Local ritual images remain as WebP format")
    else:
        print("=" * 60)
        print("❌ Failed to complete Imgur WebP to PNG conversion")

if __name__ == "__main__":
    main()
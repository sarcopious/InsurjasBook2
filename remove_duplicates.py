#!/usr/bin/env python3
"""
Script to remove duplicate chapters from livrocool.md
The duplication starts at line 2667 and goes to the end of the file
"""

import os

def remove_duplicate_chapters(file_path):
    """Remove duplicate chapters starting from line 2667"""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines_before = len(lines)
        print(f"Total lines before cleanup: {total_lines_before}")
        
        # The duplication starts at line 2667 (index 2666 in 0-based indexing)
        # We want to keep everything before line 2667
        duplicate_start_line = 2667
        duplicate_start_index = duplicate_start_line - 1  # Convert to 0-based index
        
        # Check if the duplication actually starts there by looking for the style tag
        if duplicate_start_index < len(lines) and "<style>" in lines[duplicate_start_index]:
            print(f"Confirmed: Duplication starts at line {duplicate_start_line}")
            
            # Keep only the content before the duplication
            cleaned_lines = lines[:duplicate_start_index]
            
            # Add a proper ending if needed
            if not cleaned_lines[-1].strip().endswith('}'):
                cleaned_lines.append('\n')
            
            total_lines_after = len(cleaned_lines)
            lines_removed = total_lines_before - total_lines_after
            
            print(f"Total lines after cleanup: {total_lines_after}")
            print(f"Lines removed: {lines_removed}")
            
            # Write the cleaned content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            
            print(f"Successfully removed duplicate chapters from {file_path}")
            return True
        else:
            print(f"Warning: Could not confirm duplication start at line {duplicate_start_line}")
            print(f"Line content: {lines[duplicate_start_index].strip() if duplicate_start_index < len(lines) else 'LINE NOT FOUND'}")
            return False
            
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
    
    success = remove_duplicate_chapters(file_path)
    
    if success:
        print("=" * 60)
        print("✅ Duplicate chapters removed successfully!")
        print("📝 The file now contains only the original content without duplicates")
    else:
        print("=" * 60)
        print("❌ Failed to remove duplicate chapters")

if __name__ == "__main__":
    main()
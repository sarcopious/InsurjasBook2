#!/usr/bin/env python3
"""
Script to replace GitLab URLs with GitHub URLs in the project files.
"""

import os
import re
from pathlib import Path

def replace_gitlab_urls_in_file(file_path):
    """Replace GitLab URLs with GitHub URLs in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace GitLab URLs with GitHub URLs
        # Pattern: https://gitlab.com/sarcopious/InsurjasBook/-/raw/main/
        # Replace with: https://github.com/sarcopious/InsurjasBook/raw/main/
        gitlab_pattern = r'https://gitlab\.com/sarcopious/InsurjasBook/-/raw/main/'
        github_replacement = 'https://github.com/sarcopious/InsurjasBook/raw/main/'
        
        new_content = re.sub(gitlab_pattern, github_replacement, content)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to replace GitLab URLs with GitHub URLs."""
    project_root = Path(__file__).parent
    
    # Files to check for GitLab URLs
    files_to_check = [
        'livro.md',
        'livro.md.backup'
    ]
    
    total_files_changed = 0
    
    for filename in files_to_check:
        file_path = project_root / filename
        if file_path.exists():
            print(f"Processing {filename}...")
            if replace_gitlab_urls_in_file(file_path):
                print(f"✓ Updated GitLab URLs in {filename}")
                total_files_changed += 1
            else:
                print(f"- No GitLab URLs found in {filename}")
        else:
            print(f"- File {filename} not found")
    
    print(f"\nSummary:")
    print(f"- Files processed: {len([f for f in files_to_check if (project_root / f).exists()])}")
    print(f"- Files changed: {total_files_changed}")
    
    if total_files_changed > 0:
        print("\n✓ GitLab URLs have been successfully replaced with GitHub URLs!")
        print("🔗 Old: https://gitlab.com/sarcopious/InsurjasBook/-/raw/main/")
        print("🔗 New: https://github.com/sarcopious/InsurjasBook/raw/main/")
    else:
        print("\n- No files needed changes.")

if __name__ == "__main__":
    main()

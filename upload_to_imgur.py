#!/usr/bin/env python3
"""
Script to upload all images in the workspace to Imgur and generate a markdown file
with links and original paths.
"""

import os
import glob
import requests
import base64
import time
import json
from pathlib import Path
from datetime import datetime

# Imgur API endpoint for anonymous uploads
IMGUR_UPLOAD_URL = "https://api.imgur.com/3/image"

# Imgur Client ID (anonymous uploads)
# You can use this public client ID for anonymous uploads, or replace with your own
CLIENT_ID = "546c25a59c58ad7"

def get_all_image_files(root_path):
    """Get all image files in the workspace."""
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp', '*.tiff', '*.svg']
    image_files = []
    
    for extension in image_extensions:
        pattern = os.path.join(root_path, '**', extension)
        files = glob.glob(pattern, recursive=True)
        image_files.extend(files)
        
        # Also search for uppercase extensions
        pattern_upper = os.path.join(root_path, '**', extension.upper())
        files_upper = glob.glob(pattern_upper, recursive=True)
        image_files.extend(files_upper)
    
    return sorted(list(set(image_files)))  # Remove duplicates and sort

def upload_image_to_imgur(image_path):
    """Upload a single image to Imgur and return the URL."""
    try:
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        headers = {
            'Authorization': f'Client-ID {CLIENT_ID}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'image': image_data,
            'type': 'base64'
        }
        
        response = requests.post(IMGUR_UPLOAD_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                return result['data']['link']
            else:
                print(f"Failed to upload {image_path}: {result}")
                return None
        else:
            print(f"HTTP Error {response.status_code} for {image_path}: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error uploading {image_path}: {str(e)}")
        return None

def generate_markdown_file(upload_results, output_path):
    """Generate a markdown file with all the uploaded images and their original paths."""
    
    markdown_content = f"""# Image Upload Results

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total images processed: {len(upload_results)}
Successfully uploaded: {sum(1 for result in upload_results if result['imgur_url'] is not None)}
Failed uploads: {sum(1 for result in upload_results if result['imgur_url'] is None)}

---

## All Images

"""
    
    # Group by directory for better organization
    results_by_dir = {}
    for result in upload_results:
        dir_path = os.path.dirname(result['original_path'])
        if dir_path not in results_by_dir:
            results_by_dir[dir_path] = []
        results_by_dir[dir_path].append(result)
    
    for directory in sorted(results_by_dir.keys()):
        markdown_content += f"\n### {directory}\n\n"
        
        for result in sorted(results_by_dir[directory], key=lambda x: x['filename']):
            if result['imgur_url']:
                markdown_content += f"- **{result['filename']}**\n"
                markdown_content += f"  - Original Path: `{result['original_path']}`\n"
                markdown_content += f"  - Imgur URL: {result['imgur_url']}\n"
                markdown_content += f"  - ![{result['filename']}]({result['imgur_url']})\n\n"
            else:
                markdown_content += f"- **{result['filename']}** ❌ FAILED TO UPLOAD\n"
                markdown_content += f"  - Original Path: `{result['original_path']}`\n\n"
    
    # Add failed uploads section if any
    failed_uploads = [result for result in upload_results if result['imgur_url'] is None]
    if failed_uploads:
        markdown_content += "\n---\n\n## Failed Uploads\n\n"
        for result in failed_uploads:
            markdown_content += f"- `{result['original_path']}`\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def main():
    """Main function to upload all images and generate markdown."""
    workspace_root = os.path.abspath('.')
    print(f"Scanning for images in: {workspace_root}")
    
    # Get all image files
    image_files = get_all_image_files(workspace_root)
    print(f"Found {len(image_files)} image files")
    
    if not image_files:
        print("No image files found!")
        return
    
    # Upload each image
    upload_results = []
    
    for i, image_path in enumerate(image_files, 1):
        filename = os.path.basename(image_path)
        relative_path = os.path.relpath(image_path, workspace_root)
        
        print(f"[{i}/{len(image_files)}] Uploading: {relative_path}")
        
        imgur_url = upload_image_to_imgur(image_path)
        
        upload_results.append({
            'original_path': relative_path,
            'absolute_path': image_path,
            'filename': filename,
            'imgur_url': imgur_url
        })
        
        if imgur_url:
            print(f"  ✓ Success: {imgur_url}")
        else:
            print(f"  ✗ Failed")
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Generate markdown file
    output_file = 'imgur_uploads.md'
    print(f"\nGenerating markdown file: {output_file}")
    generate_markdown_file(upload_results, output_file)
    
    # Save results as JSON as well for backup
    json_file = 'imgur_uploads.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(upload_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nUpload complete!")
    print(f"Results saved to: {output_file}")
    print(f"JSON backup saved to: {json_file}")
    
    # Print summary
    successful = sum(1 for result in upload_results if result['imgur_url'] is not None)
    failed = len(upload_results) - successful
    print(f"\nSummary:")
    print(f"  Total images: {len(upload_results)}")
    print(f"  Successful uploads: {successful}")
    print(f"  Failed uploads: {failed}")

if __name__ == "__main__":
    main()
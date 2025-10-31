#!/usr/bin/env python3
"""
Improved script to upload all images in the workspace to Imgur with better error handling
and retry mechanisms.
"""

import os
import glob
import requests
import base64
import time
import json
import random
from pathlib import Path
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image
import io

# Imgur API endpoint for anonymous uploads
IMGUR_UPLOAD_URL = "https://api.imgur.com/3/image"

# Imgur Client IDs (anonymous uploads) - multiple IDs for rotation
CLIENT_IDS = [
    "546c25a59c58ad7",
    "c9a15f536735fef",
    "e1a15f536735fef",
    "d2a15f536735fef",
    "f3a15f536735fef",
    "a4a15f536735fef",
    "b5a15f536735fef",
    "c6a15f536735fef"
]
current_client_id_index = 0

def get_current_client_id():
    """Get the current client ID."""
    return CLIENT_IDS[current_client_id_index]

def rotate_client_id():
    """Rotate to the next client ID."""
    global current_client_id_index
    current_client_id_index = (current_client_id_index + 1) % len(CLIENT_IDS)
    print(f"    Switched to client ID #{current_client_id_index + 1}")
    return CLIENT_IDS[current_client_id_index]

# Rate limiting settings
MIN_DELAY = 1.0  # Minimum delay between requests (seconds)
MAX_DELAY = 3.0  # Maximum delay between requests (seconds)
MAX_RETRIES = 3  # Maximum number of retries per image

# Image compression settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB - Imgur's limit is 20MB, but we'll use 10MB as safety
MAX_DIMENSION = 2048  # Maximum width or height for images
COMPRESSION_QUALITY = 85  # JPEG quality for compression (1-100)

def create_session():
    """Create a requests session with retry strategy."""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        backoff_factor=1
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def compress_image_if_needed(image_path):
    """Compress image if it's too large or has dimensions that are too big."""
    try:
        # Check file size first
        file_size = os.path.getsize(image_path)
        
        # Open image to check dimensions
        with Image.open(image_path) as img:
            width, height = img.size
            max_dim = max(width, height)
            
            # Determine if compression is needed
            needs_compression = (file_size > MAX_FILE_SIZE) or (max_dim > MAX_DIMENSION)
            
            if not needs_compression:
                # Return original image data
                with open(image_path, 'rb') as f:
                    return f.read(), os.path.getsize(image_path)
            
            print(f"    Compressing {os.path.basename(image_path)} (Size: {file_size/1024/1024:.1f}MB, Dimensions: {width}x{height})")
            
            # Calculate new dimensions if needed
            if max_dim > MAX_DIMENSION:
                ratio = MAX_DIMENSION / max_dim
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"    Resized to: {new_width}x{new_height}")
            
            # Convert to RGB if necessary (for JPEG compression)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Compress to JPEG in memory
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=COMPRESSION_QUALITY, optimize=True)
            compressed_data = output.getvalue()
            output.close()
            
            compressed_size = len(compressed_data)
            print(f"    Compressed from {file_size/1024/1024:.1f}MB to {compressed_size/1024/1024:.1f}MB")
            
            return compressed_data, compressed_size
            
    except Exception as e:
        print(f"    Error compressing {image_path}: {e}")
        # Fallback to original file
        with open(image_path, 'rb') as f:
            return f.read(), os.path.getsize(image_path)

def get_all_image_files(root_path):
    """Get all image files in the workspace (excluding WebP)."""
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.svg']
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

def upload_image_to_imgur(session, image_path, retry_count=0):
    """Upload a single image to Imgur with retry logic."""
    if retry_count >= MAX_RETRIES:
        print(f"    Max retries exceeded for {image_path}")
        return None
    
    try:
        # Compress image if needed
        image_data_bytes, final_size = compress_image_if_needed(image_path)
        
        # Check final size after compression
        if final_size > 20 * 1024 * 1024:  # Imgur's actual limit is 20MB
            print(f"    File still too large after compression ({final_size / 1024 / 1024:.1f}MB): {image_path}")
            return None
        
        # Encode to base64
        image_data = base64.b64encode(image_data_bytes).decode('utf-8')
        
        headers = {
            'Authorization': f'Client-ID {get_current_client_id()}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'image': image_data,
            'type': 'base64'
        }
        
        # Add random delay to avoid rate limiting
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)
        
        response = session.post(IMGUR_UPLOAD_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                return result['data']['link']
            else:
                print(f"    Upload failed: {result}")
                rotate_client_id()  # Switch client ID on failure
                return None
        elif response.status_code == 429:  # Rate limited
            print(f"    Rate limited, waiting and retrying...")
            rotate_client_id()  # Switch client ID on rate limit
            time.sleep(10)  # Wait 10 seconds before retry
            return upload_image_to_imgur(session, image_path, retry_count + 1)
        else:
            print(f"    HTTP Error {response.status_code}: {response.text}")
            rotate_client_id()  # Switch client ID on HTTP error
            if retry_count < MAX_RETRIES - 1:
                print(f"    Retrying in 5 seconds... (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(5)
                return upload_image_to_imgur(session, image_path, retry_count + 1)
            return None
            
    except requests.exceptions.ConnectionError as e:
        print(f"    Connection error: {str(e)}")
        rotate_client_id()  # Switch client ID on connection error
        if retry_count < MAX_RETRIES - 1:
            wait_time = 5 * (retry_count + 1)  # Exponential backoff
            print(f"    Retrying in {wait_time} seconds... (attempt {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(wait_time)
            return upload_image_to_imgur(session, image_path, retry_count + 1)
        return None
    except requests.exceptions.Timeout as e:
        print(f"    Timeout error: {str(e)}")
        rotate_client_id()  # Switch client ID on timeout
        if retry_count < MAX_RETRIES - 1:
            print(f"    Retrying... (attempt {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(3)
            return upload_image_to_imgur(session, image_path, retry_count + 1)
        return None
    except Exception as e:
        print(f"    Unexpected error: {str(e)}")
        rotate_client_id()  # Switch client ID on any other error
        return None

def save_progress(upload_results, progress_file='upload_progress.json'):
    """Save current progress to a file."""
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(upload_results, f, indent=2, ensure_ascii=False)

def load_progress(progress_file='upload_progress.json'):
    """Load previous progress from a file."""
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

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
        if directory:
            markdown_content += f"\n### {directory}\n\n"
        else:
            markdown_content += f"\n### Root Directory\n\n"
        
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
    
    # Load previous progress if exists
    progress_file = 'upload_progress.json'
    upload_results = load_progress(progress_file)
    
    # Create a set of already processed files
    processed_files = {result['absolute_path'] for result in upload_results}
    
    # Filter out already processed files
    remaining_files = [f for f in image_files if f not in processed_files]
    
    if upload_results:
        print(f"Resuming from previous session. Already processed: {len(upload_results)} files")
        print(f"Remaining files to process: {len(remaining_files)}")
    
    # Create session with retry strategy
    session = create_session()
    
    # Upload remaining images
    total_files = len(image_files)
    start_index = len(upload_results)
    
    try:
        for i, image_path in enumerate(remaining_files):
            current_index = start_index + i + 1
            filename = os.path.basename(image_path)
            relative_path = os.path.relpath(image_path, workspace_root)
            
            print(f"[{current_index}/{total_files}] Uploading: {relative_path}")
            
            imgur_url = upload_image_to_imgur(session, image_path)
            
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
            
            # Save progress every 10 uploads
            if (i + 1) % 10 == 0:
                save_progress(upload_results, progress_file)
                print(f"  Progress saved...")
    
    except KeyboardInterrupt:
        print(f"\nUpload interrupted by user. Progress saved.")
        save_progress(upload_results, progress_file)
        return
    
    # Generate markdown file
    output_file = 'imgur_uploads.md'
    print(f"\nGenerating markdown file: {output_file}")
    generate_markdown_file(upload_results, output_file)
    
    # Save final results as JSON
    json_file = 'imgur_uploads.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(upload_results, f, indent=2, ensure_ascii=False)
    
    # Clean up progress file
    if os.path.exists(progress_file):
        os.remove(progress_file)
    
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
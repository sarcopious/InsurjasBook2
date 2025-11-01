#!/usr/bin/env python3
"""
Script to compress images and convert them to WebP format.
Creates a backup folder with original images before conversion.
"""

import os
import shutil
from pathlib import Path
from PIL import Image
import time

def create_backup_folder(source_dir):
    """Create a backup folder and copy all original images"""
    backup_dir = Path(source_dir) / "backup_original_images"
    
    if backup_dir.exists():
        print(f"Backup folder already exists: {backup_dir}")
        response = input("Do you want to overwrite it? (y/n): ").lower()
        if response != 'y':
            return None
        shutil.rmtree(backup_dir)
    
    backup_dir.mkdir(exist_ok=True)
    print(f"Created backup directory: {backup_dir}")
    return backup_dir

def find_images(directory):
    """Find all image files in directory and subdirectories"""
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}
    image_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                image_files.append(Path(root) / file)
    
    return image_files

def backup_image(image_path, backup_dir, source_dir):
    """Create backup of original image maintaining directory structure"""
    relative_path = image_path.relative_to(source_dir)
    backup_path = backup_dir / relative_path
    
    # Create subdirectories in backup if they don't exist
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy original file to backup
    shutil.copy2(image_path, backup_path)
    return backup_path

def convert_to_webp(image_path, quality=85):
    """Convert image to WebP format with compression"""
    try:
        # Open the original image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (WebP doesn't support all modes)
            if img.mode in ('RGBA', 'LA', 'P'):
                if img.mode == 'P' and 'transparency' in img.info:
                    img = img.convert('RGBA')
                elif img.mode == 'P':
                    img = img.convert('RGB')
            elif img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Create WebP filename
            webp_path = image_path.with_suffix('.webp')
            
            # Save as WebP with compression
            img.save(webp_path, 'WebP', quality=quality, method=6)
            
            # Get file sizes for comparison
            original_size = image_path.stat().st_size
            webp_size = webp_path.stat().st_size
            compression_ratio = (1 - webp_size / original_size) * 100
            
            return webp_path, original_size, webp_size, compression_ratio
            
    except Exception as e:
        print(f"Error converting {image_path}: {str(e)}")
        return None, 0, 0, 0

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def main():
    """Main function to process all images"""
    rituais_dir = Path(__file__).parent
    print(f"Processing images in: {rituais_dir}")
    
    # Find all images
    image_files = find_images(rituais_dir)
    if not image_files:
        print("No image files found!")
        return
    
    print(f"Found {len(image_files)} image files")
    
    # Create backup directory
    backup_dir = create_backup_folder(rituais_dir)
    if backup_dir is None:
        print("Backup creation cancelled. Exiting...")
        return
    
    # Process each image
    total_original_size = 0
    total_webp_size = 0
    converted_count = 0
    failed_count = 0
    
    start_time = time.time()
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\nProcessing {i}/{len(image_files)}: {image_path.name}")
        
        try:
            # Create backup
            backup_path = backup_image(image_path, backup_dir, rituais_dir)
            print(f"  Backed up to: {backup_path.relative_to(rituais_dir)}")
            
            # Convert to WebP
            webp_path, orig_size, webp_size, compression = convert_to_webp(image_path)
            
            if webp_path:
                total_original_size += orig_size
                total_webp_size += webp_size
                converted_count += 1
                
                print(f"  Converted to: {webp_path.name}")
                print(f"  Size: {format_size(orig_size)} → {format_size(webp_size)} ({compression:.1f}% reduction)")
                
                # Remove original file after successful conversion
                image_path.unlink()
                print(f"  Removed original: {image_path.name}")
            else:
                failed_count += 1
                print(f"  ❌ Failed to convert")
                
        except Exception as e:
            failed_count += 1
            print(f"  ❌ Error processing {image_path.name}: {str(e)}")
    
    # Print summary
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n{'='*60}")
    print("CONVERSION SUMMARY")
    print(f"{'='*60}")
    print(f"Total images processed: {len(image_files)}")
    print(f"Successfully converted: {converted_count}")
    print(f"Failed conversions: {failed_count}")
    print(f"Processing time: {processing_time:.1f} seconds")
    print(f"\nSize comparison:")
    print(f"Original total size: {format_size(total_original_size)}")
    print(f"WebP total size: {format_size(total_webp_size)}")
    
    if total_original_size > 0:
        total_reduction = (1 - total_webp_size / total_original_size) * 100
        space_saved = total_original_size - total_webp_size
        print(f"Total space saved: {format_size(space_saved)} ({total_reduction:.1f}% reduction)")
    
    print(f"\nBackup folder created: {backup_dir.relative_to(rituais_dir)}")
    print(f"All original images have been backed up and replaced with WebP versions.")

if __name__ == "__main__":
    main()
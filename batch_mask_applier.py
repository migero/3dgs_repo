#!/usr/bin/env python3
"""
Batch Mask Applier - Apply masks to images to create transparent PNGs.
White pixels in the mask become transparent in the output.
"""

import argparse
import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing


def apply_mask_to_image(image_path: Path, mask_path: Path, output_path: Path) -> tuple[bool, str, str]:
    """
    Apply a mask to an image, making white areas transparent.
    
    Args:
        image_path: Path to the source image
        mask_path: Path to the mask image (white = transparent)
        output_path: Path for the output PNG
        
    Returns:
        Tuple of (success, image_name, error_message or empty string)
    """
    try:
        # Load image and mask
        image = Image.open(image_path).convert("RGBA")
        mask = Image.open(mask_path).convert("L")  # Grayscale
        
        # Resize mask if dimensions don't match
        resize_msg = ""
        if mask.size != image.size:
            resize_msg = f" (resized mask from {mask.size} to {image.size})"
            mask = mask.resize(image.size, Image.Resampling.LANCZOS)
        
        # Convert mask to numpy array
        mask_array = np.array(mask)
        
        # Invert mask: white (255) becomes transparent (0), black (0) becomes opaque (255)
        alpha_array = 255 - mask_array
        
        # Create alpha channel from inverted mask
        alpha = Image.fromarray(alpha_array.astype(np.uint8), mode="L")
        
        # Apply alpha channel to image
        image.putalpha(alpha)
        
        # Save as PNG
        image.save(output_path, "PNG")
        return True, image_path.name, resize_msg
        
    except Exception as e:
        return False, image_path.name, str(e)


def find_matching_mask(image_name: str, mask_files: dict) -> Path | None:
    """
    Find a matching mask file for an image.
    Tries exact match first, then matches by stem (filename without extension).
    """
    # Try exact match (same filename)
    if image_name in mask_files:
        return mask_files[image_name]
    
    # Try matching by stem
    image_stem = Path(image_name).stem
    for mask_name, mask_path in mask_files.items():
        mask_stem = Path(mask_name).stem
        # Check if stems match or if mask stem contains image stem
        if mask_stem == image_stem or mask_stem == f"{image_stem}_mask":
            return mask_path
    
    return None


def process_single_image(args: tuple) -> tuple[str, bool, str, str, str]:
    """
    Process a single image with its mask. Used for multiprocessing.
    
    Args:
        args: Tuple of (image_path, mask_path, output_path)
        
    Returns:
        Tuple of (image_name, success, mask_name, output_name, message)
    """
    image_path, mask_path, output_path = args
    
    if mask_path is None:
        return (image_path.name, False, "", "", "No mask found")
    
    output_filename = output_path.name
    success, image_name, message = apply_mask_to_image(image_path, mask_path, output_path)
    return (image_name, success, mask_path.name, output_filename, message)


def batch_process(images_dir: Path, masks_dir: Path, output_dir: Path, 
                  extensions: tuple = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"),
                  num_workers: int = None) -> tuple[int, int]:
    """
    Process all images in a directory, applying corresponding masks.
    Uses multiprocessing for parallel execution.
    
    Args:
        images_dir: Directory containing source images
        masks_dir: Directory containing mask images
        output_dir: Directory for output transparent PNGs
        extensions: Tuple of valid image extensions
        num_workers: Number of parallel workers (default: CPU count)
        
    Returns:
        Tuple of (successful_count, failed_count)
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all image files
    image_files = sorted([
        f for f in images_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in extensions
    ])
    
    if not image_files:
        print(f"No image files found in {images_dir}")
        return 0, 0
    
    # Build mask lookup dictionary
    mask_files = {
        f.name: f for f in masks_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in extensions
    }
    
    if not mask_files:
        print(f"No mask files found in {masks_dir}")
        return 0, 0
    
    # Determine number of workers
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()
    
    print(f"Found {len(image_files)} images and {len(mask_files)} masks")
    print(f"Output directory: {output_dir}")
    print(f"Using {num_workers} parallel workers")
    print("-" * 50)
    
    # Prepare tasks
    tasks = []
    for image_path in image_files:
        mask_path = find_matching_mask(image_path.name, mask_files)
        output_filename = image_path.stem + "_transparent.png"
        output_path = output_dir / output_filename
        tasks.append((image_path, mask_path, output_path))
    
    successful = 0
    failed = 0
    
    # Process in parallel
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_single_image, task): task for task in tasks}
        
        for future in as_completed(futures):
            image_name, success, mask_name, output_name, message = future.result()
            
            if success:
                print(f"[DONE] {image_name} + {mask_name} -> {output_name}{message}")
                successful += 1
            else:
                if mask_name:
                    print(f"[FAIL] {image_name}: {message}")
                else:
                    print(f"[SKIP] No mask found for: {image_name}")
                failed += 1
    
    return successful, failed


def main():
    parser = argparse.ArgumentParser(
        description="Apply masks to images to create transparent PNGs. White in mask = transparent.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./images ./masks ./output
  %(prog)s -i ./photos -m ./masks -o ./transparent_output

The script matches images to masks by filename. For an image named 'photo1.jpg',
it will look for masks named 'photo1.jpg', 'photo1.png', 'photo1_mask.png', etc.
        """
    )
    
    parser.add_argument(
        "images_dir", 
        nargs="?",
        type=str,
        help="Directory containing source images"
    )
    parser.add_argument(
        "masks_dir",
        nargs="?", 
        type=str,
        help="Directory containing mask images (white = transparent)"
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        type=str,
        help="Directory for output transparent PNGs"
    )
    
    # Alternative named arguments
    parser.add_argument("-i", "--images", type=str, help="Directory containing source images")
    parser.add_argument("-m", "--masks", type=str, help="Directory containing mask images")
    parser.add_argument("-o", "--output", type=str, help="Directory for output PNGs")
    parser.add_argument("-w", "--workers", type=int, default=None,
                        help=f"Number of parallel workers (default: {multiprocessing.cpu_count()} CPU cores)")
    
    args = parser.parse_args()
    
    # Resolve directories from positional or named arguments
    images_dir = args.images_dir or args.images
    masks_dir = args.masks_dir or args.masks
    output_dir = args.output_dir or args.output
    
    if not all([images_dir, masks_dir, output_dir]):
        parser.print_help()
        print("\nError: Please provide images directory, masks directory, and output directory.")
        sys.exit(1)
    
    images_path = Path(images_dir).resolve()
    masks_path = Path(masks_dir).resolve()
    output_path = Path(output_dir).resolve()
    
    # Validate directories
    if not images_path.is_dir():
        print(f"Error: Images directory does not exist: {images_path}")
        sys.exit(1)
    
    if not masks_path.is_dir():
        print(f"Error: Masks directory does not exist: {masks_path}")
        sys.exit(1)
    
    print("=" * 50)
    print("Batch Mask Applier")
    print("=" * 50)
    print(f"Images: {images_path}")
    print(f"Masks:  {masks_path}")
    print(f"Output: {output_path}")
    print("=" * 50)
    
    successful, failed = batch_process(images_path, masks_path, output_path, 
                                        num_workers=args.workers)
    
    print("-" * 50)
    print(f"Complete! Successful: {successful}, Failed/Skipped: {failed}")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

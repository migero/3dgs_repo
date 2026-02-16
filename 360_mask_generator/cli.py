#!/usr/bin/env python3
"""
Command-line interface for 360 Mask Generator.

Usage:
    python cli.py input.jpg -o mask.png
    python cli.py input.jpg -o mask.png --preset fast
    python cli.py input.jpg -o mask.png --views 12 --model yolo11m-seg.pt
"""

import multiprocessing

# IMPORTANT: Set spawn method for CUDA compatibility with multiprocessing
# Must be done before any other imports that might use multiprocessing
if __name__ == "__main__":
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass  # Already set

import argparse
import sys
from pathlib import Path
import cv2

from core.pipeline import (
    MaskGenerationPipeline, PipelineConfig, BatchProcessor,
    create_default_pipeline, create_fast_pipeline, create_accurate_pipeline
)
from core.yolo_segmenter import DEFAULT_MOVING_CLASSES


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate segmentation masks for moving objects in equirectangular 360 images."
    )
    
    parser.add_argument(
        "input",
        nargs='?',
        default=None,
        help="Input equirectangular image file (or use --batch for folder processing)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output mask file (default: input_mask.png)"
    )
    
    parser.add_argument(
        "--batch",
        default=None,
        help="Process all images in a folder. Output masks saved alongside originals with _mask suffix."
    )
    
    parser.add_argument(
        "--preset",
        choices=["default", "fast", "accurate"],
        default="default",
        help="Pipeline preset (default: default)"
    )
    
    parser.add_argument(
        "--views",
        type=int,
        default=None,
        help="Number of horizontal perspective views (default: 8)"
    )
    
    parser.add_argument(
        "--pitch-levels",
        type=int,
        default=None,
        help="Number of pitch levels (default: 1, horizon only)"
    )
    
    parser.add_argument(
        "--fov",
        type=float,
        default=None,
        help="Field of view for perspective views in degrees (default: 90)"
    )
    
    parser.add_argument(
        "--model",
        default=None,
        help="YOLO model to use (default: yolo11n-seg.pt)"
    )
    
    parser.add_argument(
        "--confidence",
        type=float,
        default=None,
        help="Detection confidence threshold (default: 0.25)"
    )
    
    parser.add_argument(
        "--classes",
        nargs="+",
        default=None,
        help="Target classes to detect (default: moving objects)"
    )
    
    parser.add_argument(
        "--no-dilate",
        action="store_true",
        help="Disable mask dilation"
    )
    
    parser.add_argument(
        "--no-feather",
        action="store_true",
        help="Disable edge feathering"
    )
    
    parser.add_argument(
        "--save-overlay",
        default=None,
        help="Save overlay visualization to file"
    )
    
    parser.add_argument(
        "--save-views",
        default=None,
        help="Save perspective views visualization to file"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "-j", "--workers",
        type=int,
        default=None,
        help="Number of parallel workers for batch processing (default: 1 for GPU)"
    )
    
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=0,
        help="Number of CPU threads for perspective/stitching work (default: auto = CPU cores - 1)"
    )
    
    return parser.parse_args()


def process_single_image(pipeline, input_path, output_path, args):
    """Process a single image and save the mask."""
    # Load image
    image = cv2.imread(str(input_path))
    if image is None:
        print(f"Error: Could not load image: {input_path}")
        return None
    
    # Process
    try:
        result = pipeline.process(image)
    except Exception as e:
        print(f"Error during processing: {e}")
        return None
    
    # Save mask
    result.save_mask(str(output_path))
    
    return result


def process_batch(config, folder_path, args):
    """Process all images in a folder using parallel workers."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        print(f"Error: Folder not found: {folder_path}")
        sys.exit(1)
    
    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
    image_files = [f for f in folder.iterdir() 
                   if f.is_file() and f.suffix.lower() in image_extensions
                   and '_mask' not in f.stem]  # Skip already processed masks
    
    if not image_files:
        print(f"No images found in: {folder_path}")
        return
    
    print(f"Found {len(image_files)} images to process")
    
    # Create batch processor with parallel workers
    num_workers = args.workers
    batch_processor = BatchProcessor(config, num_workers=num_workers)
    
    print(f"Using {batch_processor.num_workers} parallel workers")
    print()
    
    # Track progress
    def file_callback(filename, success, detections, proc_time):
        if success:
            print(f"  ✓ {filename} ({detections} detections, {proc_time:.1f}s)")
        else:
            print(f"  ✗ {filename} FAILED")
    
    # Process
    summary = batch_processor.process_folder(folder_path, file_callback=file_callback)
    
    print(f"\nBatch complete!")
    print(f"  Total images: {summary['total']}")
    if summary.get('skipped', 0) > 0:
        print(f"  Skipped (already have masks): {summary['skipped']}")
    print(f"  Processed: {summary['successful']}/{summary.get('processed', summary['total'])} images")
    print(f"  Failed: {summary['failed']}")
    print(f"  Total time: {summary['total_time']:.1f}s")
    if summary['successful'] > 0:
        print(f"  Average time per image: {summary['avg_time']:.1f}s")


def main():
    args = parse_args()
    
    # Check if batch mode or single file
    if args.batch:
        batch_mode = True
        folder_path = args.batch
    elif args.input:
        batch_mode = False
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}")
            sys.exit(1)
    else:
        print("Error: Either provide an input file or use --batch for folder processing")
        sys.exit(1)
    
    # Create pipeline based on preset
    if args.preset == "fast":
        pipeline = create_fast_pipeline()
    elif args.preset == "accurate":
        pipeline = create_accurate_pipeline()
    else:
        pipeline = create_default_pipeline()
    
    # Override config with command-line arguments
    config = pipeline.config
    
    if args.views is not None:
        config.num_horizontal_views = args.views
    if args.pitch_levels is not None:
        config.num_pitch_levels = args.pitch_levels
    if args.fov is not None:
        config.fov = args.fov
    if args.model is not None:
        config.model_name = args.model
    if args.confidence is not None:
        config.confidence_threshold = args.confidence
    if args.classes is not None:
        config.target_classes = args.classes
    if args.no_dilate:
        config.dilate_mask = False
    if args.no_feather:
        config.feather_edges = False
    if args.threads:
        config.num_cpu_threads = args.threads
    
    # Recreate pipeline with updated config
    pipeline = MaskGenerationPipeline(config)
    
    # Progress callback for verbose mode
    if args.verbose and not batch_mode:
        pipeline.set_progress_callback(
            lambda msg, prog: print(f"[{prog*100:5.1f}%] {msg}")
        )
    
    print(f"Preset: {args.preset}")
    print(f"Views: {config.num_horizontal_views} horizontal x {config.num_pitch_levels} pitch")
    print(f"Model: {config.model_name}")
    print()
    
    # Handle batch mode
    if batch_mode:
        process_batch(config, folder_path, args)
        return
    
    # Single file mode
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.stem) + "_mask.png"
    
    print(f"Processing: {input_path}")
    print(f"Output: {output_path}")
    print()
    
    # Load image
    image = cv2.imread(str(input_path))
    if image is None:
        print(f"Error: Could not load image: {input_path}")
        sys.exit(1)
    
    # Process
    try:
        result = pipeline.process(image)
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)
    
    # Save mask
    result.save_mask(output_path)
    print(f"\nSaved mask to: {output_path}")
    
    # Save overlay if requested
    if args.save_overlay:
        overlay = image.copy()
        opacity = 0.5
        mask = result.mask
        mask_3ch = (mask[:, :, None] * [0, 0, 255]).astype(np.uint8)
        overlay = (overlay * (1 - opacity * mask[:, :, None]) + 
                  mask_3ch * opacity).astype(np.uint8)
        cv2.imwrite(args.save_overlay, overlay)
        print(f"Saved overlay to: {args.save_overlay}")
    
    # Save views if requested
    if args.save_views:
        views_image = pipeline.visualize_views(
            result.perspective_views,
            result.segmentation_results
        )
        cv2.imwrite(args.save_views, views_image)
        print(f"Saved views to: {args.save_views}")
    
    # Print summary
    summary = pipeline.get_detection_summary(result)
    print(f"\nResults:")
    print(f"  Total detections: {summary['total_detections']}")
    print(f"  Class breakdown: {summary['class_counts']}")
    print(f"  Average confidence: {summary['avg_confidence']:.2f}")
    print(f"  Mask coverage: {summary['mask_coverage']:.1f}%")
    print(f"  Processing time: {summary['processing_time']:.1f}s")


if __name__ == "__main__":
    import numpy as np  # Import here for overlay generation
    main()

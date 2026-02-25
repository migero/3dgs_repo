#!/usr/bin/env python3
"""
Command-line interface for Fisheye Mask Generator.

Processes dual fisheye images (185° FOV) from max2sphere.py output.

Usage:
    python cli.py front_fisheye.jpg -o front_mask.png
    python cli.py front_fisheye.jpg --preset fast
    python cli.py --batch /path/to/fisheye/folder
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
import numpy as np

from core.pipeline import (
    FisheyeMaskGenerationPipeline, PipelineConfig, FisheyeBatchProcessor
)
from core.fisheye_converter import find_fisheye_pair, get_mask_output_paths
from core.yolo_segmenter import DEFAULT_MOVING_CLASSES


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate segmentation masks for moving objects in dual fisheye images (185° FOV)."
    )
    
    parser.add_argument(
        "input",
        nargs='?',
        default=None,
        help="Input front fisheye image file (back will be auto-detected)"
    )
    
    parser.add_argument(
        "--back",
        default=None,
        help="Manually specify the back fisheye image (optional, auto-detected by default)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output front mask file (default: input_mask.png, back mask auto-named)"
    )
    
    parser.add_argument(
        "--batch",
        default=None,
        help="Process all fisheye pairs in a folder. Masks saved with _mask suffix."
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
        help="Number of horizontal perspective views (default: 6)"
    )
    
    parser.add_argument(
        "--pitch-levels",
        type=int,
        default=None,
        help="Number of pitch levels (default: 2)"
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
        help="YOLO model to use (default: yolo11l-seg.pt)"
    )
    
    parser.add_argument(
        "--confidence",
        type=float,
        default=None,
        help="Detection confidence threshold (default: 0.35)"
    )
    
    parser.add_argument(
        "--classes",
        nargs="+",
        default=None,
        help="Target classes to detect (default: person, backpack, handbag, suitcase)"
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
        "--save-equirect",
        default=None,
        help="Save intermediate equirectangular image to file"
    )
    
    parser.add_argument(
        "--save-equirect-mask",
        default=None,
        help="Save intermediate equirectangular mask to file"
    )
    
    parser.add_argument(
        "--save-overlay",
        default=None,
        help="Save overlay visualization to file (on equirectangular)"
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
        help="Number of CPU threads for perspective/stitching work (default: auto)"
    )
    
    return parser.parse_args()


def create_config_from_preset(preset: str) -> PipelineConfig:
    """Create a pipeline config based on preset name."""
    if preset == "fast":
        return PipelineConfig(
            num_horizontal_views=4,
            num_pitch_levels=1,
            model_name="yolo11n-seg.pt",
            view_size=(640, 640)
        )
    elif preset == "accurate":
        return PipelineConfig(
            num_horizontal_views=8,
            num_pitch_levels=2,
            model_name="yolo11x-seg.pt",
            view_size=(1024, 1024),
            fov=90.0
        )
    else:  # default
        return PipelineConfig(
            num_horizontal_views=6,
            num_pitch_levels=2,
            model_name="yolo11l-seg.pt",
            view_size=(1024, 1024)
        )


def process_batch(config, folder_path, args):
    """Process all fisheye pairs in a folder using parallel workers."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        print(f"Error: Folder not found: {folder_path}")
        sys.exit(1)
    
    # Create batch processor
    num_workers = args.workers
    batch_processor = FisheyeBatchProcessor(config, num_workers=num_workers)
    
    # Find pairs
    pairs = batch_processor.find_fisheye_pairs(folder_path)
    
    if not pairs:
        print(f"No fisheye pairs found in: {folder_path}")
        print("\nExpected naming conventions:")
        print("  - frame0001_fisheye_front.jpg / frame0001_fisheye_back.jpg")
        print("  - image_front.png / image_back.png")
        print("  - lens0_0001.jpg / lens1_0001.jpg")
        return
    
    print(f"Found {len(pairs)} fisheye pairs to process")
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
    print(f"  Total pairs: {summary['total']}")
    if summary.get('skipped', 0) > 0:
        print(f"  Skipped (already have masks): {summary['skipped']}")
    print(f"  Processed: {summary['successful']}/{summary.get('processed', summary['total'])} pairs")
    print(f"  Failed: {summary['failed']}")
    print(f"  Total time: {summary['total_time']:.1f}s")
    if summary['successful'] > 0:
        print(f"  Average time per pair: {summary['avg_time']:.1f}s")


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
    
    # Create config based on preset
    config = create_config_from_preset(args.preset)
    
    # Override config with command-line arguments
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
    
    print(f"Fisheye Mask Generator")
    print(f"Preset: {args.preset}")
    print(f"Views: {config.num_horizontal_views} horizontal x {config.num_pitch_levels} pitch")
    print(f"Model: {config.model_name}")
    print()
    
    # Handle batch mode
    if batch_mode:
        process_batch(config, folder_path, args)
        return
    
    # Single file mode - find back fisheye
    if args.back:
        back_path = Path(args.back)
    else:
        back_path = find_fisheye_pair(str(input_path))
        if back_path is None:
            print(f"Error: Could not find matching back fisheye image for: {input_path}")
            print("Use --back to specify the back image manually.")
            sys.exit(1)
        back_path = Path(back_path)
    
    if not back_path.exists():
        print(f"Error: Back fisheye file not found: {back_path}")
        sys.exit(1)
    
    # Determine output paths
    if args.output:
        front_mask_path = args.output
        # Derive back mask path from front mask path
        front_p = Path(front_mask_path)
        back_mask_path = str(front_p.parent / f"{front_p.stem.replace('front', 'back')}{front_p.suffix}")
    else:
        front_mask_path, back_mask_path = get_mask_output_paths(str(input_path), str(back_path))
    
    print(f"Processing fisheye pair:")
    print(f"  Front: {input_path}")
    print(f"  Back:  {back_path}")
    print(f"Output masks:")
    print(f"  Front: {front_mask_path}")
    print(f"  Back:  {back_mask_path}")
    print()
    
    # Load images
    front_image = cv2.imread(str(input_path))
    back_image = cv2.imread(str(back_path))
    
    if front_image is None:
        print(f"Error: Could not load front image: {input_path}")
        sys.exit(1)
    if back_image is None:
        print(f"Error: Could not load back image: {back_path}")
        sys.exit(1)
    
    # Create pipeline
    pipeline = FisheyeMaskGenerationPipeline(config)
    
    # Progress callback for verbose mode
    if args.verbose:
        pipeline.set_progress_callback(
            lambda msg, prog: print(f"[{prog*100:5.1f}%] {msg}")
        )
    
    # Process
    try:
        result = pipeline.process(front_image, back_image)
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Save masks
    result.save_masks(front_mask_path, back_mask_path)
    print(f"\nSaved masks:")
    print(f"  Front: {front_mask_path}")
    print(f"  Back:  {back_mask_path}")
    
    # Save intermediate equirectangular if requested
    if args.save_equirect:
        cv2.imwrite(args.save_equirect, result.equirect_image)
        print(f"Saved equirectangular: {args.save_equirect}")
    
    if args.save_equirect_mask:
        mask_uint8 = (result.equirect_mask * 255).astype(np.uint8)
        cv2.imwrite(args.save_equirect_mask, mask_uint8)
        print(f"Saved equirectangular mask: {args.save_equirect_mask}")
    
    # Save overlay if requested
    if args.save_overlay:
        overlay = result.equirect_image.copy()
        opacity = 0.5
        mask = result.equirect_mask
        mask_3ch = (mask[:, :, None] * [0, 0, 255]).astype(np.uint8)
        overlay = (overlay * (1 - opacity * mask[:, :, None]) + 
                  mask_3ch * opacity).astype(np.uint8)
        cv2.imwrite(args.save_overlay, overlay)
        print(f"Saved overlay: {args.save_overlay}")
    
    # Save views if requested
    if args.save_views:
        views_image = pipeline.visualize_views(
            result.perspective_views,
            result.segmentation_results
        )
        cv2.imwrite(args.save_views, views_image)
        print(f"Saved views: {args.save_views}")
    
    # Print summary
    summary = pipeline.get_detection_summary(result)
    print(f"\nResults:")
    print(f"  Total detections: {summary['total_detections']}")
    print(f"  Class breakdown: {summary['class_counts']}")
    print(f"  Average confidence: {summary['avg_confidence']:.2f}")
    print(f"  Front mask coverage: {summary['front_mask_coverage']:.1f}%")
    print(f"  Back mask coverage: {summary['back_mask_coverage']:.1f}%")
    print(f"  Processing time: {summary['processing_time']:.1f}s")


if __name__ == "__main__":
    main()

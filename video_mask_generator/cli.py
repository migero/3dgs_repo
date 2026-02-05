#!/usr/bin/env python3
"""
Command-line interface for Video Mask Generator.

Usage:
    python cli.py video.mp4 --output-dir masks/
    python cli.py video.mp4 --fps 1 --model yolo11l-seg.pt
    python cli.py image.jpg --output mask.png
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.video_processor import VideoMaskProcessor, ProcessorConfig
from core.yolo_segmenter import COCO_CLASSES, DEFAULT_MOVING_CLASSES


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate segmentation masks for videos/images using YOLO",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a video, extract 1 frame per second
  python cli.py video.mp4 --output-dir masks/ --fps 1
  
  # Process with larger model for better accuracy
  python cli.py video.mp4 --output-dir masks/ --model yolo11l-seg.pt
  
  # Process single image
  python cli.py image.jpg --output mask.png
  
  # Custom confidence threshold
  python cli.py video.mp4 --output-dir masks/ --confidence 0.5
  
  # Detect only people
  python cli.py video.mp4 --output-dir masks/ --classes person
        """
    )
    
    parser.add_argument(
        "input",
        help="Input video or image file"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for masks (for video processing)"
    )
    
    parser.add_argument(
        "--output",
        help="Output file path (for single image processing)"
    )
    
    parser.add_argument(
        "--fps",
        type=float,
        default=1.0,
        help="Frames per second to extract (default: 1.0)"
    )
    
    parser.add_argument(
        "--model",
        default="yolo11n-seg.pt",
        help="YOLO model to use (default: yolo11n-seg.pt)"
    )
    
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.35,
        help="Confidence threshold (default: 0.35)"
    )
    
    parser.add_argument(
        "--classes",
        nargs="+",
        help="Classes to detect (default: person, car, etc.)"
    )
    
    parser.add_argument(
        "--dilate",
        action="store_true",
        default=True,
        help="Dilate masks (default: True)"
    )
    
    parser.add_argument(
        "--no-dilate",
        action="store_true",
        help="Disable mask dilation"
    )
    
    parser.add_argument(
        "--feather",
        action="store_true",
        default=True,
        help="Feather mask edges (default: True)"
    )
    
    parser.add_argument(
        "--no-feather",
        action="store_true",
        help="Disable edge feathering"
    )
    
    parser.add_argument(
        "--save-overlay",
        action="store_true",
        help="Also save overlay visualization"
    )
    
    parser.add_argument(
        "--device",
        help="Device to use (cuda, cpu, etc.)"
    )
    
    parser.add_argument(
        "--list-classes",
        action="store_true",
        help="List all available COCO classes and exit"
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # List classes if requested
    if args.list_classes:
        print("Available COCO classes:")
        for i, cls in enumerate(COCO_CLASSES):
            marker = " *" if cls in DEFAULT_MOVING_CLASSES else ""
            print(f"  {i:2d}: {cls}{marker}")
        print("\n* = Default moving object classes")
        return 0
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    # Determine if video or image
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v'}
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    ext = input_path.suffix.lower()
    is_video = ext in video_extensions
    is_image = ext in image_extensions
    
    if not is_video and not is_image:
        print(f"Error: Unsupported file format: {ext}")
        print(f"Supported video formats: {', '.join(video_extensions)}")
        print(f"Supported image formats: {', '.join(image_extensions)}")
        return 1
    
    # Create config
    config = ProcessorConfig(
        model_name=args.model,
        target_classes=args.classes or DEFAULT_MOVING_CLASSES,
        confidence_threshold=args.confidence,
        device=args.device,
        dilate_mask=not args.no_dilate,
        feather_edges=not args.no_feather,
        fps=args.fps,
        save_overlay=args.save_overlay
    )
    
    # Create processor
    processor = VideoMaskProcessor(config)
    
    if is_video:
        # Video processing
        output_dir = args.output_dir or str(input_path.stem) + "_masks"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Processing video: {args.input}")
        print(f"Output directory: {output_dir}")
        print(f"FPS: {args.fps}")
        print(f"Model: {args.model}")
        print()
        
        def progress_callback(msg, progress, frame_num, total_frames):
            bar_width = 40
            filled = int(bar_width * progress)
            bar = "█" * filled + "░" * (bar_width - filled)
            print(f"\r[{bar}] {progress*100:5.1f}% - Frame {frame_num}/{total_frames}", end="")
            sys.stdout.flush()
        
        result = processor.process_video(
            str(input_path),
            output_dir,
            progress_callback=progress_callback
        )
        
        print()
        print()
        print(f"✓ Processing complete!")
        print(f"  Total frames: {result['total_frames']}")
        print(f"  Frames with detections: {result['frames_with_detections']}")
        print(f"  Total detections: {result['total_detections']}")
        print(f"  Processing time: {result['processing_time']:.1f}s")
        print(f"  Output: {output_dir}")
        
    else:
        # Single image processing
        import cv2
        
        output_path = args.output or str(input_path.stem) + "_mask.png"
        
        print(f"Processing image: {args.input}")
        print(f"Output: {output_path}")
        print(f"Model: {args.model}")
        print()
        
        # Load image
        image = cv2.imread(str(input_path))
        if image is None:
            print(f"Error: Could not load image: {args.input}")
            return 1
        
        # Process
        result = processor.process_image(image)
        
        # Save mask
        mask_uint8 = (result.mask * 255).astype('uint8')
        cv2.imwrite(output_path, mask_uint8)
        
        print(f"✓ Processing complete!")
        print(f"  Detections: {len(result.class_names)}")
        if result.class_names:
            print(f"  Classes: {', '.join(result.class_names)}")
        print(f"  Output: {output_path}")
        
        # Save overlay if requested
        if args.save_overlay:
            overlay = processor.create_overlay(image, result)
            overlay_path = str(input_path.stem) + "_overlay.png"
            cv2.imwrite(overlay_path, overlay)
            print(f"  Overlay: {overlay_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
360 Motion Deblur - Command Line Interface
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.video_pipeline import VideoPipeline, PipelineConfig, get_video_info
from core.cube_projector import CubeProjector


def main():
    parser = argparse.ArgumentParser(
        description="Apply motion deblurring to 360° equirectangular videos using PVDNet"
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Input video path'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output video path (default: input_deblurred.mp4)'
    )
    
    parser.add_argument(
        '-r', '--resolution',
        type=int,
        default=1024,
        choices=[512, 640, 768, 1024, 1280, 1536],
        help='Cube face resolution (default: 1024)'
    )
    
    parser.add_argument(
        '-c', '--checkpoint',
        type=str,
        default='ckpt/PVDNet_DVD.pytorch',
        help='Path to PVDNet checkpoint (default: ckpt/PVDNet_DVD.pytorch)'
    )
    
    parser.add_argument(
        '--large-model',
        action='store_true',
        help='Use large PVDNet model (more accurate, slower)'
    )
    
    parser.add_argument(
        '--codec',
        type=str,
        default='libx264',
        choices=['libx264', 'libx265', 'libvpx-vp9'],
        help='Output video codec (default: libx264)'
    )
    
    parser.add_argument(
        '--quality',
        type=int,
        default=18,
        help='Output quality CRF (0-51, lower=better, default: 18)'
    )
    
    parser.add_argument(
        '--preset',
        type=str,
        default='medium',
        choices=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 
                 'medium', 'slow', 'slower', 'veryslow'],
        help='Encoding preset (default: medium)'
    )
    
    parser.add_argument(
        '--buffer-size',
        type=int,
        default=30,
        help='Frame buffer size (default: 30)'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show video information only'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Show video info if requested
    if args.info:
        info = get_video_info(args.input)
        if info:
            print(f"Video: {args.input}")
            print(f"  Resolution: {info['width']}x{info['height']}")
            print(f"  FPS: {info['fps']:.2f}")
            print(f"  Frames: {info['frame_count']}")
            print(f"  Duration: {info['duration']:.1f}s")
        else:
            print(f"Error: Could not read video info")
        sys.exit(0)
    
    # Set output path
    output_path = args.output
    if not output_path:
        base = os.path.splitext(args.input)[0]
        output_path = f"{base}_deblurred.mp4"
    
    print(f"Input: {args.input}")
    print(f"Output: {output_path}")
    print(f"Resolution: {args.resolution}px")
    print(f"Checkpoint: {args.checkpoint}")
    print()
    
    # Create pipeline config
    config = PipelineConfig(
        cube_face_size=args.resolution,
        checkpoint_path=args.checkpoint,
        use_large_model=args.large_model,
        frame_buffer_size=args.buffer_size,
        output_codec=args.codec,
        output_quality=args.quality,
        output_preset=args.preset
    )
    
    # Create pipeline
    pipeline = VideoPipeline(config)
    
    # Set progress callback
    def on_progress(stats):
        if stats.total_frames > 0:
            pct = (stats.processed_frames / stats.total_frames) * 100
            print(f"\r{stats.status} [{pct:.1f}%] "
                  f"FPS: {stats.fps:.1f} ETA: {stats.estimated_remaining:.0f}s", 
                  end='', flush=True)
    
    pipeline.set_progress_callback(on_progress)
    
    # Process video
    print("Starting deblurring...")
    success = pipeline.process_video(args.input, output_path)
    print()
    
    if success:
        print(f"✅ Successfully saved to: {output_path}")
    else:
        print(f"❌ Processing failed")
        sys.exit(1)


if __name__ == '__main__':
    main()

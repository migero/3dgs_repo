#!/usr/bin/env python3
"""
Combined 360 Video Processing App

Combines frame extraction, geolocation, and mask generation for 360 videos.

Workflow:
1. Extract best frames from MP4 using adaptive quality detection
2. Geolocate frames using KML path and write GPS to EXIF
3. Generate segmentation masks for moving objects in 360 images

Usage:
    python combined_app.py video.mp4 path.kml --fps 1.0 --preset fast
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path
import shutil
import cv2
import numpy as np

# Add paths for imports
sys.path.insert(0, 'frame_quality_detector')

# Import frame extractor
from core.adaptive_frame_extractor import AdaptiveFrameExtractor


class Combined360Processor:
    """Combined processor for 360 video frame extraction, geolocation, and masking."""

    def __init__(self, verbose=False):
        self.verbose = verbose

    def process_video(self, video_path, kml_path, fps=1.0, mask_preset="default",
                     mask_views=12, mask_pitch_levels=1, mask_model=None, mask_confidence=0.25,
                     start_offset=0.0, end_offset=0.0, reverse_direction=False):
        """
        Process a 360 video through the complete pipeline.

        Args:
            video_path: Path to MP4 video
            kml_path: Path to KML file for geolocation (optional)
            fps: Target frames per second for extraction
            mask_preset: Mask generation preset ("default", "fast", "accurate")
            mask_views: Number of horizontal views for mask generation
            mask_pitch_levels: Number of pitch levels for mask generation
            mask_model: YOLO model for mask generation
            mask_confidence: Confidence threshold for detection
            start_offset: Skip meters at start of path
            end_offset: Skip meters at end of path
            reverse_direction: Reverse photo order if going opposite to KML
        """
        video_path = Path(video_path)
        if kml_path:
            kml_path = Path(kml_path)

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if kml_path and not kml_path.exists():
            raise FileNotFoundError(f"KML file not found: {kml_path}")

        # Create output directory next to video
        output_dir = video_path.parent / video_path.stem
        output_dir.mkdir(exist_ok=True)

        images_dir = output_dir / "images"
        masks_dir = output_dir / "masks"
        images_dir.mkdir(exist_ok=True)
        masks_dir.mkdir(exist_ok=True)

        if self.verbose:
            print(f"Output directory: {output_dir}")
            print(f"Images will be saved to: {images_dir}")
            print(f"Masks will be saved to: {masks_dir}")
            if not kml_path:
                print("No KML provided - skipping geolocation")

        # Step 1: Extract frames
        if self.verbose:
            print("\n=== STEP 1: Extracting Frames ===")

        print("DEBUG: About to call _extract_frames")
        frame_files = self._extract_frames(video_path, images_dir, fps)
        print(f"DEBUG: _extract_frames returned {len(frame_files)} files")

        if not frame_files:
            raise RuntimeError("No frames were extracted")

        if self.verbose:
            print(f"Extracted {len(frame_files)} frames")

        # Step 2: Geolocate frames (if KML provided)
        if kml_path:
            if self.verbose:
                print("\n=== STEP 2: Geolocating Frames ===")

            print("DEBUG: About to call _geolocate_frames")
            self._geolocate_frames(images_dir, kml_path, start_offset, end_offset, reverse_direction)
            print("DEBUG: _geolocate_frames completed")
        else:
            if self.verbose:
                print("\n=== STEP 2: Geolocation Skipped (no KML provided) ===")

        # Step 3: Generate masks
        if self.verbose:
            print("\n=== STEP 3: Generating Masks ===")

        print("DEBUG: About to call _generate_masks")
        self._generate_masks(images_dir, masks_dir, mask_preset, mask_views, mask_pitch_levels, mask_model, mask_confidence)
        print("DEBUG: _generate_masks completed")

        if self.verbose:
            print("\n=== Processing Complete ===")
            print(f"Results saved to: {output_dir}")

        return str(output_dir)

    def _extract_frames(self, video_path, output_dir, fps):
        """Extract frames using adaptive quality detection."""
        print(f"DEBUG: Starting frame extraction")
        print(f"DEBUG: Video path: {video_path}")
        print(f"DEBUG: Output directory: {output_dir}")
        print(f"DEBUG: Target FPS: {fps}")

        # Create extractor that always picks the best available frame
        print("DEBUG: Creating AdaptiveFrameExtractor...")
        extractor = AdaptiveFrameExtractor(quality_threshold=0.0, verbose=self.verbose)

        # Extract frames
        print("DEBUG: Calling extract_adaptive_frames...")
        extractor.extract_adaptive_frames(str(video_path), str(output_dir), fps)

        # Get list of extracted frame files
        frame_files = sorted(output_dir.glob("*.jpg"))
        print(f"DEBUG: Frame extraction completed. Found {len(frame_files)} frame files")

        return frame_files

    def _geolocate_frames(self, images_dir, kml_path, start_offset, end_offset, reverse_direction):
        """Geolocate frames using KML path and write GPS to EXIF."""
        print(f"DEBUG: Starting geolocation with KML: {kml_path}")
        print(f"DEBUG: Images directory: {images_dir}")
        print(f"DEBUG: Parameters: start_offset={start_offset}, end_offset={end_offset}, reverse={reverse_direction}")

        cmd = [
            sys.executable, "360_geolocator/cli.py",
            str(kml_path), str(images_dir),
            "--write-exif", "--no-backup",
            "--start-offset", str(start_offset),
            "--end-offset", str(end_offset)
        ]

        if reverse_direction:
            cmd.append("--reverse")

        if self.verbose:
            cmd.append("--verbose")
            print(f"DEBUG: Running geolocator command: {' '.join(cmd)}")

        print("DEBUG: Executing geolocator subprocess...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout

        print(f"DEBUG: Geolocator subprocess completed with return code: {result.returncode}")
        print(f"DEBUG: STDOUT length: {len(result.stdout)}")
        print(f"DEBUG: STDERR length: {len(result.stderr)}")

        if result.returncode != 0:
            print(f"DEBUG: Geolocator failed. STDERR: {result.stderr}")
            raise RuntimeError(f"Geolocation failed: {result.stderr}")

        if self.verbose:
            print("DEBUG: Geolocator output:")
            print(result.stdout)

        print("DEBUG: Geolocation step completed successfully")

    def _generate_masks(self, images_dir, masks_dir, preset, views, pitch_levels, model, confidence):
        """Generate segmentation masks for 360 images."""
        print(f"DEBUG: Starting mask generation")
        print(f"DEBUG: Images directory: {images_dir}")
        print(f"DEBUG: Masks directory: {masks_dir}")
        print(f"DEBUG: Parameters: preset={preset}, views={views}, pitch_levels={pitch_levels}, model={model}, confidence={confidence}")

        cmd = [
            sys.executable, "360_mask_generator/cli.py",
            "--batch", str(images_dir),
            "--preset", preset,
            "--views", str(views),
            "--pitch-levels", str(pitch_levels),
            "--confidence", str(confidence)
        ]

        if model:
            cmd.extend(["--model", model])

        if self.verbose:
            cmd.append("--verbose")
            print(f"DEBUG: Running mask generator command: {' '.join(cmd)}")

        print("DEBUG: Executing mask generator subprocess...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 minute timeout

        print(f"DEBUG: Mask generator subprocess completed with return code: {result.returncode}")
        print(f"DEBUG: STDOUT length: {len(result.stdout)}")
        print(f"DEBUG: STDERR length: {len(result.stderr)}")

        if result.returncode != 0:
            print(f"DEBUG: Mask generator failed. STDERR: {result.stderr}")
            raise RuntimeError(f"Mask generation failed: {result.stderr}")

        if self.verbose:
            print("DEBUG: Mask generator output:")
            print(result.stdout)

        print("DEBUG: Moving and inverting masks...")
        # Move mask files to masks directory and invert them
        mask_files = list(images_dir.glob("*_mask.png"))
        print(f"DEBUG: Found {len(mask_files)} mask files to process")

        for i, mask_path in enumerate(mask_files):
            print(f"DEBUG: Processing mask {i+1}/{len(mask_files)}: {mask_path.name}")
            # Invert the mask
            mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
            if mask is not None:
                inverted = 255 - mask
                new_path = masks_dir / mask_path.name
                cv2.imwrite(str(new_path), inverted)
                print(f"DEBUG: Saved inverted mask to: {new_path}")
            else:
                print(f"DEBUG: Failed to read mask: {mask_path}")

            # Remove original mask
            mask_path.unlink()
            print(f"DEBUG: Removed original mask: {mask_path}")

        print(f"DEBUG: Mask generation completed. Moved and inverted {len(mask_files)} masks to {masks_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Combined 360 Video Processing: Extract frames, geolocate, and generate masks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic processing with geolocation
  python combined_app.py video.mp4 path.kml

  # Skip geolocation (no KML)
  python combined_app.py video.mp4

  # Custom FPS and fast mask generation
  python combined_app.py video.mp4 path.kml --fps 0.5 --preset fast

  # Advanced settings
  python combined_app.py video.mp4 path.kml --fps 2.0 --views 16 --pitch-levels 3 --confidence 0.3 --reverse
"""
    )

    parser.add_argument("video", help="Input MP4 video file")
    parser.add_argument("kml", nargs='?', default=None, help="KML file containing the path for geolocation (optional)")

    parser.add_argument("--fps", type=float, default=1.0,
                       help="Target frames per second for extraction (default: 1.0)")

    # Mask generation options
    parser.add_argument("--preset", choices=["default", "fast", "accurate"], default="default",
                       help="Mask generation preset (default: default)")
    parser.add_argument("--views", type=int, default=12,
                       help="Number of horizontal views for mask generation (default: 12)")
    parser.add_argument("--pitch-levels", type=int, default=1,
                       help="Number of pitch levels for mask generation (default: 1, horizon only)")
    parser.add_argument("--model", help="YOLO model for mask generation")
    parser.add_argument("--confidence", type=float, default=0.25,
                       help="Detection confidence threshold (default: 0.25)")

    # Geolocation options
    parser.add_argument("--start-offset", type=float, default=0.0,
                       help="Skip this many meters at the start of path")
    parser.add_argument("--end-offset", type=float, default=0.0,
                       help="Skip this many meters at the end of path")
    parser.add_argument("--reverse", action="store_true",
                       help="Reverse photo order if going opposite to KML direction")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Create processor
    processor = Combined360Processor(verbose=args.verbose)

    try:
        result_dir = processor.process_video(
            args.video, args.kml, args.fps, args.preset, args.views, args.pitch_levels,
            args.model, args.confidence, args.start_offset, args.end_offset, args.reverse
        )
        print(f"\nProcessing complete! Results saved to: {result_dir}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
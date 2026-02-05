#!/usr/bin/env python3
"""
Example usage of Frame Quality Detector

This script demonstrates how to use the Frame Quality Detector
both programmatically and through command line interface.
"""

import os
import tempfile
from pathlib import Path

# Import our modules
from frame_quality_detector.core.frame_extractor import FrameExtractor
from frame_quality_detector.core.quality_analyzer import FrameQualityAnalyzer


def example_video_analysis(video_path: str):
    """
    Example of analyzing a video file for best frames.
    
    Args:
        video_path: Path to video file (e.g., 'Shinjuku.webm')
    """
    print(f"Analyzing video: {video_path}")
    print("="*60)
    
    # Step 1: Extract frames
    print("Step 1: Extracting frames...")
    extractor = FrameExtractor(verbose=True)
    
    # Extract 1 frame per second
    frames_dir = extractor.extract_frames(video_path, fps=1.0)
    print(f"Frames extracted to: {frames_dir}")
    
    # Step 2: Analyze frame quality
    print("\nStep 2: Analyzing frame quality...")
    analyzer = FrameQualityAnalyzer(
        sharpness_weight=0.7,
        blur_weight=0.3,
        verbose=True
    )
    
    results = analyzer.analyze_directory(frames_dir, quality_threshold=0.0)
    
    # Step 3: Get best frames
    print(f"\nStep 3: Finding best frames...")
    best_frames = analyzer.get_top_frames(results, top_n=5)
    
    # Step 4: Save results
    print(f"\nStep 4: Saving results...")
    output_dir = Path("best_frames_output")
    output_dir.mkdir(exist_ok=True)
    
    # Save best frames
    analyzer.save_best_frames(best_frames, frames_dir, output_dir)
    
    # Save reports
    analyzer.save_json_report(results, output_dir / 'analysis_report.json')
    analyzer.save_csv_report(results, output_dir / 'analysis_report.csv')
    
    # Print summary
    analyzer.print_text_report(best_frames)
    
    print(f"\nBest frames saved to: {output_dir}")
    print(f"Total frames analyzed: {len(results)}")


def example_frames_analysis(frames_directory: str):
    """
    Example of analyzing pre-extracted frames.
    
    Args:
        frames_directory: Directory containing frame images
    """
    print(f"Analyzing frames in: {frames_directory}")
    print("="*60)
    
    analyzer = FrameQualityAnalyzer(verbose=True)
    
    # Analyze all frames
    results = analyzer.analyze_directory(frames_directory)
    
    # Get top 3 frames
    best_frames = analyzer.get_top_frames(results, top_n=3)
    
    # Print results
    analyzer.print_text_report(best_frames)
    
    return best_frames


def demonstrate_quality_metrics():
    """
    Demonstrate individual quality detection methods.
    """
    print("Quality Detection Methods Demo")
    print("="*60)
    
    # This would work with an actual image file
    sample_image_path = "sample_frame.png"
    
    if not os.path.exists(sample_image_path):
        print("Create a sample image file 'sample_frame.png' to run this demo")
        return
    
    from frame_quality_detector.core.sharpness_detector import SharpnessDetector
    from frame_quality_detector.core.motion_blur_detector import MotionBlurDetector
    import cv2
    
    # Load image
    image = cv2.imread(sample_image_path)
    
    # Test sharpness detection
    sharpness_detector = SharpnessDetector(verbose=True)
    sharpness_metrics = sharpness_detector.analyze_sharpness(image)
    
    print("\nSharpness Analysis Results:")
    for metric, value in sharpness_metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Test motion blur detection
    blur_detector = MotionBlurDetector(verbose=True)
    blur_metrics = blur_detector.analyze_motion_blur(image)
    
    print("\nMotion Blur Analysis Results:")
    for metric, value in blur_metrics.items():
        print(f"  {metric}: {value:.4f}")


def main():
    """
    Main example function - choose which demo to run.
    """
    print("Frame Quality Detector - Example Usage")
    print("="*60)
    
    # Example 1: Analyze a video file
    video_file = "Shinjuku.webm"  # Replace with your video file
    
    if os.path.exists(video_file):
        print("Found video file - running video analysis example...")
        example_video_analysis(video_file)
    else:
        print(f"Video file '{video_file}' not found.")
        print("To test with your own video, replace the filename in this script.")
    
    print("\n" + "="*60)
    
    # Example 2: Analyze existing frames directory
    frames_dir = "extracted_frames"  # Replace with your frames directory
    
    if os.path.isdir(frames_dir):
        print("Found frames directory - running frames analysis example...")
        example_frames_analysis(frames_dir)
    else:
        print(f"Frames directory '{frames_dir}' not found.")
        print("To test with existing frames, create a directory with image files.")
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("\nTo run the GUI application:")
    print("  python main.py")
    print("\nTo use the command line interface:")
    print("  python cli.py --help")
    print("  python cli.py --video input.webm --top-n 5")
    print("  python cli.py --frames-dir extracted_frames/ --analyze-only")


if __name__ == "__main__":
    main()
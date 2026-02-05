#!/usr/bin/env python3
"""
Command Line Interface for Frame Quality Detector
"""

import argparse
import sys
import os
from pathlib import Path
from core.quality_analyzer import FrameQualityAnalyzer
from core.frame_extractor import FrameExtractor
from core.adaptive_frame_extractor import AdaptiveFrameExtractor


def main():
    parser = argparse.ArgumentParser(
        description='Analyze frames for quality (sharpness and motion blur detection)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --video input.mp4 --output frames/ --top-n 10 --adaptive
  %(prog)s --frames-dir extracted_frames/ --analyze-only
  %(prog)s --video input.webv --fps 0.5 --quality-threshold 80 --adaptive
"""
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--video', type=str, help='Input video file')
    input_group.add_argument('--frames-dir', type=str, help='Directory with extracted frames')
    
    # Output options
    parser.add_argument('--output', type=str, default='quality_frames',
                        help='Output directory for best frames (default: quality_frames)')
    
    # Extraction options
    parser.add_argument('--fps', type=float, default=1.0,
                        help='Frames per second to extract (default: 1.0)')
    parser.add_argument('--adaptive', action='store_true',
                        help='Use adaptive frame extraction (recommended)')
    parser.add_argument('--extraction-quality-threshold', type=float, default=60.0,
                        help='Quality threshold for adaptive extraction (default: 60.0)')
    parser.add_argument('--jpeg-quality', type=int, default=90,
                        help='JPEG quality 1-100 (default: 90)')
    
    # GPS options
    parser.add_argument('--embed-gps', action='store_true', default=True,
                        help='Embed GPS coordinates in JPEG EXIF (default: True)')
    parser.add_argument('--no-gps', action='store_true',
                        help='Disable GPS EXIF embedding')
    parser.add_argument('--extract-gps-only', action='store_true',
                        help='Only extract GPS track from video (no frame extraction)')
    parser.add_argument('--gpx-output', type=str,
                        help='Save GPS track as GPX file')
    
    # Analysis options
    parser.add_argument('--top-n', type=int, default=5,
                        help='Number of best frames to save (default: 5)')
    parser.add_argument('--quality-threshold', type=float, default=0.0,
                        help='Minimum quality score (0-100, default: 0)')
    parser.add_argument('--analyze-only', action='store_true',
                        help='Only analyze existing frames, don\'t extract')
    
    # Output format
    parser.add_argument('--report', choices=['json', 'csv', 'text'], default='text',
                        help='Report format (default: text)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        analyzer = FrameQualityAnalyzer(verbose=args.verbose)
        extractor = FrameExtractor(verbose=args.verbose)
        
        # Handle GPS-only extraction
        if args.extract_gps_only:
            if not args.video:
                print("Error: --extract-gps-only requires --video")
                sys.exit(1)
            
            print(f"Extracting GPS from {args.video}...")
            geo_info = extractor.extract_geolocation(args.video)
            
            print(f"\n=== GPS Information ===")
            print(f"Has location: {geo_info.has_location()}")
            if geo_info.has_location():
                print(f"  Latitude: {geo_info.latitude}")
                print(f"  Longitude: {geo_info.longitude}")
            print(f"Has GPS track: {geo_info.has_gps_track()}")
            if geo_info.has_gps_track():
                print(f"  Track points: {len(geo_info.gps_track)}")
            print(f"Creation time: {geo_info.creation_time}")
            print(f"Camera: {geo_info.camera_model}")
            print(f"Firmware: {geo_info.firmware}")
            
            if args.gpx_output and geo_info.has_gps_track():
                geo_info.save_gpx(args.gpx_output)
                print(f"\nGPX track saved to: {args.gpx_output}")
            
            sys.exit(0)
        
        if args.video and not args.analyze_only:
            # Extract frames from video first
            print(f"Extracting frames from {args.video}...")
            
            embed_gps = not args.no_gps
            
            if args.adaptive:
                # Use adaptive extraction
                adaptive_extractor = AdaptiveFrameExtractor(
                    quality_threshold=args.extraction_quality_threshold,
                    verbose=args.verbose
                )
                temp_frames_dir = adaptive_extractor.extract_adaptive_frames(
                    args.video, 
                    output_dir=args.output + "_temp",
                    target_fps=args.fps,
                    jpeg_quality=args.jpeg_quality
                )
                
                # Embed GPS in extracted frames if requested
                if embed_gps:
                    geo_info = extractor.extract_geolocation(args.video)
                    if geo_info.has_gps_track() or geo_info.has_location():
                        frame_files = extractor.get_frame_files(temp_frames_dir)
                        video_info = extractor.get_video_info(args.video)
                        video_fps = video_info['fps']
                        frame_interval = int(video_fps / args.fps) if args.fps > 0 else 1
                        
                        gps_written = 0
                        for i, frame_path in enumerate(frame_files):
                            original_frame_num = i * frame_interval
                            gps = geo_info.get_gps_for_frame(original_frame_num)
                            if gps:
                                frame_time = None
                                if geo_info.creation_time:
                                    from datetime import timedelta
                                    frame_time = geo_info.creation_time + timedelta(seconds=gps.timestamp)
                                if extractor.write_gps_exif(frame_path, gps, frame_time):
                                    gps_written += 1
                        
                        if args.verbose:
                            print(f"Embedded GPS EXIF in {gps_written}/{len(frame_files)} frames")
                    
                    # Save GPX if requested
                    if args.gpx_output and geo_info.has_gps_track():
                        geo_info.save_gpx(args.gpx_output)
                        print(f"GPX track saved to: {args.gpx_output}")
            else:
                # Use regular extraction with GPS
                if embed_gps:
                    temp_frames_dir, frame_gps = extractor.extract_frames_with_gps(
                        args.video, 
                        fps=args.fps,
                        jpeg_quality=args.jpeg_quality,
                        embed_gps=True
                    )
                    
                    # Get geo_info for GPX export
                    if args.gpx_output:
                        geo_info = extractor.extract_geolocation(args.video)
                        if geo_info.has_gps_track():
                            geo_info.save_gpx(args.gpx_output)
                            print(f"GPX track saved to: {args.gpx_output}")
                else:
                    temp_frames_dir = extractor.extract_frames(
                        args.video, 
                        fps=args.fps,
                        jpeg_quality=args.jpeg_quality
                    )
            
            frames_dir = temp_frames_dir
        elif args.frames_dir:
            frames_dir = args.frames_dir
        else:
            print("Error: Must provide either --video or --frames-dir")
            sys.exit(1)
        
        # Analyze frame quality
        print(f"Analyzing frames in {frames_dir}...")
        results = analyzer.analyze_directory(
            frames_dir,
            quality_threshold=args.quality_threshold
        )
        
        # Get top N frames
        best_frames = analyzer.get_top_frames(results, args.top_n)
        
        # Create output directory
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Copy best frames
        analyzer.save_best_frames(best_frames, frames_dir, output_path)
        
        # Generate report
        if args.report == 'json':
            analyzer.save_json_report(results, output_path / 'quality_report.json')
        elif args.report == 'csv':
            analyzer.save_csv_report(results, output_path / 'quality_report.csv')
        else:
            analyzer.print_text_report(best_frames)
        
        print(f"\nBest {len(best_frames)} frames saved to {output_path}")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
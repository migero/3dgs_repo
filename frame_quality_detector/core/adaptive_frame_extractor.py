#!/usr/bin/env python3
"""
Adaptive Frame Extractor

Extracts frames intelligently by checking nearby frames when the target frame
doesn't meet quality requirements.
"""

import os
import cv2
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
from tqdm import tqdm

from .quality_analyzer import FrameQualityAnalyzer


class AdaptiveFrameExtractor:
    """Extracts frames with adaptive quality-based selection."""
    
    def __init__(self, quality_threshold: float = 60.0, verbose: bool = False):
        """
        Initialize adaptive frame extractor.
        
        Args:
            quality_threshold: Minimum quality score to accept a frame
            verbose: Enable verbose output
        """
        self.quality_threshold = quality_threshold
        self.verbose = verbose
        self.analyzer = FrameQualityAnalyzer(verbose=False)
    
    def extract_adaptive_frames(self, video_path: str, output_dir: str, 
                              target_fps: float = 1.0, jpeg_quality: int = 90) -> str:
        """
        Extract frames with adaptive quality selection.
        
        For each target frame position:
        1. Check the frame at that position
        2. If quality < threshold, check nearby frames (forward/backward)
        3. Select the best frame within the search window
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save frames
            target_fps: Target frames per second for extraction
            jpeg_quality: JPEG quality (1-100, default 90)
            
        Returns:
            Path to output directory
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video: {video_path}")
        
        # Get video properties
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if video_fps <= 0:
            raise RuntimeError("Could not determine video FPS")
        
        # Calculate frame interval and search window
        frame_interval = int(video_fps / target_fps)
        max_search_radius = max(1, frame_interval // 2)  # Half the interval
        
        if self.verbose:
            print(f"Video FPS: {video_fps}")
            print(f"Target FPS: {target_fps}")
            print(f"Frame interval: {frame_interval}")
            print(f"Max search radius: {max_search_radius}")
            print(f"Quality threshold: {self.quality_threshold}")
        
        # Generate target frame positions
        target_positions = list(range(0, total_frames, frame_interval))
        
        if self.verbose:
            print(f"Target positions: {len(target_positions)} frames")
        
        extracted_frames = []
        pbar = tqdm(target_positions, desc="Extracting adaptive frames") if self.verbose else None
        
        for i, target_pos in enumerate(target_positions):
            if pbar:
                pbar.update(1)
            
            best_frame_data = self._find_best_frame_around_position(
                cap, target_pos, max_search_radius, total_frames
            )
            
            if best_frame_data is not None:
                # Save the best frame as JPEG
                frame, frame_pos, quality_score = best_frame_data
                output_path = os.path.join(output_dir, f'frame_{i:05d}_pos{frame_pos:06d}_q{quality_score:.1f}.jpg')
                cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
                extracted_frames.append({
                    'target_position': target_pos,
                    'actual_position': frame_pos,
                    'quality_score': quality_score,
                    'filename': os.path.basename(output_path)
                })
                
                if self.verbose and len(extracted_frames) % 10 == 0:
                    avg_quality = np.mean([f['quality_score'] for f in extracted_frames])
                    print(f"Extracted {len(extracted_frames)} frames, avg quality: {avg_quality:.2f}")
            
            elif self.verbose:
                print(f"No suitable frame found around position {target_pos}")
        
        if pbar:
            pbar.close()
        
        cap.release()
        
        if self.verbose:
            avg_quality = np.mean([f['quality_score'] for f in extracted_frames]) if extracted_frames else 0
            print(f"Adaptive extraction complete:")
            print(f"  Extracted: {len(extracted_frames)}/{len(target_positions)} frames")
            print(f"  Average quality: {avg_quality:.2f}")
            print(f"  Frames saved to: {output_dir}")
        
        return output_dir
    
    def _find_best_frame_around_position(self, cap: cv2.VideoCapture, 
                                       target_pos: int, max_radius: int, 
                                       total_frames: int) -> Optional[Tuple[np.ndarray, int, float]]:
        """
        Find the best quality frame around a target position.
        
        Search pattern: target, target+1, target-1, target+2, target-2, etc.
        
        Args:
            cap: Video capture object
            target_pos: Target frame position
            max_radius: Maximum search radius
            total_frames: Total frames in video
            
        Returns:
            Tuple of (frame, position, quality_score) or None if no suitable frame
        """
        best_frame = None
        best_position = None
        best_quality = 0.0
        
        # Search positions in order: 0, +1, -1, +2, -2, ...
        search_positions = [target_pos]  # Start with target position
        
        for offset in range(1, max_radius + 1):
            if target_pos + offset < total_frames:
                search_positions.append(target_pos + offset)
            if target_pos - offset >= 0:
                search_positions.append(target_pos - offset)
        
        for pos in search_positions:
            # Read frame at position
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ret, frame = cap.read()
            
            if not ret or frame is None:
                continue
            
            try:
                # Quick quality analysis (just use combined metrics)
                quality_score = self._quick_quality_check(frame)
                
                # If this frame meets threshold, use it immediately
                if quality_score >= self.quality_threshold:
                    if self.verbose and pos != target_pos:
                        print(f"Found good frame at offset {pos - target_pos} (pos {pos}, quality {quality_score:.2f})")
                    return frame.copy(), pos, quality_score
                
                # Keep track of best frame found so far
                if quality_score > best_quality:
                    best_frame = frame.copy()
                    best_position = pos
                    best_quality = quality_score
                    
            except Exception as e:
                if self.verbose:
                    print(f"Error analyzing frame at position {pos}: {e}")
                continue
        
        # If no frame met threshold, return the best one found
        if best_frame is not None:
            if self.verbose and best_position != target_pos:
                print(f"Best available frame at offset {best_position - target_pos} (pos {best_position}, quality {best_quality:.2f})")
            return best_frame, best_position, best_quality
        
        return None
    
    def _quick_quality_check(self, frame: np.ndarray) -> float:
        """
        Perform a quick quality check on a frame.
        
        Uses a simplified version of the full quality analysis for speed.
        
        Args:
            frame: Input frame
            
        Returns:
            Quality score (0-100)
        """
        # Convert to grayscale
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        # Quick sharpness metrics
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_var = laplacian.var()
        
        # Quick gradient metric
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_mag = np.mean(np.sqrt(grad_x**2 + grad_y**2))
        
        # Simple blur detection (edge sharpness)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
        
        # Combine metrics into quality score
        sharpness_score = min(laplacian_var / 1000, 1.0) * 0.5 + min(gradient_mag / 100, 1.0) * 0.3 + min(edge_density * 10, 1.0) * 0.2
        blur_penalty = max(0, 1.0 - edge_density * 5)  # Lower edge density = more blur
        
        quality_score = (sharpness_score * 0.7 + (1 - blur_penalty) * 0.3) * 100
        
        return quality_score
    
    def extract_with_fallback(self, video_path: str, output_dir: str, 
                            target_fps: float = 1.0, use_ffmpeg: bool = True) -> str:
        """
        Extract frames with fallback to regular extraction if adaptive fails.
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save frames
            target_fps: Target frames per second
            use_ffmpeg: Whether to try ffmpeg first for regular extraction
            
        Returns:
            Path to output directory
        """
        try:
            # Try adaptive extraction first
            return self.extract_adaptive_frames(video_path, output_dir, target_fps)
            
        except Exception as e:
            if self.verbose:
                print(f"Adaptive extraction failed: {e}")
                print("Falling back to regular frame extraction...")
            
            # Fallback to regular extraction
            from .frame_extractor import FrameExtractor
            extractor = FrameExtractor(verbose=self.verbose)
            return extractor.extract_frames(video_path, target_fps, output_dir, use_ffmpeg)


def adaptive_extract_cli():
    """Command line interface for adaptive frame extraction."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Adaptive frame extraction')
    parser.add_argument('--video', required=True, help='Input video file')
    parser.add_argument('--output', default='adaptive_frames', help='Output directory')
    parser.add_argument('--fps', type=float, default=1.0, help='Target FPS')
    parser.add_argument('--quality-threshold', type=float, default=60.0, 
                       help='Quality threshold (0-100)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    extractor = AdaptiveFrameExtractor(
        quality_threshold=args.quality_threshold,
        verbose=args.verbose
    )
    
    try:
        result_dir = extractor.extract_adaptive_frames(
            args.video, args.output, args.fps
        )
        print(f"Adaptive extraction completed: {result_dir}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(adaptive_extract_cli())
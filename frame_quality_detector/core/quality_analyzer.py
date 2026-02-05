#!/usr/bin/env python3
"""
Frame Quality Analyzer

Main analyzer that combines sharpness detection and motion blur detection
to provide comprehensive frame quality analysis.
"""

import os
import json
import csv
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from tqdm import tqdm

from .sharpness_detector import SharpnessDetector
from .motion_blur_detector import MotionBlurDetector


class FrameQualityAnalyzer:
    """Analyzes frame quality using sharpness and motion blur detection."""
    
    def __init__(self, 
                 sharpness_weight: float = 0.7,
                 blur_weight: float = 0.3,
                 verbose: bool = False):
        """
        Initialize quality analyzer.
        
        Args:
            sharpness_weight: Weight for sharpness in combined score
            blur_weight: Weight for blur penalty in combined score  
            verbose: Enable verbose output
        """
        self.sharpness_weight = sharpness_weight
        self.blur_weight = blur_weight
        self.verbose = verbose
        
        self.sharpness_detector = SharpnessDetector(verbose=verbose)
        self.blur_detector = MotionBlurDetector(verbose=verbose)
    
    def analyze_frame(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze a single frame for quality metrics.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with all quality metrics
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Get filename without path
        filename = os.path.basename(image_path)
        
        # Analyze sharpness
        sharpness_metrics = self.sharpness_detector.analyze_sharpness(image)
        
        # Analyze motion blur
        blur_metrics = self.blur_detector.analyze_motion_blur(image)
        
        # Calculate combined quality score
        sharpness_score = sharpness_metrics['combined_sharpness']
        blur_score = blur_metrics['combined_blur']  # Higher = more blurred
        
        # Combined score: high sharpness good, high blur bad
        # Invert blur score so lower blur = higher score
        blur_penalty = 100 - blur_score
        
        quality_score = (
            self.sharpness_weight * sharpness_score + 
            self.blur_weight * blur_penalty
        )
        
        # Compile results
        result = {
            'filename': filename,
            'path': image_path,
            'quality_score': quality_score,
            'sharpness_score': sharpness_score,
            'blur_score': blur_score,
            'sharpness_metrics': sharpness_metrics,
            'blur_metrics': blur_metrics,
            'image_size': image.shape[:2]  # height, width
        }
        
        if self.verbose:
            print(f"\nAnalyzed {filename}:")
            print(f"  Quality Score: {quality_score:.2f}")
            print(f"  Sharpness: {sharpness_score:.2f}")
            print(f"  Blur Score: {blur_score:.2f}")
        
        return result
    
    def analyze_directory(self, 
                         frames_dir: str, 
                         quality_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Analyze all frames in a directory.
        
        Args:
            frames_dir: Directory containing frame images
            quality_threshold: Minimum quality score to include
            
        Returns:
            List of analysis results for all frames
        """
        # Get list of image files
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        image_files = []
        
        for file_path in Path(frames_dir).iterdir():
            if file_path.suffix.lower() in image_extensions:
                image_files.append(str(file_path))
        
        image_files.sort()
        
        if not image_files:
            raise ValueError(f"No image files found in {frames_dir}")
        
        if self.verbose:
            print(f"Found {len(image_files)} image files")
        
        # Analyze each frame
        results = []
        
        # Progress bar
        pbar = tqdm(image_files, desc="Analyzing frames") if self.verbose else image_files
        
        for image_path in pbar:
            try:
                result = self.analyze_frame(image_path)
                
                # Apply quality threshold
                if result['quality_score'] >= quality_threshold:
                    results.append(result)
                elif self.verbose:
                    print(f"Skipping {result['filename']} (score: {result['quality_score']:.2f} < {quality_threshold})")
                    
            except Exception as e:
                if self.verbose:
                    print(f"Error analyzing {image_path}: {e}")
                continue
        
        # Sort by quality score (descending)
        results.sort(key=lambda x: x['quality_score'], reverse=True)
        
        if self.verbose:
            print(f"\nAnalyzed {len(results)} frames meeting quality threshold")
        
        return results
    
    def get_top_frames(self, results: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
        """
        Get the top N frames by quality score.
        
        Args:
            results: List of analysis results
            top_n: Number of top frames to return
            
        Returns:
            List of top N frame analysis results
        """
        # Results should already be sorted by quality_score
        return results[:top_n]
    
    def save_best_frames(self, 
                        best_frames: List[Dict[str, Any]], 
                        source_dir: str, 
                        output_dir: Path) -> None:
        """
        Copy the best frames to output directory.
        
        Args:
            best_frames: List of best frame analysis results
            source_dir: Source directory containing original frames
            output_dir: Output directory for best frames
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, frame_data in enumerate(best_frames):
            source_path = frame_data['path']
            
            # Create descriptive filename
            original_name = Path(source_path).stem
            extension = Path(source_path).suffix
            quality_score = frame_data['quality_score']
            
            new_filename = f"{i+1:02d}_best_{original_name}_q{quality_score:.1f}{extension}"
            dest_path = output_dir / new_filename
            
            shutil.copy2(source_path, dest_path)
            
            if self.verbose:
                print(f"Copied {frame_data['filename']} -> {new_filename}")
    
    def save_json_report(self, results: List[Dict[str, Any]], output_path: Path) -> None:
        """
        Save detailed analysis report in JSON format.
        
        Args:
            results: Analysis results
            output_path: Output file path
        """
        # Create simplified results for JSON serialization
        json_results = []
        
        for result in results:
            json_result = {
                'filename': result['filename'],
                'quality_score': round(result['quality_score'], 2),
                'sharpness_score': round(result['sharpness_score'], 2),
                'blur_score': round(result['blur_score'], 2),
                'image_size': result['image_size'],
                'sharpness_metrics': {
                    k: round(v, 4) for k, v in result['sharpness_metrics'].items()
                },
                'blur_metrics': {
                    k: round(v, 4) for k, v in result['blur_metrics'].items()
                }
            }
            json_results.append(json_result)
        
        with open(output_path, 'w') as f:
            json.dump({
                'analysis_summary': {
                    'total_frames': len(results),
                    'average_quality': np.mean([r['quality_score'] for r in results]),
                    'best_quality': max([r['quality_score'] for r in results]) if results else 0,
                    'worst_quality': min([r['quality_score'] for r in results]) if results else 0,
                    'sharpness_weight': self.sharpness_weight,
                    'blur_weight': self.blur_weight
                },
                'frames': json_results
            }, f, indent=2)
        
        if self.verbose:
            print(f"JSON report saved to {output_path}")
    
    def save_csv_report(self, results: List[Dict[str, Any]], output_path: Path) -> None:
        """
        Save analysis report in CSV format.
        
        Args:
            results: Analysis results  
            output_path: Output file path
        """
        with open(output_path, 'w', newline='') as f:
            if not results:
                return
                
            # Define CSV columns
            fieldnames = [
                'filename', 'quality_score', 'sharpness_score', 'blur_score',
                'laplacian_variance', 'sobel_magnitude', 'gradient_magnitude', 
                'tenengrad_focus', 'high_frequency', 'combined_sharpness',
                'frequency_blur', 'edge_blur', 'gradient_blur', 'spectral_blur',
                'kernel_blur', 'combined_blur', 'width', 'height'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                row = {
                    'filename': result['filename'],
                    'quality_score': round(result['quality_score'], 2),
                    'sharpness_score': round(result['sharpness_score'], 2),
                    'blur_score': round(result['blur_score'], 2),
                    'width': result['image_size'][1],
                    'height': result['image_size'][0]
                }
                
                # Add sharpness metrics
                for key, value in result['sharpness_metrics'].items():
                    row[key] = round(value, 4)
                
                # Add blur metrics
                for key, value in result['blur_metrics'].items():
                    row[key] = round(value, 4)
                
                writer.writerow(row)
        
        if self.verbose:
            print(f"CSV report saved to {output_path}")
    
    def print_text_report(self, best_frames: List[Dict[str, Any]]) -> None:
        """
        Print a text summary of the best frames.
        
        Args:
            best_frames: List of best frame analysis results
        """
        print(f"\n{'='*60}")
        print(f"FRAME QUALITY ANALYSIS REPORT")
        print(f"{'='*60}")
        
        if not best_frames:
            print("No frames analyzed.")
            return
        
        print(f"Best {len(best_frames)} frames:")
        print(f"\n{'Rank':<4} {'Filename':<20} {'Quality':<8} {'Sharpness':<10} {'Blur':<8}")
        print(f"{'-'*4} {'-'*20} {'-'*8} {'-'*10} {'-'*8}")
        
        for i, frame in enumerate(best_frames):
            print(f"{i+1:<4} {frame['filename']:<20} "
                  f"{frame['quality_score']:<8.2f} "
                  f"{frame['sharpness_score']:<10.2f} "
                  f"{frame['blur_score']:<8.2f}")
        
        # Statistics
        quality_scores = [f['quality_score'] for f in best_frames]
        sharpness_scores = [f['sharpness_score'] for f in best_frames]
        blur_scores = [f['blur_score'] for f in best_frames]
        
        print(f"\n{'='*60}")
        print(f"STATISTICS")
        print(f"{'='*60}")
        print(f"Average Quality Score: {np.mean(quality_scores):.2f}")
        print(f"Best Quality Score:    {np.max(quality_scores):.2f}")
        print(f"Average Sharpness:     {np.mean(sharpness_scores):.2f}")
        print(f"Average Blur Score:    {np.mean(blur_scores):.2f}")
        print(f"\nAnalysis Weights:")
        print(f"  Sharpness: {self.sharpness_weight:.1f}")
        print(f"  Blur Penalty: {self.blur_weight:.1f}")
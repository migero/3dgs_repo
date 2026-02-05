"""
Video Mask Processor
Processes videos frame-by-frame for segmentation mask generation.
"""

import numpy as np
from typing import List, Optional, Tuple, Callable, Dict, Any
from dataclasses import dataclass, field
import cv2
from pathlib import Path
import time
import os

from .yolo_segmenter import YoloSegmenter, SegmentationResult, DEFAULT_MOVING_CLASSES


@dataclass
class ProcessorConfig:
    """Configuration for video mask processing."""
    
    # YOLO settings
    model_name: str = "yolo11n-seg.pt"
    target_classes: List[str] = field(default_factory=lambda: DEFAULT_MOVING_CLASSES.copy())
    confidence_threshold: float = 0.35
    device: Optional[str] = None
    
    # Post-processing
    dilate_mask: bool = True
    dilation_iterations: int = 2
    dilation_kernel_size: int = 5
    feather_edges: bool = True
    feather_amount: int = 10
    
    # Video processing
    fps: float = 1.0  # Frames per second to extract
    max_frames: Optional[int] = None  # Maximum frames to process (None = all)
    
    # Output
    save_overlay: bool = False  # Save overlay visualization
    overlay_alpha: float = 0.5  # Overlay transparency
    
    # Logging
    verbose: bool = True


@dataclass
class ProcessingResult:
    """Result from processing a single frame."""
    frame_number: int
    timestamp: float
    mask: np.ndarray
    num_detections: int
    class_names: List[str]
    confidences: List[float]
    processing_time: float


class VideoMaskProcessor:
    """
    Processes videos to generate segmentation masks.
    
    Extracts frames at specified FPS, runs YOLO segmentation,
    and saves masks to disk.
    """
    
    def __init__(self, config: Optional[ProcessorConfig] = None):
        """
        Initialize the processor.
        
        Args:
            config: Processing configuration. Uses defaults if None.
        """
        self.config = config or ProcessorConfig()
        
        self.segmenter = YoloSegmenter(
            model_name=self.config.model_name,
            target_classes=self.config.target_classes,
            confidence_threshold=self.config.confidence_threshold,
            device=self.config.device,
            verbose=self.config.verbose
        )
    
    def process_image(self, image: np.ndarray) -> SegmentationResult:
        """
        Process a single image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            SegmentationResult with mask and detection info
        """
        # Run segmentation
        result = self.segmenter.segment(image)
        
        # Apply post-processing
        result.combined_mask = self._post_process_mask(result.combined_mask)
        
        return result
    
    def process_video(
        self,
        video_path: str,
        output_dir: str,
        progress_callback: Optional[Callable[[str, float, int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Process a video and save masks.
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save masks
            progress_callback: Callback function(message, progress, frame_num, total_frames)
            
        Returns:
            Dictionary with processing summary
        """
        start_time = time.time()
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_video_frames / video_fps if video_fps > 0 else 0
        
        # Calculate frame interval
        frame_interval = int(video_fps / self.config.fps) if self.config.fps > 0 else 1
        frame_interval = max(1, frame_interval)
        
        # Estimate total frames to process
        total_frames_to_process = total_video_frames // frame_interval
        if self.config.max_frames:
            total_frames_to_process = min(total_frames_to_process, self.config.max_frames)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Process frames
        frame_number = 0
        processed_count = 0
        frames_with_detections = 0
        total_detections = 0
        
        video_name = Path(video_path).stem
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Check if we should process this frame
            if frame_number % frame_interval == 0:
                # Check max frames limit
                if self.config.max_frames and processed_count >= self.config.max_frames:
                    break
                
                # Get timestamp
                timestamp = frame_number / video_fps if video_fps > 0 else 0
                
                # Process frame
                result = self.process_image(frame)
                
                # Update stats
                if result.num_detections > 0:
                    frames_with_detections += 1
                    total_detections += result.num_detections
                
                # Save mask
                mask_filename = f"{video_name}_frame_{frame_number:06d}_mask.png"
                mask_path = os.path.join(output_dir, mask_filename)
                mask_uint8 = (result.mask * 255).astype(np.uint8)
                cv2.imwrite(mask_path, mask_uint8)
                
                # Save overlay if requested
                if self.config.save_overlay:
                    overlay = self.create_overlay(frame, result)
                    overlay_filename = f"{video_name}_frame_{frame_number:06d}_overlay.png"
                    overlay_path = os.path.join(output_dir, overlay_filename)
                    cv2.imwrite(overlay_path, overlay)
                
                processed_count += 1
                
                # Progress callback
                if progress_callback:
                    progress = processed_count / total_frames_to_process
                    progress_callback(
                        f"Processing frame {frame_number}",
                        progress,
                        processed_count,
                        total_frames_to_process
                    )
            
            frame_number += 1
        
        cap.release()
        
        processing_time = time.time() - start_time
        
        return {
            'total_frames': processed_count,
            'frames_with_detections': frames_with_detections,
            'total_detections': total_detections,
            'processing_time': processing_time,
            'video_fps': video_fps,
            'video_duration': duration,
            'frame_interval': frame_interval,
            'output_dir': output_dir
        }
    
    def process_folder(
        self,
        input_folder: str,
        output_folder: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, Any]:
        """
        Process all images in a folder.
        
        Args:
            input_folder: Input folder with images
            output_folder: Output folder for masks
            progress_callback: Callback function(message, progress)
            
        Returns:
            Dictionary with processing summary
        """
        start_time = time.time()
        
        # Find all images
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        input_path = Path(input_folder)
        
        image_files = [
            f for f in input_path.iterdir()
            if f.suffix.lower() in image_extensions
        ]
        image_files.sort()
        
        if not image_files:
            raise ValueError(f"No images found in: {input_folder}")
        
        # Create output directory
        os.makedirs(output_folder, exist_ok=True)
        
        # Process images
        total_images = len(image_files)
        processed_count = 0
        images_with_detections = 0
        total_detections = 0
        
        for i, image_file in enumerate(image_files):
            # Load image
            image = cv2.imread(str(image_file))
            if image is None:
                continue
            
            # Process
            result = self.process_image(image)
            
            # Update stats
            if result.num_detections > 0:
                images_with_detections += 1
                total_detections += result.num_detections
            
            # Save mask
            mask_filename = f"{image_file.stem}_mask.png"
            mask_path = os.path.join(output_folder, mask_filename)
            mask_uint8 = (result.mask * 255).astype(np.uint8)
            cv2.imwrite(mask_path, mask_uint8)
            
            # Save overlay if requested
            if self.config.save_overlay:
                overlay = self.create_overlay(image, result)
                overlay_filename = f"{image_file.stem}_overlay.png"
                overlay_path = os.path.join(output_folder, overlay_filename)
                cv2.imwrite(overlay_path, overlay)
            
            processed_count += 1
            
            # Progress callback
            if progress_callback:
                progress = (i + 1) / total_images
                progress_callback(f"Processing {image_file.name}", progress)
        
        processing_time = time.time() - start_time
        
        return {
            'total_images': processed_count,
            'images_with_detections': images_with_detections,
            'total_detections': total_detections,
            'processing_time': processing_time,
            'output_folder': output_folder
        }
    
    def _post_process_mask(self, mask: np.ndarray) -> np.ndarray:
        """
        Apply post-processing to mask.
        
        Args:
            mask: Input mask (H, W) float32 0-1
            
        Returns:
            Post-processed mask
        """
        result = mask.copy()
        
        # Dilate mask
        if self.config.dilate_mask:
            kernel = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE,
                (self.config.dilation_kernel_size, self.config.dilation_kernel_size)
            )
            result = cv2.dilate(
                result, 
                kernel, 
                iterations=self.config.dilation_iterations
            )
        
        # Feather edges
        if self.config.feather_edges and self.config.feather_amount > 0:
            result = cv2.GaussianBlur(
                result,
                (0, 0),
                self.config.feather_amount
            )
            # Normalize back to 0-1 range
            if result.max() > 0:
                result = result / result.max()
        
        return result
    
    def create_overlay(
        self,
        image: np.ndarray,
        result: SegmentationResult,
        alpha: Optional[float] = None
    ) -> np.ndarray:
        """
        Create overlay visualization.
        
        Args:
            image: Original image
            result: Segmentation result
            alpha: Overlay transparency (uses config default if None)
            
        Returns:
            Image with mask overlay
        """
        if alpha is None:
            alpha = self.config.overlay_alpha
        
        return self.segmenter.visualize_result(
            image, 
            result, 
            alpha=alpha,
            show_labels=True
        )
    
    def get_device_info(self) -> str:
        """Get device information."""
        return self.segmenter.get_device_info()

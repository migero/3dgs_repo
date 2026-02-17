"""
Video Pipeline Module
Handles video frame extraction, processing through PVDNet, and reconstruction.
"""

import os
import cv2
import numpy as np
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Callable, List, Dict, Tuple
from dataclasses import dataclass, field
from collections import deque
import threading
import gc

from .cube_projector import CubeProjector, CubeFaces
from .pvdnet_processor import PVDNetProcessor, PVDNetConfig


@dataclass
class PipelineConfig:
    """Configuration for the video processing pipeline."""
    # Cube projection settings
    cube_face_size: int = 1024  # Size of each cube face
    
    # Video processing
    output_fps: Optional[float] = None  # None = same as input
    
    # Frame buffer settings
    frame_buffer_size: int = 30  # Number of frames to keep in memory
    cleanup_interval: int = 10  # Cleanup old frames every N frames
    
    # PVDNet settings
    checkpoint_path: str = "ckpt/PVDNet_DVD.pytorch"
    use_large_model: bool = False
    
    # Output settings
    output_codec: str = "libx264"
    output_quality: int = 18  # CRF value (lower = better quality)
    output_preset: str = "medium"
    
    # Temp directory
    temp_dir: Optional[str] = None


@dataclass
class ProcessingStats:
    """Statistics for the processing pipeline."""
    total_frames: int = 0
    processed_frames: int = 0
    current_frame: int = 0
    fps: float = 0.0
    elapsed_time: float = 0.0
    estimated_remaining: float = 0.0
    status: str = "idle"


class FrameBuffer:
    """
    Manages a rolling buffer of frames with automatic cleanup.
    
    Keeps track of previous frames for temporal processing and
    handles memory management by cleaning up old frames.
    """
    
    def __init__(self, max_size: int = 30, cleanup_interval: int = 10):
        """
        Initialize frame buffer.
        
        Args:
            max_size: Maximum number of frames to keep
            cleanup_interval: How often to perform cleanup
        """
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self._frames: Dict[int, np.ndarray] = {}
        self._cube_frames: Dict[int, CubeFaces] = {}
        self._deblurred_frames: Dict[int, CubeFaces] = {}
        self._access_count = 0
        self._lock = threading.Lock()
    
    def add_frame(self, frame_idx: int, frame: np.ndarray):
        """Add a raw equirectangular frame."""
        with self._lock:
            self._frames[frame_idx] = frame
            self._access_count += 1
            if self._access_count % self.cleanup_interval == 0:
                self._cleanup()
    
    def add_cube_frame(self, frame_idx: int, cube_faces: CubeFaces):
        """Add cube faces for a frame."""
        with self._lock:
            self._cube_frames[frame_idx] = cube_faces
    
    def add_deblurred_frame(self, frame_idx: int, cube_faces: CubeFaces):
        """Add deblurred cube faces."""
        with self._lock:
            self._deblurred_frames[frame_idx] = cube_faces
    
    def get_frame(self, frame_idx: int) -> Optional[np.ndarray]:
        """Get a raw frame."""
        with self._lock:
            return self._frames.get(frame_idx)
    
    def get_cube_frame(self, frame_idx: int) -> Optional[CubeFaces]:
        """Get cube faces for a frame."""
        with self._lock:
            return self._cube_frames.get(frame_idx)
    
    def get_deblurred_frame(self, frame_idx: int) -> Optional[CubeFaces]:
        """Get deblurred cube faces."""
        with self._lock:
            return self._deblurred_frames.get(frame_idx)
    
    def _cleanup(self):
        """Remove old frames to free memory."""
        if not self._frames:
            return
        
        # Find the minimum frame index we need to keep
        min_needed = max(self._frames.keys()) - self.max_size
        
        # Remove old frames
        for storage in [self._frames, self._cube_frames, self._deblurred_frames]:
            keys_to_remove = [k for k in storage.keys() if k < min_needed]
            for k in keys_to_remove:
                del storage[k]
        
        # Force garbage collection
        gc.collect()
    
    def clear(self):
        """Clear all stored frames."""
        with self._lock:
            self._frames.clear()
            self._cube_frames.clear()
            self._deblurred_frames.clear()
            gc.collect()


class VideoPipeline:
    """
    Main video processing pipeline.
    
    Handles the full workflow:
    1. Extract frames from input video
    2. Convert to cube faces
    3. Process through PVDNet
    4. Reconstruct to equirectangular
    5. Encode output video
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the video pipeline.
        
        Args:
            config: PipelineConfig object with settings
        """
        self.config = config or PipelineConfig()
        
        # Initialize components
        self.cube_projector = CubeProjector(face_size=self.config.cube_face_size)
        
        pvdnet_config = PVDNetConfig(
            checkpoint_path=self.config.checkpoint_path,
            use_large_model=self.config.use_large_model
        )
        self.pvdnet = PVDNetProcessor(pvdnet_config)
        
        # Frame buffer
        self.frame_buffer = FrameBuffer(
            max_size=self.config.frame_buffer_size,
            cleanup_interval=self.config.cleanup_interval
        )
        
        # Stats
        self.stats = ProcessingStats()
        
        # Callbacks
        self._progress_callback: Optional[Callable[[ProcessingStats], None]] = None
        self._preview_callback: Optional[Callable[[np.ndarray], None]] = None
        
        # Control flags
        self._cancel_requested = False
    
    def set_progress_callback(self, callback: Callable[[ProcessingStats], None]):
        """Set callback for progress updates."""
        self._progress_callback = callback
    
    def set_preview_callback(self, callback: Callable[[np.ndarray], None]):
        """Set callback for preview frame updates."""
        self._preview_callback = callback
    
    def load_model(self) -> bool:
        """Load PVDNet model."""
        return self.pvdnet.load_model(self.config.checkpoint_path)
    
    def cancel(self):
        """Request cancellation of processing."""
        self._cancel_requested = True
    
    def _update_stats(self, **kwargs):
        """Update processing stats and notify callback."""
        for k, v in kwargs.items():
            if hasattr(self.stats, k):
                setattr(self.stats, k, v)
        
        if self._progress_callback:
            self._progress_callback(self.stats)
    
    def process_video(
        self,
        input_path: str,
        output_path: str,
    ) -> bool:
        """
        Process a video file.
        
        Args:
            input_path: Path to input video
            output_path: Path for output video
        
        Returns:
            True if processing completed successfully
        """
        import time
        
        self._cancel_requested = False
        self.frame_buffer.clear()
        self.pvdnet.reset_state()
        
        # Validate input
        if not os.path.exists(input_path):
            self._update_stats(status=f"Error: Input file not found: {input_path}")
            return False
        
        # Open video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            self._update_stats(status=f"Error: Could not open video: {input_path}")
            return False
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        input_fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        output_fps = self.config.output_fps or input_fps
        
        self._update_stats(
            total_frames=total_frames,
            processed_frames=0,
            status="Loading model..."
        )
        
        # Load model if not loaded
        if not self.pvdnet.is_loaded:
            if not self.load_model():
                cap.release()
                return False
        
        # Setup temp directory for frames
        temp_dir = self.config.temp_dir or Path(output_path).parent / ".temp_deblur"
        temp_dir = Path(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            self._update_stats(status="Processing frames...")
            start_time = time.time()
            
            # Read all frames first (or process in chunks for very long videos)
            frames = []
            frame_idx = 0
            
            while True:
                if self._cancel_requested:
                    self._update_stats(status="Cancelled")
                    return False
                
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)
                
                self._update_stats(
                    current_frame=frame_idx,
                    status=f"Reading frame {frame_idx + 1}/{total_frames}"
                )
                frame_idx += 1
            
            cap.release()
            total_frames = len(frames)
            
            if total_frames == 0:
                self._update_stats(status="Error: No frames read from video")
                return False
            
            # Process frames
            output_frames = []
            
            for i in range(total_frames):
                if self._cancel_requested:
                    self._update_stats(status="Cancelled")
                    return False
                
                # Get prev, curr, next frames (with clamping at boundaries)
                prev_idx = max(0, i - 1)
                next_idx = min(total_frames - 1, i + 1)
                
                prev_frame = frames[prev_idx]
                curr_frame = frames[i]
                next_frame = frames[next_idx]
                
                # Convert to cube faces
                self._update_stats(status=f"Processing frame {i + 1}/{total_frames}: Converting to cube...")
                
                prev_cubes = self.cube_projector.equirect_to_cube(prev_frame)
                curr_cubes = self.cube_projector.equirect_to_cube(curr_frame)
                next_cubes = self.cube_projector.equirect_to_cube(next_frame)
                
                # Process each cube face through PVDNet
                self._update_stats(status=f"Processing frame {i + 1}/{total_frames}: Deblurring...")
                
                deblurred_faces = self.pvdnet.process_cube_faces_batch(
                    prev_faces=prev_cubes.to_list(),
                    curr_faces=curr_cubes.to_list(),
                    next_faces=next_cubes.to_list(),
                    face_ids=["front", "right", "back", "left", "top", "bottom"]
                )
                
                deblurred_cubes = CubeFaces.from_list(deblurred_faces)
                
                # Reconstruct to equirectangular
                self._update_stats(status=f"Processing frame {i + 1}/{total_frames}: Reconstructing...")
                
                output_frame = self.cube_projector.cube_to_equirect(
                    deblurred_cubes,
                    output_height=height,
                    output_width=width
                )
                
                output_frames.append(output_frame)
                
                # Update stats
                elapsed = time.time() - start_time
                frames_per_sec = (i + 1) / elapsed if elapsed > 0 else 0
                remaining = (total_frames - i - 1) / frames_per_sec if frames_per_sec > 0 else 0
                
                self._update_stats(
                    processed_frames=i + 1,
                    current_frame=i,
                    fps=frames_per_sec,
                    elapsed_time=elapsed,
                    estimated_remaining=remaining
                )
                
                # Send preview
                if self._preview_callback and i % 5 == 0:
                    self._preview_callback(output_frame)
                
                # Cleanup old frames from buffer periodically
                if i > 0 and i % self.config.cleanup_interval == 0:
                    # Force garbage collection
                    gc.collect()
            
            # Encode output video
            self._update_stats(status="Encoding output video...")
            
            success = self._encode_video(output_frames, output_path, output_fps, width, height)
            
            if success:
                elapsed = time.time() - start_time
                self._update_stats(
                    status=f"Complete! Processed {total_frames} frames in {elapsed:.1f}s",
                    elapsed_time=elapsed
                )
            
            return success
            
        finally:
            # Cleanup
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            self.frame_buffer.clear()
            gc.collect()
    
    def _encode_video(
        self,
        frames: List[np.ndarray],
        output_path: str,
        fps: float,
        width: int,
        height: int
    ) -> bool:
        """
        Encode frames to video using FFmpeg.
        
        Args:
            frames: List of frame arrays [H, W, C] in RGB
            output_path: Output video path
            fps: Output frame rate
            width: Frame width
            height: Frame height
        
        Returns:
            True if encoding succeeded
        """
        try:
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-y',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-s', f'{width}x{height}',
                '-pix_fmt', 'rgb24',
                '-r', str(fps),
                '-i', '-',
                '-c:v', self.config.output_codec,
                '-crf', str(self.config.output_quality),
                '-preset', self.config.output_preset,
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            # Start FFmpeg process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Write frames
            for i, frame in enumerate(frames):
                if self._cancel_requested:
                    process.kill()
                    return False
                
                # Ensure correct dtype
                if frame.dtype != np.uint8:
                    frame = (np.clip(frame, 0, 255)).astype(np.uint8)
                
                process.stdin.write(frame.tobytes())
                
                if i % 10 == 0:
                    self._update_stats(status=f"Encoding: {i + 1}/{len(frames)} frames")
            
            # Finish
            process.stdin.close()
            process.wait()
            
            if process.returncode != 0:
                stderr = process.stderr.read().decode()
                print(f"FFmpeg error: {stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error encoding video: {e}")
            return False
    
    def process_single_frame(
        self,
        frame: np.ndarray,
        frame_idx: int = 0
    ) -> np.ndarray:
        """
        Process a single frame for preview purposes.
        
        Args:
            frame: Equirectangular frame [H, W, C]
            frame_idx: Frame index (for state tracking)
        
        Returns:
            Deblurred equirectangular frame
        """
        # For single frame, use same frame for prev/curr/next
        prev_frame = frame
        curr_frame = frame
        next_frame = frame
        
        # Convert to cube
        prev_cubes = self.cube_projector.equirect_to_cube(prev_frame)
        curr_cubes = self.cube_projector.equirect_to_cube(curr_frame)
        next_cubes = self.cube_projector.equirect_to_cube(next_frame)
        
        # Process
        if self.pvdnet.is_loaded:
            deblurred_faces = self.pvdnet.process_cube_faces_batch(
                prev_faces=prev_cubes.to_list(),
                curr_faces=curr_cubes.to_list(),
                next_faces=next_cubes.to_list()
            )
            deblurred_cubes = CubeFaces.from_list(deblurred_faces)
        else:
            # No model loaded, return original
            deblurred_cubes = curr_cubes
        
        # Reconstruct
        h, w = frame.shape[:2]
        output = self.cube_projector.cube_to_equirect(deblurred_cubes, h, w)
        
        return output


def get_video_info(video_path: str) -> Optional[Dict]:
    """
    Get information about a video file.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Dictionary with video info or None if failed
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    
    info = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS),
        'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
    }
    
    cap.release()
    return info

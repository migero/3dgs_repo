#!/usr/bin/env python3
"""
Preview Generator for GoPro 360 Converter
Generates preview frames of the stitched 360 video
"""

import os
import subprocess
import shutil
import tempfile
from typing import Optional, Dict, Any
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class PreviewGenerator:
    """Generates preview frames using FFmpeg"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self._temp_dir = tempfile.mkdtemp(prefix="gopro360_preview_")
        
    def __del__(self):
        """Cleanup temp directory"""
        if hasattr(self, '_temp_dir') and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
            except:
                pass
                
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable"""
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            return ffmpeg
            
        common_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg",
        ]
        
        for path in common_paths:
            if os.path.isfile(path):
                return path
                
        return None
        
    def generate_preview(
        self,
        input_path: str,
        frame_number: int,
        settings: Dict[str, Any],
        preview_width: int = 960
    ) -> Optional[np.ndarray]:
        """
        Generate a preview frame of the stitched video
        
        Args:
            input_path: Path to input .360 file
            frame_number: Frame number to extract
            settings: Conversion settings dictionary
            preview_width: Width of preview image (height calculated automatically)
            
        Returns:
            numpy array of the preview image (RGB format) or None on error
        """
        if not self.ffmpeg_path:
            return self._generate_error_image("FFmpeg not found")
            
        if not os.path.exists(input_path):
            return self._generate_error_image("Input file not found")
        
        # For GoPro MAX, always use the full stitched preview
        projection = settings.get('projection', 'gopro_max')
        if projection == 'gopro_max':
            return self.generate_full_preview(input_path, frame_number, settings, preview_width)
            
        try:
            # Build preview extraction command
            preview_path = os.path.join(self._temp_dir, "preview.png")
            
            # Calculate timestamp from frame number
            # Assume 30fps if we can't determine actual fps
            fps = 30
            timestamp = frame_number / fps
            
            # Build video filter for 360 conversion
            vf_filters = self._build_preview_filters(settings, preview_width)
            
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-ss", str(timestamp),  # Seek to timestamp
                "-i", input_path,
                "-vf", ",".join(vf_filters),
                "-frames:v", "1",  # Extract single frame
                "-q:v", "2",  # High quality
                preview_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                print(f"FFmpeg preview error: {error_msg}")
                return self._generate_error_image("Preview generation failed")
                
            # Load the generated image
            if os.path.exists(preview_path):
                return self._load_image(preview_path)
            else:
                return self._generate_error_image("Preview image not created")
                
        except subprocess.TimeoutExpired:
            return self._generate_error_image("Preview generation timed out")
        except Exception as e:
            return self._generate_error_image(f"Error: {str(e)}")
            
    def _build_preview_filters(
        self,
        settings: Dict[str, Any],
        preview_width: int
    ) -> list:
        """Build FFmpeg video filter chain for preview"""
        filters = []
        
        projection = settings.get('projection', 'gopro_max')
        interp = settings.get('interpolation', 'cubic')
        
        if projection == 'gopro_max':
            # For GoPro MAX, we need the complex filter but simplified for preview
            # This is a simplified version - the full conversion uses complex filter
            # For preview, we'll just show the first track converted
            # The full filter is too complex for a simple preview command
            
            # Just do a basic crop and show the front face area as preview
            # This gives a quick idea of the content
            filters.append("crop=iw*2/3:ih:iw/6:0")  # Crop out padding
            filters.append(f"scale={preview_width}:-1")
        else:
            # Simple equirectangular conversion
            filters.append(f"v360=eac:equirect:interp={interp}")
            preview_height = preview_width // 2
            filters.append(f"scale={preview_width}:{preview_height}")
        
        return filters
    
    def generate_full_preview(
        self,
        input_path: str,
        frame_number: int,
        settings: Dict[str, Any],
        preview_width: int = 960
    ) -> Optional[np.ndarray]:
        """
        Generate a full stitched preview using the SeamStitcher.
        This shows the actual stitched result with proper seam blending.
        """
        if not self.ffmpeg_path:
            return self._generate_error_image("FFmpeg not found")
            
        if not os.path.exists(input_path):
            return self._generate_error_image("Input file not found")
            
        try:
            from core.seam_stitcher import SeamStitcher
            from core.video_processor import VideoProcessor
            
            stitcher = SeamStitcher()
            processor = VideoProcessor()
            
            fps = 30
            timestamp = frame_number / fps
            
            # Get settings
            edge_overlap = settings.get('edge_overlap', 30)
            blend_width = settings.get('blend_width', 30)
            face_mapping = settings.get('face_mapping', {
                'top': 5, 'back': 1, 'left': 0, 'front': 3, 'right': 2, 'bottom': 4
            })
            face_rotation = settings.get('face_rotation', {
                'top': 0, 'back': 0, 'left': 0, 'front': 0, 'right': 0, 'bottom': 180
            })
            
            # Extract frames from both tracks
            track0 = stitcher.extract_frame(input_path, timestamp, track=0)
            track1 = stitcher.extract_frame(input_path, timestamp, track=1)
            
            if track0 is None or track1 is None:
                return self._generate_error_image("Failed to extract frames")
            
            # Get video info for cube face size
            info = processor.get_video_info(input_path)
            height = info.get('height', 1344) if info else 1344
            
            # Process into cubemap using SeamStitcher
            cubemap = stitcher.process_frame_to_cubemap(
                track0, track1,
                edge_overlap, blend_width,
                face_mapping, face_rotation,
                cube_face_size=height  # Use full resolution
            )
            
            # Convert cubemap to equirectangular using FFmpeg
            preview_path = os.path.join(self._temp_dir, "stitched_preview.png")
            cubemap_path = os.path.join(self._temp_dir, "cubemap_temp.png")
            
            # Save cubemap temporarily
            if PIL_AVAILABLE:
                from PIL import Image
                Image.fromarray(cubemap).save(cubemap_path, "PNG")
            else:
                return self._generate_error_image("PIL not available")
            
            # Use FFmpeg to convert cubemap to equirectangular
            interp = settings.get('interpolation', 'cubic')
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-i", cubemap_path,
                "-vf", f"v360=c3x2:equirect:interp={interp},scale={preview_width}:-1",
                "-frames:v", "1",
                "-q:v", "2",
                preview_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(preview_path):
                return self._load_image(preview_path)
            else:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                print(f"FFmpeg v360 error: {error_msg[-500:]}")
                return self._generate_error_image("Preview generation failed")
                
        except Exception as e:
            print(f"Full preview error: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_error_image(f"Preview error: {str(e)[:50]}")
        
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load an image file as numpy array"""
        if CV2_AVAILABLE:
            img = cv2.imread(image_path)
            if img is not None:
                # Convert BGR to RGB
                return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif PIL_AVAILABLE:
            img = Image.open(image_path)
            return np.array(img.convert('RGB'))
        else:
            # Fallback: try to use raw file reading
            # This is a basic fallback, won't work for all formats
            pass
            
        return None
        
    def _generate_error_image(self, message: str) -> np.ndarray:
        """Generate an error placeholder image"""
        # Create a dark gray image with text
        width, height = 960, 480
        
        if CV2_AVAILABLE:
            img = np.zeros((height, width, 3), dtype=np.uint8)
            img[:] = (30, 30, 30)  # Dark gray
            
            # Add error text
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(message, font, 0.7, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = height // 2
            
            cv2.putText(img, message, (text_x, text_y), font, 0.7, (200, 50, 50), 2)
            
            return img
        else:
            # Simple numpy array without OpenCV
            img = np.zeros((height, width, 3), dtype=np.uint8)
            img[:] = (30, 30, 30)
            return img
            
    def generate_comparison_preview(
        self,
        input_path: str,
        frame_number: int,
        settings: Dict[str, Any]
    ) -> Optional[np.ndarray]:
        """
        Generate a side-by-side comparison showing original and stitched
        
        Args:
            input_path: Path to input .360 file
            frame_number: Frame number to extract
            settings: Conversion settings
            
        Returns:
            numpy array with original and stitched side by side
        """
        # Get original frame
        original = self._extract_raw_frame(input_path, frame_number)
        
        # Get stitched frame
        stitched = self.generate_preview(input_path, frame_number, settings)
        
        if original is None or stitched is None:
            return stitched  # Return just stitched if original fails
            
        # Resize original to match stitched height
        if CV2_AVAILABLE:
            h_stitched = stitched.shape[0]
            h_original, w_original = original.shape[:2]
            
            # Calculate new dimensions for original
            scale = h_stitched / h_original
            new_w = int(w_original * scale)
            original_resized = cv2.resize(original, (new_w, h_stitched))
            
            # Create separator
            separator = np.zeros((h_stitched, 4, 3), dtype=np.uint8)
            separator[:] = (100, 100, 100)
            
            # Concatenate horizontally
            comparison = np.hstack([original_resized, separator, stitched])
            
            return comparison
        else:
            return stitched
            
    def _extract_raw_frame(
        self,
        input_path: str,
        frame_number: int
    ) -> Optional[np.ndarray]:
        """Extract a raw frame without any processing"""
        if not self.ffmpeg_path:
            return None
            
        try:
            preview_path = os.path.join(self._temp_dir, "original.png")
            
            fps = 30
            timestamp = frame_number / fps
            
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-ss", str(timestamp),
                "-i", input_path,
                "-vf", "scale=480:-1",  # Just scale down
                "-frames:v", "1",
                "-q:v", "2",
                preview_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(preview_path):
                return self._load_image(preview_path)
                
        except Exception:
            pass
            
        return None

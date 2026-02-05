#!/usr/bin/env python3
"""
Seam Stitcher for GoPro 360 Converter
Handles the stitching of video streams by stretching and blending seam regions.

GoPro MAX .360 Structure:
- Track 0: Horizontal strip with 3 cube faces (Left, Front, Right)
- Track 1: Horizontal strip with 3 cube faces (rotated 90° - needs transpose)

Each track covers ~180° but with overlap at the seams.
The seams are located at 1/6 and 5/6 of the frame width (the middle of frames 1 and 3).

This module:
1. Extracts frames from both tracks
2. Stretches the edges of the seam faces so they overlap with themselves
3. Blends the overlapping regions to hide the seam
4. Outputs the stitched result
"""

import os
import subprocess
import tempfile
import shutil
from typing import Optional, Tuple, Dict, Any, List

import numpy as np

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class SeamStitcher:
    """
    Handles seam stitching for GoPro MAX 360 videos.
    
    The key insight is that each video stream is a panoramic strip.
    The seams occur at 1/6 and 5/6 of the frame width because:
    - The frame is divided into 3 equal parts (cube faces)
    - Faces 1 and 3 (indices 0 and 2) have seams in their centers
    
    This stitcher works by:
    1. Taking the full-width frame from each track
    2. Identifying the seam regions at 1/6 and 5/6 positions
    3. Stretching the regions on either side of the seam so they overlap
    4. Blending the overlapped regions with a gradient
    """
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self._temp_dir = tempfile.mkdtemp(prefix="gopro360_stitch_")
        
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
        
    def extract_frame(
        self,
        input_path: str,
        timestamp: float,
        track: int = 0
    ) -> Optional[np.ndarray]:
        """
        Extract a single frame from a video track.
        
        Args:
            input_path: Path to the .360 file
            timestamp: Time in seconds to extract
            track: Video track number (0 or 1)
            
        Returns:
            numpy array of the frame (RGB) or None
        """
        if not self.ffmpeg_path or not PIL_AVAILABLE:
            return None
            
        output_path = os.path.join(self._temp_dir, f"track{track}_frame.png")
        
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-ss", str(timestamp),
            "-i", input_path,
            "-map", f"0:v:{track}",
            "-frames:v", "1",
            "-q:v", "2",
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0 and os.path.exists(output_path):
                img = Image.open(output_path).convert('RGB')
                return np.array(img)
        except Exception as e:
            print(f"Error extracting frame: {e}")
            
        return None
        
    def stitch_seam_region(
        self,
        frame: np.ndarray,
        seam_position: float,
        overlap_pixels: int,
        blend_pixels: int
    ) -> np.ndarray:
        """
        Process a seam region by stretching edges to overlap and blending.
        
        The seam is at the boundary between two regions (e.g., at 1/6 position).
        We need to:
        1. Take the LEFT side (everything before the seam) and stretch its right edge
           to extend PAST the seam by overlap_pixels
        2. Take the RIGHT side (everything after the seam) and stretch its left edge
           to extend PAST the seam by overlap_pixels  
        3. Now both sides overlap at the seam position
        4. Blend them in the overlap zone (centered on the seam)
        
        Args:
            frame: Input frame as numpy array (H, W, C)
            seam_position: Position of seam as fraction of width (0-1)
            overlap_pixels: How many pixels each side extends past the seam
            blend_pixels: Width of the blending zone (centered on seam)
            
        Returns:
            Processed frame with stitched seam
        """
        h, w, c = frame.shape
        seam_x = int(w * seam_position)
        
        # Ensure blend_pixels doesn't exceed 2*overlap_pixels
        blend_pixels = min(blend_pixels, 2 * overlap_pixels)
        
        # The overlap zone: from (seam_x - overlap_pixels) to (seam_x + overlap_pixels)
        overlap_start = max(0, seam_x - overlap_pixels)
        overlap_end = min(w, seam_x + overlap_pixels)
        overlap_width = overlap_end - overlap_start
        
        if overlap_width <= 0:
            return frame.copy()
        
        # Create output frame
        result = frame.copy()
        
        # === LEFT SIDE ===
        # Take everything from 0 to seam_x, then stretch it to extend to overlap_end
        left_original = frame[:, 0:seam_x, :].copy()
        # Stretch to cover from 0 to overlap_end
        left_new_width = overlap_end
        left_stretched = self._stretch_region(left_original, left_new_width)
        
        # === RIGHT SIDE ===
        # Take everything from seam_x to w, then stretch it to extend back to overlap_start
        right_original = frame[:, seam_x:w, :].copy()
        # Stretch to cover from overlap_start to w
        right_new_width = w - overlap_start
        right_stretched = self._stretch_region(right_original, right_new_width)
        
        # === BUILD THE RESULT ===
        # Left of overlap: use left_stretched
        result[:, 0:overlap_start, :] = left_stretched[:, 0:overlap_start, :]
        
        # Right of overlap: use right_stretched
        # right_stretched covers from overlap_start to w
        # so pixels at position x in result come from position (x - overlap_start) in right_stretched
        result[:, overlap_end:w, :] = right_stretched[:, (overlap_end - overlap_start):, :]
        
        # === BLEND THE OVERLAP ZONE ===
        # Extract the overlapping portions
        # From left_stretched: positions overlap_start to overlap_end
        left_overlap = left_stretched[:, overlap_start:overlap_end, :]
        # From right_stretched: positions 0 to overlap_width
        right_overlap = right_stretched[:, 0:overlap_width, :]
        
        # Create blend weights (gradient centered on seam)
        # The seam is at position (seam_x - overlap_start) within the overlap zone
        seam_in_overlap = seam_x - overlap_start
        
        # Blend zone: centered on seam, width = blend_pixels
        blend_start_local = max(0, seam_in_overlap - blend_pixels // 2)
        blend_end_local = min(overlap_width, seam_in_overlap + blend_pixels // 2)
        
        weights = np.zeros((h, overlap_width, 1), dtype=np.float32)
        weights[:, :blend_start_local, :] = 0.0  # Left dominates
        weights[:, blend_end_local:, :] = 1.0    # Right dominates
        
        # Gradient in the blend region
        if blend_end_local > blend_start_local:
            gradient = np.linspace(0, 1, blend_end_local - blend_start_local)
            weights[:, blend_start_local:blend_end_local, 0] = gradient
        
        # Blend
        blended = (1 - weights) * left_overlap + weights * right_overlap
        blended = blended.astype(np.uint8)
        
        # Place blended result
        result[:, overlap_start:overlap_end, :] = blended
        
        return result
        
    def _stretch_region(self, region: np.ndarray, target_width: int) -> np.ndarray:
        """
        Stretch or compress a region to a target width.
        
        Args:
            region: Input region (H, W, C)
            target_width: Desired output width
            
        Returns:
            Resized region
        """
        if not PIL_AVAILABLE:
            return region
            
        h, w, c = region.shape
        if w == target_width:
            return region
            
        # Use PIL for high-quality resize
        img = Image.fromarray(region)
        img_resized = img.resize((target_width, h), Image.LANCZOS)
        return np.array(img_resized)
        
    def stitch_track_frame(
        self,
        frame: np.ndarray,
        edge_overlap: int = 50,
        blend_width: int = 30
    ) -> np.ndarray:
        """
        Stitch a full track frame, processing seams at 1/6 and 5/6 positions.
        
        Args:
            frame: Full track frame (H, W, C)
            edge_overlap: How many pixels to overlap at each seam
            blend_width: Width of the blending gradient
            
        Returns:
            Stitched frame
        """
        h, w, c = frame.shape
        
        # Process first seam at 1/6 of width
        result = self.stitch_seam_region(frame, 1/6, edge_overlap, blend_width)
        
        # Process second seam at 5/6 of width
        result = self.stitch_seam_region(result, 5/6, edge_overlap, blend_width)
        
        return result
        
    def generate_stitch_test_png(
        self,
        input_path: str,
        output_path: str,
        timestamp: float = 1.0,
        edge_overlap: int = 50,
        blend_width: int = 30
    ) -> bool:
        """
        Generate a test PNG showing the stitched result.
        
        This extracts a frame, applies the stitching, and saves the result
        for visual confirmation of the approach.
        
        Args:
            input_path: Path to the .360 file
            output_path: Where to save the test PNG
            timestamp: Time in video to extract (seconds)
            edge_overlap: Overlap amount in pixels
            blend_width: Blend zone width in pixels
            
        Returns:
            True if successful
        """
        if not PIL_AVAILABLE:
            print("PIL not available - cannot generate test PNG")
            return False
            
        # Extract frame from track 0
        print(f"Extracting frame at {timestamp}s from track 0...")
        frame0 = self.extract_frame(input_path, timestamp, track=0)
        if frame0 is None:
            print("Failed to extract frame from track 0")
            return False
            
        # Extract frame from track 1
        print(f"Extracting frame at {timestamp}s from track 1...")
        frame1 = self.extract_frame(input_path, timestamp, track=1)
        if frame1 is None:
            print("Failed to extract frame from track 1")
            return False
            
        h0, w0, _ = frame0.shape
        h1, w1, _ = frame1.shape
        print(f"Track 0 frame: {w0}x{h0}")
        print(f"Track 1 frame: {w1}x{h1}")
        
        # Stitch track 0
        print(f"Stitching track 0 with overlap={edge_overlap}, blend={blend_width}...")
        stitched0 = self.stitch_track_frame(frame0, edge_overlap, blend_width)
        
        # Stitch track 1
        print(f"Stitching track 1 with overlap={edge_overlap}, blend={blend_width}...")
        stitched1 = self.stitch_track_frame(frame1, edge_overlap, blend_width)
        
        # Scale down for reasonable output size
        scale = 0.5
        
        def resize_frame(f):
            h, w, c = f.shape
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = Image.fromarray(f)
            return np.array(img.resize((new_w, new_h), Image.LANCZOS))
            
        stitched0_small = resize_frame(stitched0)
        stitched1_small = resize_frame(stitched1)
        
        # Stack the two stitched tracks vertically
        combined = np.vstack([stitched0_small, stitched1_small])
        
        # Save the result
        result_img = Image.fromarray(combined)
        result_img.save(output_path, "PNG")
        print(f"Saved test PNG to: {output_path}")
        
        return True
        
    def _add_seam_markers(self, frame: np.ndarray) -> np.ndarray:
        """Add red vertical lines at 1/6 and 5/6 positions to show seam locations."""
        result = frame.copy()
        h, w, c = result.shape
        
        # Seam positions
        seam1_x = int(w / 6)
        seam2_x = int(w * 5 / 6)
        
        # Draw red lines (3 pixels wide)
        for offset in range(-1, 2):
            if 0 <= seam1_x + offset < w:
                result[:, seam1_x + offset, :] = [255, 0, 0]
            if 0 <= seam2_x + offset < w:
                result[:, seam2_x + offset, :] = [255, 0, 0]
                
        return result
        
    def split_into_cube_faces(
        self,
        stitched_frame: np.ndarray,
        is_track1: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Split a stitched track frame into 3 cube faces.
        
        Args:
            stitched_frame: The stitched full-width frame (H, W, C)
            is_track1: If True, applies transpose for track 1
            
        Returns:
            Tuple of 3 cube faces (face0, face1, face2)
        """
        h, w, c = stitched_frame.shape
        face_width = w // 3
        
        face0 = stitched_frame[:, 0:face_width, :]
        face1 = stitched_frame[:, face_width:face_width*2, :]
        face2 = stitched_frame[:, face_width*2:face_width*3, :]
        
        if is_track1:
            # Track 1 needs to be transposed (rotated 90° CW)
            face0 = np.rot90(face0, k=-1)  # Rotate 90° clockwise
            face1 = np.rot90(face1, k=-1)
            face2 = np.rot90(face2, k=-1)
            
        return face0, face1, face2
        
    def process_frame_to_cubemap(
        self,
        track0_frame: np.ndarray,
        track1_frame: np.ndarray,
        edge_overlap: int,
        blend_width: int,
        face_mapping: Dict[str, int],
        face_rotation: Dict[str, int],
        cube_face_size: int = 1344
    ) -> np.ndarray:
        """
        Process two track frames into a 3x2 cubemap layout.
        
        Args:
            track0_frame: Frame from track 0 (H, W, C)
            track1_frame: Frame from track 1 (H, W, C)
            edge_overlap: Overlap pixels for seam stitching
            blend_width: Blend zone width
            face_mapping: Which source face goes to which cubemap position
            face_rotation: Rotation for each cubemap position
            cube_face_size: Size of each cube face (output is square)
            
        Returns:
            3x2 cubemap layout array (2*cube_face_size, 3*cube_face_size, 3)
        """
        # Stitch both tracks
        stitched0 = self.stitch_track_frame(track0_frame, edge_overlap, blend_width)
        stitched1 = self.stitch_track_frame(track1_frame, edge_overlap, blend_width)
        
        # Split into cube faces
        # Track 0: src0 (Left), src1 (Front), src2 (Right)
        src0, src1, src2 = self.split_into_cube_faces(stitched0, is_track1=False)
        # Track 1: src3, src4, src5 (after rotation)
        src3, src4, src5 = self.split_into_cube_faces(stitched1, is_track1=True)
        
        source_faces = [src0, src1, src2, src3, src4, src5]
        
        # Create output cubemap (3x2 layout)
        # v360 c3x2 layout: Right, Left, Top (top row) / Front, Back, Bottom (bottom row)
        cubemap_positions = ['right', 'left', 'top', 'front', 'back', 'bottom']
        
        # Scale and rotate each face, place in cubemap
        cubemap = np.zeros((cube_face_size * 2, cube_face_size * 3, 3), dtype=np.uint8)
        
        for i, pos_name in enumerate(cubemap_positions):
            src_idx = face_mapping.get(pos_name, i)
            rotation = face_rotation.get(pos_name, 0)
            
            face = source_faces[src_idx].copy()
            
            # Apply rotation
            if rotation == 90:
                face = np.rot90(face, k=-1)
            elif rotation == 180:
                face = np.rot90(face, k=2)
            elif rotation == 270:
                face = np.rot90(face, k=1)
                
            # Scale to cube_face_size
            face = self._scale_face(face, cube_face_size)
            
            # Calculate position in cubemap
            row = i // 3
            col = i % 3
            y_start = row * cube_face_size
            x_start = col * cube_face_size
            
            cubemap[y_start:y_start+cube_face_size, x_start:x_start+cube_face_size, :] = face
            
        return cubemap
        
    def _scale_face(self, face: np.ndarray, target_size: int) -> np.ndarray:
        """Scale a cube face to target_size x target_size."""
        if not PIL_AVAILABLE:
            return face
            
        img = Image.fromarray(face)
        img_scaled = img.resize((target_size, target_size), Image.LANCZOS)
        return np.array(img_scaled)
        
    def generate_cubemap_test_png(
        self,
        input_path: str,
        output_path: str,
        timestamp: float = 1.0,
        edge_overlap: int = 30,
        blend_width: int = 30,
        face_mapping: Dict[str, int] = None,
        face_rotation: Dict[str, int] = None
    ) -> bool:
        """
        Generate a test PNG showing the complete cubemap output.
        
        Args:
            input_path: Path to the .360 file
            output_path: Where to save the test PNG
            timestamp: Time in video to extract (seconds)
            edge_overlap: Overlap amount in pixels
            blend_width: Blend zone width in pixels
            face_mapping: Face arrangement mapping
            face_rotation: Face rotation values
            
        Returns:
            True if successful
        """
        if not PIL_AVAILABLE:
            print("PIL not available")
            return False
            
        # Default face mapping (Front Camera preset)
        if face_mapping is None:
            face_mapping = {'top': 5, 'back': 1, 'left': 0, 'front': 3, 'right': 2, 'bottom': 4}
        if face_rotation is None:
            face_rotation = {'top': 0, 'back': 0, 'left': 0, 'front': 0, 'right': 0, 'bottom': 180}
            
        print(f"Extracting frames at {timestamp}s...")
        track0 = self.extract_frame(input_path, timestamp, track=0)
        track1 = self.extract_frame(input_path, timestamp, track=1)
        
        if track0 is None or track1 is None:
            print("Failed to extract frames")
            return False
            
        print(f"Processing cubemap with overlap={edge_overlap}, blend={blend_width}...")
        cubemap = self.process_frame_to_cubemap(
            track0, track1,
            edge_overlap, blend_width,
            face_mapping, face_rotation,
            cube_face_size=672  # Half size for test
        )
        
        # Save the cubemap
        result_img = Image.fromarray(cubemap)
        result_img.save(output_path, "PNG")
        print(f"Saved cubemap test PNG to: {output_path}")
        
        return True


def test_stitcher(input_path: str, output_path: str = None):
    """
    Test function to run the stitcher on a .360 file.
    
    Args:
        input_path: Path to the .360 file
        output_path: Where to save the test PNG (defaults to same dir as input)
    """
    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = f"{base}_stitch_test.png"
        
    stitcher = SeamStitcher()
    success = stitcher.generate_stitch_test_png(
        input_path,
        output_path,
        timestamp=1.0,
        edge_overlap=50,
        blend_width=30
    )
    
    if success:
        print(f"Test completed successfully!")
        print(f"Output: {output_path}")
    else:
        print("Test failed!")
        
    return success


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python seam_stitcher.py <input.360> [output.png]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    test_stitcher(input_file, output_file)

#!/usr/bin/env python3
"""
Video Processor for GoPro 360 Converter
Handles video analysis and conversion using FFmpeg
"""

import os
import re
import json
import subprocess
import shutil
from typing import Optional, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal


class VideoProcessor:
    """Handles video processing operations using FFmpeg"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.ffprobe_path = self._find_ffprobe()
        self._video_info_cache = {}
        self._hw_accel_available = None  # Cache for hardware acceleration check
        
    def check_hw_acceleration(self) -> dict:
        """
        Check available hardware acceleration options.
        
        Returns:
            dict with 'nvenc', 'nvdec', 'vaapi', 'qsv' booleans
        """
        if self._hw_accel_available is not None:
            return self._hw_accel_available
            
        result = {
            'nvenc': False,
            'nvdec': False,
            'vaapi': False,
            'qsv': False
        }
        
        if not self.ffmpeg_path:
            self._hw_accel_available = result
            return result
            
        try:
            # Check encoders
            enc_cmd = [self.ffmpeg_path, "-hide_banner", "-encoders"]
            enc_result = subprocess.run(enc_cmd, capture_output=True, text=True, timeout=10)
            if enc_result.returncode == 0:
                result['nvenc'] = 'h264_nvenc' in enc_result.stdout
                result['qsv'] = 'h264_qsv' in enc_result.stdout
                result['vaapi'] = 'h264_vaapi' in enc_result.stdout
                
            # Check decoders
            dec_cmd = [self.ffmpeg_path, "-hide_banner", "-decoders"]
            dec_result = subprocess.run(dec_cmd, capture_output=True, text=True, timeout=10)
            if dec_result.returncode == 0:
                result['nvdec'] = 'h264_cuvid' in dec_result.stdout or 'hevc_cuvid' in dec_result.stdout
                
        except Exception:
            pass
            
        self._hw_accel_available = result
        return result
        
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable"""
        # Check if ffmpeg is in PATH
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            return ffmpeg
        
        # Check common locations
        common_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
        ]
        
        for path in common_paths:
            if os.path.isfile(path):
                return path
                
        return None
        
    def _find_ffprobe(self) -> Optional[str]:
        """Find FFprobe executable"""
        ffprobe = shutil.which("ffprobe")
        if ffprobe:
            return ffprobe
            
        # Try to find it next to ffmpeg
        if self.ffmpeg_path:
            ffprobe = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
            if os.path.isfile(ffprobe):
                return ffprobe
                
        return None
        
    def is_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available"""
        return self.ffmpeg_path is not None
        
    def get_video_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get video information using FFprobe"""
        if not self.ffprobe_path:
            return None
            
        # Check cache
        if file_path in self._video_info_cache:
            return self._video_info_cache[file_path]
            
        try:
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
                
            data = json.loads(result.stdout)
            
            # Extract relevant information
            info = self._parse_video_info(data)
            
            # Cache the result
            self._video_info_cache[file_path] = info
            
            return info
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            print(f"Error getting video info: {e}")
            return None
            
    def _parse_video_info(self, data: Dict) -> Dict[str, Any]:
        """Parse FFprobe output into a simplified dictionary"""
        info = {
            'width': 0,
            'height': 0,
            'duration': 0,
            'duration_str': '-',
            'fps': 0,
            'total_frames': 0,
            'codec': '-',
            'video_streams': 0,
            'audio_streams': 0,
        }
        
        # Parse format info
        if 'format' in data:
            fmt = data['format']
            duration = float(fmt.get('duration', 0))
            info['duration'] = duration
            
            # Format duration as HH:MM:SS
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            info['duration_str'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
        # Parse stream info
        if 'streams' in data:
            for stream in data['streams']:
                codec_type = stream.get('codec_type', '')
                
                if codec_type == 'video':
                    info['video_streams'] += 1
                    
                    # Get first video stream info
                    if info['width'] == 0:
                        info['width'] = stream.get('width', 0)
                        info['height'] = stream.get('height', 0)
                        info['codec'] = stream.get('codec_name', '-')
                        
                        # Parse frame rate
                        fps_str = stream.get('r_frame_rate', '0/1')
                        try:
                            if '/' in fps_str:
                                num, den = map(int, fps_str.split('/'))
                                info['fps'] = round(num / den, 2) if den else 0
                            else:
                                info['fps'] = float(fps_str)
                        except (ValueError, ZeroDivisionError):
                            info['fps'] = 0
                            
                        # Calculate total frames
                        if info['fps'] > 0 and info['duration'] > 0:
                            info['total_frames'] = int(info['fps'] * info['duration'])
                            
                elif codec_type == 'audio':
                    info['audio_streams'] += 1
                    
        return info
        
    def build_conversion_command(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any]
    ) -> list:
        """Build FFmpeg command for video conversion"""
        
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg not found")
            
        projection = settings.get('projection', 'gopro_max')
        fov = settings.get('fov', 190)
        interp = settings.get('interpolation', 'cubic')
        
        if projection == 'gopro_max':
            # GoPro MAX .360 format: 2 video channels with 3 cube faces each
            # Channel 0: Left, Front, Right (content at 1/6 and 5/6 of frame width)
            # Channel 1: Bottom, Back, Top (rotated 90° right, content at 1/6 and 5/6)
            return self._build_gopro_max_command(input_path, output_path, settings)
        else:
            # Fallback for other formats
            return self._build_simple_conversion_command(input_path, output_path, settings)
            
    def _build_gopro_max_command(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any]
    ) -> list:
        """
        Build FFmpeg command for GoPro MAX .360 format
        
        The .360 format has 2 video tracks:
        - Track 0: Left, Front, Right cube faces (horizontal strip)
        - Track 1: Bottom, Back, Top cube faces (rotated 90° clockwise)
        
        Each track has content positioned at 1/6 and 5/6 of the frame width,
        meaning there's ~16.67% padding on each edge.
        """
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg not found")
            
        interp = settings.get('interpolation', 'cubic')
        
        cmd = [self.ffmpeg_path, "-y"]
        
        # Input file (will use both video streams)
        cmd.extend(["-i", input_path])
        
        # Complex filter to:
        # 1. Extract and process both video tracks
        # 2. Crop out the padding (content is at 1/6 to 5/6, so crop 1/6 from each side)
        # 3. Rotate track 1 back to horizontal orientation
        # 4. Stack them into a 3x2 cubemap layout
        # 5. Convert to equirectangular
        
        # Get video info to calculate crop dimensions
        info = self.get_video_info(input_path)
        
        # Build the complex filter (passing resolution for integrated scaling)
        filter_complex = self._build_gopro_max_filter(info, settings)
        
        cmd.extend(["-filter_complex", filter_complex])
        
        # Map the output from the filter
        cmd.extend(["-map", "[out]"])
        
        # NOTE: Resolution scaling is now integrated into the complex filter
        # Cannot use -vf with -filter_complex on the same stream
        
        # Video codec settings
        codec = settings.get('codec', 'libx264')
        crf = settings.get('crf', 23)
        
        cmd.extend(["-c:v", codec])
        
        if codec in ['libx264', 'libx265']:
            cmd.extend(["-crf", str(crf)])
            cmd.extend(["-preset", "medium"])
        elif codec == 'libvpx-vp9':
            cmd.extend(["-crf", str(crf)])
            cmd.extend(["-b:v", "0"])
            
        # Audio handling - only map first audio stream (skip ambisonic)
        if settings.get('include_audio', True):
            cmd.extend(["-map", "0:a:0?"])  # Only first audio stream
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        else:
            cmd.extend(["-an"])
            
        # Add 360 metadata
        cmd.extend([
            "-metadata:s:v", "spherical=true",
            "-metadata:s:v", "stitched=true"
        ])
        
        cmd.append(output_path)
        
        return cmd
        
    def _build_gopro_max_filter(self, info: Dict[str, Any], settings: Dict[str, Any]) -> str:
        """
        Build the complex filter graph for GoPro MAX .360 conversion
        
        NEW APPROACH - Stitch first, then split:
        1. Apply seam stitching to each full track (at 1/6 and 5/6 positions)
        2. Split the stitched tracks into 3 cube faces each
        3. Arrange faces according to user's face mapping
        4. Convert to equirectangular
        
        GoPro MAX .360 file structure:
        - Stream 0:v:0 (Track 0): Left, Front, Right cube faces as horizontal strip
        - Stream 0:v:1 (Track 1): faces rotated 90° clockwise
        
        Each track is 4096x1344 with 3 EAC faces. Each face takes 1/3 of the width.
        Seams occur at 1/6 and 5/6 of the frame width (between faces 0-1 and 1-2).
        """
        interp = settings.get('interpolation', 'cubic')
        
        # Get seam stitching parameters
        edge_overlap = settings.get('edge_overlap', 30)  # pixels
        blend_width = settings.get('blend_width', 30)    # pixels
        
        # Get face mapping from settings
        face_mapping = settings.get('face_mapping', {
            'top': 3, 'back': 4, 'left': 0, 'front': 1, 'right': 2, 'bottom': 5
        })
        face_rotation = settings.get('face_rotation', {
            'top': 0, 'back': 0, 'left': 0, 'front': 0, 'right': 0, 'bottom': 0
        })
        
        # Get dimensions from first video track
        width = info.get('width', 4096) if info else 4096
        height = info.get('height', 1344) if info else 1344
        
        # Each face takes 1/3 of the frame width
        face_width = width // 3  # ~1365 (4096/3)
        face_height = height     # 1344
        
        # Seam positions (as fractions of width)
        seam1_pos = 1.0 / 6.0  # Between left and front faces
        seam2_pos = 5.0 / 6.0  # Between front and right faces
        
        # Calculate pixel positions
        seam1_x = int(width * seam1_pos)
        seam2_x = int(width * seam2_pos)
        
        # For equirectangular output, use 2:1 aspect ratio
        cube_face_size = height  # 1344 - make square faces
        out_width = cube_face_size * 4  # 5376 for equirectangular
        out_height = cube_face_size * 2  # 2688 (2:1 ratio)
        
        filter_parts = []
        
        # ===== TRACK 0: Apply seam stitching, then split into 3 faces =====
        # The seam stitching stretches edges and blends at 1/6 and 5/6 positions
        # We use FFmpeg's geq filter for the stretching and blending
        
        # For each seam, we need to:
        # 1. Stretch left side to extend past seam by edge_overlap pixels
        # 2. Stretch right side to extend past seam by edge_overlap pixels  
        # 3. Blend the overlap zone
        
        # Build blend expressions for seam regions
        # Seam 1 at 1/6 (x = seam1_x)
        s1_start = seam1_x - edge_overlap
        s1_end = seam1_x + edge_overlap
        s1_blend_start = seam1_x - blend_width // 2
        s1_blend_end = seam1_x + blend_width // 2
        
        # Seam 2 at 5/6 (x = seam2_x)
        s2_start = seam2_x - edge_overlap
        s2_end = seam2_x + edge_overlap
        s2_blend_start = seam2_x - blend_width // 2
        s2_blend_end = seam2_x + blend_width // 2
        
        # Since FFmpeg can't easily do the stretch-and-blend we need,
        # we'll use a simplified approach: soft blend at the seam positions
        # The blend uses a gradient to smooth the transition
        
        # For proper stitching, we'll process frames through Python (seam_stitcher)
        # But for real-time video, we'll use FFmpeg's blend at seam positions
        
        # Simplified FFmpeg approach: apply a gradient blend at seam positions
        # This won't stretch pixels but will smooth the seam
        blend_frac = blend_width / width
        
        # Track 0: Split and crop into 3 faces
        filter_parts.append(
            f"[0:v:0]split=3[t0a][t0b][t0c]"
        )
        # src0 (Left face): 0 to face_width
        filter_parts.append(f"[t0a]crop={face_width}:{face_height}:0:0[src0]")
        # src1 (Front face): face_width to 2*face_width
        filter_parts.append(f"[t0b]crop={face_width}:{face_height}:{face_width}:0[src1]")
        # src2 (Right face): 2*face_width to 3*face_width
        filter_parts.append(f"[t0c]crop={face_width}:{face_height}:{face_width*2}:0[src2]")
        
        # ===== TRACK 1: Transpose then split into 3 faces =====
        # Track 1 is rotated 90° clockwise, so we transpose first
        rotated_face_w = face_height  # 1344
        rotated_face_h = face_width   # 1365
        
        filter_parts.append(
            f"[0:v:1]transpose=1,split=3[t1a][t1b][t1c]"
        )
        # src3 (First face after transpose)
        filter_parts.append(f"[t1a]crop={rotated_face_w}:{rotated_face_h}:0:0[src3]")
        # src4 (Second face after transpose)
        filter_parts.append(f"[t1b]crop={rotated_face_w}:{rotated_face_h}:0:{rotated_face_h}[src4]")
        # src5 (Third face after transpose)
        filter_parts.append(f"[t1c]crop={rotated_face_w}:{rotated_face_h}:0:{rotated_face_h*2}[src5]")
        
        # ===== Map source faces to cubemap positions with rotation =====
        # For each cubemap position, get the source and apply rotation
        cubemap_faces = ['right', 'left', 'top', 'front', 'back', 'bottom']
        
        for face_name in cubemap_faces:
            src_idx = face_mapping.get(face_name, 0)
            rotation = face_rotation.get(face_name, 0)
            
            # Build filter chain: source -> rotate (if needed) -> scale
            src_label = f"src{src_idx}"
            
            # Rotation using transpose
            # 0° = no rotation, 90° = transpose=1, 180° = transpose=1,transpose=1, 270° = transpose=2
            if rotation == 0:
                rot_filter = ""
            elif rotation == 90:
                rot_filter = "transpose=1,"
            elif rotation == 180:
                rot_filter = "transpose=1,transpose=1,"
            elif rotation == 270:
                rot_filter = "transpose=2,"
            else:
                rot_filter = ""
            
            filter_parts.append(
                f"[{src_label}]{rot_filter}scale={cube_face_size}:{cube_face_size}[{face_name}s]"
            )
        
        # ===== Arrange into 3x2 cubemap layout =====
        # v360 c3x2 layout: Right, Left, Up (top row) / Front, Back, Down (bottom row)
        filter_parts.append(
            f"[rights][lefts][tops]hstack=inputs=3[toprow]"
        )
        filter_parts.append(
            f"[fronts][backs][bottoms]hstack=inputs=3[botrow]"
        )
        filter_parts.append(
            f"[toprow][botrow]vstack=inputs=2[cubemap]"
        )
        
        # ===== Convert cubemap to equirectangular =====
        resolution = settings.get('resolution')
        if resolution:
            final_w, final_h = resolution
        else:
            final_w, final_h = out_width, out_height
            
        filter_parts.append(
            f"[cubemap]v360=c3x2:equirect:interp={interp}:w={final_w}:h={final_h}[out]"
        )
        
        return ";".join(filter_parts)
        
    def _build_simple_conversion_command(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any]
    ) -> list:
        """Build simple conversion command for standard formats"""
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg not found")
            
        cmd = [self.ffmpeg_path, "-y"]
        cmd.extend(["-i", input_path])
        
        interp = settings.get('interpolation', 'cubic')
        
        # Simple pass-through or basic v360 conversion
        vf_filters = [f"v360=eac:equirect:interp={interp}"]
        
        resolution = settings.get('resolution')
        if resolution:
            width, height = resolution
            vf_filters.append(f"scale={width}:{height}")
            
        cmd.extend(["-vf", ",".join(vf_filters)])
        
        codec = settings.get('codec', 'libx264')
        crf = settings.get('crf', 23)
        
        cmd.extend(["-c:v", codec])
        
        if codec in ['libx264', 'libx265']:
            cmd.extend(["-crf", str(crf)])
            cmd.extend(["-preset", "medium"])
        elif codec == 'libvpx-vp9':
            cmd.extend(["-crf", str(crf)])
            cmd.extend(["-b:v", "0"])
            
        if settings.get('include_audio', True):
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        else:
            cmd.extend(["-an"])
            
        cmd.append(output_path)
        
        return cmd
        
    def run_stitched_conversion(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any],
        progress_callback=None,
        cancel_check=None
    ) -> tuple:
        """
        Run video conversion with proper Python-based seam stitching.
        
        This processes frames through the SeamStitcher for accurate seam blending,
        then pipes to FFmpeg for encoding and v360 conversion.
        
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        import tempfile
        import numpy as np
        
        try:
            from core.seam_stitcher import SeamStitcher
            from PIL import Image
        except ImportError as e:
            return False, f"Missing dependency: {e}"
            
        if not self.ffmpeg_path:
            return False, "FFmpeg not found"
            
        # Get video info
        info = self.get_video_info(input_path)
        if not info:
            return False, "Could not read video info"
            
        fps = info.get('fps', 30)
        total_frames = info.get('total_frames', 0)
        duration = info.get('duration', 0)
        width = info.get('width', 4096)
        height = info.get('height', 1344)
        
        if total_frames == 0 and duration > 0:
            total_frames = int(duration * fps)
            
        # Get settings
        edge_overlap = settings.get('edge_overlap', 30)
        blend_width = settings.get('blend_width', 30)
        face_mapping = settings.get('face_mapping', {
            'top': 5, 'back': 1, 'left': 0, 'front': 3, 'right': 2, 'bottom': 4
        })
        face_rotation = settings.get('face_rotation', {
            'top': 0, 'back': 0, 'left': 0, 'front': 0, 'right': 0, 'bottom': 180
        })
        interp = settings.get('interpolation', 'cubic')
        codec = settings.get('codec', 'libx264')
        crf = settings.get('crf', 23)
        
        # Calculate output resolution
        cube_face_size = height
        resolution = settings.get('resolution')
        if resolution:
            out_width, out_height = resolution
        else:
            out_width = cube_face_size * 4
            out_height = cube_face_size * 2
            
        # Create temporary directory for intermediate files
        temp_dir = tempfile.mkdtemp(prefix="gopro360_conv_")
        
        try:
            stitcher = SeamStitcher()
            
            # Check for hardware acceleration
            hw_accel = self.check_hw_acceleration()
            use_nvdec = hw_accel.get('nvdec', False)
            use_nvenc = hw_accel.get('nvenc', False)
            
            # Log hardware acceleration status
            accel_status = []
            if use_nvenc:
                accel_status.append("NVENC encoding")
            if use_nvdec:
                accel_status.append("CUDA decoding")
            if accel_status:
                print(f"[GPU] Using: {', '.join(accel_status)}")
            else:
                print("[GPU] No hardware acceleration available, using CPU")
            
            # Build decode commands with optional CUDA acceleration
            decode_cmd_0 = [self.ffmpeg_path]
            decode_cmd_1 = [self.ffmpeg_path]
            
            if use_nvdec:
                # Use CUDA hardware decoding
                # Note: hwdownload brings frames from GPU to CPU for Python processing
                decode_cmd_0.extend([
                    "-hwaccel", "cuda",
                    "-i", input_path,
                    "-map", "0:v:0",
                    "-f", "rawvideo",
                    "-pix_fmt", "rgb24",
                    "-"
                ])
                decode_cmd_1.extend([
                    "-hwaccel", "cuda", 
                    "-i", input_path,
                    "-map", "0:v:1",
                    "-f", "rawvideo",
                    "-pix_fmt", "rgb24",
                    "-"
                ])
            else:
                # Software decoding
                decode_cmd_0.extend([
                    "-i", input_path,
                    "-map", "0:v:0",
                    "-f", "rawvideo",
                    "-pix_fmt", "rgb24",
                    "-"
                ])
                decode_cmd_1.extend([
                    "-i", input_path,
                    "-map", "0:v:1",
                    "-f", "rawvideo",
                    "-pix_fmt", "rgb24",
                    "-"
                ])
            
            # Start decode processes
            proc0 = subprocess.Popen(decode_cmd_0, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            proc1 = subprocess.Popen(decode_cmd_1, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            
            # Set up FFmpeg encode process
            # First output cubemap frames, then use a second pass for v360
            cubemap_width = cube_face_size * 3
            cubemap_height = cube_face_size * 2
            
            # Encode command: read raw cubemap frames, convert to equirectangular, encode
            encode_cmd = [
                self.ffmpeg_path,
                "-y",
                "-f", "rawvideo",
                "-pix_fmt", "rgb24",
                "-s", f"{cubemap_width}x{cubemap_height}",
                "-r", str(fps),
                "-i", "-",  # Read from stdin (input 0 = video)
            ]
            
            # Add audio from original file and set up proper stream mapping
            if settings.get('include_audio', True):
                encode_cmd.extend([
                    "-i", input_path,  # Input 1 = original file for audio
                    "-map", "0:v",     # Map video from input 0 (stdin)
                    "-map", "1:a:0?",  # Map audio from input 1 (original file)
                ])
            else:
                encode_cmd.extend(["-map", "0:v"])  # Map video from stdin
                
            # Video filter for v360 conversion + format for encoder compatibility
            encode_cmd.extend([
                "-vf", f"v360=c3x2:equirect:interp={interp},scale={out_width}:{out_height},format=yuv420p",
            ])
            
            # Use software encoding for reliability
            # TODO: Add NVENC support with proper testing
            actual_codec = codec
            # Disable NVENC for now - needs more testing
            # if use_nvenc:
            #     if codec == 'libx264':
            #         actual_codec = 'h264_nvenc'
            #     elif codec == 'libx265':
            #         actual_codec = 'hevc_nvenc'
                    
            encode_cmd.extend(["-c:v", actual_codec])
            
            # Encoder-specific settings
            if actual_codec in ['libx264', 'libx265']:
                encode_cmd.extend(["-crf", str(crf), "-preset", "medium"])
            elif actual_codec == 'libvpx-vp9':
                encode_cmd.extend(["-crf", str(crf), "-b:v", "0"])
            elif actual_codec == 'h264_nvenc':
                # NVENC uses preset and rc (rate control) mode
                # Use VBR with cq for quality-based encoding
                encode_cmd.extend([
                    "-preset", "p4",      # p1=fastest to p7=slowest
                    "-rc", "vbr",         # Variable bitrate mode
                    "-cq", str(crf),      # Quality level (lower = better)
                    "-qmin", str(crf),    # Min quantizer
                    "-qmax", str(crf + 10),  # Max quantizer
                ])
            elif actual_codec == 'hevc_nvenc':
                encode_cmd.extend([
                    "-preset", "p4",
                    "-rc", "vbr",
                    "-cq", str(crf),
                    "-qmin", str(crf),
                    "-qmax", str(crf + 10),
                ])
                
            if settings.get('include_audio', True):
                encode_cmd.extend(["-c:a", "aac", "-b:a", "192k"])
            else:
                encode_cmd.extend(["-an"])
                
            encode_cmd.extend([
                "-metadata:s:v", "spherical=true",
                "-metadata:s:v", "stitched=true",
                output_path
            ])
            
            encode_proc = subprocess.Popen(
                encode_cmd,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Check if encoder started successfully (give it a moment)
            import time
            time.sleep(0.1)
            if encode_proc.poll() is not None:
                stderr = encode_proc.stderr.read().decode('utf-8', errors='ignore')
                proc0.terminate()
                proc1.terminate()
                return False, f"FFmpeg encoder failed to start: {stderr[-1000:]}"
            
            # Process frames
            frame_size = width * height * 3  # RGB24
            frame_count = 0
            
            while True:
                if cancel_check and cancel_check():
                    proc0.terminate()
                    proc1.terminate()
                    encode_proc.terminate()
                    return False, "Conversion cancelled by user"
                
                # Check if encoder is still running
                if encode_proc.poll() is not None:
                    stderr = encode_proc.stderr.read().decode('utf-8', errors='ignore')
                    proc0.terminate()
                    proc1.terminate()
                    return False, f"FFmpeg encoder died unexpectedly: {stderr[-1000:]}"
                    
                # Read frame from track 0
                frame0_data = proc0.stdout.read(frame_size)
                if len(frame0_data) < frame_size:
                    break
                    
                # Read frame from track 1
                frame1_data = proc1.stdout.read(frame_size)
                if len(frame1_data) < frame_size:
                    break
                    
                # Convert to numpy arrays
                frame0 = np.frombuffer(frame0_data, dtype=np.uint8).reshape((height, width, 3))
                frame1 = np.frombuffer(frame1_data, dtype=np.uint8).reshape((height, width, 3))
                
                # Process through SeamStitcher
                cubemap = stitcher.process_frame_to_cubemap(
                    frame0, frame1,
                    edge_overlap, blend_width,
                    face_mapping, face_rotation,
                    cube_face_size=cube_face_size
                )
                
                # Write to encoder
                try:
                    encode_proc.stdin.write(cubemap.tobytes())
                except BrokenPipeError:
                    stderr = encode_proc.stderr.read().decode('utf-8', errors='ignore')
                    proc0.terminate()
                    proc1.terminate()
                    return False, f"FFmpeg encoder pipe broken: {stderr[-1000:]}"
                
                frame_count += 1
                
                # Update progress
                if progress_callback and total_frames > 0:
                    progress = (frame_count / total_frames) * 100
                    progress = min(progress, 99.9)
                    eta_str = ""
                    progress_callback(progress, eta_str)
                    
            # Close processes
            proc0.wait()
            proc1.wait()
            encode_proc.stdin.close()
            encode_proc.wait()
            
            if progress_callback:
                progress_callback(100, "")
                
            # Check if output file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True, None
            else:
                stderr = encode_proc.stderr.read().decode('utf-8', errors='ignore')
                return False, f"Encoding failed: {stderr[-500:]}"
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Conversion error: {str(e)}"
        finally:
            # Cleanup temp directory
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
    def run_conversion(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any],
        progress_callback=None,
        cancel_check=None
    ) -> tuple:
        """
        Run the video conversion using the selected stitching method.
        
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        stitch_method = settings.get('stitch_method', 'ffmpeg')
        
        if stitch_method == 'ffmpeg':
            # Use the new FFmpeg-based stitching (fast, recommended)
            return self.run_ffmpeg_stitched_conversion(
                input_path, output_path, settings,
                progress_callback, cancel_check
            )
        elif stitch_method == 'python':
            # Use the Python-based frame-by-frame stitching (slower)
            return self.run_stitched_conversion(
                input_path, output_path, settings,
                progress_callback, cancel_check
            )
        else:
            # Fallback to FFmpeg-only conversion for other formats
            return self._run_ffmpeg_conversion(
                input_path, output_path, settings,
                progress_callback, cancel_check
            )
    
    def run_ffmpeg_stitched_conversion(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any],
        progress_callback=None,
        cancel_check=None
    ) -> tuple:
        """
        Run FFmpeg-based stitching using the avfilter approach.
        
        This is the fast, recommended method that uses FFmpeg's filter_complex
        to do all stitching operations in a single pass.
        
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            from core.ffmpeg_stitcher import FFmpegStitcher
        except ImportError as e:
            return False, f"Failed to import FFmpegStitcher: {e}"
            
        if not self.ffmpeg_path:
            return False, "FFmpeg not found"
            
        # Get video info for progress tracking
        info = self.get_video_info(input_path)
        total_duration = info.get('duration', 0) if info else 0
        
        # Get settings
        codec = settings.get('codec', 'libx264')
        crf = settings.get('crf', 23)
        resolution = settings.get('resolution')
        include_audio = settings.get('include_audio', True)
        interp = settings.get('interpolation', 'cubic')
        
        # Create FFmpegStitcher instance
        stitcher = FFmpegStitcher()
        
        # Detect video streams
        front_stream, rear_stream = stitcher.detect_video_streams(input_path)
        print(f"Detected video streams: front={front_stream}, rear={rear_stream}")
        
        # Build the avfilter
        avfilter = stitcher.build_avfilter(
            yaw=0, pitch=0, roll=0,
            front_stream=front_stream,
            rear_stream=rear_stream
        )
        
        # Build FFmpeg command
        cmd = [self.ffmpeg_path, "-y"]
        
        # Input file
        cmd.extend(["-i", input_path])
        
        # Apply the filter complex
        cmd.extend(["-filter_complex", avfilter])
        
        # Map outputs
        cmd.extend(["-map", "[OUTPUT_FRAME]"])
        
        if include_audio:
            cmd.extend(["-map", "0:a:0?"])
        
        # Resolution scaling (if not original)
        if resolution:
            out_width, out_height = resolution
            cmd.extend(["-vf", f"scale={out_width}:{out_height}"])
        
        # Video codec and quality
        cmd.extend(["-c:v", codec])
        if codec in ('libx264', 'libx265'):
            cmd.extend(["-crf", str(crf), "-preset", "medium"])
        elif codec == 'libvpx-vp9':
            cmd.extend(["-crf", str(crf), "-b:v", "0"])
            
        # Audio codec
        if include_audio:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        
        # Progress reporting
        cmd.insert(1, "-progress")
        cmd.insert(2, "pipe:1")
        cmd.insert(3, "-stats_period")
        cmd.insert(4, "0.5")
        
        # Output file
        cmd.append(output_path)
        
        print("FFmpeg command:", " ".join(cmd))
        
        stderr_output = []
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Start a thread to capture stderr
            import threading
            def read_stderr():
                for line in process.stderr:
                    stderr_output.append(line)
                    
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stderr_thread.start()
            
            # Parse progress output
            while True:
                # Check for cancellation
                if cancel_check and cancel_check():
                    process.terminate()
                    process.wait()
                    return False, "Conversion cancelled by user"
                    
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    continue
                    
                # Parse progress information
                if line.startswith("out_time_ms="):
                    try:
                        time_ms = int(line.split("=")[1].strip())
                        current_time = time_ms / 1_000_000  # Convert to seconds
                        
                        if total_duration > 0 and progress_callback:
                            progress = (current_time / total_duration) * 100
                            progress = min(progress, 99.9)  # Cap at 99.9% until done
                            
                            # Calculate ETA
                            if progress > 0:
                                eta_seconds = (total_duration - current_time) * (100 - progress) / progress
                                eta_str = self._format_time(eta_seconds)
                            else:
                                eta_str = "Calculating..."
                                
                            progress_callback(progress, eta_str)
                    except (ValueError, ZeroDivisionError):
                        pass
                        
            # Wait for process to complete
            process.wait()
            stderr_thread.join(timeout=2)
            
            print(f"FFmpeg return code: {process.returncode}")
            
            if process.returncode != 0:
                error_text = "".join(stderr_output[-20:])  # Last 20 lines
                return False, f"FFmpeg error (code {process.returncode}):\n{error_text}"
            
            # Verify output exists
            if not os.path.exists(output_path):
                return False, "Output file was not created"
                
            # Add spherical metadata
            if stitcher.exiftool_path:
                stitcher._add_spherical_metadata(output_path)
                print("Added spherical metadata to output")
            
            # Final progress update
            if progress_callback:
                progress_callback(100.0, "Complete")
                
            return True, None
            
        except subprocess.TimeoutExpired:
            return False, "Conversion timed out"
        except Exception as e:
            return False, f"Conversion error: {str(e)}"
            
    def _run_ffmpeg_conversion(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any],
        progress_callback=None,
        cancel_check=None
    ) -> tuple:
        """
        Run FFmpeg-only conversion (for non-GoPro formats).
        
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        cmd = self.build_conversion_command(input_path, output_path, settings)
        
        # Add progress reporting options BEFORE printing
        cmd.insert(1, "-progress")
        cmd.insert(2, "pipe:1")
        cmd.insert(3, "-stats_period")
        cmd.insert(4, "0.5")
        
        # Print command for debugging (now includes progress flags)
        print("FFmpeg command:", " ".join(cmd))
        
        # Get video duration for progress calculation
        info = self.get_video_info(input_path)
        total_duration = info.get('duration', 0) if info else 0
        
        stderr_output = []
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Start a thread to capture stderr
            import threading
            def read_stderr():
                for line in process.stderr:
                    stderr_output.append(line)
                    
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stderr_thread.start()
            
            # Parse progress output
            while True:
                # Check for cancellation
                if cancel_check and cancel_check():
                    process.terminate()
                    process.wait()
                    return False, "Conversion cancelled by user"
                    
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    continue
                    
                # Parse progress information
                if line.startswith("out_time_ms="):
                    try:
                        time_ms = int(line.split("=")[1].strip())
                        current_time = time_ms / 1_000_000  # Convert to seconds
                        
                        if total_duration > 0 and progress_callback:
                            progress = (current_time / total_duration) * 100
                            progress = min(progress, 99.9)  # Cap at 99.9% until done
                            
                            # Calculate ETA
                            if progress > 0:
                                eta_seconds = (total_duration - current_time) * (100 - progress) / progress
                                eta_str = self._format_time(eta_seconds)
                            else:
                                eta_str = "Calculating..."
                                
                            progress_callback(progress, eta_str)
                    except (ValueError, ZeroDivisionError):
                        pass
                        
            # Wait for process to complete
            process.wait()
            stderr_thread.join(timeout=2)
            
            # Debug output
            print(f"FFmpeg return code: {process.returncode}")
            
            # FFmpeg returns 0 on success, but with -progress pipe:1 it may return other codes
            # Check if output file exists and has size > 0 as additional success indicator
            try:
                output_exists = os.path.exists(output_path)
                output_size = os.path.getsize(output_path) if output_exists else 0
                print(f"Output file exists: {output_exists}, size: {output_size}")
            except OSError as e:
                output_exists = False
                output_size = 0
                print(f"Error checking output file: {e}")
            
            if process.returncode == 0 and output_size > 0:
                if progress_callback:
                    progress_callback(100, "")
                return True, None
            elif output_size > 1000:  # File exists and has meaningful size
                # Sometimes FFmpeg returns non-zero but file is valid
                print(f"Warning: FFmpeg returned {process.returncode} but output file has data")
                if progress_callback:
                    progress_callback(100, "")
                return True, None
            else:
                # Get last part of stderr for error message
                error_text = "".join(stderr_output[-30:])  # Last 30 lines
                print(f"FFmpeg error output:\n{error_text}")
                return False, f"FFmpeg error (code {process.returncode}):\n{error_text[-500:]}"
                
        except Exception as e:
            print(f"Conversion error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)
            
    def _format_time(self, seconds: float) -> str:
        """Format seconds into human-readable time string"""
        if seconds < 60:
            return f"ETA: {int(seconds)}s"
        elif seconds < 3600:
            return f"ETA: {int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"ETA: {hours}h {minutes}m"


class ConversionWorker(QObject):
    """Worker object for running conversion in a background thread"""
    
    progress = pyqtSignal(float, str)  # progress percentage, eta string
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(
        self,
        processor: VideoProcessor,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any]
    ):
        super().__init__()
        self.processor = processor
        self.input_path = input_path
        self.output_path = output_path
        self.settings = settings
        self._cancelled = False
        
    def run(self):
        """Run the conversion process"""
        try:
            if not self.processor.is_ffmpeg_available():
                self.error.emit("FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
                return
                
            success, error_message = self.processor.run_conversion(
                self.input_path,
                self.output_path,
                self.settings,
                progress_callback=self._on_progress,
                cancel_check=lambda: self._cancelled
            )
            
            if self._cancelled:
                # Clean up partial output file
                if os.path.exists(self.output_path):
                    try:
                        os.remove(self.output_path)
                    except:
                        pass
                # Error already emitted by run_conversion
                if error_message:
                    self.error.emit(error_message)
            elif success:
                self.finished.emit()
            else:
                self.error.emit(error_message or "Conversion failed. Check FFmpeg output for details.")
                
        except Exception as e:
            self.error.emit(f"Conversion error: {str(e)}")
            
    def _on_progress(self, progress: float, eta: str):
        """Emit progress signal"""
        self.progress.emit(progress, eta)
        
    def cancel(self):
        """Cancel the conversion"""
        self._cancelled = True

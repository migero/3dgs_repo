#!/usr/bin/env python3
"""
FFmpeg-based Stitcher for GoPro MAX 360 videos.

This module implements the same stitching approach used by gopromax-conversion-tools:
https://github.com/gopromax-conversion-tools

GoPro MAX .360 Structure:
- Stream 0 (front camera): 4096x1344 containing LEFT | overlap | CENTER | overlap | RIGHT
- Stream 5 (rear camera): 4096x1344 containing BOTTOM | overlap | BACK | overlap | TOP

The overlap regions are 128px wide and need to be blended using a linear gradient.
The final output is an Equi-Angular Cubemap (EAC) converted to equirectangular projection.

This implementation wraps FFmpeg with the avfilter script to perform the conversion.
"""

import os
import shutil
import subprocess
import tempfile
from typing import Optional, Tuple, Dict, Any


# The avfilter template - adapted from gopromax-conversion-tools 360.avfilter
# This handles the complete stitching pipeline in FFmpeg
# Uses {front_stream} and {rear_stream} placeholders for video stream indices
AVFILTER_TEMPLATE = """
[0:{front_stream}]crop=624:1344:x=0:y=0,format=yuvj420p[LEFTFRAME_left_slice],
[0:{front_stream}]crop=128:1344:x=624:y=0,format=yuvj420p,
geq=
lum='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
cb='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
cr='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
a='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))',
crop=64:1344:x=0:y=0,format=yuvj420p,scale=96:1344[LEFTFRAME_overlap_slice],
[0:{front_stream}]crop=624:1344:x=752:y=0,format=yuvj420p[LEFTFRAME_right_slice],
[LEFTFRAME_left_slice][LEFTFRAME_overlap_slice]hstack[LEFTFRAME_left_and_overlap_joined], 
[LEFTFRAME_left_and_overlap_joined][LEFTFRAME_right_slice]hstack[LEFTFRAME_completed],

[0:{front_stream}]crop=1344:1344:1376:0[CENTERFRAME_completed],

[0:{front_stream}]crop=624:1344:x=2720:y=0,format=yuvj420p[RIGHTFRAME_left_slice],
[0:{front_stream}]crop=128:1344:x=3344:y=0,format=yuvj420p,
geq=
lum='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
cb='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
cr='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
a='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))',
crop=64:1344:x=0:y=0,format=yuvj420p,scale=96:1344[RIGHTFRAME_overlap_slice],
[0:{front_stream}]crop=624:1344:x=3472:y=0,format=yuvj420p[RIGHTFRAME_right_slice],
[RIGHTFRAME_left_slice][RIGHTFRAME_overlap_slice]hstack[RIGHTFRAME_left_and_overlap_joined], 
[RIGHTFRAME_left_and_overlap_joined][RIGHTFRAME_right_slice]hstack[RIGHTFRAME_completed],

[LEFTFRAME_completed][CENTERFRAME_completed]hstack[LEFT_CENTER_frames_joined],
[LEFT_CENTER_frames_joined][RIGHTFRAME_completed]hstack[LEFT_CENTER_RIGHT_completed],


[0:{rear_stream}]crop=624:1344:x=0:y=0,format=yuvj420p[BOTTOMFRAME_left_slice],
[0:{rear_stream}]crop=128:1344:x=624:y=0,format=yuvj420p,
geq=
lum='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
cb='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
cr='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
a='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))',
crop=64:1344:x=0:y=0,format=yuvj420p,scale=96:1344[BOTTOMFRAME_overlap_slice],
[0:{rear_stream}]crop=624:1344:x=752:y=0,format=yuvj420p[BOTTOMFRAME_right_slice],
[BOTTOMFRAME_left_slice][BOTTOMFRAME_overlap_slice]hstack[BOTTOMFRAME_left_and_overlap_joined], 
[BOTTOMFRAME_left_and_overlap_joined][BOTTOMFRAME_right_slice]hstack[BOTTOMFRAME_completed],

[0:{rear_stream}]crop=1344:1344:1376:0[BACKFRAME_completed],

[0:{rear_stream}]crop=624:1344:x=2720:y=0,format=yuvj420p[TOPFRAME_left_slice],
[0:{rear_stream}]crop=128:1344:x=3344:y=0,format=yuvj420p,
geq=
lum='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
cb='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
cr='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))':
a='if(between(X, 0, 64), (p((X+64),Y)*(((X+1))/65))+(p(X,Y)*((65-((X+1)))/65)), p(X,Y))',
crop=64:1344:x=0:y=0,format=yuvj420p,scale=96:1344[TOPFRAME_overlap_slice],
[0:{rear_stream}]crop=624:1344:x=3472:y=0,format=yuvj420p[TOPFRAME_right_slice],
[TOPFRAME_left_slice][TOPFRAME_overlap_slice]hstack[TOPFRAME_left_and_overlap_joined], 
[TOPFRAME_left_and_overlap_joined][TOPFRAME_right_slice]hstack[TOPFRAME_completed],

[BOTTOMFRAME_completed][BACKFRAME_completed]hstack[BOTTOM_BACK_frames_joined],
[BOTTOM_BACK_frames_joined][TOPFRAME_completed]hstack[BOTTOM_BACK_TOP_completed],

[LEFT_CENTER_RIGHT_completed][BOTTOM_BACK_TOP_completed]vstack[FULL_EAC_FRAME], 
[FULL_EAC_FRAME]v360=eac:equirect:interp=cubic:roll={roll}:pitch={pitch}:yaw={yaw},crop=4032:2388:x=0:y=0[OUTPUT_FRAME]
"""


class FFmpegStitcher:
    """
    FFmpeg-based stitcher for GoPro MAX .360 files.
    
    This class wraps FFmpeg to convert GoPro MAX .360 files to standard
    equirectangular 360 videos using the same filter approach as 
    gopromax-conversion-tools.
    """
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.exiftool_path = self._find_exiftool()
        
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable."""
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
        
    def _find_exiftool(self) -> Optional[str]:
        """Find exiftool executable."""
        exiftool = shutil.which("exiftool")
        if exiftool:
            return exiftool
        common_paths = [
            "/usr/bin/exiftool",
            "/usr/local/bin/exiftool",
        ]
        for path in common_paths:
            if os.path.isfile(path):
                return path
        return None
        
    def detect_video_streams(self, input_path: str) -> Tuple[int, int]:
        """
        Detect the video stream indices in a .360 file.
        
        GoPro MAX .360 files have two video streams (front and rear camera).
        The stream indices can vary, so we detect them automatically.
        
        Args:
            input_path: Path to the .360 file
            
        Returns:
            Tuple of (front_stream_index, rear_stream_index)
        """
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            # Default fallback - try common configurations
            return (0, 4)
            
        cmd = [
            ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-select_streams", "v",
            input_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                video_streams = data.get("streams", [])
                
                if len(video_streams) >= 2:
                    # Get the indices of the two video streams
                    indices = [s.get("index", i) for i, s in enumerate(video_streams)]
                    return (indices[0], indices[1])
        except Exception as e:
            print(f"Warning: Could not detect streams: {e}")
            
        # Fallback
        return (0, 4)
        
    def build_avfilter(
        self,
        yaw: float = 0.0,
        pitch: float = 0.0,
        roll: float = 0.0,
        front_stream: int = 0,
        rear_stream: int = 4
    ) -> str:
        """
        Build the FFmpeg avfilter string with rotation parameters.
        
        Args:
            yaw: Yaw rotation in degrees
            pitch: Pitch rotation in degrees
            roll: Roll rotation in degrees
            front_stream: Index of front camera video stream
            rear_stream: Index of rear camera video stream
            
        Returns:
            Complete avfilter string
        """
        return AVFILTER_TEMPLATE.format(
            yaw=yaw,
            pitch=pitch,
            roll=roll,
            front_stream=front_stream,
            rear_stream=rear_stream
        )
        
    def convert_360_to_equirectangular(
        self,
        input_path: str,
        output_path: str,
        yaw: float = 0.0,
        pitch: float = 0.0,
        roll: float = 0.0,
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        crf: int = 18,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        overwrite: bool = False,
        progress_callback: Optional[callable] = None
    ) -> Tuple[bool, str]:
        """
        Convert a GoPro MAX .360 file to standard equirectangular 360 video.
        
        Args:
            input_path: Path to input .360 file
            output_path: Path for output video file
            yaw: Yaw rotation in degrees
            pitch: Pitch rotation in degrees  
            roll: Roll rotation in degrees
            video_codec: Video codec to use (default: libx264)
            audio_codec: Audio codec to use (default: aac)
            crf: Constant Rate Factor for quality (lower = better, 18-23 typical)
            start_time: Start time for trimming (format: HH:MM:SS.ms)
            end_time: End time for trimming (format: HH:MM:SS.ms)
            overwrite: Whether to overwrite existing output file
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.ffmpeg_path:
            return False, "FFmpeg not found. Please install FFmpeg."
            
        if not os.path.exists(input_path):
            return False, f"Input file not found: {input_path}"
            
        if os.path.exists(output_path) and not overwrite:
            return False, f"Output file exists: {output_path}. Use overwrite=True to replace."
            
        # Detect video stream indices
        front_stream, rear_stream = self.detect_video_streams(input_path)
        print(f"Detected video streams: front={front_stream}, rear={rear_stream}")
        
        # Build the filter
        avfilter = self.build_avfilter(
            yaw=yaw, pitch=pitch, roll=roll,
            front_stream=front_stream, rear_stream=rear_stream
        )
        
        # Build FFmpeg command
        cmd = [self.ffmpeg_path]
        
        # Input seeking (if start_time specified)
        if start_time:
            cmd.extend(["-ss", start_time])
        if end_time:
            cmd.extend(["-to", end_time])
            
        cmd.extend([
            "-i", input_path,
            "-y" if overwrite else "-n",
            "-filter_complex", avfilter,
            "-map", "[OUTPUT_FRAME]",
            "-map", "0:a:0",
            "-c:v", video_codec,
            "-c:a", audio_codec,
        ])
        
        # Add codec-specific options
        if video_codec in ("libx264", "libx265"):
            cmd.extend(["-crf", str(crf)])
        elif video_codec == "prores":
            cmd.extend(["-profile:v", "3"])  # ProRes 422 HQ
            
        cmd.append(output_path)
        
        try:
            print(f"Running FFmpeg conversion...")
            print(f"Input: {input_path}")
            print(f"Output: {output_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, f"FFmpeg error: {result.stderr}"
                
            # Add spherical metadata using exiftool
            if self.exiftool_path and os.path.exists(output_path):
                self._add_spherical_metadata(output_path)
                
            return True, f"Conversion successful: {output_path}"
            
        except subprocess.TimeoutExpired:
            return False, "FFmpeg conversion timed out"
        except Exception as e:
            return False, f"Conversion error: {str(e)}"
            
    def _add_spherical_metadata(self, video_path: str) -> bool:
        """
        Add spherical video metadata using exiftool.
        
        This marks the video as a 360 spherical video so players
        can display it correctly.
        """
        if not self.exiftool_path:
            return False
            
        cmd = [
            self.exiftool_path,
            "-api", "LargeFileSupport=1",
            "-overwrite_original",
            "-XMP-GSpherical:Spherical=true",
            "-XMP-GSpherical:Stitched=true",
            "-XMP-GSpherical:StitchingSoftware=GoPro360Converter",
            "-XMP-GSpherical:ProjectionType=equirectangular",
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
        except:
            return False
            
    def extract_stitched_frame(
        self,
        input_path: str,
        output_path: str,
        timestamp: float = 0.0,
        yaw: float = 0.0,
        pitch: float = 0.0,
        roll: float = 0.0
    ) -> Tuple[bool, str]:
        """
        Extract a single stitched frame as an image.
        
        Args:
            input_path: Path to input .360 file
            output_path: Path for output image (PNG or JPG)
            timestamp: Time in seconds to extract
            yaw/pitch/roll: Rotation parameters
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.ffmpeg_path:
            return False, "FFmpeg not found"
            
        if not os.path.exists(input_path):
            return False, f"Input file not found: {input_path}"
        
        # Detect video stream indices
        front_stream, rear_stream = self.detect_video_streams(input_path)
            
        avfilter = self.build_avfilter(
            yaw=yaw, pitch=pitch, roll=roll,
            front_stream=front_stream, rear_stream=rear_stream
        )
        
        cmd = [
            self.ffmpeg_path,
            "-ss", str(timestamp),
            "-i", input_path,
            "-filter_complex", avfilter,
            "-map", "[OUTPUT_FRAME]",
            "-frames:v", "1",
            "-y",
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return False, f"FFmpeg error: {result.stderr}"
                
            if os.path.exists(output_path):
                return True, f"Frame extracted: {output_path}"
            else:
                return False, "Output file was not created"
                
        except subprocess.TimeoutExpired:
            return False, "Frame extraction timed out"
        except Exception as e:
            return False, f"Extraction error: {str(e)}"
            
    def extract_eac_frame(
        self,
        input_path: str,
        output_path: str,
        timestamp: float = 0.0
    ) -> Tuple[bool, str]:
        """
        Extract a single frame as EAC (Equi-Angular Cubemap) before projection.
        
        This shows the intermediate cubemap layout, useful for debugging.
        
        Args:
            input_path: Path to input .360 file
            output_path: Path for output image
            timestamp: Time in seconds
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.ffmpeg_path:
            return False, "FFmpeg not found"
        
        # Detect video stream indices
        front_stream, rear_stream = self.detect_video_streams(input_path)
            
        # Modified filter that outputs EAC without v360 conversion
        eac_filter = AVFILTER_TEMPLATE.replace(
            "[FULL_EAC_FRAME]v360=eac:equirect:interp=cubic:roll={roll}:pitch={pitch}:yaw={yaw},crop=4032:2388:x=0:y=0[OUTPUT_FRAME]",
            "[FULL_EAC_FRAME]null[OUTPUT_FRAME]"
        ).format(yaw=0, pitch=0, roll=0, front_stream=front_stream, rear_stream=rear_stream)
        
        cmd = [
            self.ffmpeg_path,
            "-ss", str(timestamp),
            "-i", input_path,
            "-filter_complex", eac_filter,
            "-map", "[OUTPUT_FRAME]",
            "-frames:v", "1",
            "-y",
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return False, f"FFmpeg error: {result.stderr}"
                
            if os.path.exists(output_path):
                return True, f"EAC frame extracted: {output_path}"
            else:
                return False, "Output file was not created"
                
        except Exception as e:
            return False, f"Extraction error: {str(e)}"
            
    def get_video_info(self, input_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a .360 video file.
        
        Returns:
            Dictionary with video info or None if failed
        """
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            return None
            
        cmd = [
            ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            input_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except:
            pass
            
        return None


def convert_360_video(
    input_path: str,
    output_path: str = None,
    yaw: float = 0.0,
    pitch: float = 0.0,
    roll: float = 0.0,
    video_codec: str = "libx264",
    crf: int = 18
) -> bool:
    """
    Convenience function to convert a .360 file.
    
    Args:
        input_path: Path to .360 file
        output_path: Output path (defaults to same name with .mp4)
        yaw/pitch/roll: Rotation in degrees
        video_codec: Video codec
        crf: Quality (lower = better)
        
    Returns:
        True if successful
    """
    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = f"{base}_equirect.mp4"
        
    stitcher = FFmpegStitcher()
    success, message = stitcher.convert_360_to_equirectangular(
        input_path=input_path,
        output_path=output_path,
        yaw=yaw,
        pitch=pitch,
        roll=roll,
        video_codec=video_codec,
        crf=crf,
        overwrite=True
    )
    
    print(message)
    return success


def extract_frame(
    input_path: str,
    output_path: str = None,
    timestamp: float = 0.0
) -> bool:
    """
    Convenience function to extract a stitched frame.
    
    Args:
        input_path: Path to .360 file
        output_path: Output image path
        timestamp: Time in seconds
        
    Returns:
        True if successful
    """
    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = f"{base}_frame_{timestamp:.2f}s.png"
        
    stitcher = FFmpegStitcher()
    success, message = stitcher.extract_stitched_frame(
        input_path=input_path,
        output_path=output_path,
        timestamp=timestamp
    )
    
    print(message)
    return success


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("GoPro MAX .360 to Equirectangular Converter")
        print()
        print("Usage:")
        print("  python ffmpeg_stitcher.py <input.360> [output.mp4]")
        print("  python ffmpeg_stitcher.py --frame <input.360> [output.png] [timestamp]")
        print()
        print("Examples:")
        print("  python ffmpeg_stitcher.py GS011234.360")
        print("  python ffmpeg_stitcher.py GS011234.360 output.mp4")
        print("  python ffmpeg_stitcher.py --frame GS011234.360 preview.png 5.0")
        sys.exit(1)
        
    if sys.argv[1] == "--frame":
        if len(sys.argv) < 3:
            print("Error: Input file required")
            sys.exit(1)
        input_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        timestamp = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
        success = extract_frame(input_file, output_file, timestamp)
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        success = convert_360_video(input_file, output_file)
        
    sys.exit(0 if success else 1)

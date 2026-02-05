#!/usr/bin/env python3
"""
Frame Extractor

Extracts frames from video files using ffmpeg or OpenCV.
Also extracts GPS/geolocation data from GoPro videos and embeds it in EXIF.
"""

import os
import re
import json
import struct
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import cv2
from tqdm import tqdm

# Try to import piexif for EXIF writing
try:
    import piexif
    PIEXIF_AVAILABLE = True
except ImportError:
    PIEXIF_AVAILABLE = False


@dataclass
class GPSPoint:
    """Represents a GPS point with timestamp."""
    latitude: float
    longitude: float
    altitude: float = 0.0
    speed: float = 0.0  # m/s
    timestamp: float = 0.0  # seconds from video start
    datetime: Optional[datetime] = None
    fix: int = 0  # GPS fix quality (0=no fix, 2=2D, 3=3D)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'speed': self.speed,
            'timestamp': self.timestamp,
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'fix': self.fix
        }


@dataclass
class VideoGeoInfo:
    """Geolocation information extracted from a video."""
    # Basic location from metadata
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    
    # Creation time
    creation_time: Optional[datetime] = None
    
    # Camera info
    firmware: Optional[str] = None
    camera_model: Optional[str] = None
    
    # GPS track from GPMF data
    gps_track: List[GPSPoint] = None
    
    # Video info
    duration: float = 0.0
    fps: float = 0.0
    
    def __post_init__(self):
        if self.gps_track is None:
            self.gps_track = []
    
    def has_location(self) -> bool:
        """Check if basic location is available."""
        return self.latitude is not None and self.longitude is not None
    
    def has_gps_track(self) -> bool:
        """Check if GPS track data is available."""
        return len(self.gps_track) > 0
    
    def get_gps_at_time(self, timestamp: float) -> Optional[GPSPoint]:
        """
        Get interpolated GPS position at a specific timestamp.
        
        Args:
            timestamp: Time in seconds from video start
            
        Returns:
            Interpolated GPSPoint or None
        """
        if not self.gps_track:
            # Return basic location if no track
            if self.has_location():
                return GPSPoint(
                    latitude=self.latitude,
                    longitude=self.longitude,
                    altitude=self.altitude or 0.0,
                    timestamp=timestamp
                )
            return None
        
        # Find surrounding points for interpolation
        prev_point = None
        next_point = None
        
        for point in self.gps_track:
            if point.timestamp <= timestamp:
                prev_point = point
            else:
                next_point = point
                break
        
        # If timestamp is before all points, return first point
        if prev_point is None:
            return self.gps_track[0]
        
        # If timestamp is after all points, return last point
        if next_point is None:
            return prev_point
        
        # Interpolate between points
        t_range = next_point.timestamp - prev_point.timestamp
        if t_range <= 0:
            return prev_point
        
        t_factor = (timestamp - prev_point.timestamp) / t_range
        
        return GPSPoint(
            latitude=prev_point.latitude + (next_point.latitude - prev_point.latitude) * t_factor,
            longitude=prev_point.longitude + (next_point.longitude - prev_point.longitude) * t_factor,
            altitude=prev_point.altitude + (next_point.altitude - prev_point.altitude) * t_factor,
            speed=prev_point.speed + (next_point.speed - prev_point.speed) * t_factor,
            timestamp=timestamp,
            fix=prev_point.fix
        )
    
    def get_gps_for_frame(self, frame_number: int) -> Optional[GPSPoint]:
        """
        Get GPS position for a specific frame number.
        
        Args:
            frame_number: Frame number (0-indexed)
            
        Returns:
            GPSPoint or None
        """
        if self.fps <= 0:
            return None
        
        timestamp = frame_number / self.fps
        return self.get_gps_at_time(timestamp)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'creation_time': self.creation_time.isoformat() if self.creation_time else None,
            'firmware': self.firmware,
            'camera_model': self.camera_model,
            'duration': self.duration,
            'fps': self.fps,
            'gps_track_points': len(self.gps_track),
            'has_location': self.has_location(),
            'has_gps_track': self.has_gps_track()
        }
    
    def save_gpx(self, output_path: str) -> bool:
        """
        Save GPS track as GPX file.
        
        Args:
            output_path: Path to save GPX file
            
        Returns:
            True if successful
        """
        if not self.gps_track:
            return False
        
        gpx_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        gpx_content.append('<gpx version="1.1" creator="FrameExtractor">')
        gpx_content.append('  <trk>')
        gpx_content.append('    <name>GoPro GPS Track</name>')
        gpx_content.append('    <trkseg>')
        
        for point in self.gps_track:
            time_str = point.datetime.isoformat() if point.datetime else ""
            gpx_content.append(
                f'      <trkpt lat="{point.latitude:.7f}" lon="{point.longitude:.7f}">'
            )
            if point.altitude:
                gpx_content.append(f'        <ele>{point.altitude:.1f}</ele>')
            if time_str:
                gpx_content.append(f'        <time>{time_str}</time>')
            gpx_content.append('      </trkpt>')
        
        gpx_content.append('    </trkseg>')
        gpx_content.append('  </trk>')
        gpx_content.append('</gpx>')
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(gpx_content))
        
        return True


class FrameExtractor:
    """Extracts frames from video files."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def extract_frames_ffmpeg(self, video_path: str, output_dir: str, fps: float = 1.0,
                              jpeg_quality: int = 90) -> str:
        """
        Extract frames using ffmpeg.
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save frames
            fps: Frames per second to extract
            jpeg_quality: JPEG quality (1-100, default 90)
            
        Returns:
            Path to output directory
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert quality to ffmpeg's qscale (2-31, lower is better)
        # 90% quality -> qscale ~2, 50% -> qscale ~15
        qscale = max(2, min(31, int(2 + (100 - jpeg_quality) * 0.29)))
        
        # Build ffmpeg command for JPEG output
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'fps={fps}',
            '-qscale:v', str(qscale),
            '-y',  # Overwrite output files
            os.path.join(output_dir, 'frame_%05d.jpg')
        ]
        
        if self.verbose:
            print(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=not self.verbose,
                text=True,
                check=True
            )
            
            if self.verbose:
                print(f"Frames extracted to {output_dir}")
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg failed: {e}")
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install ffmpeg.")
        
        return output_dir
    
    def extract_frames_opencv(self, video_path: str, output_dir: str, fps: float = 1.0,
                              jpeg_quality: int = 90) -> str:
        """
        Extract frames using OpenCV.
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save frames
            fps: Frames per second to extract
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
        
        # Calculate frame interval
        frame_interval = int(video_fps / fps)
        
        if self.verbose:
            print(f"Video FPS: {video_fps}")
            print(f"Extracting every {frame_interval} frames")
            print(f"Total frames to process: {total_frames}")
        
        frame_count = 0
        saved_count = 0
        
        # JPEG compression params
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
        
        # Progress bar
        pbar = tqdm(total=total_frames, desc="Extracting frames") if self.verbose else None
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Save frame if it matches our interval
                if frame_count % frame_interval == 0:
                    output_path = os.path.join(output_dir, f'frame_{saved_count:05d}.jpg')
                    cv2.imwrite(output_path, frame, encode_params)
                    saved_count += 1
                
                frame_count += 1
                
                if pbar:
                    pbar.update(1)
                    
        finally:
            cap.release()
            if pbar:
                pbar.close()
        
        if self.verbose:
            print(f"Extracted {saved_count} frames to {output_dir}")
        
        return output_dir
    
    def extract_frames(self, video_path: str, fps: float = 1.0, 
                      output_dir: Optional[str] = None, use_ffmpeg: bool = True,
                      jpeg_quality: int = 90) -> str:
        """
        Extract frames from video.
        
        Args:
            video_path: Path to input video
            fps: Frames per second to extract
            output_dir: Directory to save frames (creates temp if None)
            use_ffmpeg: Whether to use ffmpeg (True) or OpenCV (False)
            jpeg_quality: JPEG quality (1-100, default 90)
            
        Returns:
            Path to output directory
        """
        if output_dir is None:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix='frame_quality_')
            output_dir = temp_dir
        
        # Check if video file exists
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Extract frames
        if use_ffmpeg:
            try:
                return self.extract_frames_ffmpeg(video_path, output_dir, fps, jpeg_quality)
            except RuntimeError as e:
                if "FFmpeg not found" in str(e):
                    print("FFmpeg not available, falling back to OpenCV...")
                    return self.extract_frames_opencv(video_path, output_dir, fps, jpeg_quality)
                else:
                    raise
        else:
            return self.extract_frames_opencv(video_path, output_dir, fps, jpeg_quality)
    
    def get_frame_files(self, frames_dir: str) -> List[str]:
        """
        Get list of frame files in directory.
        
        Args:
            frames_dir: Directory containing frames
            
        Returns:
            List of frame file paths
        """
        frame_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        
        frame_files = []
        for file_path in Path(frames_dir).iterdir():
            if file_path.suffix.lower() in frame_extensions:
                frame_files.append(str(file_path))
        
        # Sort files naturally
        frame_files.sort()
        
        return frame_files
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get video information.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video: {video_path}")
        
        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return info
    
    def extract_geolocation(self, video_path: str) -> VideoGeoInfo:
        """
        Extract geolocation/GPS data from a GoPro video.
        
        GoPro cameras store GPS data in two ways:
        1. Basic location in the file metadata (format tags)
        2. Detailed GPS track in the GPMF (GoPro Metadata Format) stream
        
        Args:
            video_path: Path to video file
            
        Returns:
            VideoGeoInfo object with GPS data
        """
        geo_info = VideoGeoInfo()
        
        # Get video info
        try:
            video_info = self.get_video_info(video_path)
            geo_info.fps = video_info['fps']
            geo_info.duration = video_info['duration']
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not get video info: {e}")
        
        # Extract metadata using ffprobe
        try:
            self._extract_metadata_ffprobe(video_path, geo_info)
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not extract metadata: {e}")
        
        # Try to extract GPMF GPS track
        try:
            self._extract_gpmf_gps(video_path, geo_info)
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not extract GPMF GPS data: {e}")
        
        return geo_info
    
    def _extract_metadata_ffprobe(self, video_path: str, geo_info: VideoGeoInfo) -> None:
        """
        Extract basic metadata using ffprobe.
        
        Args:
            video_path: Path to video
            geo_info: VideoGeoInfo to populate
        """
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {result.stderr}")
        
        data = json.loads(result.stdout)
        
        # Get format tags
        tags = data.get('format', {}).get('tags', {})
        
        # Parse location (format: +50.0849+018.9894/)
        location = tags.get('location', '') or tags.get('location-eng', '')
        if location:
            match = re.match(r'([+-][\d.]+)([+-][\d.]+)/?', location)
            if match:
                geo_info.latitude = float(match.group(1))
                geo_info.longitude = float(match.group(2))
        
        # Parse creation time
        creation_time = tags.get('creation_time', '')
        if creation_time:
            try:
                # Remove timezone info for parsing
                creation_time = creation_time.replace('Z', '+00:00')
                geo_info.creation_time = datetime.fromisoformat(creation_time.replace('.000000', ''))
            except:
                pass
        
        # Get firmware
        geo_info.firmware = tags.get('firmware', '')
        
        # Try to get camera model from stream handler
        for stream in data.get('streams', []):
            handler = stream.get('tags', {}).get('handler_name', '')
            if 'GoPro' in handler:
                geo_info.camera_model = 'GoPro'
                break
    
    def _extract_gpmf_gps(self, video_path: str, geo_info: VideoGeoInfo) -> None:
        """
        Extract GPS track from GPMF (GoPro Metadata Format) stream.
        
        This provides frame-by-frame GPS data at ~18Hz.
        
        Args:
            video_path: Path to video
            geo_info: VideoGeoInfo to populate with GPS track
        """
        # First, find the GPMF stream
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return
        
        data = json.loads(result.stdout)
        
        # Find GPMF stream (codec_tag_string = 'gpmd')
        gpmf_stream_index = None
        for stream in data.get('streams', []):
            if stream.get('codec_tag_string') == 'gpmd':
                gpmf_stream_index = stream.get('index')
                break
        
        if gpmf_stream_index is None:
            if self.verbose:
                print("No GPMF stream found in video")
            return
        
        # Extract GPMF data to temporary file
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            cmd = [
                'ffmpeg',
                '-y',
                '-i', video_path,
                '-codec', 'copy',
                '-map', f'0:{gpmf_stream_index}',
                '-f', 'rawvideo',
                tmp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                if self.verbose:
                    print(f"Failed to extract GPMF stream")
                return
            
            # Parse GPMF data
            with open(tmp_path, 'rb') as f:
                gpmf_data = f.read()
            
            # Parse GPS from GPMF
            gps_points = self._parse_gpmf_gps(gpmf_data, geo_info.duration)
            geo_info.gps_track = gps_points
            
            if self.verbose and gps_points:
                print(f"Extracted {len(gps_points)} GPS points from GPMF stream")
                
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _parse_gpmf_gps(self, data: bytes, video_duration: float) -> List[GPSPoint]:
        """
        Parse GPS data from raw GPMF binary data.
        
        GPMF uses a nested KLV (Key-Length-Value) format with FourCC keys.
        GPS data is stored under the GPS5 key with scale factors from SCAL.
        
        The structure is: DEVC -> STRM -> [SCAL, GPS5, ...]
        
        Args:
            data: Raw GPMF binary data
            video_duration: Video duration in seconds
            
        Returns:
            List of GPSPoint objects
        """
        gps_samples = []
        
        # Default GPS scales
        gps_scale = [10000000, 10000000, 1000, 1000, 100]
        
        # Find all GPS5 entries by searching for the key
        # This is simpler than trying to parse the full nested structure
        search_offset = 0
        
        while True:
            # Find next GPS5 key
            gps5_pos = data.find(b'GPS5', search_offset)
            if gps5_pos < 0:
                break
            
            # Look for SCAL before this GPS5 (within same stream)
            # Search backwards up to 200 bytes
            scal_search_start = max(0, gps5_pos - 200)
            scal_pos = data.rfind(b'SCAL', scal_search_start, gps5_pos)
            
            if scal_pos >= 0 and scal_pos + 8 < gps5_pos:
                # Parse SCAL
                try:
                    scal_type = chr(data[scal_pos + 4])
                    scal_struct_size = data[scal_pos + 5]
                    scal_repeat = struct.unpack('>H', data[scal_pos + 6:scal_pos + 8])[0]
                    
                    if scal_type == 'l':  # signed 32-bit
                        num_vals = (scal_struct_size * scal_repeat) // 4
                        if num_vals == 5:
                            scales = []
                            for i in range(5):
                                val = struct.unpack('>i', data[scal_pos + 8 + i*4:scal_pos + 12 + i*4])[0]
                                scales.append(val if val != 0 else 1)
                            gps_scale = scales
                except:
                    pass
            
            # Parse GPS5 header
            try:
                type_char = chr(data[gps5_pos + 4])
                struct_size = data[gps5_pos + 5]
                repeat_count = struct.unpack('>H', data[gps5_pos + 6:gps5_pos + 8])[0]
                
                if type_char == 'l' and struct_size == 20:
                    # Parse GPS samples
                    data_start = gps5_pos + 8
                    
                    for i in range(repeat_count):
                        sample_offset = data_start + i * 20
                        if sample_offset + 20 <= len(data):
                            try:
                                lat_raw = struct.unpack('>i', data[sample_offset:sample_offset+4])[0]
                                lon_raw = struct.unpack('>i', data[sample_offset+4:sample_offset+8])[0]
                                alt_raw = struct.unpack('>i', data[sample_offset+8:sample_offset+12])[0]
                                speed_2d_raw = struct.unpack('>i', data[sample_offset+12:sample_offset+16])[0]
                                speed_3d_raw = struct.unpack('>i', data[sample_offset+16:sample_offset+20])[0]
                                
                                # Apply scales
                                lat = lat_raw / gps_scale[0]
                                lon = lon_raw / gps_scale[1]
                                alt = alt_raw / gps_scale[2]
                                speed = speed_2d_raw / gps_scale[3]
                                
                                # Validate GPS coordinates
                                if -90 <= lat <= 90 and -180 <= lon <= 180:
                                    gps_samples.append({
                                        'latitude': lat,
                                        'longitude': lon,
                                        'altitude': alt,
                                        'speed': speed
                                    })
                            except struct.error:
                                pass
            except:
                pass
            
            # Move search position past this GPS5
            search_offset = gps5_pos + 8
        
        # Convert samples to GPSPoints with timestamps
        gps_points = []
        if gps_samples:
            # Distribute timestamps evenly across video duration
            time_step = video_duration / len(gps_samples) if len(gps_samples) > 1 else 0
            
            for i, sample in enumerate(gps_samples):
                gps_points.append(GPSPoint(
                    latitude=sample['latitude'],
                    longitude=sample['longitude'],
                    altitude=sample['altitude'],
                    speed=sample['speed'],
                    timestamp=i * time_step,
                    fix=3  # Assume 3D fix if we have data
                ))
        
        return gps_points
    
    def get_gps_for_frames(self, video_path: str, frame_numbers: List[int]) -> Dict[int, Optional[GPSPoint]]:
        """
        Get GPS coordinates for specific frame numbers.
        
        Args:
            video_path: Path to video file
            frame_numbers: List of frame numbers to get GPS for
            
        Returns:
            Dictionary mapping frame number to GPSPoint (or None)
        """
        geo_info = self.extract_geolocation(video_path)
        
        result = {}
        for frame_num in frame_numbers:
            result[frame_num] = geo_info.get_gps_for_frame(frame_num)
        
        return result
    
    def _decimal_to_dms(self, decimal_degrees: float) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        """
        Convert decimal degrees to degrees, minutes, seconds for EXIF.
        
        Args:
            decimal_degrees: Decimal degrees value
            
        Returns:
            Tuple of ((degrees, 1), (minutes, 1), (seconds * 100, 100))
        """
        is_negative = decimal_degrees < 0
        decimal_degrees = abs(decimal_degrees)
        
        degrees = int(decimal_degrees)
        minutes_float = (decimal_degrees - degrees) * 60
        minutes = int(minutes_float)
        seconds = (minutes_float - minutes) * 60
        
        # Use high precision for seconds (multiply by 10000)
        seconds_num = int(seconds * 10000)
        
        return ((degrees, 1), (minutes, 1), (seconds_num, 10000))
    
    def write_gps_exif(self, image_path: str, gps_point: GPSPoint, 
                       creation_time: Optional[datetime] = None) -> bool:
        """
        Write GPS coordinates to JPEG EXIF data.
        
        Args:
            image_path: Path to JPEG image
            gps_point: GPS point to write
            creation_time: Optional creation time to write
            
        Returns:
            True if successful, False otherwise
        """
        if not PIEXIF_AVAILABLE:
            if self.verbose:
                print("Warning: piexif not installed. Install with: pip install piexif")
            return False
        
        if not image_path.lower().endswith(('.jpg', '.jpeg')):
            if self.verbose:
                print(f"Warning: EXIF only supported for JPEG files: {image_path}")
            return False
        
        try:
            # Load existing EXIF or create new
            try:
                exif_dict = piexif.load(image_path)
            except:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            
            # GPS IFD
            gps_ifd = {}
            
            # Latitude
            lat_dms = self._decimal_to_dms(gps_point.latitude)
            gps_ifd[piexif.GPSIFD.GPSLatitude] = lat_dms
            gps_ifd[piexif.GPSIFD.GPSLatitudeRef] = 'N' if gps_point.latitude >= 0 else 'S'
            
            # Longitude
            lon_dms = self._decimal_to_dms(gps_point.longitude)
            gps_ifd[piexif.GPSIFD.GPSLongitude] = lon_dms
            gps_ifd[piexif.GPSIFD.GPSLongitudeRef] = 'E' if gps_point.longitude >= 0 else 'W'
            
            # Altitude
            if gps_point.altitude:
                alt_int = int(abs(gps_point.altitude) * 100)
                gps_ifd[piexif.GPSIFD.GPSAltitude] = (alt_int, 100)
                gps_ifd[piexif.GPSIFD.GPSAltitudeRef] = 0 if gps_point.altitude >= 0 else 1
            
            # Speed (convert m/s to km/h)
            if gps_point.speed:
                speed_kmh = gps_point.speed * 3.6
                speed_int = int(speed_kmh * 100)
                gps_ifd[piexif.GPSIFD.GPSSpeed] = (speed_int, 100)
                gps_ifd[piexif.GPSIFD.GPSSpeedRef] = 'K'  # km/h
            
            exif_dict['GPS'] = gps_ifd
            
            # Add creation time to EXIF if provided
            if creation_time:
                date_str = creation_time.strftime("%Y:%m:%d %H:%M:%S")
                exif_dict['0th'][piexif.ImageIFD.DateTime] = date_str
                exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_str
                exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = date_str
            
            # Write EXIF
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_path)
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Warning: Failed to write EXIF to {image_path}: {e}")
            return False
    
    def extract_frames_with_gps(
        self, 
        video_path: str, 
        fps: float = 1.0,
        output_dir: Optional[str] = None,
        use_ffmpeg: bool = True,
        jpeg_quality: int = 90,
        embed_gps: bool = True
    ) -> Tuple[str, Dict[str, Optional[GPSPoint]]]:
        """
        Extract frames from video and get GPS for each frame.
        Optionally embeds GPS coordinates in JPEG EXIF data.
        
        Args:
            video_path: Path to input video
            fps: Frames per second to extract
            output_dir: Directory to save frames
            use_ffmpeg: Whether to use ffmpeg
            jpeg_quality: JPEG quality (1-100, default 90)
            embed_gps: Whether to embed GPS in EXIF (default True)
            
        Returns:
            Tuple of (output_directory, dict mapping frame filename to GPSPoint)
        """
        # Extract frames
        output_dir = self.extract_frames(video_path, fps, output_dir, use_ffmpeg, jpeg_quality)
        
        # Get geolocation info
        geo_info = self.extract_geolocation(video_path)
        
        # Get frame files
        frame_files = self.get_frame_files(output_dir)
        
        # Calculate GPS for each frame
        video_info = self.get_video_info(video_path)
        video_fps = video_info['fps']
        frame_interval = int(video_fps / fps) if fps > 0 else 1
        
        frame_gps = {}
        gps_written = 0
        
        for i, frame_path in enumerate(frame_files):
            # Calculate original frame number
            original_frame_num = i * frame_interval
            gps = geo_info.get_gps_for_frame(original_frame_num)
            frame_gps[Path(frame_path).name] = gps
            
            # Embed GPS in EXIF if requested
            if embed_gps and gps:
                # Calculate frame timestamp for datetime
                frame_time = None
                if geo_info.creation_time:
                    from datetime import timedelta
                    frame_time = geo_info.creation_time + timedelta(seconds=gps.timestamp)
                
                if self.write_gps_exif(frame_path, gps, frame_time):
                    gps_written += 1
        
        if self.verbose and embed_gps:
            print(f"Embedded GPS EXIF in {gps_written}/{len(frame_files)} frames")
        
        return output_dir, frame_gps
#!/usr/bin/env python3
"""
Extract motion vectors (gyro/accelerometer) from GoPro .360 file and visualize on MP4 frame.

This script extracts GPMF metadata from a GoPro .360 file, parses gyroscope and 
accelerometer data, and draws motion vectors as arrows on a frame extracted from 
the corresponding stitched MP4 video.

NOTE: For interactive 3D visualization with camera path, use visualize_motion_stream.py instead.
"""

import argparse
import subprocess
import struct
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import cv2
import numpy as np


class GPMFParser:
    """Parser for GoPro Metadata Format (GPMF) data."""
    
    def __init__(self, data: bytes):
        self.data = data
        self.gyro_samples = []
        self.accel_samples = []
        
    def parse(self):
        """Parse GPMF data to extract gyro and accelerometer samples."""
        self._parse_gyro()
        self._parse_accel()
        
    def _find_scale_factor(self, search_end: int, fourcc: str = 'SCAL') -> List[float]:
        """Find scale factor before a sensor data block."""
        scale = [1.0, 1.0, 1.0]
        scal_pos = self.data.rfind(fourcc.encode(), max(0, search_end - 300), search_end)
        
        if scal_pos >= 0:
            try:
                # SCAL structure: 4-byte fourcc, 1-byte type, 1-byte size, 2-byte repeat, data
                type_char = chr(self.data[scal_pos + 4]) if scal_pos + 4 < len(self.data) else ''
                struct_size = self.data[scal_pos + 5] if scal_pos + 5 < len(self.data) else 0
                repeat_count = struct.unpack('>H', self.data[scal_pos + 6:scal_pos + 8])[0]
                
                if repeat_count >= 3:
                    # Type 'l' = signed long (4 bytes), 's' = signed short (2 bytes)
                    if type_char == 'l':
                        for i in range(min(3, repeat_count)):
                            offset = scal_pos + 8 + i * 4
                            if offset + 4 <= len(self.data):
                                val = struct.unpack('>i', self.data[offset:offset + 4])[0]
                                if val != 0:
                                    scale[i] = float(val)
                    elif type_char == 's':
                        for i in range(min(3, repeat_count)):
                            offset = scal_pos + 8 + i * 2
                            if offset + 2 <= len(self.data):
                                val = struct.unpack('>h', self.data[offset:offset + 2])[0]
                                if val != 0:
                                    scale[i] = float(val)
            except Exception as e:
                print(f"Warning: Could not parse scale factor: {e}")
                
        return scale
    
    def _parse_gyro(self):
        """Parse gyroscope data (GYRO fourcc)."""
        search_offset = 0
        
        while True:
            gyro_pos = self.data.find(b'GYRO', search_offset)
            if gyro_pos < 0:
                break
                
            try:
                # Find scale factor
                gyro_scale = self._find_scale_factor(gyro_pos)
                
                # Parse GYRO header
                type_char = chr(self.data[gyro_pos + 4]) if gyro_pos + 4 < len(self.data) else ''
                struct_size = self.data[gyro_pos + 5] if gyro_pos + 5 < len(self.data) else 0
                repeat_count = struct.unpack('>H', self.data[gyro_pos + 6:gyro_pos + 8])[0]
                
                if type_char == 's' and struct_size == 6:  # 3 * 2-byte signed shorts
                    data_start = gyro_pos + 8
                    
                    for i in range(repeat_count):
                        offset = data_start + i * 6
                        if offset + 6 <= len(self.data):
                            # Read 3 signed 16-bit integers (big-endian)
                            # GoPro HERO6+/MAX order: Y, -X, Z
                            raw_y = struct.unpack('>h', self.data[offset:offset + 2])[0]
                            raw_x = struct.unpack('>h', self.data[offset + 2:offset + 4])[0]
                            raw_z = struct.unpack('>h', self.data[offset + 4:offset + 6])[0]
                            
                            # Apply scale factors (convert to rad/s)
                            self.gyro_samples.append({
                                'x': raw_x / gyro_scale[1],  # Note: -X in data
                                'y': raw_y / gyro_scale[0],
                                'z': raw_z / gyro_scale[2]
                            })
            except Exception as e:
                print(f"Warning: Error parsing GYRO at position {gyro_pos}: {e}")
                
            search_offset = gyro_pos + 8
            
    def _parse_accel(self):
        """Parse accelerometer data (ACCL fourcc)."""
        search_offset = 0
        
        while True:
            accl_pos = self.data.find(b'ACCL', search_offset)
            if accl_pos < 0:
                break
                
            try:
                # Find scale factor
                accel_scale = self._find_scale_factor(accl_pos)
                
                # Parse ACCL header
                type_char = chr(self.data[accl_pos + 4]) if accl_pos + 4 < len(self.data) else ''
                struct_size = self.data[accl_pos + 5] if accl_pos + 5 < len(self.data) else 0
                repeat_count = struct.unpack('>H', self.data[accl_pos + 6:accl_pos + 8])[0]
                
                if type_char == 's' and struct_size == 6:  # 3 * 2-byte signed shorts
                    data_start = accl_pos + 8
                    
                    for i in range(repeat_count):
                        offset = data_start + i * 6
                        if offset + 6 <= len(self.data):
                            # Read 3 signed 16-bit integers (big-endian)
                            raw_y = struct.unpack('>h', self.data[offset:offset + 2])[0]
                            raw_x = struct.unpack('>h', self.data[offset + 2:offset + 4])[0]
                            raw_z = struct.unpack('>h', self.data[offset + 4:offset + 6])[0]
                            
                            # Apply scale factors (convert to m/s²)
                            self.accel_samples.append({
                                'x': raw_x / accel_scale[1],
                                'y': raw_y / accel_scale[0],
                                'z': raw_z / accel_scale[2]
                            })
            except Exception as e:
                print(f"Warning: Error parsing ACCL at position {accl_pos}: {e}")
                
            search_offset = accl_pos + 8


def find_gpmf_stream(video_path: str) -> Optional[int]:
    """Find the GPMF metadata stream index in the video."""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
               '-show_streams', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        for stream in data.get('streams', []):
            codec_tag = stream.get('codec_tag_string', '')
            handler_name = stream.get('tags', {}).get('handler_name', '')
            
            if codec_tag == 'gpmd' or 'GoPro MET' in handler_name:
                return stream['index']
                
        return None
    except Exception as e:
        print(f"Error finding GPMF stream: {e}")
        return None


def extract_gpmf_data(video_path: str, output_path: str) -> bool:
    """Extract GPMF metadata binary data from video."""
    stream_index = find_gpmf_stream(video_path)
    
    if stream_index is None:
        print(f"Error: No GPMF metadata stream found in {video_path}")
        print("Make sure you're using the original .360 file, not a processed video.")
        return False
    
    print(f"Found GPMF stream at index {stream_index}")
    
    try:
        cmd = [
            'ffmpeg', '-y', '-v', 'quiet',
            '-i', video_path,
            '-codec', 'copy',
            '-map', f'0:{stream_index}',
            '-f', 'rawvideo',
            output_path
        ]
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting GPMF data: {e}")
        return False


def extract_frame(video_path: str, time_seconds: float, output_path: str) -> bool:
    """Extract a single frame from video at specified time."""
    try:
        cmd = [
            'ffmpeg', '-y', '-v', 'quiet',
            '-ss', str(time_seconds),
            '-i', video_path,
            '-frames:v', '1',
            '-q:v', '2',
            output_path
        ]
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting frame: {e}")
        return False


def get_video_duration(video_path: str) -> Optional[float]:
    """Get video duration in seconds."""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
               '-show_format', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None


def interpolate_motion_at_time(gyro_samples: List[Dict], accel_samples: List[Dict], 
                                time_seconds: float, duration: float) -> Tuple[Dict, Dict]:
    """Get motion data at specific time by averaging nearby samples."""
    if not gyro_samples or not accel_samples:
        return {'x': 0, 'y': 0, 'z': 0}, {'x': 0, 'y': 0, 'z': 0}
    
    # Calculate sample indices based on time
    # Assume even distribution of samples across video duration
    gyro_idx = int((time_seconds / duration) * len(gyro_samples))
    accel_idx = int((time_seconds / duration) * len(accel_samples))
    
    # Clamp to valid range
    gyro_idx = max(0, min(gyro_idx, len(gyro_samples) - 1))
    accel_idx = max(0, min(accel_idx, len(accel_samples) - 1))
    
    # Average over a small window (±0.1 seconds)
    window_size = max(1, int(0.1 * len(gyro_samples) / duration))
    
    gyro_start = max(0, gyro_idx - window_size)
    gyro_end = min(len(gyro_samples), gyro_idx + window_size)
    
    accel_start = max(0, accel_idx - window_size)
    accel_end = min(len(accel_samples), accel_idx + window_size)
    
    # Average gyro
    gyro_avg = {'x': 0, 'y': 0, 'z': 0}
    for sample in gyro_samples[gyro_start:gyro_end]:
        gyro_avg['x'] += sample['x']
        gyro_avg['y'] += sample['y']
        gyro_avg['z'] += sample['z']
    
    count = gyro_end - gyro_start
    if count > 0:
        gyro_avg['x'] /= count
        gyro_avg['y'] /= count
        gyro_avg['z'] /= count
    
    # Average accel
    accel_avg = {'x': 0, 'y': 0, 'z': 0}
    for sample in accel_samples[accel_start:accel_end]:
        accel_avg['x'] += sample['x']
        accel_avg['y'] += sample['y']
        accel_avg['z'] += sample['z']
    
    count = accel_end - accel_start
    if count > 0:
        accel_avg['x'] /= count
        accel_avg['y'] /= count
        accel_avg['z'] /= count
    
    return gyro_avg, accel_avg


def draw_motion_arrows(image_path: str, gyro: Dict, accel: Dict, output_path: str):
    """Draw motion vectors as arrows on the image grid for equirectangular 360° image."""
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return
    
    h, w = img.shape[:2]
    
    # Gyroscope data: rotation rates in rad/s
    # X = pitch (rotation around X axis)
    # Y = yaw (rotation around Y axis) 
    # Z = roll (rotation around Z axis)
    gyro_pitch = gyro['x']
    gyro_yaw = gyro['y']
    gyro_roll = gyro['z']
    
    print(f"Debug - Gyro: pitch={gyro_pitch:.3f}, yaw={gyro_yaw:.3f}, roll={gyro_roll:.3f}")
    
    # Draw arrows every 100 pixels in a grid
    grid_spacing = 100
    arrow_color = (0, 255, 255)  # Yellow arrows
    arrow_thickness = 2
    arrow_scale = 5.0  # Scale factor for arrow length
    
    for img_y in range(grid_spacing // 2, h, grid_spacing):
        for img_x in range(grid_spacing // 2, w, grid_spacing):
            # Convert equirectangular pixel coordinates to spherical coordinates
            # X maps to longitude (0 to 2π), Y maps to latitude (-π/2 to π/2)
            lon = (img_x / w) * 2 * np.pi  # 0 to 2π
            lat = (img_y / h) * np.pi - np.pi / 2  # -π/2 to π/2
            
            # Convert spherical to 3D unit vector (direction we're looking at)
            # Standard spherical coordinates: 
            # x = cos(lat) * sin(lon)
            # y = sin(lat)
            # z = cos(lat) * cos(lon)
            cos_lat = np.cos(lat)
            sin_lat = np.sin(lat)
            cos_lon = np.cos(lon)
            sin_lon = np.sin(lon)
            
            # Calculate motion vector in 3D space due to camera rotation
            # Angular velocity ω cross product with position r gives linear velocity v = ω × r
            # For a point on unit sphere, the tangent velocity is:
            # v = [gyro_yaw, gyro_pitch, gyro_roll] × [x, y, z]
            
            dir_x = cos_lat * sin_lon
            dir_y = sin_lat
            dir_z = cos_lat * cos_lon
            
            # Cross product: ω × r
            # ω = [gyro_pitch, gyro_yaw, gyro_roll] (but in camera coordinate system)
            # Camera coords: Y-up, X-right, Z-forward
            # Standard coords: Y-up, X-right, Z-back
            
            # Velocity in 3D from rotation
            vel_x = gyro_yaw * dir_z - gyro_roll * dir_y
            vel_y = gyro_roll * dir_x - gyro_pitch * dir_z
            vel_z = gyro_pitch * dir_y - gyro_yaw * dir_x
            
            # Project 3D velocity back to 2D tangent plane (equirectangular derivative)
            # In equirectangular: 
            # d(lon)/dt affects horizontal image motion
            # d(lat)/dt affects vertical image motion
            
            # Tangent basis vectors in spherical coords
            # ∂r/∂lon = [-cos(lat)*cos(lon), 0, cos(lat)*sin(lon)]
            # ∂r/∂lat = [-sin(lat)*sin(lon), cos(lat), -sin(lat)*cos(lon)]
            
            # Project velocity onto tangent vectors
            d_lon_dt = vel_x * (-cos_lon) + vel_z * sin_lon
            d_lat_dt = vel_x * (-sin_lat * sin_lon) + vel_y * cos_lat + vel_z * (-sin_lat * cos_lon)
            
            # Convert to pixel velocities
            # Longitude change → horizontal pixels
            # Latitude change → vertical pixels
            motion_x = (d_lon_dt / (2 * np.pi)) * w * arrow_scale
            motion_y = (d_lat_dt / np.pi) * h * arrow_scale
            
            # Calculate arrow length
            arrow_length = np.sqrt(motion_x**2 + motion_y**2)
            
            if arrow_length > 2:  # Only draw if motion is significant
                # Clamp arrow length
                max_length = 60
                if arrow_length > max_length:
                    scale = max_length / arrow_length
                    motion_x *= scale
                    motion_y *= scale
                
                # Calculate arrow end point
                end_x = int(img_x + motion_x)
                end_y = int(img_y + motion_y)
                
                # Draw arrow
                cv2.arrowedLine(img, (img_x, img_y), (end_x, end_y), 
                               arrow_color, arrow_thickness, tipLength=0.3)
    
    # Draw legend
    legend_x, legend_y = 20, 30
    cv2.putText(img, "Motion Direction (360 Equirectangular)", (legend_x, legend_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Draw a reference arrow in the legend
    ref_start = (legend_x, legend_y + 20)
    ref_end = (legend_x + 40, legend_y + 20)
    cv2.arrowedLine(img, ref_start, ref_end, arrow_color, 2, tipLength=0.3)
    cv2.putText(img, "Direction from camera rotation", (legend_x + 50, legend_y + 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Save result
    cv2.imwrite(output_path, img)
    print(f"Motion visualization saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract motion vectors from GoPro .360 file and visualize on MP4 frame",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  %(prog)s \\
    --video360 /path/to/GS011388.360 \\
    --video-mp4 /path/to/GS011388.mp4 \\
    --time 5.0 \\
    --output motion_vectors_5s.png
        """
    )
    
    parser.add_argument('--video360', required=True, 
                        help='Path to GoPro .360 file (contains GPMF metadata)')
    parser.add_argument('--video-mp4', required=True,
                        help='Path to stitched MP4 file (to extract frame from)')
    parser.add_argument('--time', type=float, required=True,
                        help='Time in seconds to extract frame and motion data')
    parser.add_argument('--output', default='motion_vectors.png',
                        help='Output image path (default: motion_vectors.png)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.video360):
        print(f"Error: .360 file not found: {args.video360}")
        sys.exit(1)
    
    if not os.path.exists(args.video_mp4):
        print(f"Error: MP4 file not found: {args.video_mp4}")
        sys.exit(1)
    
    # Get video duration
    print("Getting video duration...")
    duration = get_video_duration(args.video_mp4)
    if duration is None:
        print("Error: Could not determine video duration")
        sys.exit(1)
    
    print(f"Video duration: {duration:.2f} seconds")
    
    if args.time < 0 or args.time > duration:
        print(f"Error: Time {args.time}s is out of range [0, {duration:.2f}]")
        sys.exit(1)
    
    # Extract GPMF data
    print(f"Extracting GPMF metadata from {args.video360}...")
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp_gpmf:
        gpmf_path = tmp_gpmf.name
    
    try:
        if not extract_gpmf_data(args.video360, gpmf_path):
            sys.exit(1)
        
        # Parse GPMF data
        print("Parsing gyroscope and accelerometer data...")
        with open(gpmf_path, 'rb') as f:
            gpmf_data = f.read()
        
        parser = GPMFParser(gpmf_data)
        parser.parse()
        
        print(f"Found {len(parser.gyro_samples)} gyroscope samples")
        print(f"Found {len(parser.accel_samples)} accelerometer samples")
        
        if not parser.gyro_samples and not parser.accel_samples:
            print("Warning: No motion data found in GPMF stream")
            print("The video may not contain IMU data, or the parser may need adjustment")
        
        # Show first few samples for debugging
        if parser.gyro_samples:
            print(f"\nFirst gyro sample: X={parser.gyro_samples[0]['x']:.3f}, "
                  f"Y={parser.gyro_samples[0]['y']:.3f}, Z={parser.gyro_samples[0]['z']:.3f}")
        if parser.accel_samples:
            print(f"First accel sample: X={parser.accel_samples[0]['x']:.3f}, "
                  f"Y={parser.accel_samples[0]['y']:.3f}, Z={parser.accel_samples[0]['z']:.3f}")
        
        # Get motion data at specified time
        gyro, accel = interpolate_motion_at_time(
            parser.gyro_samples, parser.accel_samples, args.time, duration
        )
        
        print(f"\nMotion data at {args.time}s:")
        print(f"  Gyroscope: X={gyro['x']:.3f}, Y={gyro['y']:.3f}, Z={gyro['z']:.3f} rad/s")
        print(f"  Accelerometer: X={accel['x']:.3f}, Y={accel['y']:.3f}, Z={accel['z']:.3f} m/s²")
        print(f"\nNote: Values seem very high - scale factors may not be correctly parsed")
        print(f"      Using gyroscope data for motion direction visualization")
        
        # Extract frame
        print(f"\nExtracting frame at {args.time}s from {args.video_mp4}...")
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_frame:
            frame_path = tmp_frame.name
        
        if not extract_frame(args.video_mp4, args.time, frame_path):
            sys.exit(1)
        
        # Draw motion arrows
        print("Drawing motion vectors on frame...")
        draw_motion_arrows(frame_path, gyro, accel, args.output)
        
        print(f"\n✓ Success! Check {args.output}")
        
    finally:
        # Cleanup
        if os.path.exists(gpmf_path):
            os.unlink(gpmf_path)
        if 'frame_path' in locals() and os.path.exists(frame_path):
            os.unlink(frame_path)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Extract and visualize gyro/accelerometer stream from GoPro .360 file.
Creates both CSV output and interactive 3D visualization with camera path.

The gyroscope data is integrated into absolute orientations, and accelerometer
data (with gravity subtracted using the orientation) is double-integrated to
estimate the camera's travel path.
"""

import argparse
import subprocess
import struct
import json
import os
import sys
import tempfile
import math
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import csv


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
                type_char = chr(self.data[scal_pos + 4]) if scal_pos + 4 < len(self.data) else ''
                struct_size = self.data[scal_pos + 5] if scal_pos + 5 < len(self.data) else 0
                repeat_count = struct.unpack('>H', self.data[scal_pos + 6:scal_pos + 8])[0]
                
                if repeat_count >= 1:
                    if type_char == 'l':
                        for i in range(min(3, repeat_count)):
                            offset = scal_pos + 8 + i * 4
                            if offset + 4 <= len(self.data):
                                val = struct.unpack('>i', self.data[offset:offset + 4])[0]
                                if val != 0:
                                    scale[i] = float(val)
                        if repeat_count == 1 and scale[0] != 1.0:
                            scale[1] = scale[2] = scale[0]
                    elif type_char == 's':
                        for i in range(min(3, repeat_count)):
                            offset = scal_pos + 8 + i * 2
                            if offset + 2 <= len(self.data):
                                val = struct.unpack('>h', self.data[offset:offset + 2])[0]
                                if val != 0:
                                    scale[i] = float(val)
                        if repeat_count == 1 and scale[0] != 1.0:
                            scale[1] = scale[2] = scale[0]
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
                gyro_scale = self._find_scale_factor(gyro_pos)
                
                type_char = chr(self.data[gyro_pos + 4]) if gyro_pos + 4 < len(self.data) else ''
                struct_size = self.data[gyro_pos + 5] if gyro_pos + 5 < len(self.data) else 0
                repeat_count = struct.unpack('>H', self.data[gyro_pos + 6:gyro_pos + 8])[0]
                
                if type_char == 's' and struct_size == 6:
                    data_start = gyro_pos + 8
                    
                    for i in range(repeat_count):
                        offset = data_start + i * 6
                        if offset + 6 <= len(self.data):
                            raw_y = struct.unpack('>h', self.data[offset:offset + 2])[0]
                            raw_neg_x = struct.unpack('>h', self.data[offset + 2:offset + 4])[0]
                            raw_z = struct.unpack('>h', self.data[offset + 4:offset + 6])[0]
                            
                            # GoPro Max data order: Y, -X, Z (convert to X, Y, Z)
                            self.gyro_samples.append({
                                'x': -raw_neg_x / gyro_scale[1],
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
                accel_scale = self._find_scale_factor(accl_pos)
                
                type_char = chr(self.data[accl_pos + 4]) if accl_pos + 4 < len(self.data) else ''
                struct_size = self.data[accl_pos + 5] if accl_pos + 5 < len(self.data) else 0
                repeat_count = struct.unpack('>H', self.data[accl_pos + 6:accl_pos + 8])[0]
                
                if type_char == 's' and struct_size == 6:
                    data_start = accl_pos + 8
                    
                    for i in range(repeat_count):
                        offset = data_start + i * 6
                        if offset + 6 <= len(self.data):
                            raw_y = struct.unpack('>h', self.data[offset:offset + 2])[0]
                            raw_x = struct.unpack('>h', self.data[offset + 2:offset + 4])[0]
                            raw_z = struct.unpack('>h', self.data[offset + 4:offset + 6])[0]
                            
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


def save_to_csv(gyro_samples: List[Dict], accel_samples: List[Dict], 
                duration: float, output_path: str):
    """Save motion data to CSV file."""
    print(f"Saving data to CSV: {output_path}")
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time(s)', 'Type', 'X', 'Y', 'Z', 'Magnitude'])
        
        for i, sample in enumerate(gyro_samples):
            time_s = (i / len(gyro_samples)) * duration
            mag = (sample['x']**2 + sample['y']**2 + sample['z']**2)**0.5
            writer.writerow([f"{time_s:.3f}", 'GYRO', 
                           f"{sample['x']:.3f}", f"{sample['y']:.3f}", 
                           f"{sample['z']:.3f}", f"{mag:.3f}"])
        
        for i, sample in enumerate(accel_samples):
            time_s = (i / len(accel_samples)) * duration
            mag = (sample['x']**2 + sample['y']**2 + sample['z']**2)**0.5
            writer.writerow([f"{time_s:.3f}", 'ACCL', 
                           f"{sample['x']:.3f}", f"{sample['y']:.3f}", 
                           f"{sample['z']:.3f}", f"{mag:.3f}"])


def quat_multiply(q1, q2):
    """Multiply two quaternions [w, x, y, z]."""
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return [
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ]


def quat_normalize(q):
    """Normalize a quaternion."""
    n = math.sqrt(q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2)
    if n < 1e-10:
        return [1, 0, 0, 0]
    return [q[0]/n, q[1]/n, q[2]/n, q[3]/n]


def quat_rotate_vec(q, v):
    """Rotate vector v by quaternion q. q=[w,x,y,z], v=[x,y,z]."""
    w, qx, qy, qz = q
    vx, vy, vz = v
    qv = quat_multiply(q, [0, vx, vy, vz])
    q_conj = [w, -qx, -qy, -qz]
    result = quat_multiply(qv, q_conj)
    return [result[1], result[2], result[3]]


def compute_absolute_orientations_and_path(gyro_samples, accel_samples, duration, force_gravity: float = None):
    """
    Integrate gyro to get absolute orientations, then use orientation to 
    rotate accelerometer into world frame, subtract gravity, and double-integrate
    to get position (camera path).
    
    Initial orientation is computed from the first accelerometer samples so that
    gravity aligns with world Y-down. A simple high-pass filter on the linear
    acceleration helps reduce drift from double integration.
    
    Returns downsampled lists of:
      - orientations: [{time, qw, qx, qy, qz}, ...]
      - path_points:  [{time, x, y, z}, ...]
      - raw_gyro:     [{time, x, y, z}, ...]
      - raw_accel:    [{time, x, y, z}, ...]
    """
    n_gyro = len(gyro_samples)
    n_accel = len(accel_samples)
    
    if n_gyro == 0:
        return [], [], [], []
    
    dt_gyro = duration / n_gyro if n_gyro > 1 else 0.005
    dt_accel = duration / n_accel if n_accel > 1 else 0.005
    
    # --- Compute initial orientation from gravity ---
    # Use first 200 samples for orientation, but allow forcing a fixed gravity magnitude
    init_samples = min(200, n_accel)
    measured_gravity_mag = 9.80665  # fallback to standard

    # Calculate average gravity magnitude across ALL samples (the dominant vector)
    if n_accel > 0:
        avg_grav = sum(math.sqrt(a['x']**2 + a['y']**2 + a['z']**2) for a in accel_samples) / n_accel
        measured_gravity_mag = avg_grav
        print(f"Average gravity magnitude (all {n_accel} samples): {avg_grav:.6f} m/s²")
    # If caller provided a forced gravity value, use that instead
    if force_gravity is not None:
        measured_gravity_mag = float(force_gravity)
        print(f"Force gravity override: using {measured_gravity_mag:.6f} m/s² for subtraction")
    
    if init_samples > 0:
        gx = sum(a['x'] for a in accel_samples[:init_samples]) / init_samples
        gy = sum(a['y'] for a in accel_samples[:init_samples]) / init_samples
        gz = sum(a['z'] for a in accel_samples[:init_samples]) / init_samples
        grav_mag = math.sqrt(gx*gx + gy*gy + gz*gz)
        
        if grav_mag > 1.0:
            # Normalize: this is "down" in sensor frame
            grav_sensor_n = [gx/grav_mag, gy/grav_mag, gz/grav_mag]
            # Find quaternion that rotates grav_sensor_n to [0, -1, 0] (world down)
            target = [0.0, -1.0, 0.0]
            cx = grav_sensor_n[1]*target[2] - grav_sensor_n[2]*target[1]
            cy = grav_sensor_n[2]*target[0] - grav_sensor_n[0]*target[2]
            cz = grav_sensor_n[0]*target[1] - grav_sensor_n[1]*target[0]
            cross_mag = math.sqrt(cx*cx + cy*cy + cz*cz)
            dot = sum(a*b for a, b in zip(grav_sensor_n, target))
            
            if cross_mag > 1e-6:
                angle = math.atan2(cross_mag, dot)
                ax, ay, az = cx/cross_mag, cy/cross_mag, cz/cross_mag
                ha = angle / 2.0
                orientation = [math.cos(ha), ax*math.sin(ha), ay*math.sin(ha), az*math.sin(ha)]
                orientation = quat_normalize(orientation)
                print(f"Initial gravity in sensor (first 200): [{gx:.2f}, {gy:.2f}, {gz:.2f}] m/s²")
                print(f"Using average gravity {measured_gravity_mag:.6f} m/s² for subtraction")
                print(f"Initial orientation set to align gravity with world Y-down")
            else:
                if dot > 0:
                    orientation = [1.0, 0.0, 0.0, 0.0]
                else:
                    orientation = [0.0, 1.0, 0.0, 0.0]  # 180° around X
        else:
            orientation = [1.0, 0.0, 0.0, 0.0]
    else:
        orientation = [1.0, 0.0, 0.0, 0.0]
    
    # Gravity vector in world frame using MEASURED magnitude
    GRAVITY_WORLD = [0.0, -measured_gravity_mag, 0.0]
    
    # --- Integrate gyro for absolute orientation ---
    orientations_full = []
    
    for i, g in enumerate(gyro_samples):
        time_s = i * dt_gyro
        
        orientations_full.append({
            'time': time_s,
            'qw': orientation[0],
            'qx': orientation[1],
            'qy': orientation[2],
            'qz': orientation[3]
        })
        
        wx, wy, wz = g['x'], g['y'], g['z']
        omega_mag = math.sqrt(wx*wx + wy*wy + wz*wz)
        angle = omega_mag * dt_gyro
        
        if angle > 1e-8:
            half_angle = angle / 2.0
            inv_w = 1.0 / omega_mag
            ax, ay, az = wx*inv_w, wy*inv_w, wz*inv_w
            sa = math.sin(half_angle)
            ca = math.cos(half_angle)
            delta_q = [ca, ax*sa, ay*sa, az*sa]
            orientation = quat_multiply(orientation, delta_q)
            if i % 100 == 0:
                orientation = quat_normalize(orientation)
    
    orientation = quat_normalize(orientation)
    
    # --- Use orientations to transform accel to world frame, subtract gravity, integrate ---
    # High-pass filter to reduce drift: exponential decay on velocity
    # Alpha controls how aggressively we suppress drift (0 = no filter, 1 = instant decay)
    HP_ALPHA = 0.005  # Gentle high-pass: allows real motion through but kills slow drift
    
    velocity = [0.0, 0.0, 0.0]
    position = [0.0, 0.0, 0.0]
    path_full = []
    
    for i, a in enumerate(accel_samples):
        time_s = i * dt_accel
        
        gyro_idx = min(int(time_s / dt_gyro), n_gyro - 1)
        ori = orientations_full[gyro_idx]
        q = [ori['qw'], ori['qx'], ori['qy'], ori['qz']]
        
        accel_sensor = [a['x'], a['y'], a['z']]
        accel_world = quat_rotate_vec(q, accel_sensor)
        
        linear_accel = [
            accel_world[0] - GRAVITY_WORLD[0],
            accel_world[1] - GRAVITY_WORLD[1],
            accel_world[2] - GRAVITY_WORLD[2]
        ]
        
        # Integrate acceleration -> velocity
        velocity[0] += linear_accel[0] * dt_accel
        velocity[1] += linear_accel[1] * dt_accel
        velocity[2] += linear_accel[2] * dt_accel
        
        # High-pass: decay velocity towards zero to fight drift
        velocity[0] *= (1.0 - HP_ALPHA)
        velocity[1] *= (1.0 - HP_ALPHA)
        velocity[2] *= (1.0 - HP_ALPHA)
        
        # Integrate velocity -> position
        position[0] += velocity[0] * dt_accel
        position[1] += velocity[1] * dt_accel
        position[2] += velocity[2] * dt_accel
        
        path_full.append({
            'time': time_s,
            'x': position[0],
            'y': position[1],
            'z': position[2]
        })
    
    # --- Downsample for web visualization ---
    downsample_step = max(1, n_gyro // 3000)
    
    orientations_ds = orientations_full[::downsample_step]
    
    path_ds = []
    for ori in orientations_ds:
        t = ori['time']
        accel_idx = min(int(t / dt_accel), len(path_full) - 1) if path_full else 0
        if path_full:
            path_ds.append(path_full[accel_idx])
        else:
            path_ds.append({'time': t, 'x': 0, 'y': 0, 'z': 0})
    
    gyro_ds = []
    accel_ds = []
    for ori in orientations_ds:
        t = ori['time']
        gi = min(int(t / dt_gyro), n_gyro - 1)
        gyro_ds.append({'time': t, **gyro_samples[gi]})
        
        ai = min(int(t / dt_accel), n_accel - 1) if n_accel > 0 else 0
        if n_accel > 0:
            accel_ds.append({'time': t, **accel_samples[ai]})
        else:
            accel_ds.append({'time': t, 'x': 0, 'y': 0, 'z': 0})
    
    print(f"Downsampled to {len(orientations_ds)} frames (step={downsample_step})")
    
    return orientations_ds, path_ds, gyro_ds, accel_ds


def create_threejs_visualization(orientations, path_points, gyro_data, accel_data,
                                 duration: float, output_path: str):
    """Create interactive three.js visualization with camera path."""
    print(f"Creating 3D visualization: {output_path}")
    
    orientations_json = json.dumps(orientations)
    path_json = json.dumps(path_points)
    gyro_json = json.dumps(gyro_data)
    accel_json = json.dumps(accel_data)
    
    n_frames = len(orientations)
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GoPro Motion Data &amp; Path Visualization</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            overflow: hidden;
            font-family: Arial, sans-serif;
            background: #111;
        }}
        #container {{
            width: 100vw;
            height: 100vh;
        }}
        #controls {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 15px;
            border-radius: 8px;
            z-index: 100;
            max-height: 95vh;
            overflow-y: auto;
            width: 420px;
        }}
        #controls h3 {{
            margin: 0 0 10px 0;
            color: #4CAF50;
        }}
        #info {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 15px;
            border-radius: 8px;
            z-index: 100;
            font-size: 12px;
        }}
        button {{
            background: #4CAF50;
            border: none;
            color: white;
            padding: 8px 16px;
            margin: 3px;
            cursor: pointer;
            border-radius: 3px;
            font-size: 13px;
        }}
        button:hover {{ background: #45a049; }}
        button.active {{ background: #ff9800; }}
        input[type="range"] {{
            width: 100%;
            margin: 4px 0;
        }}
        .value {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .section {{
            margin-top: 12px;
            padding-top: 8px;
            border-top: 1px solid #444;
        }}
        label {{
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div id="container"></div>
    
    <div id="controls">
        <h3>&#x1F3A5; Motion &amp; Path Viewer</h3>
        
        <div>
            <label>Time: <span class="value" id="timeDisplay">0.0s</span> / {duration:.1f}s</label><br>
            <input type="range" id="timeSlider" min="0" max="{n_frames - 1}" value="0" step="1">
        </div>
        <div>
            <button id="playPause">&#9654; Play</button>
            <button id="reset">&#x21BA; Reset</button>
        </div>
        
        <div class="section">
            <label><input type="checkbox" id="showCamera" checked> Camera Model</label><br>
            <label><input type="checkbox" id="showPath" checked> Camera Path</label><br>
            <label><input type="checkbox" id="showVideoSphere" checked> 360&deg; Video Sphere</label>
        </div>
        
        <div class="section">
            <label>Gyro Sensitivity:</label>
            <div style="display:flex;align-items:center;gap:8px;">
                <input type="range" id="sensitivitySlider" min="0.1" max="50" value="10.0" step="0.1" style="flex:1;">
                <input type="number" id="sensitivityNumber" min="0.1" max="200" value="10.0" step="0.1" style="width:65px;background:#222;color:#4CAF50;border:1px solid #555;border-radius:3px;padding:3px;text-align:center;">
                <span style="font-size:11px;">x</span>
            </div>
        </div>

        <div class="section">
            <label>Distance Scale:</label>
            <div style="display:flex;align-items:center;gap:8px;">
                <input type="range" id="distanceSlider" min="0.001" max="100" value="1.0" step="0.001" style="flex:1;">
                <input type="number" id="distanceNumber" min="0.001" max="10000" value="1.0" step="0.001" style="width:65px;background:#222;color:#4CAF50;border:1px solid #555;border-radius:3px;padding:3px;text-align:center;">
                <span style="font-size:11px;">x</span>
            </div>
            <div style="font-size:10px;color:#888;">Fine-tune how far the camera travels</div>
        </div>
        
        <div class="section">
            <label>Path Point Size:</label>
            <div style="display:flex;align-items:center;gap:8px;">
                <input type="range" id="pointSizeSlider" min="1" max="15" value="3" step="1" style="flex:1;">
                <input type="number" id="pointSizeNumber" min="1" max="30" value="3" step="1" style="width:50px;background:#222;color:#4CAF50;border:1px solid #555;border-radius:3px;padding:3px;text-align:center;">
            </div>
        </div>
        
        <div class="section">
            <label><input type="checkbox" id="followCamera"> Follow Camera</label>
        </div>

        <div class="section">
            <input type="file" id="videoFile" accept="video/*" style="font-size: 10px;">
            <div style="font-size:10px;color:#888;">Load 360&deg; video to project on sphere</div>
        </div>
        
        <div class="section" style="font-size: 11px;">
            <strong>Controls:</strong><br>
            Mouse drag: Orbit view<br>
            Scroll: Zoom<br>
            Right-click drag: Pan
        </div>
    </div>
    
    <div id="info">
        <strong>Orientation (quaternion):</strong><br>
        W: <span class="value" id="oriW">1.000</span>
        X: <span class="value" id="oriX">0.000</span><br>
        Y: <span class="value" id="oriY">0.000</span>
        Z: <span class="value" id="oriZ">0.000</span><br>
        <br>
        <strong>Gyroscope (rad/s):</strong><br>
        X: <span class="value" id="gyroX">0.000</span>
        Y: <span class="value" id="gyroY">0.000</span>
        Z: <span class="value" id="gyroZ">0.000</span><br>
        <br>
        <strong>Accelerometer (m/s&sup2;):</strong><br>
        X: <span class="value" id="accelX">0.000</span>
        Y: <span class="value" id="accelY">0.000</span>
        Z: <span class="value" id="accelZ">0.000</span><br>
        <br>
        <strong>Position (m):</strong><br>
        X: <span class="value" id="posX">0.000</span>
        Y: <span class="value" id="posY">0.000</span>
        Z: <span class="value" id="posZ">0.000</span><br>
        <br>
        <strong>Frame:</strong> <span class="value" id="frameNum">0</span> / {n_frames - 1}
    </div>

    <script type="importmap">
    {{
        "imports": {{
            "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
            "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
        }}
    }}
    </script>
    
    <script type="module">
        import * as THREE from 'three';
        import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
        import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';

        // ── Embedded sensor data (pre-computed absolute values) ──
        const orientations = {orientations_json};
        const pathPoints = {path_json};
        const gyroData = {gyro_json};
        const accelData = {accel_json};

        // ── State ──
        let scene, camera, renderer, controls;
        let cameraModel, videoSphere;
        let video, videoTexture;
        let videoReady = false;
        let playing = false;
        let currentFrame = 0;
        let gyroSensitivity = 10.0;
        let distanceScale = 1.0;
        const SPHERE_RADIUS = 50;

        // Path visualization objects
        let pathLine = null;
        let pathDots = null;
        let currentDot = null;

        // ────────────────────────────────────────────
        //  INIT
        // ────────────────────────────────────────────
        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111111);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.01, 5000);
            camera.position.set(5, 5, 5);
            camera.lookAt(0, 0, 0);

            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.getElementById('container').appendChild(renderer.domElement);

            controls = new OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.1;

            // Grid + axes
            const grid = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
            scene.add(grid);
            const axes = new THREE.AxesHelper(3);
            scene.add(axes);
            addAxisLabels();

            // Lights
            scene.add(new THREE.AmbientLight(0x404040));
            const light1 = new THREE.PointLight(0xffffff, 0.6);
            light1.position.set(5, 5, 5);
            scene.add(light1);
            const light2 = new THREE.PointLight(0xffffff, 0.3);
            light2.position.set(-5, 3, -5);
            scene.add(light2);

            // Camera model
            cameraModel = createCameraModel();
            scene.add(cameraModel);

            // Video sphere (attached to camera model so it rotates together)
            video = document.createElement('video');
            video.loop = false;
            video.muted = true;
            video.playsInline = true;
            video.crossOrigin = 'anonymous';

            const sphereGeo = new THREE.SphereGeometry(SPHERE_RADIUS, 64, 64);
            const sphereMat = new THREE.MeshBasicMaterial({{
                map: null,
                side: THREE.DoubleSide,
                transparent: false
            }});
            videoSphere = new THREE.Mesh(sphereGeo, sphereMat);
            videoSphere.visible = false;
            cameraModel.add(videoSphere);

            // Build path visualization
            buildPathVisualization();

            // Current position indicator (bright red sphere)
            const dotGeo = new THREE.SphereGeometry(0.08, 16, 16);
            const dotMat = new THREE.MeshBasicMaterial({{ color: 0xff4444 }});
            currentDot = new THREE.Mesh(dotGeo, dotMat);
            scene.add(currentDot);

            // Event listeners
            document.getElementById('playPause').addEventListener('click', togglePlay);
            document.getElementById('reset').addEventListener('click', reset);
            document.getElementById('timeSlider').addEventListener('input', onSliderChange);
            document.getElementById('sensitivitySlider').addEventListener('input', onSensitivityChange);
            document.getElementById('sensitivityNumber').addEventListener('input', onSensitivityChange);
            document.getElementById('distanceSlider').addEventListener('input', onDistanceChange);
            document.getElementById('distanceNumber').addEventListener('input', onDistanceChange);
            document.getElementById('pointSizeSlider').addEventListener('input', onPointSizeChange);
            document.getElementById('pointSizeNumber').addEventListener('input', onPointSizeChange);
            document.getElementById('showCamera').addEventListener('change', () => {{
                cameraModel.visible = document.getElementById('showCamera').checked;
            }});
            document.getElementById('showPath').addEventListener('change', () => {{
                const v = document.getElementById('showPath').checked;
                if (pathLine) pathLine.visible = v;
                if (pathDots) pathDots.visible = v;
                if (currentDot) currentDot.visible = v;
            }});
            document.getElementById('showVideoSphere').addEventListener('change', () => {{
                if (videoSphere) videoSphere.visible = document.getElementById('showVideoSphere').checked && videoReady;
            }});
            document.getElementById('videoFile').addEventListener('change', onVideoFileSelected);
            window.addEventListener('resize', onWindowResize);

            updateFrame(0);
            animate();
        }}

        // ────────────────────────────────────────────
        //  PATH VISUALIZATION
        // ────────────────────────────────────────────
        function buildPathVisualization() {{
            if (pathLine) {{ scene.remove(pathLine); pathLine.geometry.dispose(); }}
            if (pathDots) {{ scene.remove(pathDots); pathDots.geometry.dispose(); }}

            const n = pathPoints.length;
            if (n < 2) return;

            const linePositions = new Float32Array(n * 3);
            const lineColors = new Float32Array(n * 3);
            const dotPositions = new Float32Array(n * 3);
            const dotColors = new Float32Array(n * 3);

            for (let i = 0; i < n; i++) {{
                const p = pathPoints[i];
                const x = p.x * distanceScale;
                const y = p.y * distanceScale;
                const z = p.z * distanceScale;

                linePositions[i*3]   = x;
                linePositions[i*3+1] = y;
                linePositions[i*3+2] = z;
                dotPositions[i*3]   = x;
                dotPositions[i*3+1] = y;
                dotPositions[i*3+2] = z;

                // Color gradient: green -> yellow -> red over time
                const t = i / (n - 1);
                let r, g, b;
                if (t < 0.5) {{
                    r = t * 2; g = 1.0; b = 0;
                }} else {{
                    r = 1.0; g = 1.0 - (t - 0.5) * 2; b = 0;
                }}
                lineColors[i*3] = r; lineColors[i*3+1] = g; lineColors[i*3+2] = b;
                dotColors[i*3] = r;  dotColors[i*3+1] = g;  dotColors[i*3+2] = b;
            }}

            const lineGeo = new THREE.BufferGeometry();
            lineGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
            lineGeo.setAttribute('color', new THREE.BufferAttribute(lineColors, 3));
            pathLine = new THREE.Line(lineGeo, new THREE.LineBasicMaterial({{ vertexColors: true, linewidth: 2 }}));
            scene.add(pathLine);

            const dotGeo = new THREE.BufferGeometry();
            dotGeo.setAttribute('position', new THREE.BufferAttribute(dotPositions, 3));
            dotGeo.setAttribute('color', new THREE.BufferAttribute(dotColors, 3));
            pathDots = new THREE.Points(dotGeo, new THREE.PointsMaterial({{
                size: parseInt(document.getElementById('pointSizeSlider').value),
                vertexColors: true,
                sizeAttenuation: true
            }}));
            scene.add(pathDots);
        }}

        // ────────────────────────────────────────────
        //  CAMERA MODEL
        // ────────────────────────────────────────────
        function createCameraModel() {{
            const group = new THREE.Group();

            const loader = new GLTFLoader();
            loader.load('gopro_max.glb', (gltf) => {{
                const model = gltf.scene;
                model.scale.set(0.5, 0.5, 0.5);
                group.add(model);
                console.log('GoPro Max model loaded');
            }}, undefined, () => {{
                console.warn('GoPro model not found, using fallback box');
                const geo = new THREE.BoxGeometry(1.5, 1, 0.8);
                const mat = new THREE.MeshPhongMaterial({{ color: 0x333333 }});
                group.add(new THREE.Mesh(geo, mat));
                const coneGeo = new THREE.ConeGeometry(0.15, 0.4, 8);
                const coneMat = new THREE.MeshBasicMaterial({{ color: 0x00ff00 }});
                const cone = new THREE.Mesh(coneGeo, coneMat);
                cone.rotation.x = -Math.PI / 2;
                cone.position.z = 0.6;
                group.add(cone);
            }});

            const sGeo = new THREE.SphereGeometry(49, 32, 32);
            const sMat = new THREE.MeshBasicMaterial({{
                color: 0xffffff, wireframe: true, transparent: true, opacity: 0.15
            }});
            group.add(new THREE.Mesh(sGeo, sMat));

            return group;
        }}

        function addAxisLabels() {{
            const makeLabel = (text, color, pos) => {{
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = 128; canvas.height = 64;
                ctx.fillStyle = color;
                ctx.font = 'Bold 48px Arial';
                ctx.fillText(text, 10, 50);
                const tex = new THREE.CanvasTexture(canvas);
                const sprite = new THREE.Sprite(new THREE.SpriteMaterial({{ map: tex }}));
                sprite.scale.set(1, 0.5, 1);
                sprite.position.copy(pos);
                scene.add(sprite);
            }};
            makeLabel('X', '#ff0000', new THREE.Vector3(3.5, 0, 0));
            makeLabel('Y', '#00ff00', new THREE.Vector3(0, 3.5, 0));
            makeLabel('Z', '#0000ff', new THREE.Vector3(0, 0, 3.5));
        }}

        // ────────────────────────────────────────────
        //  UPDATE FRAME (uses pre-computed absolute values)
        // ────────────────────────────────────────────
        function updateFrame(frameIndex) {{
            if (frameIndex < 0) frameIndex = 0;
            if (frameIndex >= orientations.length) frameIndex = orientations.length - 1;
            currentFrame = frameIndex;

            const ori = orientations[frameIndex];
            const path = pathPoints[frameIndex];
            const gyro = gyroData[frameIndex];
            const accel = accelData[frameIndex];

            // Absolute orientation from pre-computed quaternion
            const baseQ = new THREE.Quaternion(ori.qx, ori.qy, ori.qz, ori.qw);

            // Apply gyro sensitivity by scaling the rotation angle
            if (Math.abs(gyroSensitivity - 1.0) > 0.01) {{
                const angle = 2 * Math.acos(Math.min(1, Math.abs(ori.qw)));
                if (angle > 1e-6) {{
                    const sinHalf = Math.sin(angle / 2);
                    const axis = new THREE.Vector3(
                        ori.qx / sinHalf, ori.qy / sinHalf, ori.qz / sinHalf
                    ).normalize();
                    baseQ.setFromAxisAngle(axis, angle * gyroSensitivity);
                }}
            }}

            cameraModel.setRotationFromQuaternion(baseQ);

            // Position from pre-computed path
            const px = path.x * distanceScale;
            const py = path.y * distanceScale;
            const pz = path.z * distanceScale;
            cameraModel.position.set(px, py, pz);

            if (currentDot) currentDot.position.set(px, py, pz);

            // Follow camera mode
            if (document.getElementById('followCamera').checked) {{
                controls.target.set(px, py, pz);
            }}

            // Update UI
            document.getElementById('timeDisplay').textContent = ori.time.toFixed(1) + 's';
            document.getElementById('timeSlider').value = frameIndex;
            document.getElementById('frameNum').textContent = frameIndex;

            document.getElementById('oriW').textContent = ori.qw.toFixed(3);
            document.getElementById('oriX').textContent = ori.qx.toFixed(3);
            document.getElementById('oriY').textContent = ori.qy.toFixed(3);
            document.getElementById('oriZ').textContent = ori.qz.toFixed(3);

            document.getElementById('gyroX').textContent = gyro.x.toFixed(3);
            document.getElementById('gyroY').textContent = gyro.y.toFixed(3);
            document.getElementById('gyroZ').textContent = gyro.z.toFixed(3);

            document.getElementById('accelX').textContent = accel.x.toFixed(3);
            document.getElementById('accelY').textContent = accel.y.toFixed(3);
            document.getElementById('accelZ').textContent = accel.z.toFixed(3);

            document.getElementById('posX').textContent = px.toFixed(3);
            document.getElementById('posY').textContent = py.toFixed(3);
            document.getElementById('posZ').textContent = pz.toFixed(3);
        }}

        // ────────────────────────────────────────────
        //  CONTROLS
        // ────────────────────────────────────────────
        function findFrameForTime(time) {{
            let lo = 0, hi = orientations.length - 1;
            if (time <= orientations[0].time) return 0;
            if (time >= orientations[hi].time) return hi;
            while (lo <= hi) {{
                const mid = (lo + hi) >> 1;
                if (Math.abs(orientations[mid].time - time) < 0.01) return mid;
                if (orientations[mid].time < time) lo = mid + 1;
                else hi = mid - 1;
            }}
            return Math.min(lo, orientations.length - 1);
        }}

        function togglePlay() {{
            playing = !playing;
            document.getElementById('playPause').textContent = playing ? '\\u23F8 Pause' : '\\u25B6 Play';
            if (video && video.readyState >= 2) {{
                if (playing) video.play().catch(() => {{}});
                else video.pause();
            }}
        }}

        function reset() {{
            playing = false;
            currentFrame = 0;
            document.getElementById('playPause').textContent = '\\u25B6 Play';
            updateFrame(0);
            if (video && video.readyState >= 2) {{
                video.currentTime = 0;
                video.pause();
            }}
        }}

        function onSliderChange(e) {{
            playing = false;
            document.getElementById('playPause').textContent = '\\u25B6 Play';
            updateFrame(parseInt(e.target.value));
            if (video && video.readyState >= 2) {{
                video.currentTime = orientations[currentFrame].time;
                video.pause();
            }}
        }}

        function onSensitivityChange(e) {{
            gyroSensitivity = parseFloat(e.target.value);
            document.getElementById('sensitivitySlider').value = gyroSensitivity;
            document.getElementById('sensitivityNumber').value = gyroSensitivity;
            updateFrame(currentFrame);
        }}

        function onDistanceChange(e) {{
            distanceScale = parseFloat(e.target.value);
            document.getElementById('distanceSlider').value = distanceScale;
            document.getElementById('distanceNumber').value = distanceScale;
            buildPathVisualization();
            updateFrame(currentFrame);
        }}

        function onPointSizeChange(e) {{
            const size = parseInt(e.target.value);
            document.getElementById('pointSizeSlider').value = size;
            document.getElementById('pointSizeNumber').value = size;
            if (pathDots) pathDots.material.size = size;
        }}

        function onVideoFileSelected(event) {{
            const file = event.target.files[0];
            if (!file) return;
            videoReady = false;
            const url = URL.createObjectURL(file);
            video.src = url;
            video.load();
            video.addEventListener('loadeddata', () => {{
                console.log('Video loaded:', file.name, video.duration + 's',
                            video.videoWidth + 'x' + video.videoHeight);
                if (!videoTexture) {{
                    videoTexture = new THREE.VideoTexture(video);
                    videoTexture.minFilter = THREE.LinearFilter;
                    videoTexture.magFilter = THREE.LinearFilter;
                    videoTexture.colorSpace = THREE.SRGBColorSpace;
                    videoSphere.material.map = videoTexture;
                    videoSphere.material.needsUpdate = true;
                }}
                videoReady = true;
                videoSphere.visible = document.getElementById('showVideoSphere').checked;
                video.currentTime = orientations[currentFrame].time;
            }}, {{ once: true }});
        }}

        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}

        // ────────────────────────────────────────────
        //  ANIMATION LOOP
        // ────────────────────────────────────────────
        function animate() {{
            requestAnimationFrame(animate);

            if (playing) {{
                if (videoReady && video && video.readyState >= 2) {{
                    const fi = findFrameForTime(video.currentTime);
                    if (fi !== currentFrame) updateFrame(fi);
                }} else {{
                    const next = currentFrame + 1;
                    if (next < orientations.length) {{
                        updateFrame(next);
                    }} else {{
                        playing = false;
                        document.getElementById('playPause').textContent = '\\u25B6 Play';
                    }}
                }}
            }}

            controls.update();
            renderer.render(scene, camera);
        }}

        init();
    </script>
</body>
</html>'''
    
    with open(output_path, 'w') as f:
        f.write(html_content)


def main():
    parser = argparse.ArgumentParser(
        description="Extract gyro/accelerometer data from GoPro .360 file and create "
                    "interactive 3D visualization with camera orientation and travel path."
    )
    
    parser.add_argument('--video360', required=True,
                        help='Path to GoPro .360 file')
    parser.add_argument('--output-csv', default='motion_data.csv',
                        help='Output CSV file path')
    parser.add_argument('--output-html', default='motion_viewer.html',
                        help='Output HTML visualization path')
    parser.add_argument('--force-gravity', type=float, default=None,
                        help='Force gravity magnitude (m/s^2) to use when subtracting gravity; overrides measured average')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video360):
        print(f"Error: File not found: {args.video360}")
        sys.exit(1)
    
    # Get video duration
    print("Getting video duration...")
    duration = get_video_duration(args.video360)
    if duration is None:
        print("Error: Could not determine video duration")
        sys.exit(1)
    
    print(f"Video duration: {duration:.2f} seconds")
    
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
        
        gpmf_parser = GPMFParser(gpmf_data)
        gpmf_parser.parse()
        
        print(f"Found {len(gpmf_parser.gyro_samples)} gyroscope samples")
        print(f"Found {len(gpmf_parser.accel_samples)} accelerometer samples")
        
        if not gpmf_parser.gyro_samples and not gpmf_parser.accel_samples:
            print("Error: No motion data found")
            sys.exit(1)
        
        if gpmf_parser.gyro_samples:
            g0 = gpmf_parser.gyro_samples[0]
            print(f"First gyro: X={g0['x']:.3f}, Y={g0['y']:.3f}, Z={g0['z']:.3f}")
        if gpmf_parser.accel_samples:
            a0 = gpmf_parser.accel_samples[0]
            print(f"First accel: X={a0['x']:.3f}, Y={a0['y']:.3f}, Z={a0['z']:.3f}")
        
        # Save raw data to CSV
        save_to_csv(gpmf_parser.gyro_samples, gpmf_parser.accel_samples, 
                     duration, args.output_csv)
        
        # Compute absolute orientations and camera path
        print("Computing absolute orientations and camera path...")
        orientations, path_points, gyro_ds, accel_ds = \
            compute_absolute_orientations_and_path(
                gpmf_parser.gyro_samples, gpmf_parser.accel_samples, duration,
                force_gravity=args.force_gravity
            )
        
        if path_points:
            max_dist = max(
                math.sqrt(p['x']**2 + p['y']**2 + p['z']**2) 
                for p in path_points
            )
            print(f"Max path distance from origin: {max_dist:.2f} m (before distance scale)")
        
        # Create 3D visualization
        create_threejs_visualization(
            orientations, path_points, gyro_ds, accel_ds,
            duration, args.output_html
        )
        
        print(f"\n✓ Done!")
        print(f"  CSV data:  {args.output_csv}")
        print(f"  3D viewer: {args.output_html}")
        print(f"\nOpen {args.output_html} in a browser to see interactive 3D visualization")
        print(f"Serve with: python3 -m http.server 8000")
        
    finally:
        if os.path.exists(gpmf_path):
            os.unlink(gpmf_path)


if __name__ == '__main__':
    main()

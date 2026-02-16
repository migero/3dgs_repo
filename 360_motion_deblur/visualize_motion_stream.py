#!/usr/bin/env python3
"""
Extract and visualize gyro/accelerometer stream from GoPro .360 file.
Creates both CSV output and interactive 3D visualization.
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
                        # If only one scale value, apply to all axes
                        if repeat_count == 1 and scale[0] != 1.0:
                            scale[1] = scale[2] = scale[0]
                    elif type_char == 's':
                        for i in range(min(3, repeat_count)):
                            offset = scal_pos + 8 + i * 2
                            if offset + 2 <= len(self.data):
                                val = struct.unpack('>h', self.data[offset:offset + 2])[0]
                                if val != 0:
                                    scale[i] = float(val)
                        # If only one scale value, apply to all axes
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
        
        # Write gyro samples
        for i, sample in enumerate(gyro_samples):
            time_s = (i / len(gyro_samples)) * duration
            mag = (sample['x']**2 + sample['y']**2 + sample['z']**2)**0.5
            writer.writerow([f"{time_s:.3f}", 'GYRO', 
                           f"{sample['x']:.3f}", f"{sample['y']:.3f}", 
                           f"{sample['z']:.3f}", f"{mag:.3f}"])
        
        # Write accel samples
        for i, sample in enumerate(accel_samples):
            time_s = (i / len(accel_samples)) * duration
            mag = (sample['x']**2 + sample['y']**2 + sample['z']**2)**0.5
            writer.writerow([f"{time_s:.3f}", 'ACCL', 
                           f"{sample['x']:.3f}", f"{sample['y']:.3f}", 
                           f"{sample['z']:.3f}", f"{mag:.3f}"])


def create_threejs_visualization(gyro_samples: List[Dict], accel_samples: List[Dict],
                                 duration: float, output_path: str):
    """Create interactive three.js visualization of motion data."""
    print(f"Creating 3D visualization: {output_path}")
    
    # Downsample for web visualization (every 50th sample)
    gyro_downsampled = gyro_samples[::50]
    accel_downsampled = accel_samples[::50]
    
    # Prepare data for JSON
    gyro_data = []
    for i, sample in enumerate(gyro_downsampled):
        time_s = (i * 50 / len(gyro_samples)) * duration
        gyro_data.append({
            'time': time_s,
            'x': sample['x'],
            'y': sample['y'],
            'z': sample['z']
        })
    
    accel_data = []
    for i, sample in enumerate(accel_downsampled):
        time_s = (i * 50 / len(accel_samples)) * duration
        accel_data.append({
            'time': time_s,
            'x': sample['x'],
            'y': sample['y'],
            'z': sample['z']
        })
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GoPro Motion Data Visualization</title>
    
    <style>
        body {{
            margin: 0;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }}
        #container {{
            width: 100vw;
            height: 100vh;
        }}
        #controls {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 15px;
            border-radius: 5px;
            z-index: 100;
        }}
        #info {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 15px;
            border-radius: 5px;
            z-index: 100;
            font-size: 12px;
        }}
        button {{
            background: #4CAF50;
            border: none;
            color: white;
            padding: 8px 16px;
            margin: 5px;
            cursor: pointer;
            border-radius: 3px;
        }}
        button:hover {{
            background: #45a049;
        }}
        input[type="range"] {{
            width: 200px;
        }}
        .value {{
            color: #4CAF50;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div id="container"></div>
    
    <div id="controls">
        <h3>Motion Data Viewer</h3>
        <div>
            <label>Time: <span class="value" id="timeDisplay">0.0s</span> / {duration:.1f}s</label><br>
            <input type="range" id="timeSlider" min="0" max="{len(gyro_downsampled)-1}" value="0" step="1">
        </div>
        <div>
            <button id="playPause">Play</button>
            <button id="reset">Reset</button>
        </div>
        <div>
            <label><input type="checkbox" id="showGyro" checked> Camera Rotation (from Gyro)</label><br>
            <label><input type="checkbox" id="showAccel" checked> Acceleration (Blue Arrow)</label>
        </div>
        <div style="margin-top: 10px;">
            <label>Gyro Sensitivity: <span class="value" id="sensitivityValue">1.0</span>x</label><br>
            <input type="range" id="sensitivitySlider" min="0.1" max="10" value="1.0" step="0.1">
        </div>
        <div style="margin-top: 10px;">
            <label><input type="checkbox" id="showVideoSphere" checked> Show 360° Video</label><br>
            <input type="file" id="videoFile" accept="video/*" style="font-size: 10px; margin-top: 5px;">
        </div>
        <div style="margin-top: 10px; font-size: 11px;">
            <strong>Controls:</strong><br>
            Mouse: Rotate view<br>
            Scroll: Zoom
        </div>
    </div>
    
    <div id="info">
        <strong>Gyroscope (rad/s):</strong><br>
        X: <span class="value" id="gyroX">0.000</span><br>
        Y: <span class="value" id="gyroY">0.000</span><br>
        Z: <span class="value" id="gyroZ">0.000</span><br>
        <br>
        <strong>Accelerometer (m/s²):</strong><br>
        X: <span class="value" id="accelX">0.000</span><br>
        Y: <span class="value" id="accelY">0.000</span><br>
        Z: <span class="value" id="accelZ">0.000</span><br>
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
        // Motion data
        const gyroData = {json.dumps(gyro_data)};
        const accelData = {json.dumps(accel_data)};
        
        let scene, camera, renderer, controls;
        let cameraModel, accelArrow, videoSphere;
        let video, videoTexture;
        let videoReady = false;
        let playing = false;
        let currentFrame = 0;
        let animationId;
        let cameraOrientation = new THREE.Quaternion();
        let gyroSensitivity = 1.0;
        const SPHERE_RADIUS = 50; // Sphere radius - 10 m/s² acceleration will reach this
        
        function init() {{
            // Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a1a);
            
            // Camera - positioned outside to orbit around the camera model
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(5, 5, 5);
            camera.lookAt(0, 0, 0);
            
            // Renderer
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('container').appendChild(renderer.domElement);
            
            // Controls
            controls = new OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            
            // Grid
            const gridHelper = new THREE.GridHelper(10, 10, 0x444444, 0x222222);
            scene.add(gridHelper);
            
            // Axes helper
            const axesHelper = new THREE.AxesHelper(5);
            scene.add(axesHelper);
            
            // Add axis labels
            addAxisLabels();
            
            // Create camera model (GoPro-like shape)
            cameraModel = createCameraModel();
            scene.add(cameraModel);
            
            // Create video sphere for 360° video
            video = document.createElement('video');
            video.loop = true;
            video.muted = true;
            video.playsInline = true;
            video.crossOrigin = 'anonymous';
            
            // Don't create texture yet - wait for video to load
            videoTexture = null;
            
            const sphereGeometry = new THREE.SphereGeometry(SPHERE_RADIUS, 64, 64);
            // Double-sided so visible from inside and outside
            
            const sphereMaterial = new THREE.MeshBasicMaterial({{
                map: null, // Will be set when video loads
                side: THREE.DoubleSide,
                transparent: false,
                opacity: 1.0
            }});
            
            videoSphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
            videoSphere.visible = false; // Hidden until video is loaded
            cameraModel.add(videoSphere); // Attach to camera so it moves together
            
            // Accelerometer arrow (blue) - scaled so 10 m/s² = SPHERE_RADIUS
            accelArrow = new THREE.ArrowHelper(
                new THREE.Vector3(0, 1, 0),
                new THREE.Vector3(0, 0, 0),
                5, // Initial length
                0x0000ff,
                2, // Head length
                1  // Head width
            );
            scene.add(accelArrow);
            
            // Event listeners
            document.getElementById('playPause').addEventListener('click', togglePlay);
            document.getElementById('reset').addEventListener('click', reset);
            document.getElementById('timeSlider').addEventListener('input', onSliderChange);
            document.getElementById('showGyro').addEventListener('change', toggleVisibility);
            document.getElementById('showAccel').addEventListener('change', toggleVisibility);
            document.getElementById('sensitivitySlider').addEventListener('input', onSensitivityChange);
            document.getElementById('videoFile').addEventListener('change', onVideoFileSelected);
            document.getElementById('showVideoSphere').addEventListener('change', () => {{
                if (videoSphere) videoSphere.visible = document.getElementById('showVideoSphere').checked;
            }});
            
            window.addEventListener('resize', onWindowResize);
            
            updateFrame(0);
            animate();
        }}
        
        function addAxisLabels() {{
            // Simple text sprites for labels
            const createTextSprite = (text, color, position) => {{
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.width = 128;
                canvas.height = 64;
                context.fillStyle = color;
                context.font = 'Bold 48px Arial';
                context.fillText(text, 10, 50);
                
                const texture = new THREE.CanvasTexture(canvas);
                const spriteMaterial = new THREE.SpriteMaterial({{ map: texture }});
                const sprite = new THREE.Sprite(spriteMaterial);
                sprite.scale.set(1, 0.5, 1);
                sprite.position.copy(position);
                scene.add(sprite);
            }};
            
            createTextSprite('X', '#ff0000', new THREE.Vector3(5.5, 0, 0));
            createTextSprite('Y', '#00ff00', new THREE.Vector3(0, 5.5, 0));
            createTextSprite('Z', '#0000ff', new THREE.Vector3(0, 0, 5.5));
        }}
        
        function createCameraModel() {{
            const group = new THREE.Group();
            
            // Load GoPro Max GLB model
            const loader = new GLTFLoader();
            loader.load('gopro_max.glb', (gltf) => {{
                const model = gltf.scene;
                
                // Scale and position the model appropriately
                model.scale.set(0.5, 0.5, 0.5);
                
                // Keep original materials (normal shading)
                
                group.add(model);
                console.log('GoPro Max model loaded');
            }}, undefined, (error) => {{
                console.error('Error loading GoPro model:', error);
                // Fallback to box if model fails to load
                const fallbackGeometry = new THREE.BoxGeometry(1.5, 1, 0.8);
                const fallbackMaterial = new THREE.MeshBasicMaterial({{ 
                    color: 0x333333,
                    wireframe: true
                }});
                const fallback = new THREE.Mesh(fallbackGeometry, fallbackMaterial);
                group.add(fallback);
            }});
            
            // White wireframe sphere for rotation visualization (radius 49, overlaps video sphere)
            const smallSphereGeometry = new THREE.SphereGeometry(49, 32, 32);
            const smallSphereMaterial = new THREE.MeshBasicMaterial({{
                color: 0xffffff,
                wireframe: true,
                transparent: true,
                opacity: 0.3
            }});
            const smallSphere = new THREE.Mesh(smallSphereGeometry, smallSphereMaterial);
            group.add(smallSphere);
            
            // Add lights to see the camera
            const light1 = new THREE.PointLight(0xffffff, 0.5);
            light1.position.set(5, 5, 5);
            scene.add(light1);
            
            const light2 = new THREE.PointLight(0xffffff, 0.3);
            light2.position.set(-5, 3, -5);
            scene.add(light2);
            
            const ambientLight = new THREE.AmbientLight(0x404040);
            scene.add(ambientLight);
            
            return group;
        }}
        
        function updateFrame(frameIndex) {{
            if (frameIndex >= gyroData.length) frameIndex = 0;
            currentFrame = frameIndex;
            
            const gyro = gyroData[frameIndex];
            const accel = accelData[Math.floor(frameIndex * accelData.length / gyroData.length)];
            
            // Update camera orientation from gyroscope
            // Gyro gives angular velocity (rad/s), need to integrate to get rotation
            // Assume ~30fps for downsampled data (every 50th sample from 200Hz = ~4Hz)
            const dt = 1.0 / 4.0; // time step between samples
            
            // Scale down the gyro values (they seem to have wrong scale factor)
            const scale = 0.01 * gyroSensitivity; // Adjust with sensitivity slider
            
            // Create rotation quaternion from angular velocity
            const angle = Math.sqrt(gyro.x*gyro.x + gyro.y*gyro.y + gyro.z*gyro.z) * scale * dt;
            
            if (angle > 0.0001) {{
                const axis = new THREE.Vector3(gyro.x, gyro.y, gyro.z).normalize();
                const deltaQ = new THREE.Quaternion().setFromAxisAngle(axis, angle);
                cameraOrientation.multiply(deltaQ);
                cameraModel.setRotationFromQuaternion(cameraOrientation);
            }}
            
            // Update accel arrow - scale so 10 m/s² = SPHERE_RADIUS
            const accelVec = new THREE.Vector3(accel.x, accel.y, accel.z);
            const accelLen = accelVec.length();
            if (accelLen > 0.001) {{
                accelArrow.setDirection(accelVec.normalize());
                // Scale: 10 m/s² = SPHERE_RADIUS (50 units)
                const arrowLength = (accelLen / 10.0) * SPHERE_RADIUS;
                accelArrow.setLength(arrowLength, 2, 1);
            }}
            
            // Update UI
            document.getElementById('timeDisplay').textContent = gyro.time.toFixed(1) + 's';
            document.getElementById('timeSlider').value = frameIndex;
            document.getElementById('gyroX').textContent = gyro.x.toFixed(3);
            document.getElementById('gyroY').textContent = gyro.y.toFixed(3);
            document.getElementById('gyroZ').textContent = gyro.z.toFixed(3);
            document.getElementById('accelX').textContent = accel.x.toFixed(3);
            document.getElementById('accelY').textContent = accel.y.toFixed(3);
            document.getElementById('accelZ').textContent = accel.z.toFixed(3);
        }}
        
        function findFrameIndexForTime(time) {{
            // Binary search to find closest frame by time
            let left = 0;
            let right = gyroData.length - 1;
            
            if (time <= gyroData[0].time) return 0;
            if (time >= gyroData[right].time) return right;
            
            while (left <= right) {{
                const mid = Math.floor((left + right) / 2);
                const midTime = gyroData[mid].time;
                
                if (Math.abs(midTime - time) < 0.01) return mid;
                
                if (midTime < time) {{
                    left = mid + 1;
                }} else {{
                    right = mid - 1;
                }}
            }}
            
            return left < gyroData.length ? left : gyroData.length - 1;
        }}
        
        function togglePlay() {{
            playing = !playing;
            document.getElementById('playPause').textContent = playing ? 'Pause' : 'Play';
            
            // Sync video playback
            if (video && video.readyState >= 2) {{
                if (playing) {{
                    video.play().catch(err => console.error('Video play error:', err));
                }} else {{
                    video.pause();
                }}
            }}
        }}
        
        function reset() {{
            playing = false;
            currentFrame = 0;
            updateFrame(0);
            document.getElementById('playPause').textContent = 'Play';
            
            // Reset video to start
            if (video && video.readyState >= 2) {{
                video.currentTime = 0;
                video.pause();
            }}
        }}
        
        function onSliderChange(e) {{
            playing = false;
            document.getElementById('playPause').textContent = 'Play';
            const frameIndex = parseInt(e.target.value);
            updateFrame(frameIndex);
            
            // Sync video to slider position
            if (video && video.readyState >= 2) {{
                video.currentTime = gyroData[frameIndex].time;
                video.pause();
            }}
        }}
        
        function toggleVisibility() {{
            gyroArrow.visible = document.getElementById('showGyro').checked;
            accelArrow.visible = document.getElementById('showAccel').checked;
        }}
        
        function onSensitivityChange(e) {{
            gyroSensitivity = parseFloat(e.target.value);
            document.getElementById('sensitivityValue').textContent = gyroSensitivity.toFixed(1);
        }}
        
        function onVideoFileSelected(event) {{
            const file = event.target.files[0];
            if (file) {{
                videoReady = false;
                const url = URL.createObjectURL(file);
                video.src = url;
                video.load();
                
                video.addEventListener('loadeddata', () => {{
                    console.log('Video loaded:', file.name, 'Duration:', video.duration, 's', 'Size:', video.videoWidth, 'x', video.videoHeight);
                    
                    // Now create the texture with actual video data
                    if (!videoTexture) {{
                        videoTexture = new THREE.VideoTexture(video);
                        videoTexture.minFilter = THREE.LinearFilter;
                        videoTexture.magFilter = THREE.LinearFilter;
                        videoTexture.colorSpace = THREE.SRGBColorSpace;
                        videoTexture.needsUpdate = true;
                        videoSphere.material.map = videoTexture;
                        videoSphere.material.needsUpdate = true;
                    }}
                    
                    videoReady = true;
                    videoSphere.visible = document.getElementById('showVideoSphere').checked;
                    
                    // Sync video to current timeline position
                    const currentTime = gyroData[currentFrame].time;
                    video.currentTime = currentTime;
                }}, {{ once: true }});
                
                video.muted = true;
                video.loop = false; // Don't loop, sync with timeline
            }}
        }}
        
        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            
            if (playing && videoReady && video && video.readyState >= 2) {{
                // Video drives the timeline - find matching frame for current video time
                const videoTime = video.currentTime;
                const frameIndex = findFrameIndexForTime(videoTime);
                if (frameIndex !== currentFrame) {{
                    currentFrame = frameIndex;
                    updateFrame(currentFrame);
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
        description="Extract and visualize gyro/accelerometer stream from GoPro .360 file"
    )
    
    parser.add_argument('--video360', required=True,
                        help='Path to GoPro .360 file')
    parser.add_argument('--output-csv', default='motion_data.csv',
                        help='Output CSV file path')
    parser.add_argument('--output-html', default='motion_viewer.html',
                        help='Output HTML visualization path')
    
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
        
        parser = GPMFParser(gpmf_data)
        parser.parse()
        
        print(f"Found {len(parser.gyro_samples)} gyroscope samples")
        print(f"Found {len(parser.accel_samples)} accelerometer samples")
        
        if not parser.gyro_samples and not parser.accel_samples:
            print("Error: No motion data found")
            sys.exit(1)
        
        # Show sample data
        if parser.gyro_samples:
            print(f"\nFirst gyro: X={parser.gyro_samples[0]['x']:.3f}, "
                  f"Y={parser.gyro_samples[0]['y']:.3f}, Z={parser.gyro_samples[0]['z']:.3f}")
            print(f"Last gyro: X={parser.gyro_samples[-1]['x']:.3f}, "
                  f"Y={parser.gyro_samples[-1]['y']:.3f}, Z={parser.gyro_samples[-1]['z']:.3f}")
        
        # Save to CSV
        save_to_csv(parser.gyro_samples, parser.accel_samples, duration, args.output_csv)
        
        # Create 3D visualization
        create_threejs_visualization(parser.gyro_samples, parser.accel_samples, 
                                     duration, args.output_html)
        
        print(f"\n✓ Done!")
        print(f"  CSV data: {args.output_csv}")
        print(f"  3D viewer: {args.output_html}")
        print(f"\nOpen {args.output_html} in a browser to see interactive 3D visualization")
        
    finally:
        if os.path.exists(gpmf_path):
            os.unlink(gpmf_path)


if __name__ == '__main__':
    main()

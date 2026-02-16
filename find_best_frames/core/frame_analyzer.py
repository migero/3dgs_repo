#!/usr/bin/env python3

import subprocess
import json
import re
import os
import tempfile
from typing import List, Dict, Optional, Callable


class FrameAnalyzer:
    
    def __init__(self, square_size: int = 256):
        self.frame_data = []
        self.video_fps = 0
        self.total_frames = 0
        self.duration = 0
        self.square_size = square_size
        self.frame_width = 0
        self.frame_height = 0
    
    def get_video_info(self, video_path: str) -> Dict:
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video':
                fps_str = stream.get('r_frame_rate', '30/1')
                num, den = map(int, fps_str.split('/'))
                self.video_fps = num / den if den else 30
                self.total_frames = int(stream.get('nb_frames', 0))
                self.frame_width = int(stream.get('width', 1920))
                self.frame_height = int(stream.get('height', 1080))
                if self.total_frames == 0:
                    duration = float(info.get('format', {}).get('duration', 0))
                    self.total_frames = int(duration * self.video_fps)
                self.duration = float(info.get('format', {}).get('duration', 0))
                break
        
        return {
            'fps': self.video_fps,
            'total_frames': self.total_frames,
            'duration': self.duration,
            'width': self.frame_width,
            'height': self.frame_height
        }
    
    def get_crop_positions(self) -> List[tuple]:
        """Calculate 5 crop positions: center + 4 at 50% distance to corners"""
        if not self.frame_width or not self.frame_height:
            return [(0, 0)]
        
        w, h = self.frame_width, self.frame_height
        size = self.square_size
        
        # Center position
        center_x = (w - size) // 2
        center_y = (h - size) // 2
        
        # 50% distance from center to each corner
        quarter_w = w // 4
        quarter_h = h // 4
        
        positions = [
            (center_x, center_y),                    # Center
            (quarter_w, quarter_h),                  # Top-left region
            (3 * quarter_w - size//2, quarter_h),   # Top-right region  
            (quarter_w, 3 * quarter_h - size//2),   # Bottom-left region
            (3 * quarter_w - size//2, 3 * quarter_h - size//2)  # Bottom-right region
        ]
        
        # Ensure crops are within bounds
        valid_positions = []
        for x, y in positions:
            x = max(0, min(x, w - size))
            y = max(0, min(y, h - size))
            valid_positions.append((x, y))
        
        return valid_positions

    def analyze_frames(self, video_path: str, progress_callback: Optional[Callable] = None) -> List[Dict]:
        self.get_video_info(video_path)
        crops = self.get_crop_positions()
        
        if progress_callback:
            progress_callback(0, f"Analyzing video with {len(crops)} crops per frame...")
        
        self.frame_data = []
        
        # For simplicity, let's analyze just the center crop first
        center_x, center_y = crops[0]  # Use center crop
        crop_filter = f"crop={self.square_size}:{self.square_size}:{center_x}:{center_y},blurdetect,metadata=print:file=-"
        
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vf', crop_filter,
            '-f', 'null', '-'
        ]
        
        process = subprocess.Popen(
            cmd, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE,
            text=True, bufsize=1
        )
        
        blur_pattern = re.compile(r'lavfi\.blur=(\d+\.?\d*)')
        frame_pattern = re.compile(r'frame:(\d+)\s+pts:\d+\s+pts_time:(\d+\.?\d*)')
        current_frame = 0
        current_time = 0.0
        
        for line in process.stdout:
            frame_match = frame_pattern.search(line)
            if frame_match:
                current_frame = int(frame_match.group(1))
                current_time = float(frame_match.group(2))
                continue
            
            blur_match = blur_pattern.search(line)
            if blur_match:
                blur_value = float(blur_match.group(1))
                sharpness = max(0, 100 - blur_value * 10)
                
                self.frame_data.append({
                    'frame': current_frame,
                    'time': current_time,
                    'blur': blur_value,
                    'sharpness': sharpness,
                    'crops_blur': [blur_value]  # Single crop for now
                })
                
                if progress_callback and len(self.frame_data) % 100 == 0:
                    pct = min(99, int((len(self.frame_data) / max(1, self.total_frames)) * 100))
                    progress_callback(pct, f"Analyzed {len(self.frame_data)} frames...")
        
        process.wait()
        
        if progress_callback:
            progress_callback(100, f"Analysis complete: {len(self.frame_data)} frames")
        
        return self.frame_data
    
    def select_best_frames(self, target_fps: float) -> List[Dict]:
        if not self.frame_data or self.video_fps <= 0:
            return []
        
        interval = int(self.video_fps / target_fps)
        if interval < 1:
            interval = 1
        
        selected = []
        num_intervals = (len(self.frame_data) + interval - 1) // interval
        
        for i in range(num_intervals):
            start_idx = i * interval
            end_idx = min(start_idx + interval, len(self.frame_data))
            
            interval_frames = self.frame_data[start_idx:end_idx]
            if interval_frames:
                best = max(interval_frames, key=lambda x: x['sharpness'])
                selected.append({
                    'interval': i,
                    'frame': best['frame'],
                    'time': best['time'],
                    'sharpness': best['sharpness'],
                    'blur': best['blur']
                })
        
        return selected
    
    def extract_frames(self, video_path: str, selected_frames: List[Dict], 
                      output_dir: str, quality: int = 95,
                      progress_callback: Optional[Callable] = None) -> List[str]:
        """Extract frames in chunks using select filter for speed with progress feedback"""
        os.makedirs(output_dir, exist_ok=True)
        
        if not selected_frames:
            return []
        
        # Get video filename without extension
        video_basename = os.path.splitext(os.path.basename(video_path))[0]
        
        saved_files = []
        total_frames = len(selected_frames)
        chunk_size = 50
        
        # Process in chunks to show progress
        for chunk_start in range(0, total_frames, chunk_size):
            chunk_end = min(chunk_start + chunk_size, total_frames)
            chunk = selected_frames[chunk_start:chunk_end]
            
            # Build select expression for this chunk
            frame_nums = [f['frame'] for f in chunk]
            select_expr = '+'.join([f'eq(n\\,{n})' for n in frame_nums])
            
            # Temp files for this chunk
            temp_pattern = os.path.join(output_dir, f'temp_chunk_{chunk_start}_%05d.jpg')
            
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vf', f'select={select_expr}',
                '-vsync', '0',
                '-q:v', str(max(1, min(31, int((100 - quality) / 3) + 1))),
                temp_pattern
            ]
            
            if progress_callback:
                pct = int((chunk_start / total_frames) * 90)
                progress_callback(pct, f"Extracting frames {chunk_start+1}-{chunk_end}/{total_frames}...")
            
            # Extract this chunk
            subprocess.run(cmd, capture_output=True)
            
            # Rename temp files with video name + frame number
            for local_idx, frame_info in enumerate(chunk):
                temp_file = os.path.join(output_dir, f'temp_chunk_{chunk_start}_{local_idx+1:05d}.jpg')
                
                if os.path.exists(temp_file):
                    frame_num = frame_info['frame']
                    final_file = os.path.join(output_dir, f'{video_basename}_{frame_num}.jpg')
                    os.rename(temp_file, final_file)
                    saved_files.append(final_file)
        
        if progress_callback:
            progress_callback(100, f"Saved {len(saved_files)} frames")
        
        return saved_files

#!/usr/bin/env python3
"""
GoPro 360 File Analyzer
Extracts metadata and stream information from .360 files
"""

import subprocess
import json
import shutil
import os
from typing import Optional, Dict, Any, List


class GoPro360Analyzer:
    """Analyzes GoPro .360 files to extract metadata and stream information"""
    
    def __init__(self):
        self.ffprobe_path = shutil.which("ffprobe")
        
    def analyze_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a .360 file and return detailed information
        
        Args:
            file_path: Path to the .360 file
            
        Returns:
            Dictionary containing file analysis or None on error
        """
        if not os.path.exists(file_path):
            return None
            
        if not self.ffprobe_path:
            return None
            
        try:
            # Get detailed stream and format information
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                "-show_programs",
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return None
                
            data = json.loads(result.stdout)
            
            return self._parse_analysis(data, file_path)
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return None
            
    def _parse_analysis(self, data: Dict, file_path: str) -> Dict[str, Any]:
        """Parse FFprobe output into analysis dictionary"""
        analysis = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'format': {},
            'video_streams': [],
            'audio_streams': [],
            'data_streams': [],
            'detected_format': 'unknown',
            'recommended_settings': {},
        }
        
        # Parse format info
        if 'format' in data:
            fmt = data['format']
            analysis['format'] = {
                'format_name': fmt.get('format_name', ''),
                'format_long_name': fmt.get('format_long_name', ''),
                'duration': float(fmt.get('duration', 0)),
                'size': int(fmt.get('size', 0)),
                'bit_rate': int(fmt.get('bit_rate', 0)),
                'tags': fmt.get('tags', {}),
            }
            
        # Parse streams
        if 'streams' in data:
            for stream in data['streams']:
                stream_info = self._parse_stream(stream)
                
                codec_type = stream.get('codec_type', '')
                if codec_type == 'video':
                    analysis['video_streams'].append(stream_info)
                elif codec_type == 'audio':
                    analysis['audio_streams'].append(stream_info)
                else:
                    analysis['data_streams'].append(stream_info)
                    
        # Detect the 360 format
        analysis['detected_format'] = self._detect_format(analysis)
        
        # Generate recommended settings
        analysis['recommended_settings'] = self._generate_recommendations(analysis)
        
        return analysis
        
    def _parse_stream(self, stream: Dict) -> Dict[str, Any]:
        """Parse individual stream information"""
        return {
            'index': stream.get('index', 0),
            'codec_type': stream.get('codec_type', ''),
            'codec_name': stream.get('codec_name', ''),
            'codec_long_name': stream.get('codec_long_name', ''),
            'width': stream.get('width', 0),
            'height': stream.get('height', 0),
            'sample_rate': stream.get('sample_rate', ''),
            'channels': stream.get('channels', 0),
            'bit_rate': stream.get('bit_rate', ''),
            'frame_rate': stream.get('r_frame_rate', ''),
            'avg_frame_rate': stream.get('avg_frame_rate', ''),
            'duration': stream.get('duration', ''),
            'nb_frames': stream.get('nb_frames', ''),
            'tags': stream.get('tags', {}),
            'disposition': stream.get('disposition', {}),
        }
        
    def _detect_format(self, analysis: Dict) -> str:
        """
        Detect the type of 360 format based on stream analysis
        
        Returns format identifier:
        - 'gopro_max_2channel': GoPro MAX .360 with 2 video tracks (3 cube faces each)
        - 'gopro_max_lrv': GoPro MAX LRV file (dual fisheye, low res)
        - 'single_stream': Single video stream
        - 'unknown': Cannot determine
        """
        video_streams = analysis.get('video_streams', [])
        
        if len(video_streams) == 0:
            return 'unknown'
            
        # Check for 2 video streams - this is the GoPro MAX .360 format
        # Channel 0: Left, Front, Right cube faces
        # Channel 1: Bottom, Back, Top cube faces (rotated)
        if len(video_streams) >= 2:
            # Both tracks should have similar dimensions
            w0 = video_streams[0].get('width', 0)
            h0 = video_streams[0].get('height', 0)
            w1 = video_streams[1].get('width', 0)
            h1 = video_streams[1].get('height', 0)
            
            if w0 == w1 and h0 == h1 and w0 > 0:
                # Check aspect ratio - should be roughly 3:1 for 3 cube faces
                aspect = w0 / h0 if h0 > 0 else 0
                if 2.5 < aspect < 3.5:
                    return 'gopro_max_2channel'
                    
            return 'dual_stream'
            
        # Single video stream
        if len(video_streams) == 1:
            stream = video_streams[0]
            width = stream.get('width', 0)
            height = stream.get('height', 0)
            
            if width > 0 and height > 0:
                aspect = width / height
                
                # 2:1 ratio for dual fisheye (LRV files)
                if 1.8 < aspect < 2.2:
                    return 'gopro_max_lrv'
                    
        return 'single_stream'
        
    def _generate_recommendations(self, analysis: Dict) -> Dict[str, Any]:
        """Generate recommended conversion settings based on analysis"""
        detected = analysis.get('detected_format', 'unknown')
        video_streams = analysis.get('video_streams', [])
        
        recommendations = {
            'input_projection': 'gopro_max',
            'fov': 190,
            'notes': [],
        }
        
        if detected == 'gopro_max_2channel':
            recommendations['input_projection'] = 'gopro_max'
            recommendations['fov'] = 190
            recommendations['notes'].append(
                "Detected GoPro MAX .360 format with 2 video channels."
            )
            recommendations['notes'].append(
                "Channel 1: Left/Front/Right | Channel 2: Bottom/Back/Top (rotated)"
            )
            recommendations['notes'].append(
                "Content is at 1/6 and 5/6 positions in each track."
            )
            
        elif detected == 'gopro_max_lrv':
            recommendations['input_projection'] = 'dfisheye'
            recommendations['fov'] = 190
            recommendations['notes'].append(
                "Detected GoPro MAX LRV format (low-res dual fisheye)."
            )
            recommendations['notes'].append(
                "This format is not fully supported - use the .360 file instead."
            )
            
        elif detected == 'dual_stream':
            recommendations['input_projection'] = 'gopro_max'
            recommendations['fov'] = 190
            recommendations['notes'].append(
                "Detected dual video streams. Likely GoPro MAX format."
            )
            
        else:
            recommendations['notes'].append(
                "Could not auto-detect format."
            )
            recommendations['notes'].append(
                "For GoPro MAX .360 files, use default settings."
            )
            
        # Add resolution info
        if video_streams:
            width = video_streams[0].get('width', 0)
            height = video_streams[0].get('height', 0)
            
            if width >= 4000:
                recommendations['notes'].append(
                    f"Track resolution: {width}x{height}. High quality source."
                )
            else:
                recommendations['notes'].append(
                    f"Track resolution: {width}x{height}."
                )
                
            if len(video_streams) >= 2:
                w2 = video_streams[1].get('width', 0)
                h2 = video_streams[1].get('height', 0)
                recommendations['notes'].append(
                    f"Second track: {w2}x{h2}"
                )
                
        return recommendations
        
    def get_stream_mapping(self, file_path: str) -> Dict[str, List[int]]:
        """
        Get mapping of stream types to indices
        Useful for advanced FFmpeg commands
        """
        analysis = self.analyze_file(file_path)
        
        if not analysis:
            return {}
            
        mapping = {
            'video': [],
            'audio': [],
            'data': [],
        }
        
        for stream in analysis.get('video_streams', []):
            mapping['video'].append(stream.get('index', 0))
            
        for stream in analysis.get('audio_streams', []):
            mapping['audio'].append(stream.get('index', 0))
            
        for stream in analysis.get('data_streams', []):
            mapping['data'].append(stream.get('index', 0))
            
        return mapping


def print_analysis(file_path: str):
    """Print detailed analysis of a .360 file"""
    analyzer = GoPro360Analyzer()
    analysis = analyzer.analyze_file(file_path)
    
    if not analysis:
        print(f"Failed to analyze: {file_path}")
        return
        
    print(f"\n{'='*60}")
    print(f"GoPro 360 File Analysis: {analysis['file_name']}")
    print(f"{'='*60}")
    
    # File info
    size_mb = analysis['file_size'] / (1024 * 1024)
    print(f"\nFile Size: {size_mb:.2f} MB")
    
    # Format info
    fmt = analysis.get('format', {})
    if fmt:
        duration = fmt.get('duration', 0)
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        print(f"Duration: {minutes}m {seconds}s")
        print(f"Format: {fmt.get('format_long_name', 'Unknown')}")
        
    # Video streams
    print(f"\nVideo Streams: {len(analysis['video_streams'])}")
    for i, stream in enumerate(analysis['video_streams']):
        print(f"  [{i}] {stream['width']}x{stream['height']} @ {stream['frame_rate']}")
        print(f"      Codec: {stream['codec_name']}")
        
    # Audio streams  
    print(f"\nAudio Streams: {len(analysis['audio_streams'])}")
    for i, stream in enumerate(analysis['audio_streams']):
        print(f"  [{i}] {stream['channels']}ch @ {stream['sample_rate']}Hz")
        print(f"      Codec: {stream['codec_name']}")
        
    # Detected format
    print(f"\nDetected Format: {analysis['detected_format']}")
    
    # Recommendations
    recs = analysis.get('recommended_settings', {})
    print(f"\nRecommended Settings:")
    print(f"  Projection: {recs.get('input_projection', 'dfisheye')}")
    print(f"  FOV: {recs.get('fov', 190)}°")
    
    for note in recs.get('notes', []):
        print(f"  Note: {note}")
        
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        print_analysis(sys.argv[1])
    else:
        print("Usage: python gopro_analyzer.py <file.360>")

"""
Photo Geolocator - Main orchestrator for geolocating sequential photos

Combines:
- KML path parsing
- Path interpolation
- Photo sorting and assignment
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

from .kml_parser import KMLPathParser, PathPoint
from .path_interpolator import PathInterpolator, InterpolatedPosition


@dataclass
class GeolocatedPhoto:
    """A photo with assigned GPS coordinates"""
    filepath: Path
    filename: str
    sequence_num: int       # Order in sequence (1-based)
    lat: float
    lon: float
    heading: float          # Camera direction in degrees
    distance_from_start: float  # meters along path
    progress: float         # 0.0 to 1.0 along path
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'filepath': str(self.filepath),
            'filename': self.filename,
            'sequence_num': self.sequence_num,
            'lat': self.lat,
            'lon': self.lon,
            'heading': self.heading,
            'distance_from_start': self.distance_from_start,
            'progress': self.progress
        }


class PhotoGeolocator:
    """
    Main class for geolocating sequential 360 photos along a known path
    """
    
    def __init__(self, kml_path: str, photos_dir: str,
                 photo_extensions: List[str] = None,
                 reverse_direction: bool = False):
        """
        Initialize the geolocator.
        
        Args:
            kml_path: Path to KML file containing the walking path
            photos_dir: Directory containing the 360 photos
            photo_extensions: List of valid extensions (default: common image formats)
            reverse_direction: If True, assigns photos in reverse order along path
        """
        self.kml_path = Path(kml_path)
        self.photos_dir = Path(photos_dir)
        self.reverse_direction = reverse_direction
        
        if photo_extensions is None:
            self.photo_extensions = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.360']
        else:
            self.photo_extensions = [ext.lower() for ext in photo_extensions]
        
        self.path_points: List[PathPoint] = []
        self.interpolator: Optional[PathInterpolator] = None
        self.photos: List[Path] = []
        self.geolocated_photos: List[GeolocatedPhoto] = []
        
    def load_path(self) -> int:
        """Load and parse the KML path. Returns number of path points."""
        parser = KMLPathParser(str(self.kml_path))
        self.path_points = parser.parse()
        
        if len(self.path_points) < 2:
            raise ValueError(f"KML path has only {len(self.path_points)} points, need at least 2")
        
        self.interpolator = PathInterpolator(self.path_points)
        return len(self.path_points)
    
    def scan_photos(self) -> int:
        """
        Scan directory for photos and sort by filename (natural sort).
        Returns number of photos found.
        """
        if not self.photos_dir.exists():
            raise FileNotFoundError(f"Photos directory not found: {self.photos_dir}")
        
        self.photos = []
        
        for file in self.photos_dir.iterdir():
            if file.is_file() and file.suffix.lower() in self.photo_extensions:
                self.photos.append(file)
        
        # Natural sort by filename (handles IMG_001, IMG_002, ..., IMG_100 correctly)
        self.photos.sort(key=lambda f: self._natural_sort_key(f.name))
        
        if self.reverse_direction:
            self.photos.reverse()
        
        print(f"Found {len(self.photos)} photos in {self.photos_dir}")
        return len(self.photos)
    
    def _natural_sort_key(self, s: str) -> List:
        """Key function for natural sorting of filenames"""
        return [int(text) if text.isdigit() else text.lower() 
                for text in re.split(r'(\d+)', s)]
    
    def geolocate(self, 
                  start_offset: float = 0.0,
                  end_offset: float = 0.0) -> List[GeolocatedPhoto]:
        """
        Assign GPS coordinates to all photos.
        
        Args:
            start_offset: Skip this many meters at the start of path
            end_offset: Skip this many meters at the end of path
            
        Returns:
            List of GeolocatedPhoto objects
        """
        if self.interpolator is None:
            self.load_path()
        
        if not self.photos:
            self.scan_photos()
        
        if not self.photos:
            raise ValueError("No photos found to geolocate")
        
        # Get spacing info
        spacing = self.interpolator.get_spacing_info(len(self.photos))
        print(f"Path length: {spacing['total_length_km']:.2f} km")
        print(f"Photo spacing: {spacing['spacing_info']}")
        
        # Interpolate positions
        positions = self.interpolator.interpolate_positions(
            len(self.photos),
            start_offset=start_offset,
            end_offset=end_offset
        )
        
        # Assign to photos
        self.geolocated_photos = []
        for i, (photo, pos) in enumerate(zip(self.photos, positions)):
            geo_photo = GeolocatedPhoto(
                filepath=photo,
                filename=photo.name,
                sequence_num=i + 1,
                lat=pos.lat,
                lon=pos.lon,
                heading=pos.heading,
                distance_from_start=pos.distance_from_start,
                progress=pos.progress
            )
            self.geolocated_photos.append(geo_photo)
        
        return self.geolocated_photos
    
    def export_json(self, output_path: str) -> str:
        """Export geolocated photos to JSON file"""
        if not self.geolocated_photos:
            raise ValueError("No geolocated photos. Run geolocate() first.")
        
        output_path = Path(output_path)
        
        data = {
            'kml_path': str(self.kml_path),
            'photos_dir': str(self.photos_dir),
            'total_photos': len(self.geolocated_photos),
            'path_length_m': self.interpolator.total_length,
            'generated_at': datetime.now().isoformat(),
            'photos': [p.to_dict() for p in self.geolocated_photos]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported to {output_path}")
        return str(output_path)
    
    def export_csv(self, output_path: str) -> str:
        """Export geolocated photos to CSV file"""
        if not self.geolocated_photos:
            raise ValueError("No geolocated photos. Run geolocate() first.")
        
        output_path = Path(output_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("sequence_num,filename,latitude,longitude,heading,distance_m,progress\n")
            for p in self.geolocated_photos:
                f.write(f"{p.sequence_num},{p.filename},{p.lat:.8f},{p.lon:.8f},"
                        f"{p.heading:.1f},{p.distance_from_start:.1f},{p.progress:.4f}\n")
        
        print(f"Exported to {output_path}")
        return str(output_path)
    
    def export_gpx(self, output_path: str, name: str = "Geolocated Photos") -> str:
        """Export geolocated photos as GPX waypoints"""
        if not self.geolocated_photos:
            raise ValueError("No geolocated photos. Run geolocate() first.")
        
        output_path = Path(output_path)
        
        gpx_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="360 Geolocator">
  <metadata>
    <name>{name}</name>
    <time>{datetime.now().isoformat()}</time>
  </metadata>
'''
        for p in self.geolocated_photos:
            gpx_content += f'''  <wpt lat="{p.lat:.8f}" lon="{p.lon:.8f}">
    <name>{p.filename}</name>
    <desc>Sequence: {p.sequence_num}, Distance: {p.distance_from_start:.1f}m</desc>
  </wpt>
'''
        gpx_content += '</gpx>'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(gpx_content)
        
        print(f"Exported to {output_path}")
        return str(output_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 3:
        geolocator = PhotoGeolocator(sys.argv[1], sys.argv[2])
        geolocator.load_path()
        geolocator.scan_photos()
        geolocated = geolocator.geolocate()
        
        # Print first and last few
        for p in geolocated[:3]:
            print(f"{p.sequence_num}: {p.filename} -> {p.lat:.6f}, {p.lon:.6f}")
        print("...")
        for p in geolocated[-3:]:
            print(f"{p.sequence_num}: {p.filename} -> {p.lat:.6f}, {p.lon:.6f}")
    else:
        print("Usage: python -m core.photo_geolocator <kml_file> <photos_dir>")

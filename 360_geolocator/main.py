"""
360 Photo Geolocator - Main entry point

Simple usage:
    from main import geolocate_photos
    
    results = geolocate_photos(
        kml_path='path.kml',
        photos_dir='photos/',
        output_json='locations.json'
    )
"""

import sys
from pathlib import Path
from typing import List, Optional

from core.kml_parser import KMLPathParser
from core.path_interpolator import PathInterpolator
from core.photo_geolocator import PhotoGeolocator, GeolocatedPhoto
from core.exif_writer import ExifGeotagWriter
from core.map_exporter import MapExporter


def geolocate_photos(
    kml_path: str,
    photos_dir: str,
    output_json: Optional[str] = None,
    output_csv: Optional[str] = None,
    output_gpx: Optional[str] = None,
    output_map: Optional[str] = None,
    write_exif: bool = False,
    reverse_direction: bool = False,
    start_offset: float = 0.0,
    end_offset: float = 0.0,
    photo_extensions: List[str] = None
) -> List[GeolocatedPhoto]:
    """
    Geolocate sequential photos along a KML path.
    
    This is the main high-level function for the 360 geolocator.
    Photos are distributed evenly along the path based on their
    filename order (natural sort).
    
    Args:
        kml_path: Path to KML file with the walking route
        photos_dir: Directory containing the photos
        output_json: Optional path to save JSON output
        output_csv: Optional path to save CSV output
        output_gpx: Optional path to save GPX output
        output_map: Optional path to save interactive HTML map
        write_exif: If True, write GPS to photo EXIF data
        reverse_direction: If True, reverse photo order along path
        start_offset: Skip this many meters at start of path
        end_offset: Skip this many meters at end of path
        photo_extensions: List of valid extensions (default: common formats)
        
    Returns:
        List of GeolocatedPhoto objects with assigned coordinates
        
    Example:
        >>> results = geolocate_photos(
        ...     'walk.kml', 
        ...     'photos/',
        ...     output_map='map.html',
        ...     write_exif=True
        ... )
        >>> print(f"Geolocated {len(results)} photos")
        >>> print(f"First photo at: {results[0].lat}, {results[0].lon}")
    """
    # Create geolocator
    geolocator = PhotoGeolocator(
        kml_path,
        photos_dir,
        photo_extensions=photo_extensions,
        reverse_direction=reverse_direction
    )
    
    # Load and process
    geolocator.load_path()
    geolocator.scan_photos()
    geolocated = geolocator.geolocate(
        start_offset=start_offset,
        end_offset=end_offset
    )
    
    # Exports
    if output_json:
        geolocator.export_json(output_json)
    
    if output_csv:
        geolocator.export_csv(output_csv)
    
    if output_gpx:
        geolocator.export_gpx(output_gpx)
    
    if output_map:
        map_exporter = MapExporter()
        map_exporter.create_map(
            geolocated,
            path_points=geolocator.path_points,
            output_path=output_map
        )
    
    if write_exif:
        writer = ExifGeotagWriter(backup_originals=True)
        writer.write_gps_batch(geolocated)
    
    return geolocated


def quick_map(kml_path: str, photos_dir: str, output: str = "photo_map.html"):
    """
    Quick function to generate a map from KML and photos.
    
    Args:
        kml_path: Path to KML file
        photos_dir: Directory with photos
        output: Output HTML file path
    """
    geolocate_photos(kml_path, photos_dir, output_map=output)
    print(f"Map saved to: {output}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python main.py <kml_file> <photos_dir> [output.json]")
        print("\nFor more options, use: python cli.py --help")
        sys.exit(1)
    
    kml_path = sys.argv[1]
    photos_dir = sys.argv[2]
    output_json = sys.argv[3] if len(sys.argv) > 3 else None
    
    results = geolocate_photos(
        kml_path,
        photos_dir,
        output_json=output_json,
        output_map=str(Path(photos_dir) / "photo_map.html")
    )
    
    print(f"\nGeolocated {len(results)} photos")
    print(f"First: {results[0].filename} at ({results[0].lat:.6f}, {results[0].lon:.6f})")
    print(f"Last: {results[-1].filename} at ({results[-1].lat:.6f}, {results[-1].lon:.6f})")

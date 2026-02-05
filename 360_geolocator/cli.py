"""
360 Photo Geolocator - CLI Interface

Command line tool for geolocating sequential 360 photos along a known path.
"""

import argparse
import sys
from pathlib import Path

from core.kml_parser import KMLPathParser
from core.path_interpolator import PathInterpolator
from core.photo_geolocator import PhotoGeolocator
from core.exif_writer import ExifGeotagWriter
from core.map_exporter import MapExporter


def main():
    parser = argparse.ArgumentParser(
        description='Geolocate sequential 360 photos along a KML path',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage - geolocate photos and export to JSON
  python cli.py path.kml photos_folder/ -o locations.json

  # Export to multiple formats
  python cli.py path.kml photos_folder/ --json out.json --csv out.csv --gpx out.gpx

  # Create interactive map
  python cli.py path.kml photos_folder/ --map photo_map.html

  # Write GPS to photo EXIF data
  python cli.py path.kml photos_folder/ --write-exif

  # Reverse direction (if photos go opposite to KML direction)
  python cli.py path.kml photos_folder/ --reverse

  # Skip first/last portion of path
  python cli.py path.kml photos_folder/ --start-offset 50 --end-offset 30
'''
    )
    
    # Required arguments
    parser.add_argument('kml_path', type=str,
                        help='Path to KML file containing the walking path')
    parser.add_argument('photos_dir', type=str,
                        help='Directory containing the 360 photos')
    
    # Export options
    parser.add_argument('-o', '--output', '--json', type=str, dest='json_output',
                        help='Output JSON file path')
    parser.add_argument('--csv', type=str,
                        help='Export to CSV file')
    parser.add_argument('--gpx', type=str,
                        help='Export to GPX file (waypoints)')
    parser.add_argument('--map', type=str,
                        help='Generate interactive HTML map')
    
    # EXIF options
    parser.add_argument('--write-exif', action='store_true',
                        help='Write GPS coordinates to photo EXIF data')
    parser.add_argument('--no-backup', action='store_true',
                        help='Do not backup original photos when writing EXIF')
    
    # Path adjustment options
    parser.add_argument('--reverse', action='store_true',
                        help='Reverse photo order (if photos go opposite to KML)')
    parser.add_argument('--start-offset', type=float, default=0.0,
                        help='Skip this many meters at the start of path')
    parser.add_argument('--end-offset', type=float, default=0.0,
                        help='Skip this many meters at the end of path')
    
    # Map options
    parser.add_argument('--marker-interval', type=int, default=1,
                        help='Show every Nth marker on map (default: 1 = all)')
    
    # Photo options
    parser.add_argument('--extensions', type=str, default='.jpg,.jpeg,.png,.360',
                        help='Comma-separated list of photo extensions')
    
    # Verbosity
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    # Validate inputs
    kml_path = Path(args.kml_path)
    photos_dir = Path(args.photos_dir)
    
    if not kml_path.exists():
        print(f"Error: KML file not found: {kml_path}", file=sys.stderr)
        return 1
    
    if not photos_dir.exists():
        print(f"Error: Photos directory not found: {photos_dir}", file=sys.stderr)
        return 1
    
    # Parse extensions
    extensions = [ext.strip() for ext in args.extensions.split(',')]
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    # Initialize geolocator
    print(f"KML path: {kml_path}")
    print(f"Photos directory: {photos_dir}")
    print(f"Photo extensions: {extensions}")
    print()
    
    geolocator = PhotoGeolocator(
        str(kml_path),
        str(photos_dir),
        photo_extensions=extensions,
        reverse_direction=args.reverse
    )
    
    # Load path
    print("Loading KML path...")
    num_points = geolocator.load_path()
    print(f"  Path has {num_points} waypoints")
    
    # Scan photos
    print("\nScanning photos...")
    num_photos = geolocator.scan_photos()
    print(f"  Found {num_photos} photos")
    
    if num_photos == 0:
        print("Error: No photos found!", file=sys.stderr)
        return 1
    
    # Show spacing info
    spacing = geolocator.interpolator.get_spacing_info(num_photos)
    print(f"\nPath length: {spacing['total_length_km']:.2f} km ({spacing['total_length_m']:.0f} m)")
    print(f"Expected spacing: {spacing['spacing_m']:.1f} m between photos")
    
    if args.start_offset > 0 or args.end_offset > 0:
        print(f"Offsets: start={args.start_offset}m, end={args.end_offset}m")
    
    if args.reverse:
        print("Direction: REVERSED")
    
    if args.dry_run:
        print("\n[DRY RUN] Would process photos without making changes")
        return 0
    
    # Geolocate
    print("\nAssigning GPS coordinates...")
    geolocated = geolocator.geolocate(
        start_offset=args.start_offset,
        end_offset=args.end_offset
    )
    
    # Show sample results
    print(f"\nSample results:")
    print(f"  First: {geolocated[0].filename} -> {geolocated[0].lat:.6f}, {geolocated[0].lon:.6f}")
    if len(geolocated) > 1:
        mid = len(geolocated) // 2
        print(f"  Middle: {geolocated[mid].filename} -> {geolocated[mid].lat:.6f}, {geolocated[mid].lon:.6f}")
    print(f"  Last: {geolocated[-1].filename} -> {geolocated[-1].lat:.6f}, {geolocated[-1].lon:.6f}")
    
    # Export to JSON
    if args.json_output:
        print(f"\nExporting to JSON: {args.json_output}")
        geolocator.export_json(args.json_output)
    
    # Export to CSV
    if args.csv:
        print(f"Exporting to CSV: {args.csv}")
        geolocator.export_csv(args.csv)
    
    # Export to GPX
    if args.gpx:
        print(f"Exporting to GPX: {args.gpx}")
        geolocator.export_gpx(args.gpx)
    
    # Generate map
    if args.map:
        print(f"Generating map: {args.map}")
        map_exporter = MapExporter(title="360 Photo Locations")
        map_exporter.create_map(
            geolocated,
            path_points=geolocator.path_points,
            marker_interval=args.marker_interval,
            output_path=args.map
        )
    
    # Write EXIF
    if args.write_exif:
        print(f"\nWriting GPS to EXIF...")
        if not args.no_backup:
            print("  (Original files will be backed up)")
        
        writer = ExifGeotagWriter(backup_originals=not args.no_backup)
        
        def progress(current, total):
            if current % 100 == 0 or current == total:
                print(f"  Progress: {current}/{total} ({100*current//total}%)")
        
        success, fail = writer.write_gps_batch(geolocated, progress_callback=progress)
        print(f"  Complete: {success} success, {fail} failed")
    
    # Default output if nothing specified
    if not any([args.json_output, args.csv, args.gpx, args.map, args.write_exif]):
        default_output = photos_dir / "geolocations.json"
        print(f"\nNo output specified, saving to: {default_output}")
        geolocator.export_json(str(default_output))
    
    print("\nDone!")
    return 0


if __name__ == '__main__':
    sys.exit(main())

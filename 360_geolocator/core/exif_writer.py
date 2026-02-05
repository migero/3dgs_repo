"""
EXIF Geotag Writer - Embed GPS coordinates into photo EXIF data

Supports writing:
- GPS coordinates (latitude, longitude)
- GPS heading/direction
- GPS altitude (if available)
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from fractions import Fraction

try:
    import piexif
    PIEXIF_AVAILABLE = True
except ImportError:
    PIEXIF_AVAILABLE = False
    print("Warning: piexif not installed. EXIF writing disabled.")
    print("Install with: pip install piexif")


class ExifGeotagWriter:
    """Write GPS coordinates to photo EXIF data"""
    
    def __init__(self, backup_originals: bool = True):
        """
        Initialize the EXIF writer.
        
        Args:
            backup_originals: If True, create backup of original files
        """
        self.backup_originals = backup_originals
        self.backup_dir: Optional[Path] = None
        
    def _decimal_to_dms(self, decimal: float) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        """
        Convert decimal degrees to degrees, minutes, seconds format for EXIF.
        Returns tuple of ((deg_num, deg_den), (min_num, min_den), (sec_num, sec_den))
        """
        decimal = abs(decimal)
        degrees = int(decimal)
        minutes_float = (decimal - degrees) * 60
        minutes = int(minutes_float)
        seconds_float = (minutes_float - minutes) * 60
        
        # Use high precision for seconds (multiplied by 10000)
        seconds_num = int(seconds_float * 10000)
        seconds_den = 10000
        
        return ((degrees, 1), (minutes, 1), (seconds_num, seconds_den))
    
    def _float_to_rational(self, value: float, precision: int = 100) -> Tuple[int, int]:
        """Convert float to rational (numerator, denominator) tuple"""
        return (int(value * precision), precision)
    
    def write_gps_to_photo(self, photo_path: str, lat: float, lon: float,
                           heading: Optional[float] = None,
                           altitude: Optional[float] = None) -> bool:
        """
        Write GPS coordinates to a single photo.
        
        Args:
            photo_path: Path to the photo file
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees  
            heading: Camera heading in degrees (0-360)
            altitude: Altitude in meters
            
        Returns:
            True if successful, False otherwise
        """
        if not PIEXIF_AVAILABLE:
            print("piexif not available, skipping EXIF write")
            return False
        
        photo_path = Path(photo_path)
        
        if not photo_path.exists():
            print(f"Photo not found: {photo_path}")
            return False
        
        try:
            # Try to load existing EXIF data
            try:
                exif_dict = piexif.load(str(photo_path))
            except:
                # No existing EXIF, create new
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            
            # Build GPS IFD
            gps_ifd = {}
            
            # Latitude
            gps_ifd[piexif.GPSIFD.GPSLatitudeRef] = b'N' if lat >= 0 else b'S'
            gps_ifd[piexif.GPSIFD.GPSLatitude] = self._decimal_to_dms(lat)
            
            # Longitude
            gps_ifd[piexif.GPSIFD.GPSLongitudeRef] = b'E' if lon >= 0 else b'W'
            gps_ifd[piexif.GPSIFD.GPSLongitude] = self._decimal_to_dms(lon)
            
            # Heading/Direction
            if heading is not None:
                gps_ifd[piexif.GPSIFD.GPSImgDirectionRef] = b'T'  # True north
                gps_ifd[piexif.GPSIFD.GPSImgDirection] = self._float_to_rational(heading, 100)
            
            # Altitude
            if altitude is not None:
                gps_ifd[piexif.GPSIFD.GPSAltitudeRef] = 0 if altitude >= 0 else 1
                gps_ifd[piexif.GPSIFD.GPSAltitude] = self._float_to_rational(abs(altitude), 10)
            
            exif_dict["GPS"] = gps_ifd
            
            # Backup original if requested
            if self.backup_originals:
                self._backup_file(photo_path)
            
            # Write EXIF data
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, str(photo_path))
            
            return True
            
        except Exception as e:
            print(f"Error writing EXIF to {photo_path}: {e}")
            return False
    
    def _backup_file(self, photo_path: Path):
        """Create backup of original file"""
        if self.backup_dir is None:
            self.backup_dir = photo_path.parent / "originals_backup"
            self.backup_dir.mkdir(exist_ok=True)
        
        backup_path = self.backup_dir / photo_path.name
        if not backup_path.exists():
            shutil.copy2(photo_path, backup_path)
    
    def write_gps_batch(self, geolocated_photos: List, progress_callback=None) -> Tuple[int, int]:
        """
        Write GPS to multiple photos.
        
        Args:
            geolocated_photos: List of GeolocatedPhoto objects
            progress_callback: Optional callback(current, total) for progress
            
        Returns:
            Tuple of (success_count, fail_count)
        """
        success = 0
        fail = 0
        total = len(geolocated_photos)
        
        for i, photo in enumerate(geolocated_photos):
            if progress_callback:
                progress_callback(i + 1, total)
            
            result = self.write_gps_to_photo(
                str(photo.filepath),
                photo.lat,
                photo.lon,
                heading=photo.heading
            )
            
            if result:
                success += 1
            else:
                fail += 1
        
        print(f"EXIF writing complete: {success} success, {fail} failed")
        return (success, fail)


def geotag_photo(photo_path: str, lat: float, lon: float, 
                 heading: float = None, backup: bool = True) -> bool:
    """Convenience function to geotag a single photo"""
    writer = ExifGeotagWriter(backup_originals=backup)
    return writer.write_gps_to_photo(photo_path, lat, lon, heading=heading)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 4:
        photo = sys.argv[1]
        lat = float(sys.argv[2])
        lon = float(sys.argv[3])
        heading = float(sys.argv[4]) if len(sys.argv) > 4 else None
        
        success = geotag_photo(photo, lat, lon, heading)
        print(f"Geotag {'successful' if success else 'failed'}")
    else:
        print("Usage: python -m core.exif_writer <photo> <lat> <lon> [heading]")

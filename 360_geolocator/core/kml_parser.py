"""
KML Path Parser - Extract path coordinates from KML files

Supports:
- LineString paths (walking/driving routes)
- Multiple LineStrings (will concatenate in order)
- Placemarks with coordinates
"""

from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import xml.etree.ElementTree as ET


@dataclass
class PathPoint:
    """A single point on the path"""
    lat: float
    lon: float
    alt: Optional[float] = None
    
    def as_tuple(self) -> Tuple[float, float]:
        return (self.lat, self.lon)
    
    def as_tuple_lon_lat(self) -> Tuple[float, float]:
        """Return (lon, lat) for shapely compatibility"""
        return (self.lon, self.lat)


class KMLPathParser:
    """Parse KML files to extract path coordinates"""
    
    # KML namespace
    KML_NS = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    def __init__(self, kml_path: str):
        self.kml_path = Path(kml_path)
        self.points: List[PathPoint] = []
        self.name: Optional[str] = None
        
    def parse(self) -> List[PathPoint]:
        """Parse the KML file and extract path coordinates"""
        if not self.kml_path.exists():
            raise FileNotFoundError(f"KML file not found: {self.kml_path}")
        
        tree = ET.parse(self.kml_path)
        root = tree.getroot()
        
        # Handle both namespaced and non-namespaced KML
        if root.tag.startswith('{'):
            namespace = root.tag.split('}')[0] + '}'
            self._parse_with_namespace(root, namespace)
        else:
            self._parse_without_namespace(root)
        
        if not self.points:
            # Try parsing as simple coordinate list
            self._parse_raw_coordinates(root)
            
        print(f"Parsed {len(self.points)} points from KML")
        return self.points
    
    def _parse_with_namespace(self, root: ET.Element, ns: str):
        """Parse KML with namespace"""
        # Try to get document name
        name_elem = root.find(f'.//{ns}name')
        if name_elem is not None:
            self.name = name_elem.text
        
        # Find all LineString coordinates
        for linestring in root.findall(f'.//{ns}LineString'):
            coords_elem = linestring.find(f'{ns}coordinates')
            if coords_elem is not None and coords_elem.text:
                self._parse_coordinate_string(coords_elem.text)
        
        # Also check for Point placemarks (in case path is defined as waypoints)
        for placemark in root.findall(f'.//{ns}Placemark'):
            point = placemark.find(f'.//{ns}Point/{ns}coordinates')
            if point is not None and point.text:
                self._parse_coordinate_string(point.text)
    
    def _parse_without_namespace(self, root: ET.Element):
        """Parse KML without namespace"""
        name_elem = root.find('.//name')
        if name_elem is not None:
            self.name = name_elem.text
            
        for linestring in root.findall('.//LineString'):
            coords_elem = linestring.find('coordinates')
            if coords_elem is not None and coords_elem.text:
                self._parse_coordinate_string(coords_elem.text)
                
        for placemark in root.findall('.//Placemark'):
            point = placemark.find('.//Point/coordinates')
            if point is not None and point.text:
                self._parse_coordinate_string(point.text)
    
    def _parse_raw_coordinates(self, root: ET.Element):
        """Try to find coordinates anywhere in the document"""
        for elem in root.iter():
            if elem.tag.endswith('coordinates') and elem.text:
                self._parse_coordinate_string(elem.text)
    
    def _parse_coordinate_string(self, coord_string: str):
        """Parse KML coordinate string format: lon,lat,alt lon,lat,alt ..."""
        coord_string = coord_string.strip()
        
        # Split by whitespace (space, newline, tab)
        coord_tuples = coord_string.split()
        
        for coord in coord_tuples:
            parts = coord.strip().split(',')
            if len(parts) >= 2:
                try:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    alt = float(parts[2]) if len(parts) > 2 else None
                    self.points.append(PathPoint(lat=lat, lon=lon, alt=alt))
                except ValueError:
                    continue  # Skip invalid coordinates
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get bounding box of the path (min_lat, min_lon, max_lat, max_lon)"""
        if not self.points:
            raise ValueError("No points parsed yet")
        
        lats = [p.lat for p in self.points]
        lons = [p.lon for p in self.points]
        
        return (min(lats), min(lons), max(lats), max(lons))
    
    def get_center(self) -> Tuple[float, float]:
        """Get center point of the path"""
        bbox = self.get_bounding_box()
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)


def parse_kml(kml_path: str) -> List[PathPoint]:
    """Convenience function to parse a KML file"""
    parser = KMLPathParser(kml_path)
    return parser.parse()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        points = parse_kml(sys.argv[1])
        for i, p in enumerate(points[:10]):
            print(f"{i}: {p.lat:.6f}, {p.lon:.6f}")
        if len(points) > 10:
            print(f"... and {len(points) - 10} more points")

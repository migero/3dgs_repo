"""
Path Interpolator - Distribute photos evenly along a path

Given a path (list of GPS coordinates) and a number of photos,
calculates the GPS position for each photo based on sequence order.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
import math

from .kml_parser import PathPoint


@dataclass
class InterpolatedPosition:
    """Position along the path with metadata"""
    index: int              # Photo index (0-based)
    lat: float
    lon: float
    distance_from_start: float  # meters
    progress: float         # 0.0 to 1.0 along path
    heading: float          # Approximate heading in degrees (0-360)
    
    def as_tuple(self) -> Tuple[float, float]:
        return (self.lat, self.lon)


class PathInterpolator:
    """Interpolate positions along a path for sequential photos"""
    
    # Earth radius in meters
    EARTH_RADIUS = 6371000
    
    def __init__(self, path_points: List[PathPoint]):
        if len(path_points) < 2:
            raise ValueError("Path must have at least 2 points")
        
        self.path_points = path_points
        self.segment_lengths: List[float] = []
        self.cumulative_distances: List[float] = []
        self.total_length: float = 0
        
        self._calculate_distances()
    
    def _calculate_distances(self):
        """Calculate distances between consecutive points"""
        self.cumulative_distances = [0.0]
        
        for i in range(1, len(self.path_points)):
            p1 = self.path_points[i - 1]
            p2 = self.path_points[i]
            
            dist = self._haversine_distance(p1.lat, p1.lon, p2.lat, p2.lon)
            self.segment_lengths.append(dist)
            self.cumulative_distances.append(self.cumulative_distances[-1] + dist)
        
        self.total_length = self.cumulative_distances[-1]
        print(f"Path total length: {self.total_length:.1f} meters ({self.total_length/1000:.2f} km)")
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates in meters"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return self.EARTH_RADIUS * c
    
    def _calculate_heading(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate heading/bearing from point 1 to point 2 in degrees"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
        
        heading = math.degrees(math.atan2(x, y))
        return (heading + 360) % 360  # Normalize to 0-360
    
    def _interpolate_point(self, distance: float) -> Tuple[float, float, float]:
        """
        Find the GPS coordinates at a given distance along the path.
        Returns (lat, lon, heading)
        """
        if distance <= 0:
            p = self.path_points[0]
            p_next = self.path_points[1]
            heading = self._calculate_heading(p.lat, p.lon, p_next.lat, p_next.lon)
            return (p.lat, p.lon, heading)
        
        if distance >= self.total_length:
            p = self.path_points[-1]
            p_prev = self.path_points[-2]
            heading = self._calculate_heading(p_prev.lat, p_prev.lon, p.lat, p.lon)
            return (p.lat, p.lon, heading)
        
        # Find the segment containing this distance
        segment_idx = 0
        for i, cum_dist in enumerate(self.cumulative_distances):
            if cum_dist > distance:
                segment_idx = i - 1
                break
        
        # Calculate position within the segment
        segment_start_dist = self.cumulative_distances[segment_idx]
        segment_length = self.segment_lengths[segment_idx]
        
        if segment_length == 0:
            t = 0
        else:
            t = (distance - segment_start_dist) / segment_length
        
        p1 = self.path_points[segment_idx]
        p2 = self.path_points[segment_idx + 1]
        
        # Linear interpolation
        lat = p1.lat + t * (p2.lat - p1.lat)
        lon = p1.lon + t * (p2.lon - p1.lon)
        heading = self._calculate_heading(p1.lat, p1.lon, p2.lat, p2.lon)
        
        return (lat, lon, heading)
    
    def interpolate_positions(self, num_photos: int, 
                              start_offset: float = 0.0,
                              end_offset: float = 0.0) -> List[InterpolatedPosition]:
        """
        Distribute photos evenly along the path.
        
        Args:
            num_photos: Number of photos to position
            start_offset: Distance in meters to skip at start of path
            end_offset: Distance in meters to skip at end of path
            
        Returns:
            List of InterpolatedPosition for each photo
        """
        effective_length = self.total_length - start_offset - end_offset
        
        if effective_length <= 0:
            raise ValueError("Path too short for given offsets")
        
        if num_photos == 1:
            # Single photo goes at the middle
            distances = [start_offset + effective_length / 2]
        else:
            # Distribute evenly from start_offset to (total - end_offset)
            step = effective_length / (num_photos - 1)
            distances = [start_offset + i * step for i in range(num_photos)]
        
        positions = []
        for i, dist in enumerate(distances):
            lat, lon, heading = self._interpolate_point(dist)
            positions.append(InterpolatedPosition(
                index=i,
                lat=lat,
                lon=lon,
                distance_from_start=dist,
                progress=dist / self.total_length,
                heading=heading
            ))
        
        return positions
    
    def get_position_at_progress(self, progress: float) -> Tuple[float, float]:
        """Get GPS coordinates at a given progress (0.0 to 1.0) along the path"""
        distance = progress * self.total_length
        lat, lon, _ = self._interpolate_point(distance)
        return (lat, lon)
    
    def get_spacing_info(self, num_photos: int) -> dict:
        """Get information about photo spacing"""
        spacing = self.total_length / max(1, num_photos - 1)
        return {
            'total_length_m': self.total_length,
            'total_length_km': self.total_length / 1000,
            'num_photos': num_photos,
            'spacing_m': spacing,
            'spacing_info': f"~{spacing:.1f}m between photos"
        }


if __name__ == "__main__":
    # Test with sample path
    test_points = [
        PathPoint(lat=52.2297, lon=21.0122),  # Warsaw
        PathPoint(lat=52.2300, lon=21.0130),
        PathPoint(lat=52.2310, lon=21.0140),
    ]
    
    interpolator = PathInterpolator(test_points)
    print(f"Total path length: {interpolator.total_length:.1f}m")
    
    positions = interpolator.interpolate_positions(10)
    for pos in positions:
        print(f"Photo {pos.index}: {pos.lat:.6f}, {pos.lon:.6f} - {pos.distance_from_start:.1f}m, heading {pos.heading:.0f}°")

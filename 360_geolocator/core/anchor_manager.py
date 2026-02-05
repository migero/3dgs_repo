"""
Anchor Point Manager - Handle manual photo-to-waypoint assignments

Allows users to create "anchor points" where they manually specify
which photo corresponds to which KML waypoint. The system then
interpolates between anchor points, allowing for variable walking speed.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import json
from pathlib import Path

from .kml_parser import PathPoint
from .path_interpolator import PathInterpolator


@dataclass
class AnchorPoint:
    """A manually assigned photo-to-waypoint mapping"""
    waypoint_index: int      # Index in KML path points
    photo_index: int         # Index in photo list (0-based)
    lat: float
    lon: float
    distance_from_start: float  # Distance along path in meters
    
    def to_dict(self) -> dict:
        return {
            'waypoint_index': self.waypoint_index,
            'photo_index': self.photo_index,
            'lat': self.lat,
            'lon': self.lon,
            'distance_from_start': self.distance_from_start
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AnchorPoint':
        return cls(**data)


@dataclass 
class PhotoAssignment:
    """Result of interpolation - photo with assigned GPS"""
    photo_index: int
    lat: float
    lon: float
    heading: float
    distance_from_start: float
    is_anchor: bool = False  # True if this is a manually set anchor


class AnchorPointManager:
    """
    Manages anchor points and interpolates photo positions between them.
    
    Workflow:
    1. Start with auto-distributed anchors at start and end
    2. User adds anchor points by selecting waypoint + photo
    3. System interpolates photos between anchor points
    """
    
    def __init__(self, path_points: List[PathPoint], num_photos: int):
        self.path_points = path_points
        self.num_photos = num_photos
        self.anchors: List[AnchorPoint] = []
        
        # Create interpolator for distance calculations
        self.interpolator = PathInterpolator(path_points)
        
        # Calculate distance for each waypoint
        self.waypoint_distances = self._calculate_waypoint_distances()
        
        # Initialize with start and end anchors
        self._init_default_anchors()
    
    def _calculate_waypoint_distances(self) -> List[float]:
        """Calculate cumulative distance for each waypoint"""
        return self.interpolator.cumulative_distances.copy()
    
    def _init_default_anchors(self):
        """Create default anchors at start and end of path"""
        # Start anchor: first waypoint, first photo
        start_wp = self.path_points[0]
        self.anchors.append(AnchorPoint(
            waypoint_index=0,
            photo_index=0,
            lat=start_wp.lat,
            lon=start_wp.lon,
            distance_from_start=0.0
        ))
        
        # End anchor: last waypoint, last photo
        end_wp = self.path_points[-1]
        self.anchors.append(AnchorPoint(
            waypoint_index=len(self.path_points) - 1,
            photo_index=self.num_photos - 1,
            lat=end_wp.lat,
            lon=end_wp.lon,
            distance_from_start=self.interpolator.total_length
        ))
    
    def add_anchor(self, waypoint_index: int, photo_index: int) -> AnchorPoint:
        """
        Add or update an anchor point.
        
        Args:
            waypoint_index: Index in path_points list
            photo_index: Index in photos list (0-based)
            
        Returns:
            The created/updated AnchorPoint
        """
        if waypoint_index < 0 or waypoint_index >= len(self.path_points):
            raise ValueError(f"Waypoint index {waypoint_index} out of range")
        if photo_index < 0 or photo_index >= self.num_photos:
            raise ValueError(f"Photo index {photo_index} out of range")
        
        wp = self.path_points[waypoint_index]
        distance = self.waypoint_distances[waypoint_index]
        
        # Check if anchor already exists for this waypoint
        existing = self.get_anchor_at_waypoint(waypoint_index)
        if existing:
            existing.photo_index = photo_index
            self._sort_anchors()
            return existing
        
        # Create new anchor
        anchor = AnchorPoint(
            waypoint_index=waypoint_index,
            photo_index=photo_index,
            lat=wp.lat,
            lon=wp.lon,
            distance_from_start=distance
        )
        
        self.anchors.append(anchor)
        self._sort_anchors()
        
        return anchor
    
    def remove_anchor(self, waypoint_index: int) -> bool:
        """Remove anchor at waypoint (except start/end)"""
        if waypoint_index == 0 or waypoint_index == len(self.path_points) - 1:
            return False  # Can't remove start/end
        
        self.anchors = [a for a in self.anchors if a.waypoint_index != waypoint_index]
        return True
    
    def get_anchor_at_waypoint(self, waypoint_index: int) -> Optional[AnchorPoint]:
        """Get anchor at specific waypoint, if exists"""
        for anchor in self.anchors:
            if anchor.waypoint_index == waypoint_index:
                return anchor
        return None
    
    def _sort_anchors(self):
        """Sort anchors by waypoint index"""
        self.anchors.sort(key=lambda a: a.waypoint_index)
    
    def validate_anchors(self) -> Tuple[bool, str]:
        """
        Validate that anchors are in correct order.
        Photo indices must increase along the path.
        
        Returns:
            (is_valid, error_message)
        """
        self._sort_anchors()
        
        for i in range(1, len(self.anchors)):
            prev = self.anchors[i - 1]
            curr = self.anchors[i]
            
            if curr.photo_index <= prev.photo_index:
                return (False, 
                    f"Photo order conflict: waypoint {curr.waypoint_index} has photo {curr.photo_index} "
                    f"but previous waypoint {prev.waypoint_index} has photo {prev.photo_index}. "
                    f"Photos must be in increasing order along path.")
        
        return (True, "")
    
    def interpolate_all_photos(self) -> List[PhotoAssignment]:
        """
        Interpolate positions for all photos based on anchor points.
        
        Photos between anchors are distributed evenly by distance.
        """
        valid, error = self.validate_anchors()
        if not valid:
            raise ValueError(error)
        
        self._sort_anchors()
        assignments: List[PhotoAssignment] = []
        
        # Process each segment between anchors
        for i in range(len(self.anchors) - 1):
            start_anchor = self.anchors[i]
            end_anchor = self.anchors[i + 1]
            
            # Photos in this segment (inclusive of start, exclusive of end except last segment)
            start_photo = start_anchor.photo_index
            end_photo = end_anchor.photo_index
            
            # Include end photo only in last segment
            is_last_segment = (i == len(self.anchors) - 2)
            
            segment_assignments = self._interpolate_segment(
                start_anchor, end_anchor,
                include_end=is_last_segment
            )
            
            # Avoid duplicates
            if assignments and segment_assignments:
                if segment_assignments[0].photo_index == assignments[-1].photo_index:
                    segment_assignments = segment_assignments[1:]
            
            assignments.extend(segment_assignments)
        
        return assignments
    
    def _interpolate_segment(self, start: AnchorPoint, end: AnchorPoint,
                            include_end: bool = False) -> List[PhotoAssignment]:
        """Interpolate photos within a segment between two anchors"""
        assignments = []
        
        num_photos_in_segment = end.photo_index - start.photo_index
        if include_end:
            num_photos_in_segment += 1
        
        if num_photos_in_segment <= 0:
            return assignments
        
        segment_distance = end.distance_from_start - start.distance_from_start
        
        for i in range(num_photos_in_segment):
            photo_idx = start.photo_index + i
            
            # Calculate position along segment
            if num_photos_in_segment == 1:
                t = 0.0
            else:
                t = i / (num_photos_in_segment - 1) if include_end else i / num_photos_in_segment
            
            distance = start.distance_from_start + t * segment_distance
            
            # Get GPS from interpolator
            lat, lon, heading = self.interpolator._interpolate_point(distance)
            
            is_anchor = (photo_idx == start.photo_index or 
                        (include_end and photo_idx == end.photo_index))
            
            assignments.append(PhotoAssignment(
                photo_index=photo_idx,
                lat=lat,
                lon=lon,
                heading=heading,
                distance_from_start=distance,
                is_anchor=is_anchor
            ))
        
        return assignments
    
    def get_estimated_photo_at_waypoint(self, waypoint_index: int) -> int:
        """
        Estimate which photo would be at a given waypoint 
        based on current anchor configuration.
        """
        if waypoint_index < 0 or waypoint_index >= len(self.path_points):
            return 0
        
        target_distance = self.waypoint_distances[waypoint_index]
        
        # Find surrounding anchors
        self._sort_anchors()
        
        prev_anchor = self.anchors[0]
        next_anchor = self.anchors[-1]
        
        for i, anchor in enumerate(self.anchors):
            if anchor.distance_from_start <= target_distance:
                prev_anchor = anchor
            if anchor.distance_from_start >= target_distance:
                next_anchor = anchor
                break
        
        # Interpolate
        if prev_anchor == next_anchor:
            return prev_anchor.photo_index
        
        segment_distance = next_anchor.distance_from_start - prev_anchor.distance_from_start
        if segment_distance == 0:
            return prev_anchor.photo_index
        
        t = (target_distance - prev_anchor.distance_from_start) / segment_distance
        
        photo_range = next_anchor.photo_index - prev_anchor.photo_index
        estimated_photo = prev_anchor.photo_index + int(t * photo_range)
        
        return max(0, min(self.num_photos - 1, estimated_photo))
    
    def get_waypoint_info(self, waypoint_index: int) -> dict:
        """Get information about a waypoint for UI display"""
        if waypoint_index < 0 or waypoint_index >= len(self.path_points):
            return {}
        
        wp = self.path_points[waypoint_index]
        anchor = self.get_anchor_at_waypoint(waypoint_index)
        estimated_photo = self.get_estimated_photo_at_waypoint(waypoint_index)
        
        return {
            'waypoint_index': waypoint_index,
            'lat': wp.lat,
            'lon': wp.lon,
            'distance_from_start': self.waypoint_distances[waypoint_index],
            'has_anchor': anchor is not None,
            'anchor_photo': anchor.photo_index if anchor else None,
            'estimated_photo': estimated_photo,
            'is_start': waypoint_index == 0,
            'is_end': waypoint_index == len(self.path_points) - 1
        }
    
    def save_anchors(self, filepath: str):
        """Save anchor configuration to JSON"""
        data = {
            'num_photos': self.num_photos,
            'num_waypoints': len(self.path_points),
            'anchors': [a.to_dict() for a in self.anchors]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_anchors(self, filepath: str):
        """Load anchor configuration from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if data['num_photos'] != self.num_photos:
            raise ValueError(f"Anchor file has {data['num_photos']} photos, but current set has {self.num_photos}")
        
        self.anchors = [AnchorPoint.from_dict(a) for a in data['anchors']]
        self._sort_anchors()
    
    def get_speed_info(self) -> List[dict]:
        """Get walking speed information for each segment"""
        self._sort_anchors()
        speeds = []
        
        for i in range(len(self.anchors) - 1):
            start = self.anchors[i]
            end = self.anchors[i + 1]
            
            distance = end.distance_from_start - start.distance_from_start
            num_photos = end.photo_index - start.photo_index
            
            if num_photos > 0:
                meters_per_photo = distance / num_photos
            else:
                meters_per_photo = 0
            
            speeds.append({
                'segment': i,
                'from_waypoint': start.waypoint_index,
                'to_waypoint': end.waypoint_index,
                'distance_m': distance,
                'num_photos': num_photos,
                'meters_per_photo': meters_per_photo,
                'relative_speed': 'normal'  # Will be calculated below
            })
        
        # Calculate relative speed
        if speeds:
            avg_mpp = sum(s['meters_per_photo'] for s in speeds) / len(speeds)
            for s in speeds:
                if avg_mpp > 0:
                    ratio = s['meters_per_photo'] / avg_mpp
                    if ratio < 0.7:
                        s['relative_speed'] = 'slow'
                    elif ratio > 1.3:
                        s['relative_speed'] = 'fast'
                    else:
                        s['relative_speed'] = 'normal'
        
        return speeds

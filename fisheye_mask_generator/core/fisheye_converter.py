"""
Fisheye Converter
Converts between dual fisheye images (185° FOV) and equirectangular 360° format.

Based on max2sphere.py geometry for GoPro Max fisheye images.
"""

import numpy as np
import cv2
from typing import Tuple, Optional, List
import math
import os


class FisheyeConverter:
    """
    Converts between dual fisheye images and equirectangular 360° format.
    
    Supports:
    - Converting front + back fisheye images to equirectangular
    - Converting equirectangular mask back to front + back fisheye masks
    
    The fisheye images are assumed to be 185° FOV equidistant projection,
    as produced by max2sphere.py from GoPro Max footage.
    """
    
    FOV_DEGREES = 185.0
    FOV_HALF = math.radians(185.0 / 2.0)  # 92.5° in radians
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the fisheye converter.
        
        Args:
            cache_dir: Directory to cache lookup tables. If None, uses current directory.
        """
        self.cache_dir = cache_dir or os.path.dirname(__file__)
        self._fisheye_to_equirect_lut = None
        self._equirect_to_fisheye_lut = None
        self._current_fisheye_size = None
        self._current_equirect_size = None
    
    def fisheye_pair_to_equirect(
        self,
        front_fisheye: np.ndarray,
        back_fisheye: np.ndarray,
        equirect_width: Optional[int] = None
    ) -> np.ndarray:
        """
        Convert a pair of fisheye images to equirectangular format.
        
        Args:
            front_fisheye: Front lens fisheye image (H, W, C)
            back_fisheye: Back lens fisheye image (H, W, C)
            equirect_width: Width of output equirectangular image.
                           Height will be width/2. If None, uses 2x fisheye width.
                           
        Returns:
            Equirectangular image (H, W, C)
        """
        fisheye_h, fisheye_w = front_fisheye.shape[:2]
        
        if equirect_width is None:
            equirect_width = fisheye_w * 2
        equirect_height = equirect_width // 2
        
        # Get or build lookup table
        x_map, y_map, lens_map = self._get_fisheye_to_equirect_lut(
            fisheye_w, fisheye_h, equirect_width, equirect_height
        )
        
        # Create output image
        channels = front_fisheye.shape[2] if front_fisheye.ndim == 3 else 1
        equirect = np.zeros((equirect_height, equirect_width, channels), dtype=front_fisheye.dtype)
        
        # Sample from both fisheye images based on lens map
        front_mask = lens_map == 0
        back_mask = lens_map == 1
        
        # Use cv2.remap for efficient sampling
        front_sampled = cv2.remap(
            front_fisheye, x_map, y_map,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0
        )
        back_sampled = cv2.remap(
            back_fisheye, x_map, y_map,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0
        )
        
        # Combine based on lens map
        if channels > 1:
            front_mask_3d = np.repeat(front_mask[:, :, np.newaxis], channels, axis=2)
            back_mask_3d = np.repeat(back_mask[:, :, np.newaxis], channels, axis=2)
            equirect = np.where(front_mask_3d, front_sampled, equirect)
            equirect = np.where(back_mask_3d, back_sampled, equirect)
        else:
            equirect = np.where(front_mask, front_sampled, equirect)
            equirect = np.where(back_mask, back_sampled, equirect)
        
        return equirect
    
    def equirect_to_fisheye_pair(
        self,
        equirect: np.ndarray,
        fisheye_size: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert an equirectangular image/mask to a pair of fisheye images.
        
        Args:
            equirect: Equirectangular image or mask (H, W) or (H, W, C)
            fisheye_size: Size of output fisheye images (square). 
                         If None, uses equirect_width / 2.
                         
        Returns:
            Tuple of (front_fisheye, back_fisheye)
        """
        equirect_h, equirect_w = equirect.shape[:2]
        
        if fisheye_size is None:
            fisheye_size = equirect_w // 2
        
        # Get or build lookup table
        front_x_map, front_y_map, back_x_map, back_y_map, front_valid, back_valid = \
            self._get_equirect_to_fisheye_lut(equirect_w, equirect_h, fisheye_size)
        
        # Sample from equirectangular for each fisheye
        front_fisheye = cv2.remap(
            equirect, front_x_map, front_y_map,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0
        )
        back_fisheye = cv2.remap(
            equirect, back_x_map, back_y_map,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0
        )
        
        # Apply circular mask (outside fisheye circle should be black)
        if equirect.ndim == 2:
            front_fisheye = np.where(front_valid, front_fisheye, 0)
            back_fisheye = np.where(back_valid, back_fisheye, 0)
        else:
            channels = equirect.shape[2]
            front_valid_3d = np.repeat(front_valid[:, :, np.newaxis], channels, axis=2)
            back_valid_3d = np.repeat(back_valid[:, :, np.newaxis], channels, axis=2)
            front_fisheye = np.where(front_valid_3d, front_fisheye, 0)
            back_fisheye = np.where(back_valid_3d, back_fisheye, 0)
        
        return front_fisheye, back_fisheye
    
    def _get_fisheye_to_equirect_lut(
        self,
        fisheye_w: int,
        fisheye_h: int,
        equirect_w: int,
        equirect_h: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get or build lookup table for fisheye to equirectangular conversion.
        
        Returns:
            Tuple of (x_map, y_map, lens_map) where lens_map indicates
            which lens (0=front, 1=back) to sample from.
        """
        key = (fisheye_w, fisheye_h, equirect_w, equirect_h)
        if self._fisheye_to_equirect_lut is not None and self._current_fisheye_size == key:
            return self._fisheye_to_equirect_lut
        
        cache_path = os.path.join(
            self.cache_dir,
            f"fisheye_to_equirect_lut_{fisheye_w}x{fisheye_h}_to_{equirect_w}x{equirect_h}.npz"
        )
        
        if os.path.exists(cache_path):
            data = np.load(cache_path)
            self._fisheye_to_equirect_lut = (data['x_map'], data['y_map'], data['lens_map'])
            self._current_fisheye_size = key
            return self._fisheye_to_equirect_lut
        
        print(f"Building fisheye-to-equirect lookup table ({equirect_w}x{equirect_h})...")
        
        # Create equirectangular coordinate grid
        # Longitude: -π to π (left to right)
        # Latitude: π/2 to -π/2 (top to bottom)
        lon = np.linspace(-np.pi, np.pi, equirect_w, endpoint=False)
        lat = np.linspace(np.pi/2, -np.pi/2, equirect_h, endpoint=False)
        lon_grid, lat_grid = np.meshgrid(lon, lat)
        
        # Convert spherical to 3D cartesian
        # World axes: +X = right, +Y = front, +Z = up
        cos_lat = np.cos(lat_grid)
        wx = cos_lat * np.sin(lon_grid)  # X
        wy = cos_lat * np.cos(lon_grid)  # Y (front direction)
        wz = np.sin(lat_grid)            # Z (up)
        
        # Determine which lens to use based on Y (front/back direction)
        # Front lens: points in +Y direction (wy > 0)
        # Back lens: points in -Y direction (wy < 0)
        lens_map = (wy < 0).astype(np.int32)
        
        # Calculate fisheye coordinates for both lenses
        x_map = np.zeros((equirect_h, equirect_w), dtype=np.float32)
        y_map = np.zeros((equirect_h, equirect_w), dtype=np.float32)
        
        for lens in [0, 1]:
            mask = lens_map == lens
            
            if lens == 0:
                # Front lens - optical axis along +Y
                # Project onto plane perpendicular to +Y
                local_x = wx[mask]
                local_y = wz[mask]
                local_z = wy[mask]  # Distance along optical axis
            else:
                # Back lens - optical axis along -Y
                local_x = -wx[mask]  # Mirror X
                local_y = wz[mask]
                local_z = -wy[mask]  # Flip optical axis
            
            # Calculate angle from optical axis (theta)
            r_xy = np.sqrt(local_x**2 + local_y**2)
            theta = np.arctan2(r_xy, local_z)
            
            # Equidistant fisheye projection: r = theta / FOV_HALF
            # Normalized radius in fisheye image (0 to 1)
            r_fisheye = theta / self.FOV_HALF
            
            # Direction in fisheye image plane
            phi = np.arctan2(local_y, local_x)
            
            # Convert to fisheye pixel coordinates
            # Center of fisheye is at (fisheye_w/2, fisheye_h/2)
            # Radius 1.0 corresponds to min(fisheye_w, fisheye_h) / 2
            radius_pixels = min(fisheye_w, fisheye_h) / 2
            
            fx = fisheye_w / 2 + r_fisheye * radius_pixels * np.cos(phi)
            fy = fisheye_h / 2 - r_fisheye * radius_pixels * np.sin(phi)  # Flip Y for image coords
            
            x_map[mask] = fx
            y_map[mask] = fy
        
        # Cache the lookup table
        np.savez_compressed(cache_path, x_map=x_map, y_map=y_map, lens_map=lens_map)
        
        self._fisheye_to_equirect_lut = (x_map, y_map, lens_map)
        self._current_fisheye_size = key
        
        return self._fisheye_to_equirect_lut
    
    def _get_equirect_to_fisheye_lut(
        self,
        equirect_w: int,
        equirect_h: int,
        fisheye_size: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Get or build lookup table for equirectangular to fisheye conversion.
        
        Returns:
            Tuple of (front_x_map, front_y_map, back_x_map, back_y_map, front_valid, back_valid)
        """
        key = (equirect_w, equirect_h, fisheye_size)
        if self._equirect_to_fisheye_lut is not None and self._current_equirect_size == key:
            return self._equirect_to_fisheye_lut
        
        cache_path = os.path.join(
            self.cache_dir,
            f"equirect_to_fisheye_lut_{equirect_w}x{equirect_h}_to_{fisheye_size}.npz"
        )
        
        if os.path.exists(cache_path):
            data = np.load(cache_path)
            self._equirect_to_fisheye_lut = (
                data['front_x_map'], data['front_y_map'],
                data['back_x_map'], data['back_y_map'],
                data['front_valid'], data['back_valid']
            )
            self._current_equirect_size = key
            return self._equirect_to_fisheye_lut
        
        print(f"Building equirect-to-fisheye lookup table ({fisheye_size}x{fisheye_size})...")
        
        # Create fisheye coordinate grid (normalized -1 to 1)
        x = np.linspace(-1, 1, fisheye_size)
        y = np.linspace(-1, 1, fisheye_size)
        x_grid, y_grid = np.meshgrid(x, y)
        
        # Radius from center
        r = np.sqrt(x_grid**2 + y_grid**2)
        
        # Valid region is within the fisheye circle
        valid = r <= 1.0
        
        # Equidistant fisheye: theta = r * FOV_HALF
        theta = r * self.FOV_HALF
        
        # Direction in fisheye image plane
        safe_r = np.where(r > 1e-10, r, 1.0)
        dx_hat = np.where(r > 1e-10, x_grid / safe_r, 0.0)
        dy_hat = np.where(r > 1e-10, -y_grid / safe_r, 0.0)  # Flip Y for image coords
        
        sin_t = np.sin(theta)
        cos_t = np.cos(theta)
        
        # Build maps for both lenses
        front_x_map = np.zeros((fisheye_size, fisheye_size), dtype=np.float32)
        front_y_map = np.zeros((fisheye_size, fisheye_size), dtype=np.float32)
        back_x_map = np.zeros((fisheye_size, fisheye_size), dtype=np.float32)
        back_y_map = np.zeros((fisheye_size, fisheye_size), dtype=np.float32)
        
        # Front lens - optical axis along +Y
        # image right (+x) → world +X
        # image up (-y) → world +Z
        wx_front = sin_t * dx_hat
        wy_front = cos_t
        wz_front = sin_t * dy_hat
        
        lon_front = np.arctan2(wx_front, wy_front)
        lat_front = np.arctan2(wz_front, np.sqrt(wx_front**2 + wy_front**2))
        
        # Convert to equirectangular pixel coordinates
        front_x_map = ((lon_front / np.pi + 1) / 2 * equirect_w).astype(np.float32)
        front_y_map = ((1 - lat_front / (np.pi / 2)) / 2 * equirect_h).astype(np.float32)
        
        # Back lens - optical axis along -Y
        # image right (+x) → world -X (mirrored)
        # image up (-y) → world +Z
        wx_back = -sin_t * dx_hat
        wy_back = -cos_t
        wz_back = sin_t * dy_hat
        
        lon_back = np.arctan2(wx_back, wy_back)
        lat_back = np.arctan2(wz_back, np.sqrt(wx_back**2 + wy_back**2))
        
        back_x_map = ((lon_back / np.pi + 1) / 2 * equirect_w).astype(np.float32)
        back_y_map = ((1 - lat_back / (np.pi / 2)) / 2 * equirect_h).astype(np.float32)
        
        # Cache the lookup table
        np.savez_compressed(
            cache_path,
            front_x_map=front_x_map, front_y_map=front_y_map,
            back_x_map=back_x_map, back_y_map=back_y_map,
            front_valid=valid, back_valid=valid
        )
        
        self._equirect_to_fisheye_lut = (
            front_x_map, front_y_map, back_x_map, back_y_map, valid, valid
        )
        self._current_equirect_size = key
        
        return self._equirect_to_fisheye_lut


def find_fisheye_pair(front_path: str) -> Optional[str]:
    """
    Given a front fisheye image path, find the corresponding back fisheye image.
    
    Naming conventions supported:
    - frame0001_fisheye_front.jpg → frame0001_fisheye_back.jpg
    - image_front.png → image_back.png
    - lens0_0001.jpg → lens1_0001.jpg
    
    Args:
        front_path: Path to front fisheye image
        
    Returns:
        Path to back fisheye image if found, None otherwise
    """
    import re
    from pathlib import Path
    
    path = Path(front_path)
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    
    # Try different naming patterns
    patterns = [
        (r'(.*)_front$', r'\1_back'),           # name_front → name_back
        (r'(.*)_fisheye_front$', r'\1_fisheye_back'),  # name_fisheye_front → name_fisheye_back
        (r'^lens0_(.*)$', r'lens1_\1'),          # lens0_name → lens1_name
        (r'^front_(.*)$', r'back_\1'),           # front_name → back_name
        (r'(.*)_0$', r'\1_1'),                   # name_0 → name_1
    ]
    
    for pattern, replacement in patterns:
        match = re.match(pattern, stem)
        if match:
            back_stem = re.sub(pattern, replacement, stem)
            back_path = parent / f"{back_stem}{suffix}"
            if back_path.exists():
                return str(back_path)
    
    return None


def find_back_for_front(front_path: str) -> Optional[str]:
    """Alias for find_fisheye_pair for clarity."""
    return find_fisheye_pair(front_path)


def get_mask_output_paths(front_path: str, back_path: str) -> Tuple[str, str]:
    """
    Get the output mask paths for a fisheye pair.
    
    Args:
        front_path: Path to front fisheye image
        back_path: Path to back fisheye image
        
    Returns:
        Tuple of (front_mask_path, back_mask_path)
    """
    from pathlib import Path
    
    front_p = Path(front_path)
    back_p = Path(back_path)
    
    front_mask = front_p.parent / f"{front_p.stem}_mask{front_p.suffix}"
    back_mask = back_p.parent / f"{back_p.stem}_mask{back_p.suffix}"
    
    return str(front_mask), str(back_mask)


def extract_frame_number(filename: str) -> Optional[int]:
    """
    Extract the frame number from a filename by finding digits at the end.
    
    Examples:
        "000001.jpg" → 1
        "lens1_000001.jpg" → 1
        "frame_0042.png" → 42
        "image123.jpg" → 123
        
    Args:
        filename: Filename (with or without path)
        
    Returns:
        Frame number as integer, or None if no number found
    """
    import re
    from pathlib import Path
    
    stem = Path(filename).stem
    
    # Find all sequences of digits in the filename
    matches = re.findall(r'\d+', stem)
    
    if not matches:
        return None
    
    # Use the last sequence of digits as the frame number
    return int(matches[-1])


def find_pairs_from_two_folders(
    front_folder: str,
    back_folder: str
) -> List[Tuple[str, str]]:
    """
    Find matching fisheye pairs from two separate folders by matching frame numbers.
    
    The pairing is done by extracting the numeric suffix from filenames.
    For example:
        front_folder/000001.jpg pairs with back_folder/lens1_000001.jpg
        front_folder/frame_0042.png pairs with back_folder/back_0042.png
    
    Args:
        front_folder: Path to folder containing front fisheye images
        back_folder: Path to folder containing back fisheye images
        
    Returns:
        List of (front_path, back_path) tuples sorted by frame number
    """
    from pathlib import Path
    
    front_dir = Path(front_folder)
    back_dir = Path(back_folder)
    
    if not front_dir.exists() or not front_dir.is_dir():
        raise ValueError(f"Front folder not found: {front_folder}")
    if not back_dir.exists() or not back_dir.is_dir():
        raise ValueError(f"Back folder not found: {back_folder}")
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
    
    # Build index of back images by frame number
    back_by_number = {}
    for f in back_dir.iterdir():
        if not f.is_file() or f.suffix.lower() not in image_extensions:
            continue
        if '_mask' in f.stem:
            continue
        
        frame_num = extract_frame_number(f.name)
        if frame_num is not None:
            back_by_number[frame_num] = str(f)
    
    # Find matching pairs
    pairs = []
    for f in front_dir.iterdir():
        if not f.is_file() or f.suffix.lower() not in image_extensions:
            continue
        if '_mask' in f.stem:
            continue
        
        frame_num = extract_frame_number(f.name)
        if frame_num is not None and frame_num in back_by_number:
            pairs.append((str(f), back_by_number[frame_num], frame_num))
    
    # Sort by frame number and return without the frame number
    pairs.sort(key=lambda x: x[2])
    return [(front, back) for front, back, _ in pairs]


def get_mask_output_paths_two_folders(
    front_path: str,
    back_path: str,
    output_folder: Optional[str] = None
) -> Tuple[str, str]:
    """
    Get output mask paths, optionally placing them in a separate output folder.
    
    Args:
        front_path: Path to front fisheye image
        back_path: Path to back fisheye image
        output_folder: Optional output folder. If None, masks are saved alongside originals.
        
    Returns:
        Tuple of (front_mask_path, back_mask_path)
    """
    from pathlib import Path
    
    front_p = Path(front_path)
    back_p = Path(back_path)
    
    if output_folder:
        out_dir = Path(output_folder)
        out_dir.mkdir(parents=True, exist_ok=True)
        front_mask = out_dir / f"{front_p.stem}_mask{front_p.suffix}"
        back_mask = out_dir / f"{back_p.stem}_mask{back_p.suffix}"
    else:
        front_mask = front_p.parent / f"{front_p.stem}_mask{front_p.suffix}"
        back_mask = back_p.parent / f"{back_p.stem}_mask{back_p.suffix}"
    
    return str(front_mask), str(back_mask)

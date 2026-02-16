"""
Perspective Projector
Converts between equirectangular and perspective projections for 360 images.
Uses py360convert library with custom enhancements.
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import cv2


@dataclass
class PerspectiveView:
    """Represents a perspective view extracted from an equirectangular image."""
    image: np.ndarray
    yaw: float  # Horizontal angle in degrees (-180 to 180)
    pitch: float  # Vertical angle in degrees (-90 to 90)
    fov: float  # Field of view in degrees
    width: int
    height: int
    
    # Cached mapping arrays for projecting back to equirectangular
    equirect_x_map: Optional[np.ndarray] = None
    equirect_y_map: Optional[np.ndarray] = None


class PerspectiveProjector:
    """
    Handles conversion between equirectangular and perspective projections.
    
    Strategy:
    - Extract multiple overlapping perspective views around the horizon
    - Skip extreme up/down views where detection is less reliable
    - Provide coordinate mapping for projecting masks back to equirectangular
    """
    
    def __init__(
        self,
        num_views: int = 8,
        fov: float = 90.0,
        view_size: Tuple[int, int] = (640, 640),
        pitch_range: Tuple[float, float] = (-45.0, 45.0),
        pitch_steps: int = 1,
        include_downward_view: bool = False
    ):
        """
        Initialize the perspective projector.
        
        Args:
            num_views: Number of horizontal views (evenly distributed around 360°)
            fov: Field of view in degrees for each perspective view
            view_size: (width, height) of each perspective view
            pitch_range: (min, max) pitch angles in degrees to sample
            pitch_steps: Number of pitch angles to sample (1 = horizon only)
        """
        self.num_views = num_views
        self.fov = fov
        self.view_size = view_size
        self.pitch_range = pitch_range
        self.pitch_steps = pitch_steps
        self.include_downward_view = include_downward_view
        
        # Calculate yaw angles for horizontal views
        self.yaw_angles = np.linspace(-180, 180, num_views, endpoint=False)
        
        # Calculate pitch angles
        if pitch_steps == 1:
            self.pitch_angles = [0.0]  # Horizon only
        else:
            self.pitch_angles = np.linspace(
                pitch_range[0], pitch_range[1], pitch_steps
            ).tolist()
    
    def extract_perspective_views(
        self, 
        equirect_img: np.ndarray
    ) -> List[PerspectiveView]:
        """
        Extract multiple perspective views from an equirectangular image.
        
        Args:
            equirect_img: Equirectangular image as numpy array (H, W, C)
            
        Returns:
            List of PerspectiveView objects
        """
        views = []
        h, w = equirect_img.shape[:2]
        view_w, view_h = self.view_size
        
        for pitch in self.pitch_angles:
            for yaw in self.yaw_angles:
                # Extract perspective view
                persp_img, x_map, y_map = self._equirect_to_perspective(
                    equirect_img, yaw, pitch, self.fov, view_w, view_h
                )
                
                view = PerspectiveView(
                    image=persp_img,
                    yaw=yaw,
                    pitch=pitch,
                    fov=self.fov,
                    width=view_w,
                    height=view_h,
                    equirect_x_map=x_map,
                    equirect_y_map=y_map
                )
                views.append(view)
        
        # Add downward-facing view if enabled
        if self.include_downward_view:
            persp_img, x_map, y_map = self._equirect_to_perspective(
                equirect_img, 180.0, -70.0, self.fov, view_w, view_h
            )
            
            view = PerspectiveView(
                image=persp_img,
                yaw=180.0,
                pitch=-70.0,
                fov=self.fov,
                width=view_w,
                height=view_h,
                equirect_x_map=x_map,
                equirect_y_map=y_map
            )
            views.append(view)
        
        return views
    
    def _equirect_to_perspective(
        self,
        equirect_img: np.ndarray,
        yaw_deg: float,
        pitch_deg: float,
        fov_deg: float,
        out_w: int,
        out_h: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Extract a perspective view from an equirectangular image.
        
        Also returns the coordinate mapping from perspective to equirectangular
        for projecting masks back.
        
        Args:
            equirect_img: Source equirectangular image (H, W, C)
            yaw_deg: Horizontal rotation in degrees (-180 to 180)
            pitch_deg: Vertical rotation in degrees (-90 to 90)
            fov_deg: Field of view in degrees
            out_w: Output width
            out_h: Output height
            
        Returns:
            Tuple of (perspective_image, x_map, y_map) where x_map and y_map
            contain the equirectangular coordinates for each perspective pixel
        """
        try:
            import py360convert
            
            # Use py360convert's e2p function
            persp_img = py360convert.e2p(
                equirect_img,
                fov_deg=(fov_deg, fov_deg * out_h / out_w),
                u_deg=yaw_deg,
                v_deg=pitch_deg,
                out_hw=(out_h, out_w),
                mode='bilinear'
            )
            
            # Generate coordinate mapping
            x_map, y_map = self._generate_equirect_mapping(
                equirect_img.shape[:2], yaw_deg, pitch_deg, fov_deg, out_w, out_h
            )
            
            return persp_img, x_map, y_map
            
        except ImportError:
            # Fallback to manual implementation
            return self._equirect_to_perspective_manual(
                equirect_img, yaw_deg, pitch_deg, fov_deg, out_w, out_h
            )
    
    def _equirect_to_perspective_manual(
        self,
        equirect_img: np.ndarray,
        yaw_deg: float,
        pitch_deg: float,
        fov_deg: float,
        out_w: int,
        out_h: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Manual implementation of equirectangular to perspective projection.
        """
        eq_h, eq_w = equirect_img.shape[:2]
        
        # Convert angles to radians
        yaw = np.radians(yaw_deg)
        pitch = np.radians(-pitch_deg)  # Negate to match py360convert convention (+ = up)
        fov = np.radians(fov_deg)
        
        # Calculate focal length
        f = out_w / (2 * np.tan(fov / 2))
        
        # Create coordinate grid for output image
        x = np.arange(out_w) - out_w / 2
        y = out_h / 2 - np.arange(out_h)  # Flip y: image top = positive y (up)
        x, y = np.meshgrid(x, y)
        
        # 3D coordinates on the image plane
        z = np.full_like(x, f, dtype=np.float32)
        
        # Normalize to unit sphere
        norm = np.sqrt(x**2 + y**2 + z**2)
        x = x / norm
        y = y / norm
        z = z / norm
        
        # Rotation matrices
        # Pitch rotation (around X axis)
        cos_p, sin_p = np.cos(pitch), np.sin(pitch)
        y_rot = y * cos_p - z * sin_p
        z_rot = y * sin_p + z * cos_p
        y, z = y_rot, z_rot
        
        # Yaw rotation (around Y axis)
        cos_y, sin_y = np.cos(yaw), np.sin(yaw)
        x_rot = x * cos_y + z * sin_y
        z_rot = -x * sin_y + z * cos_y
        x, z = x_rot, z_rot
        
        # Convert 3D coordinates to spherical (lon, lat)
        lon = np.arctan2(x, z)
        lat = np.arcsin(np.clip(y, -1, 1))
        
        # Convert to equirectangular pixel coordinates
        eq_x = (lon / np.pi + 1) / 2 * eq_w
        eq_y = (-lat / (np.pi / 2) + 1) / 2 * eq_h
        
        # Store mapping
        x_map = eq_x.astype(np.float32)
        y_map = eq_y.astype(np.float32)
        
        # Sample from equirectangular image
        persp_img = cv2.remap(
            equirect_img, 
            x_map, 
            y_map,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_WRAP
        )
        
        return persp_img, x_map, y_map
    
    def _generate_equirect_mapping(
        self,
        equirect_shape: Tuple[int, int],
        yaw_deg: float,
        pitch_deg: float,
        fov_deg: float,
        out_w: int,
        out_h: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate coordinate mapping from perspective to equirectangular.
        
        Returns arrays (x_map, y_map) where each element contains the 
        equirectangular (x, y) coordinate that maps to that perspective pixel.
        
        Note: For extreme pitch angles (near ±90°), the mapping becomes 
        challenging at the poles where longitude is undefined.
        """
        eq_h, eq_w = equirect_shape
        
        # Convert angles to radians
        yaw = np.radians(yaw_deg)
        pitch = np.radians(-pitch_deg)  # Negate to match py360convert convention (+ = up)
        fov = np.radians(fov_deg)
        
        # Calculate focal length
        f = out_w / (2 * np.tan(fov / 2))
        
        # Create coordinate grid for output image
        x = np.arange(out_w) - out_w / 2
        y = out_h / 2 - np.arange(out_h)  # Flip y: image top = positive y (up)
        x, y = np.meshgrid(x, y)
        
        # 3D coordinates on the image plane
        z = np.full_like(x, f, dtype=np.float32)
        
        # Normalize to unit sphere
        norm = np.sqrt(x**2 + y**2 + z**2)
        x = x / norm
        y = y / norm
        z = z / norm
        
        # Rotation matrices
        # Pitch rotation (around X axis)
        cos_p, sin_p = np.cos(pitch), np.sin(pitch)
        y_rot = y * cos_p - z * sin_p
        z_rot = y * sin_p + z * cos_p
        y, z = y_rot, z_rot
        
        # Yaw rotation (around Y axis)
        cos_y, sin_y = np.cos(yaw), np.sin(yaw)
        x_rot = x * cos_y + z * sin_y
        z_rot = -x * sin_y + z * cos_y
        x, z = x_rot, z_rot
        
        # Convert 3D coordinates to spherical (lon, lat)
        lon = np.arctan2(x, z)
        lat = np.arcsin(np.clip(y, -1, 1))
        
        # Convert to equirectangular pixel coordinates
        eq_x = (lon / np.pi + 1) / 2 * eq_w
        eq_y = (-lat / (np.pi / 2) + 1) / 2 * eq_h
        
        return eq_x.astype(np.float32), eq_y.astype(np.float32)
    
    def project_mask_to_equirect(
        self,
        mask: np.ndarray,
        view: PerspectiveView,
        equirect_shape: Tuple[int, int]
    ) -> np.ndarray:
        """
        Project a mask from perspective view back to equirectangular.
        
        Args:
            mask: Binary or soft mask in perspective space (H, W) or (H, W, 1)
            view: The PerspectiveView the mask was generated for
            equirect_shape: (height, width) of the output equirectangular image
            
        Returns:
            Mask projected to equirectangular coordinates (H, W)
        """
        if mask.ndim == 3:
            mask = mask[:, :, 0]
        
        eq_h, eq_w = equirect_shape
        
        # Create output mask
        equirect_mask = np.zeros((eq_h, eq_w), dtype=np.float32)
        
        # Use the pre-computed coordinate mapping
        if view.equirect_x_map is not None and view.equirect_y_map is not None:
            x_map = view.equirect_x_map
            y_map = view.equirect_y_map
            
            # Clip coordinates to valid range
            x_idx = np.clip(x_map, 0, eq_w - 1).astype(np.int32)
            y_idx = np.clip(y_map, 0, eq_h - 1).astype(np.int32)
            
            # Map mask values to equirectangular
            for py in range(mask.shape[0]):
                for px in range(mask.shape[1]):
                    if mask[py, px] > 0:
                        eq_x = x_idx[py, px]
                        eq_y = y_idx[py, px]
                        equirect_mask[eq_y, eq_x] = max(
                            equirect_mask[eq_y, eq_x], 
                            mask[py, px]
                        )
        
        return equirect_mask
    
    def project_mask_to_equirect_vectorized(
        self,
        mask: np.ndarray,
        view: PerspectiveView,
        equirect_shape: Tuple[int, int]
    ) -> np.ndarray:
        """
        Vectorized version of project_mask_to_equirect for better performance.
        
        Args:
            mask: Binary or soft mask in perspective space (H, W) or (H, W, 1)
            view: The PerspectiveView the mask was generated for
            equirect_shape: (height, width) of the output equirectangular image
            
        Returns:
            Mask projected to equirectangular coordinates (H, W)
        """
        if mask.ndim == 3:
            mask = mask[:, :, 0]
        
        eq_h, eq_w = equirect_shape
        
        # Create output mask
        equirect_mask = np.zeros((eq_h, eq_w), dtype=np.float32)
        
        if view.equirect_x_map is None or view.equirect_y_map is None:
            return equirect_mask
        
        # Flatten arrays for vectorized indexing
        x_flat = view.equirect_x_map.flatten()
        y_flat = view.equirect_y_map.flatten()
        mask_flat = mask.flatten()
        
        # Clip to valid range
        x_idx = np.clip(x_flat, 0, eq_w - 1).astype(np.int32)
        y_idx = np.clip(y_flat, 0, eq_h - 1).astype(np.int32)
        
        # Use np.maximum.at for efficient accumulation with max
        np.maximum.at(equirect_mask, (y_idx, x_idx), mask_flat)
        
        return equirect_mask

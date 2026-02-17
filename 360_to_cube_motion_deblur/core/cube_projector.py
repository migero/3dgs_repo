"""
Cube Projector Module
Handles conversion between equirectangular and cubemap formats using py360convert.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import py360convert
    HAS_PY360CONVERT = True
except ImportError:
    HAS_PY360CONVERT = False
    print("Warning: py360convert not found. Install with: pip install py360convert")


class CubeFace(Enum):
    """Cube face identifiers matching py360convert convention."""
    FRONT = 0   # F
    RIGHT = 1   # R
    BACK = 2    # B
    LEFT = 3    # L
    TOP = 4     # U (Up)
    BOTTOM = 5  # D (Down)


@dataclass
class CubeFaces:
    """Container for all 6 cube faces."""
    front: np.ndarray
    right: np.ndarray
    back: np.ndarray
    left: np.ndarray
    top: np.ndarray
    bottom: np.ndarray
    
    def to_dict(self) -> Dict[CubeFace, np.ndarray]:
        """Convert to dictionary keyed by CubeFace enum."""
        return {
            CubeFace.FRONT: self.front,
            CubeFace.RIGHT: self.right,
            CubeFace.BACK: self.back,
            CubeFace.LEFT: self.left,
            CubeFace.TOP: self.top,
            CubeFace.BOTTOM: self.bottom,
        }
    
    def to_list(self) -> list:
        """Convert to list in standard order [F, R, B, L, U, D]."""
        return [self.front, self.right, self.back, self.left, self.top, self.bottom]
    
    @classmethod
    def from_dict(cls, faces: Dict[CubeFace, np.ndarray]) -> 'CubeFaces':
        """Create from dictionary."""
        return cls(
            front=faces[CubeFace.FRONT],
            right=faces[CubeFace.RIGHT],
            back=faces[CubeFace.BACK],
            left=faces[CubeFace.LEFT],
            top=faces[CubeFace.TOP],
            bottom=faces[CubeFace.BOTTOM],
        )
    
    @classmethod
    def from_list(cls, faces: list) -> 'CubeFaces':
        """Create from list in standard order [F, R, B, L, U, D]."""
        return cls(
            front=faces[0],
            right=faces[1],
            back=faces[2],
            left=faces[3],
            top=faces[4],
            bottom=faces[5],
        )


class CubeProjector:
    """
    Handles equirectangular <-> cubemap conversions.
    
    Uses py360convert for efficient projection operations.
    Cube face layout follows the 'dice' format for compatibility.
    """
    
    # Standard resolutions that work well with neural networks (multiples of 8)
    SUPPORTED_RESOLUTIONS = [512, 640, 768, 1024, 1280, 1536, 2048]
    
    def __init__(self, face_size: int = 1024):
        """
        Initialize the cube projector.
        
        Args:
            face_size: Size of each cube face in pixels (should be multiple of 8)
        """
        if not HAS_PY360CONVERT:
            raise ImportError("py360convert is required. Install with: pip install py360convert")
        
        self.face_size = face_size
        
        # Validate face size is a multiple of 8 for neural network compatibility
        if face_size % 8 != 0:
            print(f"Warning: face_size {face_size} is not a multiple of 8. "
                  f"This may cause issues with neural network processing.")
    
    def equirect_to_cube(self, equirect: np.ndarray) -> CubeFaces:
        """
        Convert equirectangular image to 6 cube faces.
        
        Args:
            equirect: Equirectangular image array [H, W, C] (H:W ratio should be 1:2)
        
        Returns:
            CubeFaces object containing all 6 faces
        """
        # py360convert.e2c returns cube faces in 'dice' layout or as dict
        # Using 'dict' mode for easier handling
        cube_dict = py360convert.e2c(
            equirect,
            face_w=self.face_size,
            mode='bilinear',
            cube_format='dict'
        )
        
        # py360convert returns dict with keys: 'F', 'R', 'B', 'L', 'U', 'D'
        return CubeFaces(
            front=cube_dict['F'],
            right=cube_dict['R'],
            back=cube_dict['B'],
            left=cube_dict['L'],
            top=cube_dict['U'],
            bottom=cube_dict['D'],
        )
    
    def cube_to_equirect(
        self, 
        cube_faces: CubeFaces, 
        output_height: Optional[int] = None,
        output_width: Optional[int] = None
    ) -> np.ndarray:
        """
        Convert 6 cube faces back to equirectangular image.
        
        Args:
            cube_faces: CubeFaces object containing all 6 faces
            output_height: Height of output equirectangular image (default: face_size * 2)
            output_width: Width of output equirectangular image (default: face_size * 4)
        
        Returns:
            Equirectangular image array [H, W, C]
        """
        if output_height is None:
            output_height = self.face_size * 2
        if output_width is None:
            output_width = self.face_size * 4
        
        # Convert to dict format for py360convert
        cube_dict = {
            'F': cube_faces.front,
            'R': cube_faces.right,
            'B': cube_faces.back,
            'L': cube_faces.left,
            'U': cube_faces.top,
            'D': cube_faces.bottom,
        }
        
        # py360convert.c2e converts cubemap back to equirectangular
        equirect = py360convert.c2e(
            cube_dict,
            h=output_height,
            w=output_width,
            mode='bilinear',
            cube_format='dict'
        )
        
        return equirect
    
    def create_cubemap_layout(self, cube_faces: CubeFaces, layout: str = 'dice') -> np.ndarray:
        """
        Create a single image with all cube faces arranged in a layout.
        
        Args:
            cube_faces: CubeFaces object containing all 6 faces
            layout: Layout format ('dice' for 3x4, 'horizon' for 1x6, 'stack' for 6x1)
        
        Returns:
            Combined image array
        """
        faces = cube_faces.to_list()
        face_h, face_w = faces[0].shape[:2]
        channels = faces[0].shape[2] if len(faces[0].shape) > 2 else 1
        
        if layout == 'dice':
            # 3x4 layout:
            #     [U]
            # [L][F][R][B]
            #     [D]
            if channels > 1:
                result = np.zeros((face_h * 3, face_w * 4, channels), dtype=faces[0].dtype)
            else:
                result = np.zeros((face_h * 3, face_w * 4), dtype=faces[0].dtype)
            
            # Top row - Up face
            result[0:face_h, face_w:face_w*2] = cube_faces.top
            # Middle row - L, F, R, B
            result[face_h:face_h*2, 0:face_w] = cube_faces.left
            result[face_h:face_h*2, face_w:face_w*2] = cube_faces.front
            result[face_h:face_h*2, face_w*2:face_w*3] = cube_faces.right
            result[face_h:face_h*2, face_w*3:face_w*4] = cube_faces.back
            # Bottom row - Down face
            result[face_h*2:face_h*3, face_w:face_w*2] = cube_faces.bottom
            
        elif layout == 'horizon':
            # 1x6 horizontal layout: [F][R][B][L][U][D]
            if channels > 1:
                result = np.zeros((face_h, face_w * 6, channels), dtype=faces[0].dtype)
            else:
                result = np.zeros((face_h, face_w * 6), dtype=faces[0].dtype)
            
            for i, face in enumerate(faces):
                result[:, i*face_w:(i+1)*face_w] = face
                
        elif layout == 'stack':
            # 6x1 vertical layout
            if channels > 1:
                result = np.zeros((face_h * 6, face_w, channels), dtype=faces[0].dtype)
            else:
                result = np.zeros((face_h * 6, face_w), dtype=faces[0].dtype)
            
            for i, face in enumerate(faces):
                result[i*face_h:(i+1)*face_h, :] = face
        else:
            raise ValueError(f"Unknown layout: {layout}")
        
        return result
    
    @staticmethod
    def get_recommended_face_size(equirect_width: int) -> int:
        """
        Get recommended cube face size based on equirectangular width.
        
        Args:
            equirect_width: Width of equirectangular image
        
        Returns:
            Recommended face size (multiple of 8)
        """
        # For equirect with 2:1 ratio, face size ≈ width / 4
        ideal_size = equirect_width // 4
        
        # Round to nearest multiple of 8
        return ((ideal_size + 4) // 8) * 8
    
    @staticmethod
    def validate_resolution(resolution: int) -> Tuple[bool, str]:
        """
        Validate if a resolution is suitable for neural network processing.
        
        Args:
            resolution: Resolution to validate
        
        Returns:
            Tuple of (is_valid, message)
        """
        if resolution % 8 != 0:
            return False, f"Resolution {resolution} is not a multiple of 8"
        if resolution < 256:
            return False, f"Resolution {resolution} is too small (minimum 256)"
        if resolution > 4096:
            return False, f"Resolution {resolution} is very large, may cause memory issues"
        return True, "OK"

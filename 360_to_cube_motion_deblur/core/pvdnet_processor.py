"""
PVDNet Processor Module
Handles loading and inference with PVDNet for motion deblurring.
"""

import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Add PVDNet to path
PVDNET_PATH = Path(__file__).parent.parent / 'PVDNet'
if str(PVDNET_PATH) not in sys.path:
    sys.path.insert(0, str(PVDNET_PATH))


@dataclass
class PVDNetConfig:
    """Configuration for PVDNet processor."""
    checkpoint_path: str = ""
    device: str = "cuda"
    use_large_model: bool = False
    # PVDNet specific
    PV_ksize: int = 5  # Pixel volume kernel size
    

class PVDNetProcessor:
    """
    Wrapper for PVDNet motion deblurring network.
    
    Handles model loading, frame preparation, and inference.
    Uses recurrent processing with previous frame state for temporal consistency.
    """
    
    # Default checkpoint locations relative to PVDNet folder
    DEFAULT_CHECKPOINTS = {
        'DVD': 'ckpt/PVDNet_DVD.pytorch',
        'nah': 'ckpt/PVDNet_nah.pytorch',
        'large_nah': 'ckpt/PVDNet_large_nah.pytorch',
    }
    
    def __init__(self, config: Optional[PVDNetConfig] = None):
        """
        Initialize PVDNet processor.
        
        Args:
            config: PVDNetConfig object with settings
        """
        self.config = config or PVDNetConfig()
        self.device = torch.device(self.config.device if torch.cuda.is_available() else 'cpu')
        
        self.network = None
        self.bimnet = None
        self._prev_deblurred_states: Dict[str, torch.Tensor] = {}
        
        # Check CUDA availability
        if self.config.device == 'cuda' and not torch.cuda.is_available():
            print("Warning: CUDA not available, falling back to CPU")
            self.device = torch.device('cpu')
    
    def load_model(self, checkpoint_path: Optional[str] = None) -> bool:
        """
        Load PVDNet model from checkpoint.
        
        Args:
            checkpoint_path: Path to .pytorch checkpoint file
        
        Returns:
            True if loading succeeded
        """
        if checkpoint_path is None:
            checkpoint_path = self.config.checkpoint_path
        
        # If relative path, look in PVDNet folder
        if not os.path.isabs(checkpoint_path):
            checkpoint_path = str(PVDNET_PATH / checkpoint_path)
        
        if not os.path.exists(checkpoint_path):
            print(f"Error: Checkpoint not found at {checkpoint_path}")
            return False
        
        try:
            # Import PVDNet architecture
            if self.config.use_large_model:
                from models.archs.PVDNet_large import Network as PVDNetwork
            else:
                from models.archs.PVDNet import Network as PVDNetwork
            from models.archs.liteFlowNet import Network as BIMNetwork
            
            # Initialize networks
            pv_input_dim = self.config.PV_ksize ** 2
            self.network = PVDNetwork(pv_input_dim).to(self.device)
            self.bimnet = BIMNetwork().to(self.device)
            
            # Load checkpoint (use weights_only=False for older checkpoints)
            state_dict = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
            
            # Handle DataParallel wrapped checkpoints
            if any(k.startswith('module.') for k in state_dict.keys()):
                # Remove 'module.' prefix
                new_state_dict = {}
                for k, v in state_dict.items():
                    if k.startswith('module.PVDNet.'):
                        new_state_dict[k.replace('module.PVDNet.', '')] = v
                self.network.load_state_dict(new_state_dict, strict=False)
                
                # Load BIMNet weights
                bimnet_dict = {}
                for k, v in state_dict.items():
                    if k.startswith('module.BIMNet.'):
                        bimnet_dict[k.replace('module.BIMNet.', '')] = v
                if bimnet_dict:
                    self.bimnet.load_state_dict(bimnet_dict, strict=False)
            else:
                # Try loading directly
                self.network.load_state_dict(state_dict, strict=False)
            
            # Also try loading BIMNet from separate file
            bimnet_path = PVDNET_PATH / 'ckpt' / 'BIMNet.pytorch'
            if bimnet_path.exists():
                bimnet_state = torch.load(str(bimnet_path), map_location=self.device, weights_only=False)
                self.bimnet.load_state_dict(bimnet_state, strict=False)
            
            self.network.eval()
            self.bimnet.eval()
            
            print(f"Successfully loaded PVDNet from {checkpoint_path}")
            return True
            
        except Exception as e:
            print(f"Error loading PVDNet: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def reset_state(self, face_id: Optional[str] = None):
        """
        Reset the recurrent state for temporal processing.
        
        Args:
            face_id: Specific face ID to reset, or None for all
        """
        if face_id is None:
            self._prev_deblurred_states.clear()
        elif face_id in self._prev_deblurred_states:
            del self._prev_deblurred_states[face_id]
    
    def _normalize(self, tensor: torch.Tensor) -> torch.Tensor:
        """Normalize tensor to [-1, 1] range for network input."""
        return tensor * 2 - 1
    
    def _denormalize(self, tensor: torch.Tensor) -> torch.Tensor:
        """Denormalize tensor from [-1, 1] to [0, 1] range."""
        return (tensor + 1) / 2
    
    def _prepare_frame(self, frame: np.ndarray) -> torch.Tensor:
        """
        Prepare a frame for network input.
        
        Args:
            frame: numpy array [H, W, C] in range [0, 255] or [0, 1]
        
        Returns:
            torch.Tensor [1, C, H, W] in range [0, 1]
        """
        if frame.dtype == np.uint8:
            frame = frame.astype(np.float32) / 255.0
        
        # Handle grayscale
        if len(frame.shape) == 2:
            frame = np.stack([frame] * 3, axis=-1)
        elif frame.shape[2] == 1:
            frame = np.concatenate([frame] * 3, axis=-1)
        
        # Convert to tensor [C, H, W]
        tensor = torch.from_numpy(frame.transpose(2, 0, 1)).float()
        
        # Add batch dimension
        tensor = tensor.unsqueeze(0)
        
        return tensor.to(self.device)
    
    def _get_pixel_volume(
        self, 
        I_prev_deblurred: torch.Tensor,
        flow: torch.Tensor,
        I_curr: torch.Tensor,
        h: int,
        w: int
    ) -> torch.Tensor:
        """
        Compute pixel volume for PVDNet input.
        Simplified version of get_pixel_volume from PVDNet.
        """
        try:
            from models.pixel_volume import get_pixel_volume
            return get_pixel_volume(I_prev_deblurred, flow, I_curr, h, w)
        except ImportError:
            # Fallback: return zeros (network will still work, just less accurately)
            k = self.config.PV_ksize
            return torch.zeros(1, k * k, h, w, device=self.device)
    
    def process_frame(
        self,
        prev_frame: np.ndarray,
        curr_frame: np.ndarray,
        next_frame: np.ndarray,
        face_id: str = "default"
    ) -> np.ndarray:
        """
        Process a single frame through PVDNet.
        
        Args:
            prev_frame: Previous frame [H, W, C]
            curr_frame: Current frame to deblur [H, W, C]
            next_frame: Next frame [H, W, C]
            face_id: Identifier for maintaining recurrent state
        
        Returns:
            Deblurred frame [H, W, C]
        """
        if self.network is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Prepare inputs
        I_prev = self._prepare_frame(prev_frame)
        I_curr = self._prepare_frame(curr_frame)
        I_next = self._prepare_frame(next_frame)
        
        _, _, h, w = I_curr.size()
        
        # Initialize recurrent state if needed
        if face_id not in self._prev_deblurred_states:
            self._prev_deblurred_states[face_id] = I_prev.clone()
        
        I_prev_deblurred = self._prev_deblurred_states[face_id]
        
        with torch.no_grad():
            # Compute optical flow using BIMNet
            # Need to crop to multiple of 32 for liteflownet
            refine_h = h - h % 32
            refine_w = w - w % 32
            
            I_curr_refined = I_curr[:, :, :refine_h, :refine_w]
            I_prev_refined = I_prev[:, :, :refine_h, :refine_w]
            
            # Normalize for BIMNet
            I_curr_norm = self._normalize(I_curr_refined)
            I_prev_norm = self._normalize(I_prev_refined)
            
            # Get flow (at refined resolution)
            flow = self.bimnet(I_curr_norm, I_prev_norm)
            
            # CRITICAL: Upsample flow to match REFINED size first (BIMNet outputs at lower res)
            # Then upsample to full size if needed
            flow_h, flow_w = flow.shape[2], flow.shape[3]
            if flow_h != refine_h or flow_w != refine_w:
                # Scale flow values proportionally when upsampling
                scale_h = refine_h / flow_h
                scale_w = refine_w / flow_w
                flow = F.interpolate(flow, size=(refine_h, refine_w), mode='bilinear', align_corners=False)
                # Adjust flow magnitudes for the scale change
                flow[:, 0, :, :] *= scale_w
                flow[:, 1, :, :] *= scale_h
            
            # Now upsample to full size if refined size differs from original
            if refine_h != h or refine_w != w:
                scale_h = h / refine_h
                scale_w = w / refine_w
                flow = F.interpolate(flow, size=(h, w), mode='bilinear', align_corners=False)
                flow[:, 0, :, :] *= scale_w
                flow[:, 1, :, :] *= scale_h
            
            # Get pixel volume
            PV = self._get_pixel_volume(I_prev_deblurred, flow, I_curr, h, w)
            
            # Run PVDNet
            result = self.network(PV, I_prev, I_curr, I_next)
            
            # Clamp to valid range
            result = torch.clamp(result, 0, 1)
            
            # Update recurrent state
            self._prev_deblurred_states[face_id] = result.clone()
        
        # Convert back to numpy
        output = result.squeeze(0).cpu().numpy().transpose(1, 2, 0)
        output = (output * 255).astype(np.uint8)
        
        return output
    
    def process_cube_faces_batch(
        self,
        prev_faces: List[np.ndarray],
        curr_faces: List[np.ndarray],
        next_faces: List[np.ndarray],
        face_ids: Optional[List[str]] = None
    ) -> List[np.ndarray]:
        """
        Process multiple cube faces in parallel (batched).
        
        Args:
            prev_faces: List of 6 previous cube face images
            curr_faces: List of 6 current cube face images
            next_faces: List of 6 next cube face images
            face_ids: Optional list of face identifiers for state tracking
        
        Returns:
            List of 6 deblurred cube face images
        """
        if face_ids is None:
            face_ids = [f"face_{i}" for i in range(len(curr_faces))]
        
        # Process each face (can be parallelized on GPU)
        results = []
        for i, (prev, curr, next_, fid) in enumerate(zip(prev_faces, curr_faces, next_faces, face_ids)):
            result = self.process_frame(prev, curr, next_, fid)
            results.append(result)
        
        return results
    
    def get_available_checkpoints(self) -> Dict[str, str]:
        """Get available checkpoint files."""
        checkpoints = {}
        ckpt_dir = PVDNET_PATH / 'ckpt'
        
        if ckpt_dir.exists():
            for f in ckpt_dir.glob('*.pytorch'):
                name = f.stem
                checkpoints[name] = str(f)
        
        return checkpoints
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.network is not None
    
    @property
    def is_cuda(self) -> bool:
        """Check if using CUDA."""
        return self.device.type == 'cuda'

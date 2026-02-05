"""
Mask Stitcher
Combines masks from multiple perspective views into a single equirectangular mask.
"""

import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass
import cv2

from .perspective_projector import PerspectiveView


@dataclass
class StitchingResult:
    """Result of stitching multiple perspective masks."""
    combined_mask: np.ndarray  # Final combined mask (H, W)
    confidence_map: np.ndarray  # Confidence/weight map (H, W)
    coverage_map: np.ndarray  # Number of views covering each pixel (H, W)


class MaskStitcher:
    """
    Combines segmentation masks from multiple perspective views
    into a single equirectangular mask.
    
    Handles overlapping regions by blending based on confidence and
    distance from view center.
    """
    
    def __init__(
        self,
        blend_mode: str = 'max',
        apply_morphology: bool = True,
        morphology_kernel_size: int = 5,
        min_confidence: float = 0.0
    ):
        """
        Initialize the mask stitcher.
        
        Args:
            blend_mode: How to combine overlapping masks.
                       'max' - Take maximum value
                       'average' - Average all values
                       'weighted' - Weight by distance from view center
            apply_morphology: Whether to apply morphological operations
                            to clean up the final mask.
            morphology_kernel_size: Size of morphology kernel.
            min_confidence: Minimum confidence to include in output mask.
        """
        self.blend_mode = blend_mode
        self.apply_morphology = apply_morphology
        self.morphology_kernel_size = morphology_kernel_size
        self.min_confidence = min_confidence
        self.num_threads = 0  # 0 = auto
    
    def stitch_masks(
        self,
        masks: List[np.ndarray],
        views: List[PerspectiveView],
        confidences: List[np.ndarray],
        equirect_shape: Tuple[int, int],
        num_threads: int = 0
    ) -> StitchingResult:
        """
        Stitch multiple perspective masks into an equirectangular mask.
        
        Uses threading for parallel mask projection when num_threads > 1.
        
        Args:
            masks: List of masks in perspective space (one per view).
            views: List of PerspectiveView objects (same order as masks).
            confidences: List of confidence maps for each mask.
            equirect_shape: (height, width) of output equirectangular image.
            num_threads: Number of threads for parallel projection (0 = auto)
            
        Returns:
            StitchingResult with combined mask and metadata.
        """
        from concurrent.futures import ThreadPoolExecutor
        import os
        
        eq_h, eq_w = equirect_shape
        
        # Determine thread count
        if num_threads <= 0:
            num_threads = max(1, os.cpu_count() - 1)
        
        # Filter out empty masks
        valid_items = [
            (mask, view, conf) for mask, view, conf in zip(masks, views, confidences)
            if mask is not None and mask.max() > 0
        ]
        
        if not valid_items:
            return StitchingResult(
                combined_mask=np.zeros((eq_h, eq_w), dtype=np.float32),
                confidence_map=np.zeros((eq_h, eq_w), dtype=np.float32),
                coverage_map=np.zeros((eq_h, eq_w), dtype=np.int32)
            )
        
        # Project all masks in parallel using threads
        def project_single(item):
            mask, view, conf = item
            eq_mask = self._project_mask_to_equirect(mask, view, equirect_shape)
            weight = self._calculate_view_weight(view, equirect_shape)
            eq_weight = self._project_mask_to_equirect(
                np.ones_like(mask) * weight, view, equirect_shape
            )
            return eq_mask, eq_weight
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            projected = list(executor.map(project_single, valid_items))
        
        # Combine projected masks (fast numpy operations)
        combined_mask = np.zeros((eq_h, eq_w), dtype=np.float32)
        weight_sum = np.zeros((eq_h, eq_w), dtype=np.float32)
        coverage = np.zeros((eq_h, eq_w), dtype=np.int32)
        
        for eq_mask, eq_weight in projected:
            # Update coverage
            valid = eq_mask > 0
            coverage[valid] += 1
            
            # Combine based on blend mode
            if self.blend_mode == 'max':
                combined_mask = np.maximum(combined_mask, eq_mask)
            elif self.blend_mode == 'average':
                combined_mask += eq_mask
                weight_sum += (eq_mask > 0).astype(np.float32)
            elif self.blend_mode == 'weighted':
                combined_mask += eq_mask * eq_weight
                weight_sum += eq_weight * (eq_mask > 0).astype(np.float32)
        
        # Finalize based on blend mode
        if self.blend_mode in ['average', 'weighted']:
            valid = weight_sum > 0
            combined_mask[valid] /= weight_sum[valid]
        
        # Apply minimum confidence threshold
        combined_mask[combined_mask < self.min_confidence] = 0
        
        # Apply morphological operations
        if self.apply_morphology:
            combined_mask = self._apply_morphology(combined_mask)
        
        # Create confidence map
        confidence_map = weight_sum if self.blend_mode == 'weighted' else combined_mask
        
        return StitchingResult(
            combined_mask=combined_mask,
            confidence_map=confidence_map,
            coverage_map=coverage
        )
    
    def stitch_from_results(
        self,
        segmentation_results: List['SegmentationResult'],
        views: List[PerspectiveView],
        equirect_shape: Tuple[int, int],
        num_threads: int = 0
    ) -> StitchingResult:
        """
        Convenience method to stitch masks directly from segmentation results.
        
        Args:
            segmentation_results: List of SegmentationResult objects.
            views: List of PerspectiveView objects.
            equirect_shape: (height, width) of output equirectangular image.
            num_threads: Number of threads for parallel projection (0 = auto)
            
        Returns:
            StitchingResult with combined mask.
        """
        masks = [r.combined_mask for r in segmentation_results]
        
        # Create confidence maps from individual mask confidences
        confidences = []
        for result in segmentation_results:
            conf_map = np.zeros_like(result.combined_mask)
            for mask, conf in zip(result.masks, result.confidences):
                conf_map = np.maximum(conf_map, mask * conf)
            confidences.append(conf_map if conf_map.max() > 0 else result.combined_mask)
        
        return self.stitch_masks(masks, views, confidences, equirect_shape, num_threads)
    
    def _project_mask_to_equirect(
        self,
        mask: np.ndarray,
        view: PerspectiveView,
        equirect_shape: Tuple[int, int]
    ) -> np.ndarray:
        """
        Project a mask from perspective view to equirectangular coordinates.
        """
        if mask.ndim == 3:
            mask = mask[:, :, 0]
        
        eq_h, eq_w = equirect_shape
        equirect_mask = np.zeros((eq_h, eq_w), dtype=np.float32)
        
        if view.equirect_x_map is None or view.equirect_y_map is None:
            return equirect_mask
        
        # Vectorized projection
        x_flat = view.equirect_x_map.flatten()
        y_flat = view.equirect_y_map.flatten()
        mask_flat = mask.flatten().astype(np.float32)
        
        # Clip to valid range
        x_idx = np.clip(x_flat, 0, eq_w - 1).astype(np.int32)
        y_idx = np.clip(y_flat, 0, eq_h - 1).astype(np.int32)
        
        # Use np.maximum.at for accumulation
        np.maximum.at(equirect_mask, (y_idx, x_idx), mask_flat)
        
        return equirect_mask
    
    def _calculate_view_weight(
        self,
        view: PerspectiveView,
        equirect_shape: Tuple[int, int]
    ) -> np.ndarray:
        """
        Calculate a weight map for a view based on distance from center.
        
        Pixels near the center of the perspective view get higher weight
        to prefer them over edge pixels which may have more distortion.
        """
        h, w = view.height, view.width
        
        # Create distance from center map
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h / 2, w / 2
        
        # Normalized distance from center (0 at center, 1 at corners)
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        dist_normalized = dist / max_dist
        
        # Weight decreases towards edges (cosine falloff)
        weight = np.cos(dist_normalized * np.pi / 2)
        
        return weight.astype(np.float32)
    
    def _apply_morphology(self, mask: np.ndarray) -> np.ndarray:
        """
        Apply morphological operations to clean up the mask.
        """
        # Convert to binary for morphology
        binary = (mask > 0.5).astype(np.uint8) * 255
        
        # Create kernel
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, 
            (self.morphology_kernel_size, self.morphology_kernel_size)
        )
        
        # Close small gaps
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Remove small noise
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)
        
        # Convert back to float
        result = opened.astype(np.float32) / 255.0
        
        # Preserve soft edges from original where mask exists
        soft_edges = mask * (1 - result) * (mask > 0.1).astype(np.float32)
        result = np.maximum(result, soft_edges * 0.5)
        
        return result
    
    def dilate_mask(
        self, 
        mask: np.ndarray, 
        iterations: int = 1,
        kernel_size: int = 5
    ) -> np.ndarray:
        """
        Dilate the mask to expand detected regions.
        
        Useful for creating slightly larger masks that better cover
        moving objects with some margin.
        
        Args:
            mask: Input mask (H, W)
            iterations: Number of dilation iterations
            kernel_size: Size of dilation kernel
            
        Returns:
            Dilated mask
        """
        binary = (mask > 0.5).astype(np.uint8) * 255
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, 
            (kernel_size, kernel_size)
        )
        dilated = cv2.dilate(binary, kernel, iterations=iterations)
        return dilated.astype(np.float32) / 255.0
    
    def feather_mask(
        self, 
        mask: np.ndarray, 
        feather_amount: int = 10
    ) -> np.ndarray:
        """
        Apply feathering/blur to mask edges for smoother blending.
        
        Args:
            mask: Input mask (H, W)
            feather_amount: Amount of feathering (blur kernel size)
            
        Returns:
            Feathered mask with soft edges
        """
        if feather_amount <= 0:
            return mask
        
        # Ensure odd kernel size
        kernel_size = feather_amount * 2 + 1
        
        # Apply Gaussian blur for soft edges
        feathered = cv2.GaussianBlur(mask, (kernel_size, kernel_size), 0)
        
        # Preserve strong mask areas
        feathered = np.maximum(feathered, mask * 0.9)
        
        return feathered

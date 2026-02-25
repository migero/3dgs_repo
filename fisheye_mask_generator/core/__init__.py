"""
Core module for Fisheye Mask Generator
Generates segmentation masks for fisheye image pairs (185° FOV from max2sphere.py)
"""

from .perspective_projector import PerspectiveProjector
from .yolo_segmenter import YoloSegmenter
from .mask_stitcher import MaskStitcher
from .pipeline import MaskGenerationPipeline, BatchProcessor
from .fisheye_converter import (
    FisheyeConverter, 
    find_fisheye_pair, 
    get_mask_output_paths,
    find_pairs_from_two_folders,
    extract_frame_number,
    get_mask_output_paths_two_folders
)

__all__ = [
    'PerspectiveProjector',
    'YoloSegmenter', 
    'MaskStitcher',
    'MaskGenerationPipeline',
    'BatchProcessor',
    'FisheyeConverter',
    'find_fisheye_pair',
    'get_mask_output_paths',
    'find_pairs_from_two_folders',
    'extract_frame_number',
    'get_mask_output_paths_two_folders'
]

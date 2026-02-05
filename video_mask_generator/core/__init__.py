"""
Video Mask Generator Core Module

Provides video processing and YOLO segmentation for regular (non-360) videos.
"""

from .yolo_segmenter import YoloSegmenter, SegmentationResult, COCO_CLASSES, DEFAULT_MOVING_CLASSES
from .video_processor import VideoMaskProcessor, ProcessorConfig, ProcessingResult

__all__ = [
    'YoloSegmenter',
    'SegmentationResult',
    'COCO_CLASSES',
    'DEFAULT_MOVING_CLASSES',
    'VideoMaskProcessor',
    'ProcessorConfig',
    'ProcessingResult'
]

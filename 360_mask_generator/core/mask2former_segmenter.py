"""
Mask2Former Segmenter
Performs instance segmentation using Mask2Former models from Facebook Research.

This is an optional alternative to YOLO that can provide higher quality segmentation
but requires additional dependencies and is typically slower.
"""

import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
import cv2
import logging

# Suppress warnings during import
logging.getLogger("detectron2").setLevel(logging.WARNING)

try:
    # import some common detectron2 utilities
    from detectron2.config import get_cfg
    from detectron2.engine import DefaultPredictor
    from detectron2.utils.visualizer import Visualizer, ColorMode
    from detectron2.data import MetadataCatalog
    from detectron2.projects.deeplab import add_deeplab_config
    
    # Add the Mask2Former folder to the Python path
    import sys
    import os
    
    # Get the root directory (gopro360-converter)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    mask2former_path = os.path.join(root_dir, "Mask2Former")
    
    if mask2former_path not in sys.path:
        sys.path.insert(0, mask2former_path)
    
    # Import Mask2Former project
    from mask2former import add_maskformer2_config
    MASK2FORMER_AVAILABLE = True
    
except ImportError as e:
    print(f"Mask2Former not available: {e}")
    print("To use Mask2Former, install detectron2 and ensure the Mask2Former repository is available.")
    MASK2FORMER_AVAILABLE = False

from .yolo_segmenter import SegmentationResult, COCO_CLASSES, DEFAULT_MOVING_CLASSES


# COCO class names mapping for Mask2Former output
COCO_THING_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
    'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
    'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
    'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
    'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
    'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
    'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
    'toothbrush'
]


class Mask2FormerSegmenter:
    """
    Performs instance segmentation using Mask2Former models.
    
    Supports both instance and panoptic segmentation modes.
    """
    
    def __init__(
        self,
        config_file: str = None,
        model_weights: str = None,
        target_classes: Optional[List[str]] = None,
        confidence_threshold: float = 0.5,
        mode: str = "instance",  # "instance", "panoptic", "semantic"
        device: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize the Mask2Former segmenter.
        
        Args:
            config_file: Path to Mask2Former config file. If None, uses default COCO instance segmentation config.
            model_weights: Path to model weights. If None, will attempt to download.
            target_classes: List of class names to detect. If None, uses DEFAULT_MOVING_CLASSES.
            confidence_threshold: Minimum confidence for detections.
            mode: Segmentation mode ("instance", "panoptic", "semantic").
            device: Device to run on ('cpu', 'cuda', etc.). None for auto-detect.
            verbose: Whether to print loading messages.
        """
        if not MASK2FORMER_AVAILABLE:
            raise ImportError("Mask2Former dependencies not available. Please install detectron2 and ensure Mask2Former is properly set up.")
        
        self.config_file = config_file
        self.model_weights = model_weights
        self.target_classes = target_classes or DEFAULT_MOVING_CLASSES
        self.confidence_threshold = confidence_threshold
        self.mode = mode
        self.device = device
        self.model = None
        self.verbose = verbose
        
        # Convert target class names to indices
        self.target_class_ids = self._get_target_class_ids()
    
    def _get_target_class_ids(self) -> List[int]:
        """Get COCO class IDs for target classes."""
        class_ids = []
        for class_name in self.target_classes:
            try:
                idx = COCO_THING_CLASSES.index(class_name)
                class_ids.append(idx)
            except ValueError:
                if self.verbose:
                    print(f"Warning: Class '{class_name}' not found in COCO thing classes")
        return class_ids
    
    def load_model(self) -> bool:
        """
        Load the Mask2Former model.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            cfg = get_cfg()
            add_deeplab_config(cfg)
            add_maskformer2_config(cfg)
            
            # Use default config if none provided
            if self.config_file is None:
                # Try to find a reasonable default config
                mask2former_root = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "Mask2Former"
                )
                config_path = os.path.join(
                    mask2former_root,
                    "configs/coco/instance-segmentation/maskformer2_R50_bs16_50ep.yaml"
                )
                
                if os.path.exists(config_path):
                    self.config_file = config_path
                else:
                    # Fallback to any available config
                    configs_dir = os.path.join(mask2former_root, "configs/coco/instance-segmentation")
                    if os.path.exists(configs_dir):
                        config_files = [f for f in os.listdir(configs_dir) if f.endswith('.yaml')]
                        if config_files:
                            self.config_file = os.path.join(configs_dir, config_files[0])
                            if self.verbose:
                                print(f"Using config: {config_files[0]}")
                
                if self.config_file is None:
                    raise FileNotFoundError("No suitable Mask2Former config file found")
            
            cfg.merge_from_file(self.config_file)
            
            # Set model weights if provided
            if self.model_weights:
                cfg.MODEL.WEIGHTS = self.model_weights
            
            # Configure segmentation modes
            if hasattr(cfg.MODEL, 'MASK_FORMER'):
                cfg.MODEL.MASK_FORMER.TEST.SEMANTIC_ON = (self.mode in ["semantic", "panoptic"])
                cfg.MODEL.MASK_FORMER.TEST.INSTANCE_ON = (self.mode in ["instance", "panoptic"])
                cfg.MODEL.MASK_FORMER.TEST.PANOPTIC_ON = (self.mode == "panoptic")
            
            # Set device
            if self.device:
                cfg.MODEL.DEVICE = self.device
            
            # Set confidence threshold
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.confidence_threshold
            cfg.MODEL.RETINANET.SCORE_THRESH_TEST = self.confidence_threshold
            
            self.predictor = DefaultPredictor(cfg)
            self.cfg = cfg
            
            # Get metadata for visualization
            try:
                self.metadata = MetadataCatalog.get("coco_2017_val")
            except:
                self.metadata = MetadataCatalog.get("coco_2017_train")
            
            if self.verbose:
                device_str = cfg.MODEL.DEVICE if hasattr(cfg.MODEL, 'DEVICE') else 'auto'
                print(f"Loaded Mask2Former model ({self.mode} mode) on device: {device_str}")
            
            return True
            
        except Exception as e:
            print(f"Error loading Mask2Former model: {e}")
            return False
    
    def get_device_info(self) -> str:
        """Get information about the current device."""
        try:
            import torch
            if torch.cuda.is_available() and hasattr(self, 'cfg') and 'cuda' in str(self.cfg.MODEL.DEVICE):
                gpu_name = torch.cuda.get_device_name(0)
                return f"GPU: {gpu_name}"
            else:
                return "CPU"
        except:
            return "CPU"
    
    def segment(self, image: np.ndarray) -> SegmentationResult:
        """
        Perform segmentation on an image.
        
        Args:
            image: Input image (H, W, 3) in BGR format.
            
        Returns:
            SegmentationResult with masks, class info, and confidence scores.
        """
        if self.model is None and self.predictor is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Run prediction
        outputs = self.predictor(image)
        
        masks = []
        class_ids = []
        class_names = []
        confidences = []
        boxes = []
        
        if self.mode == "instance" or self.mode == "panoptic":
            # Process instance predictions
            if "instances" in outputs and len(outputs["instances"]) > 0:
                instances = outputs["instances"].to("cpu")
                
                # Get masks
                if hasattr(instances, 'pred_masks'):
                    pred_masks = instances.pred_masks.numpy()
                    pred_classes = instances.pred_classes.numpy()
                    pred_scores = instances.scores.numpy()
                    pred_boxes = instances.pred_boxes.tensor.numpy()
                    
                    for i, (mask, class_id, score, box) in enumerate(
                        zip(pred_masks, pred_classes, pred_scores, pred_boxes)
                    ):
                        # Filter by confidence and target classes
                        if score >= self.confidence_threshold and class_id in self.target_class_ids:
                            masks.append(mask.astype(np.uint8))
                            class_ids.append(int(class_id))
                            class_names.append(COCO_THING_CLASSES[class_id])
                            confidences.append(float(score))
                            boxes.append(box.astype(np.float32))
        
        elif self.mode == "semantic":
            # Process semantic segmentation
            if "sem_seg" in outputs:
                sem_seg = outputs["sem_seg"].argmax(dim=0).to("cpu").numpy()
                
                # Extract masks for target classes
                for class_id in self.target_class_ids:
                    mask = (sem_seg == class_id).astype(np.uint8)
                    if mask.sum() > 100:  # Only include if significant area
                        masks.append(mask)
                        class_ids.append(class_id)
                        class_names.append(COCO_THING_CLASSES[class_id])
                        confidences.append(1.0)  # Semantic segmentation doesn't provide confidence
                        
                        # Create bounding box from mask
                        coords = np.column_stack(np.where(mask))
                        if len(coords) > 0:
                            y1, x1 = coords.min(axis=0)
                            y2, x2 = coords.max(axis=0)
                            boxes.append(np.array([x1, y1, x2, y2], dtype=np.float32))
                        else:
                            boxes.append(np.array([0, 0, 1, 1], dtype=np.float32))
        
        # Create combined mask
        if masks:
            combined_mask = np.zeros(image.shape[:2], dtype=np.float32)
            for mask in masks:
                combined_mask = np.maximum(combined_mask, mask.astype(np.float32))
        else:
            combined_mask = np.zeros(image.shape[:2], dtype=np.float32)
        
        return SegmentationResult(
            masks=masks,
            class_ids=class_ids,
            class_names=class_names,
            confidences=confidences,
            boxes=boxes,
            combined_mask=combined_mask
        )


def is_mask2former_available() -> bool:
    """Check if Mask2Former is available for use."""
    return MASK2FORMER_AVAILABLE
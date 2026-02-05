"""
YOLO Segmenter
Performs instance segmentation using Ultralytics YOLO models.
"""

import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass
import cv2


# COCO class names for reference
COCO_CLASSES = [
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

# Default classes for moving objects that should be masked
DEFAULT_MOVING_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'bus', 'train', 'truck',
    'backpack', 'umbrella', 'handbag', 'suitcase'
]


@dataclass
class SegmentationResult:
    """Result of segmentation on a single image."""
    masks: List[np.ndarray]  # List of binary masks (H, W)
    class_ids: List[int]  # Class ID for each mask
    class_names: List[str]  # Class name for each mask
    confidences: List[float]  # Confidence score for each detection
    boxes: List[np.ndarray]  # Bounding boxes (x1, y1, x2, y2)
    combined_mask: np.ndarray  # Combined mask of all detections (H, W)
    
    @property
    def mask(self) -> np.ndarray:
        """Alias for combined_mask for compatibility."""
        return self.combined_mask
    
    @property
    def num_detections(self) -> int:
        """Number of detections."""
        return len(self.masks)


class YoloSegmenter:
    """
    Performs instance segmentation using YOLO models from Ultralytics.
    
    Supports both detection and segmentation models.
    """
    
    def __init__(
        self,
        model_name: str = "yolo11n-seg.pt",
        target_classes: Optional[List[str]] = None,
        confidence_threshold: float = 0.35,
        device: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize the YOLO segmenter.
        
        Args:
            model_name: Name of the YOLO model to use. 
                       Options: yolo11n-seg, yolo11s-seg, yolo11m-seg, yolo11l-seg, yolo11x-seg
            target_classes: List of class names to detect. If None, uses DEFAULT_MOVING_CLASSES.
            confidence_threshold: Minimum confidence for detections.
            device: Device to run on ('cpu', 'cuda', 'cuda:0', etc.). None for auto-detect.
            verbose: Whether to print loading messages.
        """
        self.model_name = model_name
        self.target_classes = target_classes or DEFAULT_MOVING_CLASSES
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.model = None
        self.verbose = verbose
        self.active_device = None
        
        # Convert target class names to indices
        self.target_class_ids = self._get_target_class_ids()
    
    def _get_target_class_ids(self) -> List[int]:
        """Get COCO class IDs for target classes."""
        class_ids = []
        for class_name in self.target_classes:
            try:
                idx = COCO_CLASSES.index(class_name)
                class_ids.append(idx)
            except ValueError:
                print(f"Warning: Class '{class_name}' not found in COCO classes")
        return class_ids
    
    def load_model(self) -> bool:
        """
        Load the YOLO model.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            from ultralytics import YOLO
            import torch
            
            self.model = YOLO(self.model_name)
            
            # Determine device
            if self.device:
                device = self.device
            elif torch.cuda.is_available():
                device = 'cuda'
            else:
                device = 'cpu'
            
            self.model.to(device)
            self.active_device = device
            
            # Print device info
            if self.verbose:
                if device == 'cuda' or device.startswith('cuda:'):
                    gpu_name = torch.cuda.get_device_name(0)
                    print(f"Loaded YOLO model: {self.model_name} on GPU ({gpu_name})")
                else:
                    print(f"Loaded YOLO model: {self.model_name} on CPU")
                    print("Note: Install CUDA-enabled PyTorch for GPU acceleration")
            
            return True
            
        except ImportError:
            print("Error: ultralytics package not installed.")
            print("Install with: pip install ultralytics")
            return False
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            return False
    
    def get_device_info(self) -> str:
        """Get information about the current device."""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                return f"GPU: {gpu_name}"
            else:
                return "CPU (CUDA not available)"
        except:
            return "CPU"
    
    def segment(self, image: np.ndarray) -> SegmentationResult:
        """
        Run segmentation on an image.
        
        Args:
            image: Input image as numpy array (H, W, C) in BGR or RGB format.
            
        Returns:
            SegmentationResult with masks, classes, and confidences.
        """
        if self.model is None:
            if not self.load_model():
                return self._empty_result(image.shape[:2])
        
        # Run inference
        results = self.model(
            image, 
            conf=self.confidence_threshold,
            classes=self.target_class_ids if self.target_class_ids else None,
            verbose=False
        )
        
        # Process results
        masks = []
        class_ids = []
        class_names = []
        confidences = []
        boxes = []
        
        if len(results) > 0 and results[0].masks is not None:
            result = results[0]
            
            # Get masks
            mask_data = result.masks.data.cpu().numpy()  # (N, H, W)
            
            # Get boxes and classes
            for i, (box, cls, conf) in enumerate(zip(
                result.boxes.xyxy.cpu().numpy(),
                result.boxes.cls.cpu().numpy(),
                result.boxes.conf.cpu().numpy()
            )):
                class_id = int(cls)
                
                # Resize mask to original image size
                mask = mask_data[i]
                if mask.shape != image.shape[:2]:
                    mask = cv2.resize(
                        mask, 
                        (image.shape[1], image.shape[0]),
                        interpolation=cv2.INTER_LINEAR
                    )
                
                masks.append((mask > 0.5).astype(np.float32))
                class_ids.append(class_id)
                class_names.append(COCO_CLASSES[class_id] if class_id < len(COCO_CLASSES) else 'unknown')
                confidences.append(float(conf))
                boxes.append(box)
        
        # Create combined mask
        combined_mask = np.zeros(image.shape[:2], dtype=np.float32)
        for mask in masks:
            combined_mask = np.maximum(combined_mask, mask)
        
        return SegmentationResult(
            masks=masks,
            class_ids=class_ids,
            class_names=class_names,
            confidences=confidences,
            boxes=boxes,
            combined_mask=combined_mask
        )
    
    def _empty_result(self, image_shape: Tuple[int, int]) -> SegmentationResult:
        """Create an empty segmentation result."""
        return SegmentationResult(
            masks=[],
            class_ids=[],
            class_names=[],
            confidences=[],
            boxes=[],
            combined_mask=np.zeros(image_shape, dtype=np.float32)
        )
    
    def get_available_classes(self) -> List[str]:
        """Return list of all available COCO classes."""
        return COCO_CLASSES.copy()
    
    def set_target_classes(self, classes: List[str]) -> None:
        """
        Update the target classes to detect.
        
        Args:
            classes: List of class names to detect.
        """
        self.target_classes = classes
        self.target_class_ids = self._get_target_class_ids()
    
    def visualize_result(
        self, 
        image: np.ndarray, 
        result: SegmentationResult,
        alpha: float = 0.5,
        show_labels: bool = True
    ) -> np.ndarray:
        """
        Visualize segmentation results on the image.
        
        Args:
            image: Original image.
            result: Segmentation result.
            alpha: Transparency for mask overlay.
            show_labels: Whether to show class labels.
            
        Returns:
            Image with masks overlaid.
        """
        output = image.copy()
        
        # Color palette for different classes
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
            (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128)
        ]
        
        for i, (mask, class_name, conf, box) in enumerate(zip(
            result.masks, result.class_names, result.confidences, result.boxes
        )):
            color = colors[i % len(colors)]
            
            # Apply mask overlay
            mask_bool = mask > 0.5
            output[mask_bool] = (
                output[mask_bool] * (1 - alpha) + 
                np.array(color) * alpha
            ).astype(np.uint8)
            
            # Draw label
            if show_labels:
                x1, y1 = int(box[0]), int(box[1])
                label = f"{class_name}: {conf:.2f}"
                cv2.putText(
                    output, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                )
        
        return output

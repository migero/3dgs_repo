"""
Mask Generation Pipeline
Orchestrates the full process of generating masks from equirectangular images.
"""

import numpy as np
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass, field
import cv2
from pathlib import Path
import time

from .perspective_projector import PerspectiveProjector, PerspectiveView
from .yolo_segmenter import YoloSegmenter, SegmentationResult, DEFAULT_MOVING_CLASSES
from .mask_stitcher import MaskStitcher, StitchingResult

try:
    from .mask2former_segmenter import Mask2FormerSegmenter, is_mask2former_available
except ImportError:
    Mask2FormerSegmenter = None
    is_mask2former_available = lambda: False


@dataclass
class PipelineConfig:
    """Configuration for the mask generation pipeline."""
    
    # Perspective projection settings
    num_horizontal_views: int = 8
    num_pitch_levels: int = 3  # 1 = horizon only, 3 = include up/down
    fov: float = 90.0
    view_size: Tuple[int, int] = (640, 640)
    pitch_range: Tuple[float, float] = (-30.0, 30.0)  # Skip extreme up/down
    
    # YOLO settings
    model_name: str = "yolo11n-seg.pt"
    target_classes: List[str] = field(default_factory=lambda: DEFAULT_MOVING_CLASSES.copy())
    confidence_threshold: float = 0.35  # Higher default to reduce false positives on posters
    device: Optional[str] = None
    
    # Segmenter selection
    segmenter_type: str = "yolo"  # "yolo" or "mask2former"
    
    # Mask2Former settings (used when segmenter_type="mask2former")
    mask2former_config: Optional[str] = None
    mask2former_weights: Optional[str] = None
    mask2former_mode: str = "instance"  # "instance", "panoptic", "semantic"
    
    # Stitching settings
    blend_mode: str = 'max'  # 'max', 'average', 'weighted'
    apply_morphology: bool = True
    morphology_kernel_size: int = 5
    
    # Post-processing
    dilate_mask: bool = True
    dilation_iterations: int = 2
    dilation_kernel_size: int = 5
    feather_edges: bool = True
    feather_amount: int = 10
    
    # Logging
    verbose: bool = True  # Print model loading messages
    
    # Performance
    num_cpu_threads: int = 0  # Number of threads for CPU work (0 = auto)


@dataclass
class PipelineResult:
    """Result from running the mask generation pipeline."""
    mask: np.ndarray  # Final combined mask (H, W)
    confidence_map: np.ndarray  # Confidence values (H, W)
    coverage_map: np.ndarray  # View coverage (H, W)
    perspective_views: List[PerspectiveView]  # Extracted views
    segmentation_results: List[SegmentationResult]  # Per-view segmentation
    processing_time: float  # Total processing time in seconds
    
    def save_mask(self, path: str, as_alpha: bool = False) -> None:
        """
        Save the mask to a file.
        
        Args:
            path: Output file path
            as_alpha: If True, save as RGBA with mask as alpha channel
        """
        mask_uint8 = (self.mask * 255).astype(np.uint8)
        cv2.imwrite(path, mask_uint8)
    
    def get_mask_as_rgba(self, original_image: np.ndarray) -> np.ndarray:
        """
        Get the original image with mask as alpha channel.
        
        Args:
            original_image: Original equirectangular image (H, W, 3)
            
        Returns:
            RGBA image with mask as alpha
        """
        if original_image.shape[2] == 4:
            rgba = original_image.copy()
        else:
            rgba = cv2.cvtColor(original_image, cv2.COLOR_BGR2BGRA)
        
        rgba[:, :, 3] = (self.mask * 255).astype(np.uint8)
        return rgba


class MaskGenerationPipeline:
    """
    Complete pipeline for generating segmentation masks from equirectangular images.
    
    Process:
    1. Extract multiple perspective views from equirectangular image
    2. Run YOLO segmentation on each perspective view
    3. Project masks back to equirectangular space
    4. Combine/stitch masks from all views
    5. Apply post-processing (morphology, dilation, feathering)
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the pipeline.
        
        Args:
            config: Pipeline configuration. Uses defaults if None.
        """
        self.config = config or PipelineConfig()
        
        # Initialize components
        self.projector = PerspectiveProjector(
            num_views=self.config.num_horizontal_views,
            fov=self.config.fov,
            view_size=self.config.view_size,
            pitch_range=self.config.pitch_range,
            pitch_steps=self.config.num_pitch_levels
        )
        
        # Initialize segmenter based on type
        if self.config.segmenter_type.lower() == "mask2former":
            if Mask2FormerSegmenter is None or not is_mask2former_available():
                raise ImportError("Mask2Former not available. Please ensure detectron2 is installed and Mask2Former is properly set up.")
            
            self.segmenter = Mask2FormerSegmenter(
                config_file=self.config.mask2former_config,
                model_weights=self.config.mask2former_weights,
                target_classes=self.config.target_classes,
                confidence_threshold=self.config.confidence_threshold,
                mode=self.config.mask2former_mode,
                device=self.config.device,
                verbose=self.config.verbose
            )
        else:  # Default to YOLO
            self.segmenter = YoloSegmenter(
                model_name=self.config.model_name,
                target_classes=self.config.target_classes,
                confidence_threshold=self.config.confidence_threshold,
                device=self.config.device,
                verbose=self.config.verbose
            )
        
        self.stitcher = MaskStitcher(
            blend_mode=self.config.blend_mode,
            apply_morphology=self.config.apply_morphology,
            morphology_kernel_size=self.config.morphology_kernel_size
        )
        
        self._progress_callback: Optional[Callable[[str, float], None]] = None
    
    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """
        Set a callback function for progress updates.
        
        Args:
            callback: Function that takes (message: str, progress: float 0-1)
        """
        self._progress_callback = callback
    
    def _report_progress(self, message: str, progress: float) -> None:
        """Report progress if callback is set."""
        if self._progress_callback:
            self._progress_callback(message, progress)
    
    def load_model(self) -> bool:
        """
        Pre-load the segmentation model.
        
        Returns:
            True if successful.
        """
        return self.segmenter.load_model()
    
    def process(self, equirect_image: np.ndarray, additional_mask: Optional[np.ndarray] = None) -> PipelineResult:
        """
        Run the full mask generation pipeline on an equirectangular image.
        
        Uses multi-threading for CPU-bound perspective extraction and stitching,
        while GPU YOLO inference runs sequentially.
        
        Args:
            equirect_image: Equirectangular image as numpy array (H, W, C)
            
        Returns:
            PipelineResult with mask and metadata
        """
        from concurrent.futures import ThreadPoolExecutor
        import os
        
        start_time = time.time()
        equirect_shape = equirect_image.shape[:2]
        
        # Determine number of CPU threads
        num_threads = self.config.num_cpu_threads
        if num_threads <= 0:
            num_threads = max(1, os.cpu_count() - 1)
        
        # Step 1: Extract perspective views (CPU-bound, can parallelize)
        self._report_progress("Extracting perspective views...", 0.1)
        views = self._extract_views_threaded(equirect_image, num_threads)
        
        total_views = len(views)
        
        # Step 2: Run segmentation on each view (GPU-bound, sequential)
        self._report_progress("Running segmentation...", 0.2)
        segmentation_results = []
        
        for i, view in enumerate(views):
            progress = 0.2 + 0.5 * (i / total_views)
            self._report_progress(
                f"Segmenting view {i+1}/{total_views}...", 
                progress
            )
            
            result = self.segmenter.segment(view.image)
            segmentation_results.append(result)
        
        # Step 3: Stitch masks together (CPU-bound, uses threading internally)
        self._report_progress("Stitching masks...", 0.75)
        stitch_result = self.stitcher.stitch_from_results(
            segmentation_results, views, equirect_shape, num_threads
        )
        
        # Step 4: Post-processing
        self._report_progress("Post-processing...", 0.9)
        final_mask = stitch_result.combined_mask
        
        if self.config.dilate_mask:
            final_mask = self.stitcher.dilate_mask(
                final_mask,
                iterations=self.config.dilation_iterations,
                kernel_size=self.config.dilation_kernel_size
            )
        
        if self.config.feather_edges:
            final_mask = self.stitcher.feather_mask(
                final_mask,
                feather_amount=self.config.feather_amount
            )
        
        # Apply additional mask if provided (logical OR, after all post-processing)
        if additional_mask is not None:
            # Ensure mask is binary float32 and same shape
            add_mask = additional_mask
            if add_mask.shape != final_mask.shape:
                add_mask = cv2.resize(add_mask, (final_mask.shape[1], final_mask.shape[0]), interpolation=cv2.INTER_NEAREST)
            if add_mask.dtype != np.float32:
                add_mask = (add_mask > 127).astype(np.float32) if add_mask.dtype == np.uint8 else add_mask.astype(np.float32)
            final_mask = np.clip(final_mask + add_mask, 0, 1)
        
        processing_time = time.time() - start_time
        self._report_progress("Complete!", 1.0)
        
        return PipelineResult(
            mask=final_mask,
            confidence_map=stitch_result.confidence_map,
            coverage_map=stitch_result.coverage_map,
            perspective_views=views,
            segmentation_results=segmentation_results,
            processing_time=processing_time
        )
    
    def _extract_views_threaded(
        self, 
        equirect_image: np.ndarray, 
        num_threads: int
    ) -> List[PerspectiveView]:
        """
        Extract perspective views using multiple threads.
        
        The actual work is numpy-based which releases the GIL,
        so threading provides real parallelism.
        """
        from concurrent.futures import ThreadPoolExecutor
        
        h, w = equirect_image.shape[:2]
        view_w, view_h = self.projector.view_size
        
        # Create list of (yaw, pitch) combinations
        view_params = []
        for pitch in self.projector.pitch_angles:
            for yaw in self.projector.yaw_angles:
                view_params.append((yaw, pitch))
        
        def extract_single_view(params):
            yaw, pitch = params
            persp_img, x_map, y_map = self.projector._equirect_to_perspective(
                equirect_image, yaw, pitch, self.projector.fov, view_w, view_h
            )
            return PerspectiveView(
                image=persp_img,
                yaw=yaw,
                pitch=pitch,
                fov=self.projector.fov,
                width=view_w,
                height=view_h,
                equirect_x_map=x_map,
                equirect_y_map=y_map
            )
        
        # Extract views in parallel using threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            views = list(executor.map(extract_single_view, view_params))
        
        return views
    
    def process_file(
        self, 
        input_path: str, 
        output_path: Optional[str] = None
    ) -> PipelineResult:
        """
        Process an equirectangular image file.
        
        Args:
            input_path: Path to input image
            output_path: Optional path to save output mask
            
        Returns:
            PipelineResult
        """
        # Load image
        self._report_progress("Loading image...", 0.0)
        image = cv2.imread(input_path)
        
        if image is None:
            raise ValueError(f"Could not load image: {input_path}")
        
        # Process
        result = self.process(image)
        
        # Save if output path provided
        if output_path:
            result.save_mask(output_path)
        
        return result
    
    def visualize_views(
        self, 
        views: List[PerspectiveView],
        segmentation_results: List[SegmentationResult],
        cols: int = 4
    ) -> np.ndarray:
        """
        Create a visualization of all perspective views with their segmentation results.
        
        Args:
            views: List of perspective views
            segmentation_results: List of segmentation results
            cols: Number of columns in the grid
            
        Returns:
            Grid image showing all views
        """
        rows = (len(views) + cols - 1) // cols
        
        view_h, view_w = views[0].height, views[0].width
        grid = np.zeros((rows * view_h, cols * view_w, 3), dtype=np.uint8)
        
        for i, (view, result) in enumerate(zip(views, segmentation_results)):
            row = i // cols
            col = i % cols
            
            # Visualize segmentation on this view
            vis = self.segmenter.visualize_result(view.image, result)
            
            # Add view info
            info = f"Y:{view.yaw:.0f} P:{view.pitch:.0f}"
            cv2.putText(vis, info, (10, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Place in grid
            y_start = row * view_h
            x_start = col * view_w
            grid[y_start:y_start+view_h, x_start:x_start+view_w] = vis
        
        return grid
    
    def get_detection_summary(self, result: PipelineResult) -> dict:
        """
        Get a summary of detections across all views.
        
        Args:
            result: Pipeline result
            
        Returns:
            Dictionary with detection statistics
        """
        all_classes = []
        all_confidences = []
        total_detections = 0
        
        for seg_result in result.segmentation_results:
            all_classes.extend(seg_result.class_names)
            all_confidences.extend(seg_result.confidences)
            total_detections += len(seg_result.masks)
        
        # Count by class
        class_counts = {}
        for cls in all_classes:
            class_counts[cls] = class_counts.get(cls, 0) + 1
        
        return {
            'total_detections': total_detections,
            'class_counts': class_counts,
            'avg_confidence': np.mean(all_confidences) if all_confidences else 0.0,
            'mask_coverage': np.mean(result.mask > 0.5) * 100,  # Percentage
            'processing_time': result.processing_time
        }


def create_default_pipeline() -> MaskGenerationPipeline:
    """Create a pipeline with default configuration."""
    return MaskGenerationPipeline(PipelineConfig())


def create_fast_pipeline() -> MaskGenerationPipeline:
    """Create a faster pipeline with fewer views and smaller model."""
    config = PipelineConfig(
        num_horizontal_views=4,
        num_pitch_levels=1,
        model_name="yolo11n-seg.pt",
        view_size=(480, 480)
    )
    return MaskGenerationPipeline(config)


def create_accurate_pipeline() -> MaskGenerationPipeline:
    """Create a more accurate pipeline with more views and larger model."""
    config = PipelineConfig(
        num_horizontal_views=12,
        num_pitch_levels=3,
        model_name="yolo11m-seg.pt",
        view_size=(640, 640),
        fov=75.0  # More overlap
    )
    return MaskGenerationPipeline(config)


# Global model cache for worker processes to avoid reloading
_worker_pipeline = None
_worker_config_hash = None


def _get_config_hash(config_dict):
    """Create a hash of config dict to detect changes."""
    import hashlib
    import json
    return hashlib.md5(json.dumps(config_dict, sort_keys=True).encode()).hexdigest()


# Worker function for multiprocessing (must be at module level)
def _process_single_file(args):
    """
    Process a single file - worker function for multiprocessing.
    
    Caches the pipeline/model within each worker process to avoid
    reloading the model for every single file.
    
    Args:
        args: Tuple of (input_path, output_path, config_dict, add_mask_path)
        
    Returns:
        Tuple of (input_path, success, detections, processing_time, error_msg)
    """
    global _worker_pipeline, _worker_config_hash
    
    input_path, output_path, config_dict, add_mask_path = args
    
    try:
        # Check if we can reuse the cached pipeline
        current_hash = _get_config_hash(config_dict)
        
        if _worker_pipeline is None or _worker_config_hash != current_hash:
            # Need to create new pipeline (first file or config changed)
            config = PipelineConfig(**config_dict)
            _worker_pipeline = MaskGenerationPipeline(config)
            _worker_config_hash = current_hash
        
        # Load image
        image = cv2.imread(str(input_path))
        if image is None:
            return (input_path, False, 0, 0.0, "Could not load image")
        
        # Load additional mask if provided
        additional_mask = None
        if add_mask_path:
            additional_mask = cv2.imread(add_mask_path, cv2.IMREAD_GRAYSCALE)
            if additional_mask is not None:
                additional_mask = (additional_mask > 127).astype(np.float32)
        
        # Process
        result = _worker_pipeline.process(image, additional_mask=additional_mask)
        
        # Save mask
        result.save_mask(str(output_path))
        
        # Count detections
        total_detections = sum(len(sr.masks) for sr in result.segmentation_results)
        
        return (input_path, True, total_detections, result.processing_time, None)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return (input_path, False, 0, 0.0, str(e))


class BatchProcessor:
    """
    Batch processor with multiprocessing support.
    
    Uses multiple CPU cores to process images in parallel.
    Each worker process loads its own YOLO model.
    """
    
    def __init__(
        self, 
        config: PipelineConfig,
        num_workers: Optional[int] = None,
        use_gpu: bool = True,
        additional_mask: Optional[np.ndarray] = None
    ):
        """
        Initialize batch processor.
        
        Args:
            config: Pipeline configuration
            num_workers: Number of worker processes. None = auto (CPU count - 1)
            use_gpu: Whether to try using GPU. If True with multiple workers,
                    only 1 worker uses GPU, others use CPU.
            additional_mask: Additional mask to apply to all images
        """
        self.config = config
        self.use_gpu = use_gpu
        self.additional_mask = additional_mask
        
        # Detect if GPU is available
        gpu_available = False
        if use_gpu:
            try:
                import torch
                gpu_available = torch.cuda.is_available()
            except ImportError:
                pass
        
        # Determine number of workers
        # IMPORTANT: When using GPU, limit to 1 worker to avoid VRAM exhaustion
        # Multiple workers would each load a copy of the model (~500MB-1GB each)
        if gpu_available:
            # GPU is fast enough - 1 worker is optimal
            self.num_workers = 1
            if num_workers and num_workers > 1:
                print(f"Note: Using 1 worker for GPU processing (GPU is shared resource)")
        elif num_workers is None:
            import os
            # CPU-only: Use CPU count - 1, minimum 1
            self.num_workers = max(1, os.cpu_count() - 1)
        else:
            self.num_workers = max(1, num_workers)
        
        self._progress_callback: Optional[Callable[[str, float, str], None]] = None
    
    def set_progress_callback(self, callback: Callable[[str, float, str], None]) -> None:
        """
        Set callback for progress updates.
        
        Args:
            callback: Function(filename, overall_progress, message)
        """
        self._progress_callback = callback
    
    def process_folder(
        self, 
        folder_path: str,
        file_callback: Optional[Callable[[str, bool, int, float], None]] = None
    ) -> dict:
        """
        Process all images in a folder using multiple workers.
        
        Args:
            folder_path: Path to folder with images
            file_callback: Optional callback(filename, success, detections, time)
            
        Returns:
            Summary dict with statistics
        """
        from concurrent.futures import ProcessPoolExecutor, as_completed
        import multiprocessing
        import os
        
        # Use spawn context for CUDA compatibility
        try:
            ctx = multiprocessing.get_context('spawn')
        except ValueError:
            ctx = multiprocessing.get_context()
        
        folder = Path(folder_path)
        
        # Find all image files (excluding mask files)
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
        image_files = [
            f for f in folder.iterdir() 
            if f.is_file() and f.suffix.lower() in image_extensions
            and '_mask' not in f.stem
        ]
        
        if not image_files:
            return {'total': 0, 'successful': 0, 'failed': 0, 'skipped': 0, 'total_time': 0.0}
        
        # Filter out files that already have masks
        files_to_process = []
        skipped_count = 0
        for input_file in sorted(image_files):
            output_file = input_file.parent / f"{input_file.stem}_mask{input_file.suffix}"
            if output_file.exists():
                skipped_count += 1
            else:
                files_to_process.append(input_file)
        
        if skipped_count > 0:
            print(f"Skipping {skipped_count} files that already have masks")
        
        if not files_to_process:
            print("All files already have masks, nothing to process")
            return {'total': len(image_files), 'successful': 0, 'failed': 0, 'skipped': skipped_count, 'total_time': 0.0}
        
        # Prepare work items - set verbose=False to avoid spam per file
        config_dict = {
            'num_horizontal_views': self.config.num_horizontal_views,
            'num_pitch_levels': self.config.num_pitch_levels,
            'fov': self.config.fov,
            'view_size': self.config.view_size,
            'pitch_range': self.config.pitch_range,
            'model_name': self.config.model_name,
            'target_classes': self.config.target_classes,
            'confidence_threshold': self.config.confidence_threshold,
            'device': self.config.device,
            'blend_mode': self.config.blend_mode,
            'apply_morphology': self.config.apply_morphology,
            'morphology_kernel_size': self.config.morphology_kernel_size,
            'dilate_mask': self.config.dilate_mask,
            'dilation_iterations': self.config.dilation_iterations,
            'dilation_kernel_size': self.config.dilation_kernel_size,
            'feather_edges': self.config.feather_edges,
            'feather_amount': self.config.feather_amount,
            'verbose': False,  # Disable per-file logging in batch mode
            'num_cpu_threads': self.config.num_cpu_threads,
        }
        
        work_items = []
        add_mask_path = None
        if self.additional_mask is not None:
            # Save mask to temp file if not already a path
            import tempfile
            import os
            fd, add_mask_path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            cv2.imwrite(add_mask_path, (self.additional_mask * 255).astype(np.uint8))
        for input_file in files_to_process:
            output_file = input_file.parent / f"{input_file.stem}_mask{input_file.suffix}"
            work_items.append((str(input_file), str(output_file), config_dict, add_mask_path))
        
        # Process with worker pool
        total = len(work_items)
        successful = 0
        failed = 0
        total_time = 0.0
        completed = 0
        
        # For GPU: use fewer workers since GPU is shared
        # For CPU-only: use all workers
        actual_workers = min(self.num_workers, total)
        
        # Determine number of CPU threads per worker
        import os
        cpu_threads = self.config.num_cpu_threads if self.config.num_cpu_threads > 0 else max(1, os.cpu_count() - 1)
        
        # Print batch info once at start
        device_info = "GPU" if self.config.device != 'cpu' else "CPU"
        print(f"Processing {total} images with {actual_workers} worker(s), {cpu_threads} CPU threads, using {self.config.model_name} on {device_info}")
        
        # Use spawn context for ProcessPoolExecutor to avoid CUDA fork issues
        with ProcessPoolExecutor(max_workers=actual_workers, mp_context=ctx) as executor:
            futures = {
                executor.submit(_process_single_file, item): item[0] 
                for item in work_items
            }
            
            for future in as_completed(futures):
                input_path, success, detections, proc_time, error = future.result()
                completed += 1
                
                if success:
                    successful += 1
                    total_time += proc_time
                else:
                    failed += 1
                
                # Progress callback
                if self._progress_callback:
                    filename = Path(input_path).name
                    progress = completed / total
                    msg = f"Completed {completed}/{total}"
                    self._progress_callback(filename, progress, msg)
                
                # File callback
                if file_callback:
                    file_callback(Path(input_path).name, success, detections, proc_time)
        
        return {
            'total': total + skipped_count,
            'processed': total,
            'successful': successful,
            'failed': failed,
            'skipped': skipped_count,
            'total_time': total_time,
            'avg_time': total_time / successful if successful > 0 else 0.0
        }

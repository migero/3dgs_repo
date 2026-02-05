"""
Main Window for 360 Mask Generator
Qt5 GUI for generating segmentation masks from equirectangular images.
"""

import sys
import os
from pathlib import Path
from typing import Optional
import numpy as np
import cv2

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QProgressBar, QGroupBox, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QSlider, QScrollArea,
    QSplitter, QListWidget, QListWidgetItem, QMessageBox, QStatusBar,
    QTabWidget, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QImage, QFont

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pipeline import (
    MaskGenerationPipeline, PipelineConfig, PipelineResult,
    create_default_pipeline, create_fast_pipeline, create_accurate_pipeline
)
from core.yolo_segmenter import COCO_CLASSES, DEFAULT_MOVING_CLASSES


class ProcessingThread(QThread):
    """Background thread for running mask generation."""
    
    progress = pyqtSignal(str, float)  # message, progress (0-1)
    finished = pyqtSignal(object)  # PipelineResult
    error = pyqtSignal(str)  # error message
    
    def __init__(self, pipeline: MaskGenerationPipeline, image: np.ndarray, additional_mask: Optional[np.ndarray] = None):
        super().__init__()
        self.pipeline = pipeline
        self.image = image
        self.additional_mask = additional_mask
    
    def run(self):
        try:
            self.pipeline.set_progress_callback(
                lambda msg, prog: self.progress.emit(msg, prog)
            )
            result = self.pipeline.process(self.image, additional_mask=self.additional_mask)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class BatchProcessingThread(QThread):
    """Background thread for batch processing a folder of images using parallel workers."""
    
    progress = pyqtSignal(str, float)  # message, progress (0-1)
    file_completed = pyqtSignal(str, int, int)  # filename, detections, success count
    finished = pyqtSignal(int, int, float)  # total processed, successful, total time
    error = pyqtSignal(str)  # error message
    
    def __init__(self, config: 'PipelineConfig', folder_path: str, num_workers: int = None, additional_mask: Optional[np.ndarray] = None):
        super().__init__()
        self.config = config
        self.folder_path = folder_path
        self.num_workers = num_workers
        self.additional_mask = additional_mask
        self._cancelled = False
    
    def cancel(self):
        self._cancelled = True
    
    def run(self):
        try:
            from core.pipeline import BatchProcessor
            
            # Create batch processor with parallel workers
            batch_processor = BatchProcessor(self.config, num_workers=self.num_workers, additional_mask=self.additional_mask)
            
            self.progress.emit(
                f"Starting batch processing with {batch_processor.num_workers} workers...",
                0.0
            )
            
            successful_count = 0
            
            def file_callback(filename, success, detections, proc_time):
                nonlocal successful_count
                if success:
                    successful_count += 1
                self.file_completed.emit(filename, detections if success else -1, successful_count)
            
            def progress_callback(filename, overall_progress, msg):
                self.progress.emit(msg, overall_progress)
            
            batch_processor.set_progress_callback(progress_callback)
            
            # Process folder
            summary = batch_processor.process_folder(
                self.folder_path, 
                file_callback=file_callback
            )
            
            self.progress.emit("Batch complete!", 1.0)
            self.finished.emit(summary['total'], summary['successful'], summary['total_time'])
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class ImageLabel(QLabel):
    """Custom label for displaying images with zoom support."""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 200)
        self.setStyleSheet("background-color: #2d2d2d; border: 1px solid #555;")
        self._pixmap = None
    
    def setImage(self, image: np.ndarray):
        """Set image from numpy array (BGR format)."""
        if image is None:
            self.clear()
            return
        
        # Convert BGR to RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif len(image.shape) == 2:
            # Grayscale/mask - convert to RGB
            image = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        
        h, w = image.shape[:2]
        bytes_per_line = 3 * w
        qimg = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self._pixmap = QPixmap.fromImage(qimg)
        self._updateDisplay()
    
    def _updateDisplay(self):
        if self._pixmap:
            scaled = self._pixmap.scaled(
                self.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            super().setPixmap(scaled)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._updateDisplay()


class MaskGeneratorWindow(QMainWindow):
    """Main window for the 360 Mask Generator application."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("360 Mask Generator")
        self.setMinimumSize(1200, 800)
        
        # State
        self.current_image: Optional[np.ndarray] = None
        self.current_result: Optional[PipelineResult] = None
        self.pipeline: Optional[MaskGenerationPipeline] = None
        self.processing_thread: Optional[ProcessingThread] = None
        self.batch_thread: Optional[BatchProcessingThread] = None
        self.additional_mask: Optional[np.ndarray] = None
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        
        # Initialize with default pipeline
        self._create_pipeline()
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        left_panel = self._create_left_panel()
        
        # Right panel - Image display
        right_panel = self._create_right_panel()
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 850])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Show device info on startup
        self._update_device_info()
    
    def _update_device_info(self):
        """Update status bar with device information."""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                self.status_bar.showMessage(f"Ready. Using GPU: {gpu_name}")
            else:
                self.status_bar.showMessage("Ready. Using CPU (install CUDA PyTorch for GPU acceleration)")
        except:
            self.status_bar.showMessage("Ready. Load an equirectangular image to begin.")
    
    def _create_left_panel(self) -> QWidget:
        """Create the left control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # File controls
        file_group = QGroupBox("File")
        file_layout = QVBoxLayout(file_group)
        
        self.load_btn = QPushButton("📂 Load Image")
        self.batch_btn = QPushButton("📁 Batch Process Folder")
        self.mask_input_btn = QPushButton("➕ Add Input Mask")
        self.save_btn = QPushButton("💾 Save Mask")
        self.save_btn.setEnabled(False)
        
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.batch_btn)
        file_layout.addWidget(self.mask_input_btn)
        file_layout.addWidget(self.save_btn)
        layout.addWidget(file_group)
        
        # Pipeline preset
        preset_group = QGroupBox("Pipeline Preset")
        preset_layout = QVBoxLayout(preset_group)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Default (Balanced)", "Fast", "Accurate"])
        preset_layout.addWidget(self.preset_combo)
        layout.addWidget(preset_group)
        
        # View settings
        view_group = QGroupBox("View Settings")
        view_layout = QGridLayout(view_group)
        
        view_layout.addWidget(QLabel("Horizontal Views:"), 0, 0)
        self.num_views_spin = QSpinBox()
        self.num_views_spin.setRange(4, 16)
        self.num_views_spin.setValue(8)
        view_layout.addWidget(self.num_views_spin, 0, 1)
        
        view_layout.addWidget(QLabel("Pitch Levels:"), 1, 0)
        self.pitch_levels_spin = QSpinBox()
        self.pitch_levels_spin.setRange(1, 5)
        self.pitch_levels_spin.setValue(1)
        self.pitch_levels_spin.setToolTip("1 = horizon only, 3 = include up/down views")
        view_layout.addWidget(self.pitch_levels_spin, 1, 1)
        
        view_layout.addWidget(QLabel("Field of View:"), 2, 0)
        self.fov_spin = QSpinBox()
        self.fov_spin.setRange(60, 120)
        self.fov_spin.setValue(90)
        self.fov_spin.setSuffix("°")
        view_layout.addWidget(self.fov_spin, 2, 1)
        
        layout.addWidget(view_group)
        
        # Detection settings
        detect_group = QGroupBox("Detection Settings")
        detect_layout = QGridLayout(detect_group)
        
        # Segmenter type selection
        detect_layout.addWidget(QLabel("Segmenter:"), 0, 0)
        self.segmenter_combo = QComboBox()
        segmenter_options = ["YOLO (Fast, GPU-optimized)"]
        
        # Check if Mask2Former is available
        try:
            from core.mask2former_segmenter import is_mask2former_available
            if is_mask2former_available():
                segmenter_options.append("Mask2Former (High quality, slower)")
        except ImportError:
            pass
        
        self.segmenter_combo.addItems(segmenter_options)
        detect_layout.addWidget(self.segmenter_combo, 0, 1)
        
        detect_layout.addWidget(QLabel("Model:"), 1, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "yolo11n-seg.pt (Fast)",
            "yolo11s-seg.pt (Small)",
            "yolo11m-seg.pt (Medium)",
            "yolo11l-seg.pt (Large)",
            "yolo11x-seg.pt (XLarge)",
            "yolo26n-seg.pt (26 Nano - Fast)",
            "yolo26s-seg.pt (26 Small)",
            "yolo26m-seg.pt (26 Medium)",
            "yolo26l-seg.pt (26 Large)",
            "yolo26x-seg.pt (26 XLarge)"
        ])
        detect_layout.addWidget(self.model_combo, 1, 1)
        
        detect_layout.addWidget(QLabel("Confidence:"), 2, 0)
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.1, 0.9)
        self.confidence_spin.setValue(0.35)  # Higher default to reduce false positives
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setToolTip("Higher values reduce false positives (e.g., posters detected as people)")
        detect_layout.addWidget(self.confidence_spin, 2, 1)
        
        layout.addWidget(detect_group)
        
        # Target classes
        classes_group = QGroupBox("Target Classes")
        classes_layout = QVBoxLayout(classes_group)
        
        self.classes_list = QListWidget()
        self.classes_list.setMaximumHeight(150)
        
        for cls in COCO_CLASSES:
            item = QListWidgetItem(cls)
            item.setCheckState(
                Qt.Checked if cls in DEFAULT_MOVING_CLASSES else Qt.Unchecked
            )
            self.classes_list.addItem(item)
        
        classes_layout.addWidget(self.classes_list)
        
        # Quick select buttons
        quick_btns = QHBoxLayout()
        self.select_all_btn = QPushButton("All")
        self.select_none_btn = QPushButton("None")
        self.select_moving_btn = QPushButton("Moving")
        quick_btns.addWidget(self.select_all_btn)
        quick_btns.addWidget(self.select_none_btn)
        quick_btns.addWidget(self.select_moving_btn)
        classes_layout.addLayout(quick_btns)
        
        layout.addWidget(classes_group)
        
        # Post-processing
        post_group = QGroupBox("Post-processing")
        post_layout = QVBoxLayout(post_group)
        
        self.dilate_check = QCheckBox("Dilate mask")
        self.dilate_check.setChecked(True)
        post_layout.addWidget(self.dilate_check)
        
        self.feather_check = QCheckBox("Feather edges")
        self.feather_check.setChecked(True)
        post_layout.addWidget(self.feather_check)
        
        layout.addWidget(post_group)
        
        # Batch processing settings
        batch_group = QGroupBox("Batch Processing")
        batch_layout = QGridLayout(batch_group)
        
        batch_layout.addWidget(QLabel("Workers:"), 0, 0)
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 32)
        import os
        default_workers = max(1, os.cpu_count() - 1) if os.cpu_count() else 4
        self.workers_spin.setValue(default_workers)
        self.workers_spin.setToolTip("Number of parallel worker processes for batch processing")
        batch_layout.addWidget(self.workers_spin, 0, 1)
        
        layout.addWidget(batch_group)
        
        # Process button
        self.process_btn = QPushButton("🔍 Generate Mask")
        self.process_btn.setEnabled(False)
        self.process_btn.setMinimumHeight(40)
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:disabled {
                background-color: #888;
            }
            QPushButton:hover:enabled {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.process_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)
        
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create the right image display panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Original image tab
        original_tab = QWidget()
        original_layout = QVBoxLayout(original_tab)
        self.original_label = ImageLabel()
        self.original_label.setText("Load an equirectangular image")
        original_layout.addWidget(self.original_label)
        self.tab_widget.addTab(original_tab, "Original")
        
        # Mask tab
        mask_tab = QWidget()
        mask_layout = QVBoxLayout(mask_tab)
        self.mask_label = ImageLabel()
        self.mask_label.setText("Mask will appear here")
        mask_layout.addWidget(self.mask_label)
        self.tab_widget.addTab(mask_tab, "Mask")
        
        # Overlay tab
        overlay_tab = QWidget()
        overlay_layout = QVBoxLayout(overlay_tab)
        self.overlay_label = ImageLabel()
        self.overlay_label.setText("Overlay will appear here")
        overlay_layout.addWidget(self.overlay_label)
        
        # Overlay opacity slider
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Mask Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)
        opacity_layout.addWidget(self.opacity_slider)
        overlay_layout.addLayout(opacity_layout)
        
        self.tab_widget.addTab(overlay_tab, "Overlay")
        
        # Perspective views tab
        views_tab = QWidget()
        views_layout = QVBoxLayout(views_tab)
        self.views_scroll = QScrollArea()
        self.views_scroll.setWidgetResizable(True)
        self.views_label = ImageLabel()
        self.views_label.setText("Perspective views will appear here")
        self.views_scroll.setWidget(self.views_label)
        views_layout.addWidget(self.views_scroll)
        self.tab_widget.addTab(views_tab, "Perspective Views")
        
        layout.addWidget(self.tab_widget)
        
        # Info panel
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.StyledPanel)
        info_layout = QHBoxLayout(info_frame)
        
        self.info_label = QLabel("No image loaded")
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_frame)
        
        return panel
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.load_btn.clicked.connect(self._load_image)
        self.batch_btn.clicked.connect(self._batch_process)
        self.mask_input_btn.clicked.connect(self._select_input_mask)
        self.save_btn.clicked.connect(self._save_mask)
        self.process_btn.clicked.connect(self._process_image)
        
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        self.opacity_slider.valueChanged.connect(self._update_overlay)
        
        # Connect segmenter change to pipeline recreation
        if hasattr(self, 'segmenter_combo'):
            self.segmenter_combo.currentIndexChanged.connect(self._create_pipeline)
        
        self.select_all_btn.clicked.connect(self._select_all_classes)
        self.select_none_btn.clicked.connect(self._select_no_classes)
        self.select_moving_btn.clicked.connect(self._select_moving_classes)
    
    def _create_pipeline(self):
        """Create the processing pipeline based on current settings."""
        # Get selected classes
        target_classes = []
        for i in range(self.classes_list.count()):
            item = self.classes_list.item(i)
            if item.checkState() == Qt.Checked:
                target_classes.append(item.text())
        
        # Get model name
        model_text = self.model_combo.currentText()
        model_name = model_text.split(" ")[0]
        
        # Determine segmenter type
        segmenter_type = "yolo"  # Default
        if hasattr(self, 'segmenter_combo'):
            segmenter_text = self.segmenter_combo.currentText()
            if "Mask2Former" in segmenter_text:
                segmenter_type = "mask2former"
        
        config = PipelineConfig(
            num_horizontal_views=self.num_views_spin.value(),
            num_pitch_levels=self.pitch_levels_spin.value(),
            fov=float(self.fov_spin.value()),
            model_name=model_name,
            target_classes=target_classes,
            confidence_threshold=self.confidence_spin.value(),
            dilate_mask=self.dilate_check.isChecked(),
            feather_edges=self.feather_check.isChecked(),
            segmenter_type=segmenter_type
        )
        
        self.pipeline = MaskGenerationPipeline(config)
    
    def _on_preset_changed(self, index: int):
        """Handle preset selection change."""
        if index == 0:  # Default
            self.num_views_spin.setValue(8)
            self.pitch_levels_spin.setValue(1)
            self.fov_spin.setValue(90)
            self.model_combo.setCurrentIndex(0)
        elif index == 1:  # Fast
            self.num_views_spin.setValue(4)
            self.pitch_levels_spin.setValue(1)
            self.fov_spin.setValue(90)
            self.model_combo.setCurrentIndex(0)
        elif index == 2:  # Accurate
            self.num_views_spin.setValue(12)
            self.pitch_levels_spin.setValue(3)
            self.fov_spin.setValue(75)
            self.model_combo.setCurrentIndex(2)
    
    def _load_image(self):
        """Load an equirectangular image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Equirectangular Image",
            "",
            "Images (*.png *.jpg *.jpeg *.tiff *.bmp);;All Files (*)"
        )
        
        if file_path:
            self.current_image = cv2.imread(file_path)
            
            if self.current_image is None:
                QMessageBox.warning(self, "Error", "Could not load image")
                return
            
            # Display image
            self.original_label.setImage(self.current_image)
            
            # Update info
            h, w = self.current_image.shape[:2]
            self.info_label.setText(f"Image: {Path(file_path).name} | Size: {w}x{h}")
            
            # Enable processing
            self.process_btn.setEnabled(True)
            self.current_result = None
            self.save_btn.setEnabled(False)
            
            self.status_bar.showMessage(f"Loaded: {file_path}")
    
    def _select_input_mask(self):
        """Open file dialog to select an additional input mask image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Additional Input Mask (360 equirectangular)",
            "",
            "Images (*.png *.jpg *.jpeg *.tiff *.bmp);;All Files (*)"
        )
        if file_path:
            mask = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if mask is None:
                QMessageBox.warning(self, "Error", "Could not load mask image")
                return
            self.additional_mask = mask
            self.status_bar.showMessage(f"Loaded additional mask: {file_path}")
        else:
            self.additional_mask = None
            self.status_bar.showMessage("No additional mask selected")
    
    def _save_mask(self):
        """Save the generated mask."""
        if self.current_result is None:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Mask",
            "mask.png",
            "PNG Images (*.png);;All Files (*)"
        )
        
        if file_path:
            self.current_result.save_mask(file_path)
            self.status_bar.showMessage(f"Saved mask to: {file_path}")
    
    def _process_image(self):
        """Process the current image."""
        if self.current_image is None:
            return
        
        # Create pipeline with current settings
        self._create_pipeline()
        
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start processing thread
        self.processing_thread = ProcessingThread(self.pipeline, self.current_image, self.additional_mask)
        self.processing_thread.progress.connect(self._on_progress)
        self.processing_thread.finished.connect(self._on_processing_finished)
        self.processing_thread.error.connect(self._on_processing_error)
        self.processing_thread.start()
    
    def _on_progress(self, message: str, progress: float):
        """Handle progress updates."""
        self.progress_bar.setValue(int(progress * 100))
        self.progress_label.setText(message)
    
    def _on_processing_finished(self, result: PipelineResult):
        """Handle processing completion."""
        self.current_result = result
        
        # Update UI
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self.process_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        
        # Display results
        self.mask_label.setImage(result.mask)
        self._update_overlay()
        
        # Show perspective views
        if result.perspective_views and result.segmentation_results:
            views_image = self.pipeline.visualize_views(
                result.perspective_views,
                result.segmentation_results
            )
            self.views_label.setImage(views_image)
        
        # Update info
        summary = self.pipeline.get_detection_summary(result)
        info_text = (
            f"Detections: {summary['total_detections']} | "
            f"Mask Coverage: {summary['mask_coverage']:.1f}% | "
            f"Time: {summary['processing_time']:.1f}s"
        )
        self.info_label.setText(info_text)
        
        # Switch to mask tab
        self.tab_widget.setCurrentIndex(1)
        
        self.status_bar.showMessage(
            f"Processing complete. Found {summary['total_detections']} objects in {summary['processing_time']:.1f}s"
        )
    
    def _on_processing_error(self, error: str):
        """Handle processing errors."""
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self.process_btn.setEnabled(True)
        
        QMessageBox.critical(self, "Error", f"Processing failed:\n{error}")
        self.status_bar.showMessage(f"Error: {error}")
    
    def _update_overlay(self):
        """Update the overlay visualization."""
        if self.current_image is None or self.current_result is None:
            return
        
        # Create overlay with mask
        opacity = self.opacity_slider.value() / 100.0
        overlay = self.current_image.copy()
        
        # Apply mask as red overlay
        mask = self.current_result.mask
        mask_3ch = np.stack([mask * 0, mask * 0, mask * 255], axis=-1)  # Red
        overlay = (overlay * (1 - opacity * mask[:, :, np.newaxis]) + 
                  mask_3ch * opacity).astype(np.uint8)
        
        self.overlay_label.setImage(overlay)
    
    def _select_all_classes(self):
        """Select all classes."""
        for i in range(self.classes_list.count()):
            self.classes_list.item(i).setCheckState(Qt.Checked)
    
    def _select_no_classes(self):
        """Deselect all classes."""
        for i in range(self.classes_list.count()):
            self.classes_list.item(i).setCheckState(Qt.Unchecked)
    
    def _select_moving_classes(self):
        """Select only moving object classes."""
        for i in range(self.classes_list.count()):
            item = self.classes_list.item(i)
            item.setCheckState(
                Qt.Checked if item.text() in DEFAULT_MOVING_CLASSES else Qt.Unchecked
            )
    
    def _batch_process(self):
        """Open folder dialog and batch process all images."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with Equirectangular Images",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not folder_path:
            return
        
        # Create pipeline with current settings (to get the config)
        self._create_pipeline()
        
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.batch_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start batch processing thread with config (uses parallel workers)
        num_workers = self.workers_spin.value()
        self.batch_thread = BatchProcessingThread(self.pipeline.config, folder_path, num_workers, self.additional_mask)
        self.batch_thread.progress.connect(self._on_batch_progress)
        self.batch_thread.file_completed.connect(self._on_batch_file_completed)
        self.batch_thread.finished.connect(self._on_batch_finished)
        self.batch_thread.error.connect(self._on_batch_error)
        self.batch_thread.start()
        
        self.status_bar.showMessage(f"Batch processing: {folder_path}")
    
    def _on_batch_progress(self, message: str, progress: float):
        """Handle batch progress updates."""
        self.progress_bar.setValue(int(progress * 100))
        self.progress_label.setText(message)
    
    def _on_batch_file_completed(self, filename: str, detections: int, successful: int):
        """Handle completion of a single file in batch."""
        if detections >= 0:
            self.status_bar.showMessage(f"Completed: {filename} ({detections} detections)")
        else:
            self.status_bar.showMessage(f"Failed: {filename}")
    
    def _on_batch_finished(self, total: int, successful: int, total_time: float):
        """Handle batch processing completion."""
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self.process_btn.setEnabled(True)
        self.batch_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        
        avg_time = total_time / successful if successful > 0 else 0
        
        QMessageBox.information(
            self,
            "Batch Complete",
            f"Batch processing complete!\n\n"
            f"Processed: {successful}/{total} images\n"
            f"Total time: {total_time:.1f}s\n"
            f"Average per image: {avg_time:.1f}s"
        )
        
        self.status_bar.showMessage(
            f"Batch complete: {successful}/{total} images processed in {total_time:.1f}s"
        )
    
    def _on_batch_error(self, error: str):
        """Handle batch processing errors."""
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self.process_btn.setEnabled(True)
        self.batch_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        
        QMessageBox.critical(self, "Batch Error", f"Batch processing failed:\n{error}")
        self.status_bar.showMessage(f"Batch error: {error}")

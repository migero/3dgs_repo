"""
Main Window for Video Mask Generator
Qt5 GUI for generating segmentation masks from regular videos.
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

from core.video_processor import VideoMaskProcessor, ProcessorConfig
from core.yolo_segmenter import COCO_CLASSES, DEFAULT_MOVING_CLASSES, SegmentationResult


class ProcessingThread(QThread):
    """Background thread for running video processing."""
    
    progress = pyqtSignal(str, float, int, int)  # message, progress, current, total
    finished = pyqtSignal(dict)  # result summary
    error = pyqtSignal(str)  # error message
    
    def __init__(
        self, 
        processor: VideoMaskProcessor, 
        video_path: str, 
        output_dir: str
    ):
        super().__init__()
        self.processor = processor
        self.video_path = video_path
        self.output_dir = output_dir
    
    def run(self):
        try:
            result = self.processor.process_video(
                self.video_path,
                self.output_dir,
                progress_callback=lambda msg, prog, cur, tot: self.progress.emit(msg, prog, cur, tot)
            )
            self.finished.emit(result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class ImageProcessingThread(QThread):
    """Background thread for processing a single image."""
    
    finished = pyqtSignal(object, np.ndarray)  # result, overlay
    error = pyqtSignal(str)
    
    def __init__(self, processor: VideoMaskProcessor, image: np.ndarray):
        super().__init__()
        self.processor = processor
        self.image = image
    
    def run(self):
        try:
            result = self.processor.process_image(self.image)
            overlay = self.processor.create_overlay(self.image, result)
            self.finished.emit(result, overlay)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class FolderProcessingThread(QThread):
    """Background thread for batch processing a folder of images."""
    
    progress = pyqtSignal(str, float)  # message, progress
    finished = pyqtSignal(dict)  # result summary
    error = pyqtSignal(str)
    
    def __init__(
        self, 
        processor: VideoMaskProcessor, 
        input_folder: str, 
        output_folder: str
    ):
        super().__init__()
        self.processor = processor
        self.input_folder = input_folder
        self.output_folder = output_folder
    
    def run(self):
        try:
            result = self.processor.process_folder(
                self.input_folder,
                self.output_folder,
                progress_callback=lambda msg, prog: self.progress.emit(msg, prog)
            )
            self.finished.emit(result)
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
            if image.dtype == np.float32 or image.dtype == np.float64:
                image = (image * 255).astype(np.uint8)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
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


class VideoMaskGeneratorWindow(QMainWindow):
    """Main window for the Video Mask Generator application."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Video Mask Generator")
        self.setMinimumSize(1200, 800)
        
        # State
        self.current_image: Optional[np.ndarray] = None
        self.current_result: Optional[SegmentationResult] = None
        self.current_overlay: Optional[np.ndarray] = None
        self.processor: Optional[VideoMaskProcessor] = None
        self.processing_thread: Optional[QThread] = None
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        
        # Initialize processor
        self._create_processor()
    
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
            self.status_bar.showMessage("Ready. Load a video or image to begin.")
    
    def _create_left_panel(self) -> QWidget:
        """Create the left control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # File controls
        file_group = QGroupBox("File")
        file_layout = QVBoxLayout(file_group)
        
        self.load_image_btn = QPushButton("🖼️ Load Image")
        self.load_video_btn = QPushButton("🎬 Load Video")
        self.batch_btn = QPushButton("📁 Batch Process Folder")
        self.save_btn = QPushButton("💾 Save Mask")
        self.save_btn.setEnabled(False)
        
        file_layout.addWidget(self.load_image_btn)
        file_layout.addWidget(self.load_video_btn)
        file_layout.addWidget(self.batch_btn)
        file_layout.addWidget(self.save_btn)
        layout.addWidget(file_group)
        
        # Video settings
        video_group = QGroupBox("Video Settings")
        video_layout = QGridLayout(video_group)
        
        video_layout.addWidget(QLabel("Extract FPS:"), 0, 0)
        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setRange(0.1, 60.0)
        self.fps_spin.setValue(1.0)
        self.fps_spin.setSingleStep(0.5)
        self.fps_spin.setToolTip("Frames per second to extract from video")
        video_layout.addWidget(self.fps_spin, 0, 1)
        
        layout.addWidget(video_group)
        
        # Detection settings
        detect_group = QGroupBox("Detection Settings")
        detect_layout = QGridLayout(detect_group)
        
        detect_layout.addWidget(QLabel("Model:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "yolo11n-seg.pt (Fast)",
            "yolo11s-seg.pt (Small)",
            "yolo11m-seg.pt (Medium)",
            "yolo11l-seg.pt (Large)",
            "yolo11x-seg.pt (XLarge)"
        ])
        detect_layout.addWidget(self.model_combo, 0, 1)
        
        detect_layout.addWidget(QLabel("Confidence:"), 1, 0)
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.1, 0.9)
        self.confidence_spin.setValue(0.35)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setToolTip("Higher values reduce false positives")
        detect_layout.addWidget(self.confidence_spin, 1, 1)
        
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
        
        self.save_overlay_check = QCheckBox("Save overlay images")
        self.save_overlay_check.setChecked(False)
        post_layout.addWidget(self.save_overlay_check)
        
        layout.addWidget(post_group)
        
        # Process button (for single image)
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
        self.original_label.setText("Load an image or video to begin")
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
        self.tab_widget.addTab(overlay_tab, "Overlay")
        
        layout.addWidget(self.tab_widget)
        
        # Info panel
        info_group = QGroupBox("Detection Info")
        info_layout = QVBoxLayout(info_group)
        self.info_label = QLabel("No detections yet")
        info_layout.addWidget(self.info_label)
        layout.addWidget(info_group)
        
        return panel
    
    def _setup_connections(self):
        """Connect signals and slots."""
        self.load_image_btn.clicked.connect(self._load_image)
        self.load_video_btn.clicked.connect(self._load_video)
        self.batch_btn.clicked.connect(self._batch_process)
        self.save_btn.clicked.connect(self._save_mask)
        self.process_btn.clicked.connect(self._process_image)
        
        # Class selection
        self.select_all_btn.clicked.connect(self._select_all_classes)
        self.select_none_btn.clicked.connect(self._select_no_classes)
        self.select_moving_btn.clicked.connect(self._select_moving_classes)
        
        # Settings changes
        self.model_combo.currentIndexChanged.connect(self._on_settings_changed)
        self.confidence_spin.valueChanged.connect(self._on_settings_changed)
        self.dilate_check.stateChanged.connect(self._on_settings_changed)
        self.feather_check.stateChanged.connect(self._on_settings_changed)
    
    def _create_processor(self):
        """Create the video mask processor with current settings."""
        config = ProcessorConfig(
            model_name=self._get_model_name(),
            target_classes=self._get_selected_classes(),
            confidence_threshold=self.confidence_spin.value(),
            dilate_mask=self.dilate_check.isChecked(),
            feather_edges=self.feather_check.isChecked(),
            fps=self.fps_spin.value(),
            save_overlay=self.save_overlay_check.isChecked()
        )
        self.processor = VideoMaskProcessor(config)
    
    def _get_model_name(self) -> str:
        """Get selected model name."""
        models = [
            "yolo11n-seg.pt",
            "yolo11s-seg.pt",
            "yolo11m-seg.pt",
            "yolo11l-seg.pt",
            "yolo11x-seg.pt"
        ]
        return models[self.model_combo.currentIndex()]
    
    def _get_selected_classes(self) -> list:
        """Get list of selected class names."""
        classes = []
        for i in range(self.classes_list.count()):
            item = self.classes_list.item(i)
            if item.checkState() == Qt.Checked:
                classes.append(item.text())
        return classes
    
    def _on_settings_changed(self):
        """Handle settings changes."""
        self._create_processor()
    
    def _select_all_classes(self):
        """Select all classes."""
        for i in range(self.classes_list.count()):
            self.classes_list.item(i).setCheckState(Qt.Checked)
        self._on_settings_changed()
    
    def _select_no_classes(self):
        """Deselect all classes."""
        for i in range(self.classes_list.count()):
            self.classes_list.item(i).setCheckState(Qt.Unchecked)
        self._on_settings_changed()
    
    def _select_moving_classes(self):
        """Select default moving object classes."""
        for i in range(self.classes_list.count()):
            item = self.classes_list.item(i)
            item.setCheckState(
                Qt.Checked if item.text() in DEFAULT_MOVING_CLASSES else Qt.Unchecked
            )
        self._on_settings_changed()
    
    def _load_image(self):
        """Load an image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.tiff *.webp);;All Files (*)"
        )
        
        if file_path:
            image = cv2.imread(file_path)
            if image is not None:
                self.current_image = image
                self.original_label.setImage(image)
                self.process_btn.setEnabled(True)
                self.save_btn.setEnabled(False)
                self.current_result = None
                self.current_overlay = None
                self.mask_label.setText("Click 'Generate Mask' to process")
                self.overlay_label.setText("Click 'Generate Mask' to process")
                self.info_label.setText(f"Loaded: {Path(file_path).name}")
                self.status_bar.showMessage(f"Loaded image: {file_path}")
            else:
                QMessageBox.warning(self, "Error", f"Could not load image: {file_path}")
    
    def _load_video(self):
        """Load a video file for processing."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            "",
            "Videos (*.mp4 *.avi *.mov *.mkv *.webm *.m4v);;All Files (*)"
        )
        
        if file_path:
            # Ask for output directory
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Output Directory for Masks",
                str(Path(file_path).parent)
            )
            
            if output_dir:
                self._process_video(file_path, output_dir)
    
    def _process_video(self, video_path: str, output_dir: str):
        """Process a video file."""
        self._create_processor()
        self.processor.config.fps = self.fps_spin.value()
        self.processor.config.save_overlay = self.save_overlay_check.isChecked()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")
        
        # Disable controls during processing
        self._set_controls_enabled(False)
        
        self.processing_thread = ProcessingThread(
            self.processor,
            video_path,
            output_dir
        )
        self.processing_thread.progress.connect(self._on_video_progress)
        self.processing_thread.finished.connect(self._on_video_finished)
        self.processing_thread.error.connect(self._on_processing_error)
        self.processing_thread.start()
    
    def _on_video_progress(self, msg: str, progress: float, current: int, total: int):
        """Handle video processing progress."""
        self.progress_bar.setValue(int(progress * 100))
        self.progress_label.setText(f"{msg} ({current}/{total})")
    
    def _on_video_finished(self, result: dict):
        """Handle video processing completion."""
        self.progress_bar.setVisible(False)
        self._set_controls_enabled(True)
        
        QMessageBox.information(
            self,
            "Processing Complete",
            f"Video processing complete!\n\n"
            f"Total frames: {result['total_frames']}\n"
            f"Frames with detections: {result['frames_with_detections']}\n"
            f"Total detections: {result['total_detections']}\n"
            f"Processing time: {result['processing_time']:.1f}s\n\n"
            f"Output saved to: {result['output_dir']}"
        )
        
        self.status_bar.showMessage(f"Processed {result['total_frames']} frames")
        self.progress_label.setText("")
    
    def _batch_process(self):
        """Batch process a folder of images."""
        input_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Input Folder with Images"
        )
        
        if not input_folder:
            return
        
        output_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder for Masks"
        )
        
        if not output_folder:
            return
        
        self._create_processor()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting batch processing...")
        
        self._set_controls_enabled(False)
        
        self.processing_thread = FolderProcessingThread(
            self.processor,
            input_folder,
            output_folder
        )
        self.processing_thread.progress.connect(self._on_batch_progress)
        self.processing_thread.finished.connect(self._on_batch_finished)
        self.processing_thread.error.connect(self._on_processing_error)
        self.processing_thread.start()
    
    def _on_batch_progress(self, msg: str, progress: float):
        """Handle batch processing progress."""
        self.progress_bar.setValue(int(progress * 100))
        self.progress_label.setText(msg)
    
    def _on_batch_finished(self, result: dict):
        """Handle batch processing completion."""
        self.progress_bar.setVisible(False)
        self._set_controls_enabled(True)
        
        QMessageBox.information(
            self,
            "Batch Processing Complete",
            f"Batch processing complete!\n\n"
            f"Total images: {result['total_images']}\n"
            f"Images with detections: {result['images_with_detections']}\n"
            f"Total detections: {result['total_detections']}\n"
            f"Processing time: {result['processing_time']:.1f}s\n\n"
            f"Output saved to: {result['output_folder']}"
        )
        
        self.status_bar.showMessage(f"Processed {result['total_images']} images")
        self.progress_label.setText("")
    
    def _process_image(self):
        """Process the currently loaded image."""
        if self.current_image is None:
            return
        
        self._create_processor()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_label.setText("Processing...")
        
        self._set_controls_enabled(False)
        
        self.processing_thread = ImageProcessingThread(
            self.processor,
            self.current_image
        )
        self.processing_thread.finished.connect(self._on_image_finished)
        self.processing_thread.error.connect(self._on_processing_error)
        self.processing_thread.start()
    
    def _on_image_finished(self, result: SegmentationResult, overlay: np.ndarray):
        """Handle image processing completion."""
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(100)
        self.progress_label.setText("")
        self._set_controls_enabled(True)
        
        self.current_result = result
        self.current_overlay = overlay
        
        # Display mask
        self.mask_label.setImage(result.mask)
        
        # Display overlay
        self.overlay_label.setImage(overlay)
        
        # Update info
        if result.num_detections > 0:
            classes_str = ", ".join(f"{name} ({conf:.2f})" 
                                    for name, conf in zip(result.class_names, result.confidences))
            self.info_label.setText(f"Detections: {result.num_detections}\n{classes_str}")
        else:
            self.info_label.setText("No detections found")
        
        self.save_btn.setEnabled(True)
        self.tab_widget.setCurrentIndex(1)  # Switch to mask tab
        self.status_bar.showMessage(f"Found {result.num_detections} detections")
    
    def _on_processing_error(self, error: str):
        """Handle processing error."""
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(100)
        self.progress_label.setText("")
        self._set_controls_enabled(True)
        
        QMessageBox.critical(self, "Processing Error", f"Error during processing:\n{error}")
        self.status_bar.showMessage("Processing failed")
    
    def _save_mask(self):
        """Save the current mask."""
        if self.current_result is None:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Mask",
            "mask.png",
            "PNG Image (*.png);;All Files (*)"
        )
        
        if file_path:
            mask_uint8 = (self.current_result.mask * 255).astype(np.uint8)
            cv2.imwrite(file_path, mask_uint8)
            
            # Also save overlay if checkbox is checked
            if self.save_overlay_check.isChecked() and self.current_overlay is not None:
                overlay_path = str(Path(file_path).stem) + "_overlay.png"
                cv2.imwrite(overlay_path, self.current_overlay)
                self.status_bar.showMessage(f"Saved mask and overlay to {file_path}")
            else:
                self.status_bar.showMessage(f"Saved mask to {file_path}")
    
    def _set_controls_enabled(self, enabled: bool):
        """Enable or disable controls during processing."""
        self.load_image_btn.setEnabled(enabled)
        self.load_video_btn.setEnabled(enabled)
        self.batch_btn.setEnabled(enabled)
        self.process_btn.setEnabled(enabled and self.current_image is not None)
        self.save_btn.setEnabled(enabled and self.current_result is not None)
        self.model_combo.setEnabled(enabled)
        self.confidence_spin.setEnabled(enabled)
        self.fps_spin.setEnabled(enabled)
        self.classes_list.setEnabled(enabled)
        self.dilate_check.setEnabled(enabled)
        self.feather_check.setEnabled(enabled)
        self.save_overlay_check.setEnabled(enabled)

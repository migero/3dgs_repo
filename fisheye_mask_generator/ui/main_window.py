"""
Main Window for Fisheye Mask Generator
Qt5 GUI for generating segmentation masks from dual fisheye images (185° FOV).
"""

import sys
import os
from pathlib import Path
from typing import Optional, Tuple
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
    FisheyeMaskGenerationPipeline, FisheyePipelineResult, PipelineConfig,
    FisheyeBatchProcessor
)
from core.fisheye_converter import FisheyeConverter, find_fisheye_pair, get_mask_output_paths
from core.yolo_segmenter import COCO_CLASSES, DEFAULT_MOVING_CLASSES


class FisheyeProcessingThread(QThread):
    """Background thread for running fisheye mask generation."""
    
    progress = pyqtSignal(str, float)  # message, progress (0-1)
    finished = pyqtSignal(object)  # FisheyePipelineResult
    error = pyqtSignal(str)  # error message
    
    def __init__(
        self, 
        pipeline: FisheyeMaskGenerationPipeline, 
        front_image: np.ndarray,
        back_image: np.ndarray
    ):
        super().__init__()
        self.pipeline = pipeline
        self.front_image = front_image
        self.back_image = back_image
    
    def run(self):
        try:
            self.pipeline.set_progress_callback(
                lambda msg, prog: self.progress.emit(msg, prog)
            )
            result = self.pipeline.process(self.front_image, self.back_image)
            self.finished.emit(result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class FisheyeBatchProcessingThread(QThread):
    """Background thread for batch processing fisheye pairs from two folders."""
    
    progress = pyqtSignal(str, float)  # message, progress (0-1)
    file_completed = pyqtSignal(str, int, int)  # filename, detections, success count
    finished = pyqtSignal(int, int, float)  # total processed, successful, total time
    error = pyqtSignal(str)  # error message
    
    def __init__(
        self, 
        config: PipelineConfig, 
        front_folder: str, 
        back_folder: str,
        output_folder: str = None,
        num_workers: int = None
    ):
        super().__init__()
        self.config = config
        self.front_folder = front_folder
        self.back_folder = back_folder
        self.output_folder = output_folder
        self.num_workers = num_workers
        self._cancelled = False
    
    def cancel(self):
        self._cancelled = True
    
    def run(self):
        try:
            batch_processor = FisheyeBatchProcessor(self.config, num_workers=self.num_workers)
            
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
            
            # Process two folders
            summary = batch_processor.process_two_folders(
                self.front_folder,
                self.back_folder,
                output_folder=self.output_folder,
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


class FisheyeMaskGeneratorWindow(QMainWindow):
    """Main window for the Fisheye Mask Generator application."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Fisheye Mask Generator (185° FOV)")
        self.setMinimumSize(1200, 800)
        
        # State
        self.front_image: Optional[np.ndarray] = None
        self.back_image: Optional[np.ndarray] = None
        self.front_path: Optional[str] = None
        self.back_path: Optional[str] = None
        self.equirect_image: Optional[np.ndarray] = None
        self.current_result: Optional[FisheyePipelineResult] = None
        self.pipeline: Optional[FisheyeMaskGenerationPipeline] = None
        self.processing_thread: Optional[FisheyeProcessingThread] = None
        self.batch_thread: Optional[FisheyeBatchProcessingThread] = None
        
        # Fisheye converter for preview
        self.fisheye_converter = FisheyeConverter()
        
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
            self.status_bar.showMessage("Ready. Load a fisheye image pair to begin.")
    
    def _create_left_panel(self) -> QWidget:
        """Create the left control panel with scrollbar."""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create content widget that will be scrollable
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # File controls
        file_group = QGroupBox("File")
        file_layout = QVBoxLayout(file_group)
        
        self.load_btn = QPushButton("📂 Load Fisheye Pair")
        self.load_btn.setToolTip("Load front fisheye image (back will be auto-detected)")
        self.load_btn.setMinimumHeight(35)
        self.load_btn.setMaximumHeight(35)
        
        self.batch_btn = QPushButton("📁 Batch Process Folder")
        self.batch_btn.setToolTip("Process all fisheye pairs in a folder")
        self.batch_btn.setMinimumHeight(35)
        self.batch_btn.setMaximumHeight(35)
        
        self.save_btn = QPushButton("💾 Save Masks")
        self.save_btn.setEnabled(False)
        self.save_btn.setMinimumHeight(35)
        self.save_btn.setMaximumHeight(35)
        
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.batch_btn)
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
        self.num_views_spin.setValue(6)
        view_layout.addWidget(self.num_views_spin, 0, 1)
        
        view_layout.addWidget(QLabel("Pitch Levels:"), 1, 0)
        self.pitch_levels_spin = QSpinBox()
        self.pitch_levels_spin.setRange(1, 5)
        self.pitch_levels_spin.setValue(2)
        self.pitch_levels_spin.setToolTip("1 = horizon only, 3 = include up/down views")
        view_layout.addWidget(self.pitch_levels_spin, 1, 1)
        
        view_layout.addWidget(QLabel("Field of View:"), 2, 0)
        self.fov_spin = QSpinBox()
        self.fov_spin.setRange(60, 120)
        self.fov_spin.setValue(90)
        self.fov_spin.setSuffix("°")
        view_layout.addWidget(self.fov_spin, 2, 1)
        
        view_layout.addWidget(QLabel("View Resolution:"), 3, 0)
        self.view_res_combo = QComboBox()
        self.view_res_combo.addItems(["640px", "800px", "1024px", "1280px"])
        self.view_res_combo.setCurrentIndex(2)  # Default to 1024px
        self.view_res_combo.setToolTip("Resolution of each perspective view")
        view_layout.addWidget(self.view_res_combo, 3, 1)
        
        self.downward_view_check = QCheckBox("Include downward perspective")
        self.downward_view_check.setChecked(False)
        view_layout.addWidget(self.downward_view_check, 4, 0, 1, 2)
        
        view_layout.addWidget(QLabel("Mask Upscale:"), 5, 0)
        self.mask_upscale_combo = QComboBox()
        self.mask_upscale_combo.addItems(["1x (Fast)", "2x (Better)", "4x (Best)"])
        self.mask_upscale_combo.setCurrentIndex(1)  # Default to 2x
        view_layout.addWidget(self.mask_upscale_combo, 5, 1)
        
        layout.addWidget(view_group)
        
        # Detection settings
        detect_group = QGroupBox("Detection Settings")
        detect_layout = QGridLayout(detect_group)
        
        detect_layout.addWidget(QLabel("Model:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "yolo26n-seg.pt (YOLO26 Nano - NEW)",
            "yolo26s-seg.pt (YOLO26 Small - NEW)",
            "yolo26m-seg.pt (YOLO26 Medium - NEW)",
            "yolo26l-seg.pt (YOLO26 Large - NEW)",
            "yolo26x-seg.pt (YOLO26 XLarge - NEW)",
            "---",
            "yolo11n-seg.pt (YOLO11 Nano)",
            "yolo11s-seg.pt (YOLO11 Small)",
            "yolo11m-seg.pt (YOLO11 Medium)",
            "yolo11l-seg.pt (YOLO11 Large)",
            "yolo11x-seg.pt (YOLO11 XLarge)",
            "---",
            "yolov10n-seg.pt (YOLOv10 Nano)",
            "yolov10s-seg.pt (YOLOv10 Small)",
            "yolov10m-seg.pt (YOLOv10 Medium)",
            "yolov10l-seg.pt (YOLOv10 Large)",
            "yolov10x-seg.pt (YOLOv10 XLarge)",
            "---",
            "yolov9c-seg.pt (YOLOv9 Compact)",
            "yolov9e-seg.pt (YOLOv9 Extended)",
            "---",
            "yolov8n-seg.pt (YOLOv8 Nano)",
            "yolov8s-seg.pt (YOLOv8 Small)",
            "yolov8m-seg.pt (YOLOv8 Medium)",
            "yolov8l-seg.pt (YOLOv8 Large)",
            "yolov8x-seg.pt (YOLOv8 XLarge)"
        ])
        self.model_combo.setCurrentIndex(4)  # Default to YOLO26 XLarge (newest and most accurate)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        detect_layout.addWidget(self.model_combo, 0, 1)
        
        detect_layout.addWidget(QLabel("Confidence:"), 1, 0)
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.1, 0.9)
        self.confidence_spin.setValue(0.35)
        self.confidence_spin.setSingleStep(0.05)
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
        self.select_all_btn.setMaximumHeight(30)
        self.select_none_btn = QPushButton("None")
        self.select_none_btn.setMaximumHeight(30)
        self.select_moving_btn = QPushButton("Moving")
        self.select_moving_btn.setMaximumHeight(30)
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
        
        # Pose Estimation
        pose_group = QGroupBox("Pose Estimation (Person Detection)")
        pose_layout = QVBoxLayout(pose_group)
        
        self.center_on_person_check = QCheckBox("Center on main person")
        self.center_on_person_check.setChecked(False)
        self.center_on_person_check.setToolTip("Find and center the view on the largest detected person")
        pose_layout.addWidget(self.center_on_person_check)
        
        self.pose_based_rotation_check = QCheckBox("Pose-based rotation adjustment")
        self.pose_based_rotation_check.setChecked(False)
        self.pose_based_rotation_check.setToolTip("Use pose keypoints to adjust rotation angle")
        pose_layout.addWidget(self.pose_based_rotation_check)
        
        self.save_pose_images_check = QCheckBox("Save pose visualization images")
        self.save_pose_images_check.setChecked(False)
        self.save_pose_images_check.setToolTip("Save debug images showing detected pose keypoints")
        pose_layout.addWidget(self.save_pose_images_check)
        
        # Pose model selection
        pose_model_layout = QHBoxLayout()
        pose_model_layout.addWidget(QLabel("Pose Model:"))
        self.pose_model_combo = QComboBox()
        self.pose_model_combo.addItems([
            "yolov8n-pose.pt (Fast)",
            "yolov8s-pose.pt (Small)",
            "yolov8m-pose.pt (Medium)",
            "yolov8l-pose.pt (Large)",
            "yolov8x-pose.pt (Most Accurate)"
        ])
        self.pose_model_combo.setCurrentIndex(0)  # Default to nano (fast)
        pose_model_layout.addWidget(self.pose_model_combo)
        pose_layout.addLayout(pose_model_layout)
        
        layout.addWidget(pose_group)
        
        # Batch processing settings
        batch_group = QGroupBox("Batch Processing")
        batch_layout = QGridLayout(batch_group)
        
        batch_layout.addWidget(QLabel("Workers:"), 0, 0)
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 32)
        default_workers = max(1, os.cpu_count() - 1) if os.cpu_count() else 4
        self.workers_spin.setValue(default_workers)
        self.workers_spin.setToolTip("Number of parallel worker processes")
        batch_layout.addWidget(self.workers_spin, 0, 1)
        
        layout.addWidget(batch_group)
        
        # Process button
        self.process_btn = QPushButton("🔍 Generate Masks")
        self.process_btn.setEnabled(False)
        self.process_btn.setMinimumHeight(45)
        self.process_btn.setMaximumHeight(45)
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
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setMaximumHeight(25)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setMaximumHeight(30)
        layout.addWidget(self.progress_label)
        
        # Set the scrollable content
        scroll_area.setWidget(panel)
        
        return scroll_area
    
    def _create_right_panel(self) -> QWidget:
        """Create the right image display panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Fisheye input tab (shows both fisheye images side by side)
        fisheye_tab = QWidget()
        fisheye_layout = QHBoxLayout(fisheye_tab)
        
        front_container = QVBoxLayout()
        front_container.addWidget(QLabel("Front Fisheye"))
        self.front_label = ImageLabel()
        self.front_label.setText("Front fisheye image")
        front_container.addWidget(self.front_label)
        fisheye_layout.addLayout(front_container)
        
        back_container = QVBoxLayout()
        back_container.addWidget(QLabel("Back Fisheye"))
        self.back_label = ImageLabel()
        self.back_label.setText("Back fisheye image")
        back_container.addWidget(self.back_label)
        fisheye_layout.addLayout(back_container)
        
        self.tab_widget.addTab(fisheye_tab, "Fisheye Input")
        
        # 360 Equirectangular tab (shows the converted 360 image)
        equirect_tab = QWidget()
        equirect_layout = QVBoxLayout(equirect_tab)
        self.equirect_label = ImageLabel()
        self.equirect_label.setText("360° equirectangular image will appear here")
        equirect_layout.addWidget(self.equirect_label)
        self.tab_widget.addTab(equirect_tab, "360° Equirectangular")
        
        # Fisheye Masks tab (shows both mask outputs side by side)
        masks_tab = QWidget()
        masks_layout = QHBoxLayout(masks_tab)
        
        front_mask_container = QVBoxLayout()
        front_mask_container.addWidget(QLabel("Front Mask"))
        self.front_mask_label = ImageLabel()
        self.front_mask_label.setText("Front fisheye mask")
        front_mask_container.addWidget(self.front_mask_label)
        masks_layout.addLayout(front_mask_container)
        
        back_mask_container = QVBoxLayout()
        back_mask_container.addWidget(QLabel("Back Mask"))
        self.back_mask_label = ImageLabel()
        self.back_mask_label.setText("Back fisheye mask")
        back_mask_container.addWidget(self.back_mask_label)
        masks_layout.addLayout(back_mask_container)
        
        self.tab_widget.addTab(masks_tab, "Fisheye Masks")
        
        # 360 Mask tab
        mask_360_tab = QWidget()
        mask_360_layout = QVBoxLayout(mask_360_tab)
        self.mask_360_label = ImageLabel()
        self.mask_360_label.setText("360° mask will appear here")
        mask_360_layout.addWidget(self.mask_360_label)
        self.tab_widget.addTab(mask_360_tab, "360° Mask")
        
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
        
        self.info_label = QLabel("No images loaded")
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_frame)
        
        return panel
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.load_btn.clicked.connect(self._load_fisheye_pair)
        self.batch_btn.clicked.connect(self._batch_process)
        self.save_btn.clicked.connect(self._save_masks)
        self.process_btn.clicked.connect(self._process_images)
        
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        self.opacity_slider.valueChanged.connect(self._update_overlay)
        
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
        # Skip separator items
        if model_text == "---":
            QMessageBox.warning(self, "Invalid Model", "Please select a valid YOLO model (not a separator).")
            return
        model_name = model_text.split(" ")[0]
        
        # Get mask upscale factor
        upscale_text = self.mask_upscale_combo.currentText()
        upscale_factor = int(upscale_text.split("x")[0])
        
        # Get view resolution
        view_res_text = self.view_res_combo.currentText()
        view_res = int(view_res_text.replace("px", ""))
        
        # Get pose model name
        pose_model_text = self.pose_model_combo.currentText()
        pose_model_name = pose_model_text.split(" ")[0]
        
        config = PipelineConfig(
            num_horizontal_views=self.num_views_spin.value(),
            num_pitch_levels=self.pitch_levels_spin.value(),
            fov=float(self.fov_spin.value()),
            view_size=(view_res, view_res),
            model_name=model_name,
            target_classes=target_classes,
            confidence_threshold=self.confidence_spin.value(),
            dilate_mask=self.dilate_check.isChecked(),
            feather_edges=self.feather_check.isChecked(),
            include_downward_view=self.downward_view_check.isChecked(),
            mask_upscale_factor=upscale_factor,
            center_on_person=self.center_on_person_check.isChecked(),
            pose_based_rotation=self.pose_based_rotation_check.isChecked(),
            save_pose_images=self.save_pose_images_check.isChecked(),
            pose_model_name=pose_model_name
        )
        
        self.pipeline = FisheyeMaskGenerationPipeline(config)
    
    def _on_model_changed(self, index: int):
        """Prevent selection of separator items in model combo."""
        if self.model_combo.currentText() == "---":
            # Skip to next valid item
            if index < self.model_combo.count() - 1:
                self.model_combo.setCurrentIndex(index + 1)
            else:
                self.model_combo.setCurrentIndex(index - 1)
    
    def _on_preset_changed(self, index: int):
        """Handle preset selection change."""
        if index == 0:  # Default
            self.num_views_spin.setValue(6)
            self.pitch_levels_spin.setValue(2)
            self.fov_spin.setValue(90)
            self.model_combo.setCurrentIndex(3)  # Large
        elif index == 1:  # Fast
            self.num_views_spin.setValue(4)
            self.pitch_levels_spin.setValue(2)
            self.fov_spin.setValue(90)
            self.model_combo.setCurrentIndex(0)  # Fast
        elif index == 2:  # Accurate
            self.num_views_spin.setValue(8)
            self.pitch_levels_spin.setValue(2)
            self.fov_spin.setValue(90)
            self.model_combo.setCurrentIndex(4)  # XLarge
    
    def _load_fisheye_pair(self):
        """Load a pair of fisheye images (front and back)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Front Fisheye Image",
            "",
            "Images (*.png *.jpg *.jpeg *.tiff *.bmp);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Try to find the back image
        back_path = find_fisheye_pair(file_path)
        
        if back_path is None:
            # Ask user to select back image manually
            back_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Back Fisheye Image",
                str(Path(file_path).parent),
                "Images (*.png *.jpg *.jpeg *.tiff *.bmp);;All Files (*)"
            )
            
            if not back_path:
                QMessageBox.warning(
                    self, "Error", 
                    "Could not find matching back fisheye image.\n"
                    "Please ensure both front and back images are available."
                )
                return
        
        # Load both images
        self.front_image = cv2.imread(file_path)
        self.back_image = cv2.imread(back_path)
        
        if self.front_image is None:
            QMessageBox.warning(self, "Error", f"Could not load front image: {file_path}")
            return
        
        if self.back_image is None:
            QMessageBox.warning(self, "Error", f"Could not load back image: {back_path}")
            return
        
        self.front_path = file_path
        self.back_path = back_path
        
        # Display fisheye images
        self.front_label.setImage(self.front_image)
        self.back_label.setImage(self.back_image)
        
        # Convert to equirectangular for preview
        self.status_bar.showMessage("Converting to 360° view...")
        try:
            self.equirect_image = self.fisheye_converter.fisheye_pair_to_equirect(
                self.front_image, self.back_image
            )
            self.equirect_label.setImage(self.equirect_image)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not generate 360° preview: {e}")
        
        # Update info
        fh, fw = self.front_image.shape[:2]
        bh, bw = self.back_image.shape[:2]
        front_name = Path(file_path).name
        back_name = Path(back_path).name
        self.info_label.setText(
            f"Front: {front_name} ({fw}x{fh}) | Back: {back_name} ({bw}x{bh})"
        )
        
        # Enable processing
        self.process_btn.setEnabled(True)
        self.current_result = None
        self.save_btn.setEnabled(False)
        
        # Switch to equirectangular tab to show 360 view
        self.tab_widget.setCurrentIndex(1)
        
        self.status_bar.showMessage(f"Loaded fisheye pair: {front_name} + {back_name}")
    
    def _save_masks(self):
        """Save the generated masks."""
        if self.current_result is None:
            return
        
        # Get default output paths
        if self.front_path and self.back_path:
            front_mask_default, back_mask_default = get_mask_output_paths(
                self.front_path, self.back_path
            )
        else:
            front_mask_default = "front_mask.png"
            back_mask_default = "back_mask.png"
        
        # Ask for front mask path
        front_mask_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Front Mask",
            front_mask_default,
            "PNG Images (*.png);;All Files (*)"
        )
        
        if not front_mask_path:
            return
        
        # Ask for back mask path
        back_mask_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Back Mask",
            back_mask_default,
            "PNG Images (*.png);;All Files (*)"
        )
        
        if not back_mask_path:
            return
        
        self.current_result.save_masks(front_mask_path, back_mask_path)
        self.status_bar.showMessage(f"Saved masks: {front_mask_path}, {back_mask_path}")
    
    def _process_images(self):
        """Process the current fisheye pair."""
        if self.front_image is None or self.back_image is None:
            return
        
        # Create pipeline with current settings
        self._create_pipeline()
        
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start processing thread
        self.processing_thread = FisheyeProcessingThread(
            self.pipeline, self.front_image, self.back_image
        )
        self.processing_thread.progress.connect(self._on_progress)
        self.processing_thread.finished.connect(self._on_processing_finished)
        self.processing_thread.error.connect(self._on_processing_error)
        self.processing_thread.start()
    
    def _on_progress(self, message: str, progress: float):
        """Handle progress updates."""
        self.progress_bar.setValue(int(progress * 100))
        self.progress_label.setText(message)
    
    def _on_processing_finished(self, result: FisheyePipelineResult):
        """Handle processing completion."""
        self.current_result = result
        
        # Update UI
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self.process_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        
        # Display results - fisheye masks
        self.front_mask_label.setImage(result.front_mask)
        self.back_mask_label.setImage(result.back_mask)
        
        # Display 360 mask
        self.mask_360_label.setImage(result.equirect_mask)
        
        # Update overlay
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
            f"Front Coverage: {summary['front_mask_coverage']:.1f}% | "
            f"Back Coverage: {summary['back_mask_coverage']:.1f}% | "
            f"Time: {summary['processing_time']:.1f}s"
        )
        self.info_label.setText(info_text)
        
        # Switch to fisheye masks tab
        self.tab_widget.setCurrentIndex(2)
        
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
        if self.equirect_image is None or self.current_result is None:
            return
        
        # Create overlay with mask on 360 image
        opacity = self.opacity_slider.value() / 100.0
        overlay = self.equirect_image.copy()
        
        # Apply mask as red overlay
        mask = self.current_result.equirect_mask
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
        """Open folder dialogs and batch process fisheye pairs from two folders."""
        # Ask for front folder
        front_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with FRONT Fisheye Images",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not front_folder:
            return
        
        # Ask for back folder
        back_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with BACK Fisheye Images",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not back_folder:
            return
        
        # Ask for optional output folder
        reply = QMessageBox.question(
            self,
            "Output Location",
            "Save masks in a separate output folder?\n\n"
            "Yes = Choose output folder\n"
            "No = Save masks alongside original images",
            QMessageBox.Yes | QMessageBox.No
        )
        
        output_folder = None
        if reply == QMessageBox.Yes:
            output_folder = QFileDialog.getExistingDirectory(
                self,
                "Select Output Folder for Masks",
                "",
                QFileDialog.ShowDirsOnly
            )
            if not output_folder:
                return
        
        # Create pipeline with current settings (to get the config)
        self._create_pipeline()
        
        # Find matching pairs by frame number
        from core.fisheye_converter import find_pairs_from_two_folders
        
        try:
            pairs = find_pairs_from_two_folders(front_folder, back_folder)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        
        if not pairs:
            QMessageBox.information(
                self,
                "No Pairs Found",
                "No matching fisheye pairs found between the two folders.\n\n"
                "Pairs are matched by the numeric suffix in filenames.\n"
                "Examples:\n"
                "- 000001.jpg ↔ lens1_000001.jpg\n"
                "- frame_0042.png ↔ back_0042.png"
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Batch Processing",
            f"Found {len(pairs)} matching fisheye pairs.\n\n"
            f"Front folder: {front_folder}\n"
            f"Back folder: {back_folder}\n"
            f"Output: {'Separate folder' if output_folder else 'Alongside originals'}\n\n"
            "Continue with batch processing?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.batch_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start batch processing thread
        num_workers = self.workers_spin.value()
        self.batch_thread = FisheyeBatchProcessingThread(
            self.pipeline.config, 
            front_folder, 
            back_folder,
            output_folder,
            num_workers
        )
        self.batch_thread.progress.connect(self._on_batch_progress)
        self.batch_thread.file_completed.connect(self._on_batch_file_completed)
        self.batch_thread.finished.connect(self._on_batch_finished)
        self.batch_thread.error.connect(self._on_batch_error)
        self.batch_thread.start()
        
        self.status_bar.showMessage(f"Batch processing: {front_folder} + {back_folder}")
    
    def _on_batch_progress(self, message: str, progress: float):
        """Handle batch progress updates."""
        self.progress_bar.setValue(int(progress * 100))
        self.progress_label.setText(message)
    
    def _on_batch_file_completed(self, filename: str, detections: int, successful: int):
        """Handle completion of a single file pair in batch."""
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
            f"Processed: {successful}/{total} fisheye pairs\n"
            f"Total time: {total_time:.1f}s\n"
            f"Average per pair: {avg_time:.1f}s"
        )
        
        self.status_bar.showMessage(
            f"Batch complete: {successful}/{total} pairs processed in {total_time:.1f}s"
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


# Keep the old class name as alias for compatibility
MaskGeneratorWindow = FisheyeMaskGeneratorWindow

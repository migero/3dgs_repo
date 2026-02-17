"""
Main Window for 360 Motion Deblur
Qt5 GUI for applying motion deblurring to equirectangular videos.
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
import numpy as np
import cv2

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QProgressBar, QGroupBox, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QSlider, QScrollArea,
    QSplitter, QListWidget, QListWidgetItem, QMessageBox, QStatusBar,
    QTabWidget, QGridLayout, QFrame, QLineEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QImage, QFont, QCursor

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.video_pipeline import VideoPipeline, PipelineConfig, ProcessingStats, get_video_info
from core.pvdnet_processor import PVDNetProcessor, PVDNetConfig, PVDNET_PATH
from core.cube_projector import CubeProjector, CubeFaces


class ProcessingThread(QThread):
    """Background thread for video processing."""
    
    progress = pyqtSignal(object)  # ProcessingStats
    preview_frame = pyqtSignal(object)  # numpy array
    finished = pyqtSignal(bool, str)  # success, message
    error = pyqtSignal(str)  # error message
    
    def __init__(self, pipeline: VideoPipeline, input_path: str, output_path: str):
        super().__init__()
        self.pipeline = pipeline
        self.input_path = input_path
        self.output_path = output_path
        self._cancelled = False
    
    def cancel(self):
        self._cancelled = True
        self.pipeline.cancel()
    
    def run(self):
        try:
            self.pipeline.set_progress_callback(
                lambda stats: self.progress.emit(stats)
            )
            self.pipeline.set_preview_callback(
                lambda frame: self.preview_frame.emit(frame)
            )
            
            success = self.pipeline.process_video(self.input_path, self.output_path)
            
            if self._cancelled:
                self.finished.emit(False, "Processing cancelled")
            elif success:
                self.finished.emit(True, f"Successfully saved to {self.output_path}")
            else:
                self.finished.emit(False, "Processing failed")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class TestDeblurThread(QThread):
    """Background thread for test deblurring a single frame."""
    
    finished = pyqtSignal(object, object)  # deblurred_frame, cube_faces_image
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, pipeline: VideoPipeline, frames: List[np.ndarray]):
        super().__init__()
        self.pipeline = pipeline
        self.frames = frames  # [prev, curr, next]
    
    def run(self):
        try:
            self.progress.emit("Loading model...")
            if not self.pipeline.pvdnet.is_loaded:
                if not self.pipeline.load_model():
                    self.error.emit("Failed to load PVDNet model")
                    return
            
            prev_frame, curr_frame, next_frame = self.frames
            
            self.progress.emit("Converting to cube faces...")
            # Convert to cube
            prev_cubes = self.pipeline.cube_projector.equirect_to_cube(prev_frame)
            curr_cubes = self.pipeline.cube_projector.equirect_to_cube(curr_frame)
            next_cubes = self.pipeline.cube_projector.equirect_to_cube(next_frame)
            
            self.progress.emit("Deblurring cube faces...")
            # Process through PVDNet
            deblurred_faces = self.pipeline.pvdnet.process_cube_faces_batch(
                prev_faces=prev_cubes.to_list(),
                curr_faces=curr_cubes.to_list(),
                next_faces=next_cubes.to_list(),
                face_ids=["front", "right", "back", "left", "top", "bottom"]
            )
            
            deblurred_cubes = CubeFaces.from_list(deblurred_faces)
            
            self.progress.emit("Reconstructing equirectangular...")
            # Reconstruct
            h, w = curr_frame.shape[:2]
            output_frame = self.pipeline.cube_projector.cube_to_equirect(
                deblurred_cubes, h, w
            )
            
            # Create cube faces visualization (2x3 grid)
            cube_vis = self._create_cube_visualization(deblurred_faces)
            
            self.finished.emit(output_frame, cube_vis)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))
    
    def _create_cube_visualization(self, faces: List[np.ndarray]) -> np.ndarray:
        """Create a 2x3 grid visualization of cube faces."""
        # Labels: Front, Right, Back, Left, Top, Bottom
        labels = ['Front', 'Right', 'Back', 'Left', 'Top', 'Bottom']
        
        # Resize faces for visualization
        vis_size = 256
        resized = []
        for face in faces:
            if face.shape[0] != vis_size or face.shape[1] != vis_size:
                face = cv2.resize(face, (vis_size, vis_size))
            resized.append(face)
        
        # Create 2x3 grid
        row1 = np.hstack([resized[0], resized[1], resized[2]])  # Front, Right, Back
        row2 = np.hstack([resized[3], resized[4], resized[5]])  # Left, Top, Bottom
        grid = np.vstack([row1, row2])
        
        # Add labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        for i, label in enumerate(labels):
            x = (i % 3) * vis_size + 10
            y = (i // 3) * vis_size + 25
            cv2.putText(grid, label, (x, y), font, 0.7, (255, 255, 255), 2)
            cv2.putText(grid, label, (x, y), font, 0.7, (0, 0, 0), 1)
        
        return grid


class ZoomableImageLabel(QLabel):
    """Custom label for displaying images with click-to-zoom functionality."""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 200)
        self.setStyleSheet("background-color: #2d2d2d; border: 1px solid #555;")
        self._pixmap = None
        self._image = None
        self._zoomed = False
        self._zoom_point = None
        self._fit_size = None  # Store the size to fit to when not zoomed
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    
    def setImage(self, image: np.ndarray):
        """Set image from numpy array (RGB format)."""
        if image is None:
            self.clear()
            self._image = None
            self._pixmap = None
            return
        
        # Ensure RGB format
        if len(image.shape) == 3 and image.shape[2] == 3:
            pass
        elif len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Ensure uint8
        if image.dtype != np.uint8:
            image = (np.clip(image, 0, 255)).astype(np.uint8)
        
        self._image = image.copy()
        h, w = image.shape[:2]
        bytes_per_line = 3 * w
        qimg = QImage(image.data.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
        self._pixmap = QPixmap.fromImage(qimg)
        self._zoomed = False
        self._updateDisplay()
    
    def _updateDisplay(self):
        if self._pixmap:
            if self._zoomed:
                # Show at 100% zoom - resize label to full pixmap size
                self.setFixedSize(self._pixmap.size())
                super().setPixmap(self._pixmap)
            else:
                # Scale to fit - remove fixed size constraint
                self.setMinimumSize(400, 200)
                self.setMaximumSize(16777215, 16777215)  # QWIDGETSIZE_MAX
                if self._fit_size:
                    scaled = self._pixmap.scaled(
                        self._fit_size, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                else:
                    scaled = self._pixmap.scaled(
                        self.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                super().setPixmap(scaled)
    
    def setFitSize(self, size):
        """Set the size to fit to when not zoomed."""
        self._fit_size = size
        if not self._zoomed:
            self._updateDisplay()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._zoomed:
            self._fit_size = event.size()
            self._updateDisplay()
    
    def mousePressEvent(self, event):
        """Handle mouse click for zoom toggle."""
        if event.button() == Qt.LeftButton and self._pixmap:
            self._zoomed = not self._zoomed
            
            if self._zoomed:
                # Calculate scroll position to center on click point
                self._zoom_point = event.pos()
            
            self._updateDisplay()
            
            # Emit signal to parent to update scroll area
            parent = self.parent()
            while parent:
                if hasattr(parent, 'on_zoom_changed'):
                    parent.on_zoom_changed(self._zoomed, event.pos())
                    break
                parent = parent.parent()
        
        super().mousePressEvent(event)
    
    @property
    def is_zoomed(self) -> bool:
        return self._zoomed


class ImageLabel(QLabel):
    """Simple auto-scaling image label (for non-zoomable displays)."""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 200)
        self.setStyleSheet("background-color: #2d2d2d; border: 1px solid #555;")
        self._pixmap = None
    
    def setImage(self, image: np.ndarray):
        """Set image from numpy array (RGB format)."""
        if image is None:
            self.clear()
            return
        
        if len(image.shape) == 3 and image.shape[2] == 3:
            pass
        elif len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        if image.dtype != np.uint8:
            image = (np.clip(image, 0, 255)).astype(np.uint8)
        
        h, w = image.shape[:2]
        bytes_per_line = 3 * w
        qimg = QImage(image.data.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
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


class ZoomableScrollArea(QScrollArea):
    """Scroll area that supports zoom functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignCenter)
        self._zoom_enabled = False
        # Ensure scrollbars appear when needed
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    
    def on_zoom_changed(self, zoomed: bool, click_pos: QPoint):
        """Called when zoom state changes."""
        self._zoom_enabled = zoomed
        
        widget = self.widget()
        
        if zoomed:
            # Disable widget resizable so the label can be larger than viewport
            self.setWidgetResizable(False)
            
            # Calculate scroll position based on click
            if widget and hasattr(widget, '_pixmap') and widget._pixmap:
                # Store current widget size before zoom
                old_size = widget.size()
                pixmap_size = widget._pixmap.size()
                
                # Calculate where to scroll to show the clicked area
                if old_size.width() > 0 and old_size.height() > 0:
                    ratio_x = click_pos.x() / old_size.width()
                    ratio_y = click_pos.y() / old_size.height()
                    
                    # Scroll to position (center the clicked point)
                    h_scroll = int(ratio_x * pixmap_size.width() - self.viewport().width() / 2)
                    v_scroll = int(ratio_y * pixmap_size.height() - self.viewport().height() / 2)
                    
                    # Apply scroll after widget updates its size
                    QTimer.singleShot(100, lambda: self._scroll_to(h_scroll, v_scroll))
        else:
            # Re-enable widget resizable for fit mode
            self.setWidgetResizable(True)
            # Tell widget what size to fit to
            if widget and hasattr(widget, 'setFitSize'):
                widget.setFitSize(self.viewport().size())
    
    def resizeEvent(self, event):
        """Handle resize to update fit size."""
        super().resizeEvent(event)
        widget = self.widget()
        if widget and hasattr(widget, 'setFitSize') and not self._zoom_enabled:
            widget.setFitSize(self.viewport().size())
    
    def _scroll_to(self, h: int, v: int):
        """Scroll to position."""
        self.horizontalScrollBar().setValue(max(0, h))
        self.verticalScrollBar().setValue(max(0, v))


class MotionDeblurWindow(QMainWindow):
    """Main window for the 360 Motion Deblur application."""
    
    # Supported cube face resolutions (multiples of 8 for neural networks)
    RESOLUTIONS = [512, 640, 768, 1024, 1280, 1536]
    
    # Frame positions for testing (percentages)
    FRAME_POSITIONS = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("360 Motion Deblur")
        self.setMinimumSize(1200, 800)
        
        # State
        self.input_path: Optional[str] = None
        self.output_path: Optional[str] = None
        self.pipeline: Optional[VideoPipeline] = None
        self.processing_thread: Optional[ProcessingThread] = None
        self.test_thread: Optional[TestDeblurThread] = None
        self.video_info: Optional[dict] = None
        
        # Frame navigation state
        self.current_frame_position = 0  # Index in FRAME_POSITIONS
        self.current_frame: Optional[np.ndarray] = None
        self.deblurred_frame: Optional[np.ndarray] = None
        self.cube_faces_image: Optional[np.ndarray] = None
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        
        # Update device info
        self._update_device_info()
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        left_panel = self._create_left_panel()
        
        # Right panel - Preview display
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
    
    def _update_device_info(self):
        """Update status bar with device information."""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                self.status_bar.showMessage(f"Ready. Using GPU: {gpu_name}")
            else:
                self.status_bar.showMessage("Ready. Using CPU (GPU recommended for faster processing)")
        except:
            self.status_bar.showMessage("Ready. Load a 360° video to begin.")
    
    def _create_left_panel(self) -> QWidget:
        """Create the left control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # File controls
        file_group = QGroupBox("Video Files")
        file_layout = QVBoxLayout(file_group)
        
        # Input file
        input_layout = QHBoxLayout()
        self.input_btn = QPushButton("📂 Select Input Video")
        input_layout.addWidget(self.input_btn)
        file_layout.addLayout(input_layout)
        
        self.input_label = QLabel("No video selected")
        self.input_label.setStyleSheet("color: #888; font-style: italic;")
        self.input_label.setWordWrap(True)
        file_layout.addWidget(self.input_label)
        
        # Output file
        output_layout = QHBoxLayout()
        self.output_btn = QPushButton("💾 Set Output Path")
        output_layout.addWidget(self.output_btn)
        file_layout.addLayout(output_layout)
        
        self.output_label = QLabel("No output path set")
        self.output_label.setStyleSheet("color: #888; font-style: italic;")
        self.output_label.setWordWrap(True)
        file_layout.addWidget(self.output_label)
        
        layout.addWidget(file_group)
        
        # Video info
        info_group = QGroupBox("Video Information")
        info_layout = QVBoxLayout(info_group)
        self.video_info_label = QLabel("Load a video to see information")
        self.video_info_label.setStyleSheet("color: #aaa;")
        info_layout.addWidget(self.video_info_label)
        layout.addWidget(info_group)
        
        # Frame Navigation for Testing
        nav_group = QGroupBox("Frame Navigation (Test)")
        nav_layout = QVBoxLayout(nav_group)
        
        # Navigation buttons
        nav_btn_layout = QHBoxLayout()
        self.prev_frame_btn = QPushButton("◀")
        self.prev_frame_btn.setFixedWidth(50)
        self.prev_frame_btn.setToolTip("Previous frame (go back 10%)")
        self.prev_frame_btn.setEnabled(False)
        
        self.frame_position_label = QLabel("0%")
        self.frame_position_label.setAlignment(Qt.AlignCenter)
        self.frame_position_label.setMinimumWidth(60)
        self.frame_position_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.next_frame_btn = QPushButton("▶")
        self.next_frame_btn.setFixedWidth(50)
        self.next_frame_btn.setToolTip("Next frame (go forward 10%)")
        self.next_frame_btn.setEnabled(False)
        
        nav_btn_layout.addWidget(self.prev_frame_btn)
        nav_btn_layout.addWidget(self.frame_position_label)
        nav_btn_layout.addWidget(self.next_frame_btn)
        nav_layout.addLayout(nav_btn_layout)
        
        # Test deblur button
        self.test_deblur_btn = QPushButton("🔬 Test Deblur Frame")
        self.test_deblur_btn.setEnabled(False)
        self.test_deblur_btn.setMinimumHeight(35)
        self.test_deblur_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #888;
            }
            QPushButton:hover:enabled {
                background-color: #7B1FA2;
            }
        """)
        nav_layout.addWidget(self.test_deblur_btn)
        
        self.test_status_label = QLabel("")
        self.test_status_label.setAlignment(Qt.AlignCenter)
        self.test_status_label.setStyleSheet("color: #888;")
        nav_layout.addWidget(self.test_status_label)
        
        layout.addWidget(nav_group)
        
        # Cube projection settings
        cube_group = QGroupBox("Cube Projection Settings")
        cube_layout = QGridLayout(cube_group)
        
        cube_layout.addWidget(QLabel("Cube Face Resolution:"), 0, 0)
        self.resolution_combo = QComboBox()
        for res in self.RESOLUTIONS:
            self.resolution_combo.addItem(f"{res}px", res)
        self.resolution_combo.setCurrentIndex(3)  # Default to 1024
        self.resolution_combo.setToolTip(
            "Size of each cube face. Higher = better quality, more VRAM needed.\n"
            "Multiples of 8 work best with neural networks."
        )
        cube_layout.addWidget(self.resolution_combo, 0, 1)
        
        layout.addWidget(cube_group)
        
        # PVDNet settings
        pvd_group = QGroupBox("PVDNet Model Settings")
        pvd_layout = QGridLayout(pvd_group)
        
        pvd_layout.addWidget(QLabel("Model Checkpoint:"), 0, 0)
        self.checkpoint_combo = QComboBox()
        self._populate_checkpoints()
        pvd_layout.addWidget(self.checkpoint_combo, 0, 1)
        
        self.large_model_check = QCheckBox("Use large model (more accurate, slower)")
        self.large_model_check.setChecked(False)
        pvd_layout.addWidget(self.large_model_check, 1, 0, 1, 2)
        
        layout.addWidget(pvd_group)
        
        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QGridLayout(output_group)
        
        output_layout.addWidget(QLabel("Video Codec:"), 0, 0)
        self.codec_combo = QComboBox()
        self.codec_combo.addItems(["libx264 (H.264)", "libx265 (H.265/HEVC)", "libvpx-vp9 (VP9)"])
        output_layout.addWidget(self.codec_combo, 0, 1)
        
        output_layout.addWidget(QLabel("Quality (CRF):"), 1, 0)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(0, 51)
        self.quality_spin.setValue(18)
        self.quality_spin.setToolTip("Lower = better quality, larger file. 18 is visually lossless.")
        output_layout.addWidget(self.quality_spin, 1, 1)
        
        output_layout.addWidget(QLabel("Encoding Preset:"), 2, 0)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", 
                                    "medium", "slow", "slower", "veryslow"])
        self.preset_combo.setCurrentIndex(5)  # medium
        output_layout.addWidget(self.preset_combo, 2, 1)
        
        layout.addWidget(output_group)
        
        # Memory settings
        memory_group = QGroupBox("Memory Management")
        memory_layout = QGridLayout(memory_group)
        
        memory_layout.addWidget(QLabel("Frame Buffer Size:"), 0, 0)
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setRange(10, 100)
        self.buffer_spin.setValue(30)
        self.buffer_spin.setToolTip("Number of frames to keep in memory")
        memory_layout.addWidget(self.buffer_spin, 0, 1)
        
        memory_layout.addWidget(QLabel("Cleanup Interval:"), 1, 0)
        self.cleanup_spin = QSpinBox()
        self.cleanup_spin.setRange(5, 50)
        self.cleanup_spin.setValue(10)
        self.cleanup_spin.setToolTip("Clean up memory every N frames")
        memory_layout.addWidget(self.cleanup_spin, 1, 1)
        
        layout.addWidget(memory_group)
        
        # Process button
        self.process_btn = QPushButton("🎬 Start Deblurring")
        self.process_btn.setEnabled(False)
        self.process_btn.setMinimumHeight(50)
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:disabled {
                background-color: #888;
            }
            QPushButton:hover:enabled {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(self.process_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #888;
            }
        """)
        layout.addWidget(self.cancel_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setWordWrap(True)
        layout.addWidget(self.progress_label)
        
        # Stats
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #888;")
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create the right preview display panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Preview tab with zoomable scroll area
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        
        self.preview_scroll = ZoomableScrollArea()
        self.preview_label = ZoomableImageLabel()
        self.preview_label.setText("Load a video to see preview\n\n(Click to zoom 100%, click again to fit)")
        self.preview_scroll.setWidget(self.preview_label)
        preview_layout.addWidget(self.preview_scroll)
        
        # Zoom hint
        self.zoom_hint_label = QLabel("💡 Click image to toggle 100% zoom")
        self.zoom_hint_label.setAlignment(Qt.AlignCenter)
        self.zoom_hint_label.setStyleSheet("color: #888; font-size: 11px;")
        preview_layout.addWidget(self.zoom_hint_label)
        
        self.tab_widget.addTab(preview_tab, "Preview")
        
        # Deblurred result tab
        deblur_tab = QWidget()
        deblur_layout = QVBoxLayout(deblur_tab)
        
        self.deblur_scroll = ZoomableScrollArea()
        self.deblur_label = ZoomableImageLabel()
        self.deblur_label.setText("Use 'Test Deblur Frame' to see results\n\n(Click to zoom 100%, click again to fit)")
        self.deblur_scroll.setWidget(self.deblur_label)
        deblur_layout.addWidget(self.deblur_scroll)
        
        self.tab_widget.addTab(deblur_tab, "Deblurred")
        
        # Cube faces tab
        cube_tab = QWidget()
        cube_layout = QVBoxLayout(cube_tab)
        
        self.cube_scroll = ZoomableScrollArea()
        self.cube_label = ZoomableImageLabel()
        self.cube_label.setText("Cube faces will appear here after test deblur\n\nLayout: Front | Right | Back\n              Left  |  Top  | Bottom")
        self.cube_scroll.setWidget(self.cube_label)
        cube_layout.addWidget(self.cube_scroll)
        
        self.tab_widget.addTab(cube_tab, "Cube Faces")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def _setup_connections(self):
        """Setup signal/slot connections."""
        self.input_btn.clicked.connect(self._select_input)
        self.output_btn.clicked.connect(self._select_output)
        self.process_btn.clicked.connect(self._start_processing)
        self.cancel_btn.clicked.connect(self._cancel_processing)
        
        # Frame navigation
        self.prev_frame_btn.clicked.connect(self._go_prev_frame)
        self.next_frame_btn.clicked.connect(self._go_next_frame)
        self.test_deblur_btn.clicked.connect(self._test_deblur)
    
    def _populate_checkpoints(self):
        """Populate checkpoint dropdown with available models."""
        self.checkpoint_combo.clear()
        
        # Check PVDNet/ckpt folder
        ckpt_dir = PVDNET_PATH / 'ckpt'
        if ckpt_dir.exists():
            for f in sorted(ckpt_dir.glob('*.pytorch')):
                name = f.stem
                self.checkpoint_combo.addItem(name, str(f))
        
        if self.checkpoint_combo.count() == 0:
            self.checkpoint_combo.addItem("No checkpoints found", "")
            self.checkpoint_combo.setToolTip(
                "Download PVDNet checkpoints from:\n"
                "https://www.dropbox.com/sh/frpegu68s0yx8n9/AACrptFFhxejSyKJBvLdk9IJa?dl=1\n"
                "and extract to PVDNet/ckpt/"
            )
    
    def _select_input(self):
        """Select input video file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input Video",
            "",
            "Video Files (*.mp4 *.mov *.avi *.mkv *.webm);;All Files (*)"
        )
        
        if path:
            self.input_path = path
            self.input_label.setText(os.path.basename(path))
            self.input_label.setStyleSheet("color: #4CAF50;")
            
            # Get video info
            self.video_info = get_video_info(path)
            if self.video_info:
                info_text = (
                    f"Resolution: {self.video_info['width']}x{self.video_info['height']}\n"
                    f"FPS: {self.video_info['fps']:.2f}\n"
                    f"Frames: {self.video_info['frame_count']}\n"
                    f"Duration: {self.video_info['duration']:.1f}s"
                )
                self.video_info_label.setText(info_text)
                
                # Auto-set output path
                if not self.output_path:
                    base = os.path.splitext(path)[0]
                    self.output_path = f"{base}_deblurred.mp4"
                    self.output_label.setText(os.path.basename(self.output_path))
                    self.output_label.setStyleSheet("color: #2196F3;")
                
                # Enable frame navigation
                self.current_frame_position = 0
                self._update_frame_navigation()
                
                # Load first frame for preview
                self._load_frame_at_position()
            
            self._update_process_button()
    
    def _update_frame_navigation(self):
        """Update frame navigation buttons and label."""
        if not self.video_info:
            self.prev_frame_btn.setEnabled(False)
            self.next_frame_btn.setEnabled(False)
            self.test_deblur_btn.setEnabled(False)
            return
        
        pos = self.FRAME_POSITIONS[self.current_frame_position]
        self.frame_position_label.setText(f"{pos}%")
        
        self.prev_frame_btn.setEnabled(self.current_frame_position > 0)
        self.next_frame_btn.setEnabled(self.current_frame_position < len(self.FRAME_POSITIONS) - 1)
        self.test_deblur_btn.setEnabled(
            self.current_frame is not None and 
            self.checkpoint_combo.currentData() != ""
        )
    
    def _go_prev_frame(self):
        """Go to previous frame position."""
        if self.current_frame_position > 0:
            self.current_frame_position -= 1
            self._load_frame_at_position()
            self._update_frame_navigation()
    
    def _go_next_frame(self):
        """Go to next frame position."""
        if self.current_frame_position < len(self.FRAME_POSITIONS) - 1:
            self.current_frame_position += 1
            self._load_frame_at_position()
            self._update_frame_navigation()
    
    def _load_frame_at_position(self):
        """Load frame at current position percentage."""
        if not self.input_path or not self.video_info:
            return
        
        pos_percent = self.FRAME_POSITIONS[self.current_frame_position]
        total_frames = self.video_info['frame_count']
        
        # Calculate frame number
        frame_num = int((pos_percent / 100.0) * (total_frames - 1))
        frame_num = max(0, min(frame_num, total_frames - 1))
        
        cap = cv2.VideoCapture(self.input_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_frame = frame
            self.preview_label.setImage(frame)
            
            # Clear previous deblur result
            self.deblurred_frame = None
            self.cube_faces_image = None
            self.deblur_label.setText("Use 'Test Deblur Frame' to see results")
            self.cube_label.setText("Cube faces will appear here after test deblur")
            self.test_status_label.setText("")
    
    def _load_preview_frame(self, video_path: str):
        """Load and display first frame of video."""
        self._load_frame_at_position()
    
    def _select_output(self):
        """Select output video path."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output Path",
            self.output_path or "",
            "MP4 Video (*.mp4);;All Files (*)"
        )
        
        if path:
            self.output_path = path
            self.output_label.setText(os.path.basename(path))
            self.output_label.setStyleSheet("color: #2196F3;")
            self._update_process_button()
    
    def _update_process_button(self):
        """Update process button enabled state."""
        enabled = (
            self.input_path is not None and 
            self.output_path is not None and
            self.checkpoint_combo.currentData() != ""
        )
        self.process_btn.setEnabled(enabled)
    
    def _create_pipeline(self) -> VideoPipeline:
        """Create pipeline with current settings."""
        # Get codec
        codec_map = {
            0: "libx264",
            1: "libx265", 
            2: "libvpx-vp9"
        }
        codec = codec_map.get(self.codec_combo.currentIndex(), "libx264")
        
        config = PipelineConfig(
            cube_face_size=self.resolution_combo.currentData(),
            checkpoint_path=self.checkpoint_combo.currentData(),
            use_large_model=self.large_model_check.isChecked(),
            frame_buffer_size=self.buffer_spin.value(),
            cleanup_interval=self.cleanup_spin.value(),
            output_codec=codec,
            output_quality=self.quality_spin.value(),
            output_preset=self.preset_combo.currentText()
        )
        
        return VideoPipeline(config)
    
    def _test_deblur(self):
        """Test deblur on current frame."""
        if self.current_frame is None:
            return
        
        # Create pipeline if needed
        if self.pipeline is None:
            self.pipeline = self._create_pipeline()
        
        # Get prev/curr/next frames
        pos_percent = self.FRAME_POSITIONS[self.current_frame_position]
        total_frames = self.video_info['frame_count']
        frame_num = int((pos_percent / 100.0) * (total_frames - 1))
        
        cap = cv2.VideoCapture(self.input_path)
        
        # Get previous frame
        prev_frame_num = max(0, frame_num - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, prev_frame_num)
        ret, prev_frame = cap.read()
        if ret:
            prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2RGB)
        else:
            prev_frame = self.current_frame.copy()
        
        # Current frame is already loaded
        curr_frame = self.current_frame
        
        # Get next frame
        next_frame_num = min(total_frames - 1, frame_num + 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, next_frame_num)
        ret, next_frame = cap.read()
        if ret:
            next_frame = cv2.cvtColor(next_frame, cv2.COLOR_BGR2RGB)
        else:
            next_frame = self.current_frame.copy()
        
        cap.release()
        
        # Start test thread
        self.test_thread = TestDeblurThread(
            self.pipeline,
            [prev_frame, curr_frame, next_frame]
        )
        
        self.test_thread.progress.connect(self._on_test_progress)
        self.test_thread.finished.connect(self._on_test_finished)
        self.test_thread.error.connect(self._on_test_error)
        
        # Disable controls
        self.test_deblur_btn.setEnabled(False)
        self.prev_frame_btn.setEnabled(False)
        self.next_frame_btn.setEnabled(False)
        self.test_status_label.setText("Processing...")
        
        self.test_thread.start()
    
    def _on_test_progress(self, msg: str):
        """Handle test progress update."""
        self.test_status_label.setText(msg)
    
    def _on_test_finished(self, deblurred_frame: np.ndarray, cube_faces_image: np.ndarray):
        """Handle test deblur completion."""
        self.deblurred_frame = deblurred_frame
        self.cube_faces_image = cube_faces_image
        
        # Update displays
        self.deblur_label.setImage(deblurred_frame)
        self.cube_label.setImage(cube_faces_image)
        
        # Switch to deblurred tab
        self.tab_widget.setCurrentIndex(1)
        
        self.test_status_label.setText("✅ Test complete!")
        self._update_frame_navigation()
    
    def _on_test_error(self, error_msg: str):
        """Handle test deblur error."""
        self.test_status_label.setText(f"❌ Error: {error_msg}")
        self._update_frame_navigation()
        QMessageBox.warning(self, "Test Error", f"Deblur test failed:\n{error_msg}")
    
    def _start_processing(self):
        """Start video processing."""
        if not self.input_path or not self.output_path:
            return
        
        # Create pipeline
        self.pipeline = self._create_pipeline()
        
        # Create processing thread
        self.processing_thread = ProcessingThread(
            self.pipeline,
            self.input_path,
            self.output_path
        )
        
        # Connect signals
        self.processing_thread.progress.connect(self._on_progress)
        self.processing_thread.preview_frame.connect(self._on_preview_frame)
        self.processing_thread.finished.connect(self._on_finished)
        self.processing_thread.error.connect(self._on_error)
        
        # Update UI
        self.process_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Disable settings during processing
        self._set_settings_enabled(False)
        
        # Start processing
        self.processing_thread.start()
    
    def _cancel_processing(self):
        """Cancel current processing."""
        if self.processing_thread:
            self.processing_thread.cancel()
            self.cancel_btn.setEnabled(False)
            self.progress_label.setText("Cancelling...")
    
    def _on_progress(self, stats: ProcessingStats):
        """Handle progress update."""
        if stats.total_frames > 0:
            progress = (stats.processed_frames / stats.total_frames) * 100
            self.progress_bar.setValue(int(progress))
        
        self.progress_label.setText(stats.status)
        
        # Update stats
        stats_text = (
            f"Frame: {stats.current_frame + 1}/{stats.total_frames} | "
            f"FPS: {stats.fps:.1f} | "
            f"Elapsed: {stats.elapsed_time:.0f}s | "
            f"ETA: {stats.estimated_remaining:.0f}s"
        )
        self.stats_label.setText(stats_text)
    
    def _on_preview_frame(self, frame: np.ndarray):
        """Handle preview frame update."""
        self.preview_label.setImage(frame)
    
    def _on_finished(self, success: bool, message: str):
        """Handle processing completion."""
        self.progress_bar.setVisible(False)
        self.cancel_btn.setEnabled(False)
        self.process_btn.setEnabled(True)
        self._set_settings_enabled(True)
        
        if success:
            self.progress_label.setText(f"✅ {message}")
            self.status_bar.showMessage("Processing complete!")
            QMessageBox.information(self, "Complete", message)
        else:
            self.progress_label.setText(f"❌ {message}")
            self.status_bar.showMessage("Processing failed or cancelled")
    
    def _on_error(self, error_msg: str):
        """Handle processing error."""
        self.progress_bar.setVisible(False)
        self.cancel_btn.setEnabled(False)
        self.process_btn.setEnabled(True)
        self._set_settings_enabled(True)
        
        self.progress_label.setText(f"❌ Error: {error_msg}")
        self.status_bar.showMessage("Processing failed")
        QMessageBox.critical(self, "Error", f"Processing failed:\n{error_msg}")
    
    def _set_settings_enabled(self, enabled: bool):
        """Enable/disable settings controls."""
        self.input_btn.setEnabled(enabled)
        self.output_btn.setEnabled(enabled)
        self.resolution_combo.setEnabled(enabled)
        self.checkpoint_combo.setEnabled(enabled)
        self.large_model_check.setEnabled(enabled)
        self.codec_combo.setEnabled(enabled)
        self.quality_spin.setEnabled(enabled)
        self.preset_combo.setEnabled(enabled)
        self.buffer_spin.setEnabled(enabled)
        self.cleanup_spin.setEnabled(enabled)
        
        # Frame navigation
        if enabled:
            self._update_frame_navigation()
        else:
            self.prev_frame_btn.setEnabled(False)
            self.next_frame_btn.setEnabled(False)
            self.test_deblur_btn.setEnabled(False)
    
    def closeEvent(self, event):
        """Handle window close."""
        if self.processing_thread and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Processing is still running. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.processing_thread.cancel()
                self.processing_thread.wait(5000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

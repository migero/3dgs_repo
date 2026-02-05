#!/usr/bin/env python3
"""
Main Window for GoPro 360 Converter
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QProgressBar,
    QGroupBox, QFormLayout, QComboBox, QSpinBox,
    QSlider, QFrame, QMessageBox, QSplitter,
    QStatusBar, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont

from core.video_processor import VideoProcessor, ConversionWorker
from core.preview_generator import PreviewGenerator
from core.ffmpeg_stitcher import FFmpegStitcher


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.output_file = None
        self.video_processor = VideoProcessor()
        self.preview_generator = PreviewGenerator()
        self.ffmpeg_stitcher = FFmpegStitcher()
        self.conversion_worker = None
        self.conversion_thread = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("GoPro 360 Converter")
        self.setMinimumSize(1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for preview and controls
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Preview
        preview_panel = self.create_preview_panel()
        splitter.addWidget(preview_panel)
        
        # Right panel - Controls
        controls_panel = self.create_controls_panel()
        splitter.addWidget(controls_panel)
        
        # Set splitter proportions
        splitter.setSizes([600, 400])
        
        main_layout.addWidget(splitter)
        
        # Progress section
        progress_section = self.create_progress_section()
        main_layout.addWidget(progress_section)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Select a .360 file to begin")
        
        # Initialize stitch method settings (disable advanced options for default FFmpeg method)
        self.on_stitch_method_changed(0)
        
    def create_preview_panel(self):
        """Create the preview panel with image display"""
        panel = QGroupBox("Preview")
        layout = QVBoxLayout(panel)
        
        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(500, 300)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 5px;
            }
        """)
        self.preview_label.setText("No preview available\n\nSelect a .360 file to see preview")
        layout.addWidget(self.preview_label)
        
        # Frame selection slider
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(QLabel("Frame:"))
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(100)
        self.frame_slider.setValue(0)
        self.frame_slider.valueChanged.connect(self.on_frame_slider_changed)
        frame_layout.addWidget(self.frame_slider)
        
        self.frame_label = QLabel("0 / 0")
        self.frame_label.setMinimumWidth(80)
        frame_layout.addWidget(self.frame_label)
        
        layout.addLayout(frame_layout)
        
        # Preview controls
        preview_controls = QHBoxLayout()
        
        self.refresh_preview_btn = QPushButton("Refresh Preview")
        self.refresh_preview_btn.clicked.connect(self.refresh_preview)
        self.refresh_preview_btn.setEnabled(False)
        preview_controls.addWidget(self.refresh_preview_btn)
        
        preview_controls.addStretch()
        
        layout.addLayout(preview_controls)
        
        return panel
        
    def create_controls_panel(self):
        """Create the controls panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        # Input file
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input:"))
        self.input_path_label = QLabel("No file selected")
        self.input_path_label.setStyleSheet("color: #888;")
        input_layout.addWidget(self.input_path_label, 1)
        
        self.browse_input_btn = QPushButton("Browse...")
        self.browse_input_btn.clicked.connect(self.browse_input_file)
        input_layout.addWidget(self.browse_input_btn)
        file_layout.addLayout(input_layout)
        
        # Output file
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output:"))
        self.output_path_label = QLabel("No file selected")
        self.output_path_label.setStyleSheet("color: #888;")
        output_layout.addWidget(self.output_path_label, 1)
        
        self.browse_output_btn = QPushButton("Browse...")
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        self.browse_output_btn.setEnabled(False)
        output_layout.addWidget(self.browse_output_btn)
        file_layout.addLayout(output_layout)
        
        layout.addWidget(file_group)
        
        # Stitch settings group
        stitch_group = QGroupBox("Stitch Settings")
        stitch_layout = QVBoxLayout(stitch_group)
        
        # Stitching method selection
        method_layout = QFormLayout()
        self.stitch_method_combo = QComboBox()
        self.stitch_method_combo.addItems([
            "FFmpeg Filter (Fast, Recommended)",
            "Python Frame-by-Frame (Slower, Experimental)",
        ])
        self.stitch_method_combo.setCurrentIndex(0)  # FFmpeg is default
        self.stitch_method_combo.currentIndexChanged.connect(self.on_stitch_method_changed)
        self.stitch_method_combo.setToolTip(
            "FFmpeg Filter: Uses FFmpeg's built-in filters for fast, reliable stitching.\n"
            "Python Frame-by-Frame: Processes each frame individually in Python (slower but customizable)."
        )
        method_layout.addRow("Stitching Method:", self.stitch_method_combo)
        stitch_layout.addLayout(method_layout)
        
        # Interpolation (always visible)
        interp_layout = QFormLayout()
        self.interp_combo = QComboBox()
        self.interp_combo.addItems([
            "Bilinear (Fast)",
            "Bicubic (Balanced)",
            "Lanczos (High Quality)",
        ])
        self.interp_combo.setCurrentIndex(1)
        interp_layout.addRow("Interpolation:", self.interp_combo)
        stitch_layout.addLayout(interp_layout)
        
        # Test PNG button (always visible)
        self.test_stitch_btn = QPushButton("Generate Test PNG")
        self.test_stitch_btn.setToolTip("Extract a frame and generate a test PNG to preview the stitching result")
        self.test_stitch_btn.clicked.connect(self.generate_test_stitch_png)
        self.test_stitch_btn.setEnabled(False)
        stitch_layout.addWidget(self.test_stitch_btn)
        
        # Collapsible advanced stitch settings
        self.advanced_stitch_btn = QPushButton("▶ Advanced Stitch Settings")
        self.advanced_stitch_btn.setStyleSheet("text-align: left; border: none; padding: 5px;")
        self.advanced_stitch_btn.clicked.connect(self.toggle_advanced_stitch)
        stitch_layout.addWidget(self.advanced_stitch_btn)
        
        # Container for advanced stitch controls (hidden by default)
        self.advanced_stitch_widget = QWidget()
        advanced_layout = QFormLayout(self.advanced_stitch_widget)
        advanced_layout.setContentsMargins(10, 0, 0, 0)
        
        # Edge overlap setting (pixels to stretch and overlap at seams)
        self.edge_overlap_spinbox = QSpinBox()
        self.edge_overlap_spinbox.setRange(10, 200)
        self.edge_overlap_spinbox.setValue(30)
        self.edge_overlap_spinbox.setSuffix(" px")
        self.edge_overlap_spinbox.setToolTip("How many pixels to stretch and overlap at seam edges (at 1/6 and 5/6 positions)")
        advanced_layout.addRow("Edge Overlap:", self.edge_overlap_spinbox)
        
        # Blend width setting (pixels for blending gradient)
        self.blend_width_spinbox = QSpinBox()
        self.blend_width_spinbox.setRange(5, 100)
        self.blend_width_spinbox.setValue(30)
        self.blend_width_spinbox.setSuffix(" px")
        self.blend_width_spinbox.setToolTip("Width of the blending gradient zone at seam overlaps")
        advanced_layout.addRow("Blend Width:", self.blend_width_spinbox)
        
        # Hide advanced controls by default
        self.advanced_stitch_widget.setVisible(False)
        stitch_layout.addWidget(self.advanced_stitch_widget)
        
        layout.addWidget(stitch_group)
        
        # Face Arrangement group
        face_group = QGroupBox("Cubemap Face Arrangement")
        face_layout = QVBoxLayout(face_group)
        
        # Preset selection
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Front Camera",
            "Back Camera",
            "Custom..."
        ])
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        preset_row.addWidget(self.preset_combo)
        preset_row.addStretch()
        face_layout.addLayout(preset_row)
        
        # Collapsible manual arrangement section
        self.manual_arrangement_btn = QPushButton("▶ Manual Arrangement")
        self.manual_arrangement_btn.setStyleSheet("text-align: left; border: none; padding: 5px;")
        self.manual_arrangement_btn.clicked.connect(self.toggle_manual_arrangement)
        face_layout.addWidget(self.manual_arrangement_btn)
        
        # Container for manual controls (hidden by default)
        self.manual_arrangement_widget = QWidget()
        manual_layout = QVBoxLayout(self.manual_arrangement_widget)
        manual_layout.setContentsMargins(10, 0, 0, 0)
        
        # Face sources (which extracted face goes to which cubemap position)
        # Track 0: left(0), front(1), right(2)
        # Track 1 after transpose: first(3), second(4), third(5)
        face_sources = ["Track0-Left", "Track0-Front", "Track0-Right", 
                        "Track1-First", "Track1-Second", "Track1-Third"]
        rotations = ["0°", "90°", "180°", "270°"]
        
        # Top face row
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Top:"))
        self.top_face_combo = QComboBox()
        self.top_face_combo.addItems(face_sources)
        self.top_face_combo.setCurrentIndex(5)  # Default: Front Camera preset
        top_row.addWidget(self.top_face_combo)
        top_row.addWidget(QLabel("Rot:"))
        self.top_rot_combo = QComboBox()
        self.top_rot_combo.addItems(rotations)
        self.top_rot_combo.setCurrentIndex(0)
        top_row.addWidget(self.top_rot_combo)
        top_row.addStretch()
        manual_layout.addLayout(top_row)
        
        # Middle row: Back, Left, Front, Right
        middle_label = QLabel("Middle row (Back | Left | Front | Right):")
        middle_label.setStyleSheet("font-size: 10px; color: #888;")
        manual_layout.addWidget(middle_label)
        
        middle_row = QHBoxLayout()
        
        # Back
        back_col = QVBoxLayout()
        back_col.addWidget(QLabel("Back:"))
        self.back_face_combo = QComboBox()
        self.back_face_combo.addItems(face_sources)
        self.back_face_combo.setCurrentIndex(1)  # Default: Front Camera preset
        back_col.addWidget(self.back_face_combo)
        back_rot_row = QHBoxLayout()
        back_rot_row.addWidget(QLabel("Rot:"))
        self.back_rot_combo = QComboBox()
        self.back_rot_combo.addItems(rotations)
        self.back_rot_combo.setCurrentIndex(0)
        back_rot_row.addWidget(self.back_rot_combo)
        back_col.addLayout(back_rot_row)
        middle_row.addLayout(back_col)
        
        # Left
        left_col = QVBoxLayout()
        left_col.addWidget(QLabel("Left:"))
        self.left_face_combo = QComboBox()
        self.left_face_combo.addItems(face_sources)
        self.left_face_combo.setCurrentIndex(0)  # Default: Front Camera preset
        left_col.addWidget(self.left_face_combo)
        left_rot_row = QHBoxLayout()
        left_rot_row.addWidget(QLabel("Rot:"))
        self.left_rot_combo = QComboBox()
        self.left_rot_combo.addItems(rotations)
        self.left_rot_combo.setCurrentIndex(0)
        left_rot_row.addWidget(self.left_rot_combo)
        left_col.addLayout(left_rot_row)
        middle_row.addLayout(left_col)
        
        # Front
        front_col = QVBoxLayout()
        front_col.addWidget(QLabel("Front:"))
        self.front_face_combo = QComboBox()
        self.front_face_combo.addItems(face_sources)
        self.front_face_combo.setCurrentIndex(3)  # Default: Front Camera preset
        front_col.addWidget(self.front_face_combo)
        front_rot_row = QHBoxLayout()
        front_rot_row.addWidget(QLabel("Rot:"))
        self.front_rot_combo = QComboBox()
        self.front_rot_combo.addItems(rotations)
        self.front_rot_combo.setCurrentIndex(0)
        front_rot_row.addWidget(self.front_rot_combo)
        front_col.addLayout(front_rot_row)
        middle_row.addLayout(front_col)
        
        # Right
        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("Right:"))
        self.right_face_combo = QComboBox()
        self.right_face_combo.addItems(face_sources)
        self.right_face_combo.setCurrentIndex(2)  # Default: Front Camera preset
        right_col.addWidget(self.right_face_combo)
        right_rot_row = QHBoxLayout()
        right_rot_row.addWidget(QLabel("Rot:"))
        self.right_rot_combo = QComboBox()
        self.right_rot_combo.addItems(rotations)
        self.right_rot_combo.setCurrentIndex(0)
        right_rot_row.addWidget(self.right_rot_combo)
        right_col.addLayout(right_rot_row)
        middle_row.addLayout(right_col)
        
        manual_layout.addLayout(middle_row)
        
        # Bottom face row
        bottom_row = QHBoxLayout()
        bottom_row.addWidget(QLabel("Bottom:"))
        self.bottom_face_combo = QComboBox()
        self.bottom_face_combo.addItems(face_sources)
        self.bottom_face_combo.setCurrentIndex(4)  # Default: Front Camera preset
        bottom_row.addWidget(self.bottom_face_combo)
        bottom_row.addWidget(QLabel("Rot:"))
        self.bottom_rot_combo = QComboBox()
        self.bottom_rot_combo.addItems(rotations)
        self.bottom_rot_combo.setCurrentIndex(2)  # 180° for Front Camera preset
        bottom_row.addWidget(self.bottom_rot_combo)
        bottom_row.addStretch()
        manual_layout.addLayout(bottom_row)
        
        # Export arrangement button
        export_btn_row = QHBoxLayout()
        self.export_arrangement_btn = QPushButton("Export Arrangement")
        self.export_arrangement_btn.clicked.connect(self.export_face_arrangement)
        self.export_arrangement_btn.setToolTip("Copy current face arrangement to clipboard")
        export_btn_row.addWidget(self.export_arrangement_btn)
        export_btn_row.addStretch()
        manual_layout.addLayout(export_btn_row)
        
        # Hide manual controls by default
        self.manual_arrangement_widget.setVisible(False)
        face_layout.addWidget(self.manual_arrangement_widget)
        
        layout.addWidget(face_group)
        
        # Compression settings group
        compression_group = QGroupBox("Output Settings")
        compression_layout = QFormLayout(compression_group)
        
        self.codec_combo = QComboBox()
        self.codec_combo.addItems([
            "H.264 (libx264) - Most Compatible",
            "H.265/HEVC (libx265) - Better Compression",
            "VP9 - Web Optimized",
        ])
        compression_layout.addRow("Video Codec:", self.codec_combo)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "High (CRF 18)",
            "Medium (CRF 23)",
            "Low (CRF 28)",
            "Very Low (CRF 35)",
        ])
        self.quality_combo.setCurrentIndex(1)
        compression_layout.addRow("Quality:", self.quality_combo)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "Original",
            "4K (3840x1920)",
            "2.7K (2704x1352)", 
            "1080p (1920x960)",
            "720p (1280x640)",
        ])
        compression_layout.addRow("Output Resolution:", self.resolution_combo)
        
        self.audio_check = QCheckBox("Include Audio")
        self.audio_check.setChecked(True)
        compression_layout.addRow("", self.audio_check)
        
        layout.addWidget(compression_group)
        
        # Spacer
        layout.addStretch()
        
        # Convert button
        self.convert_btn = QPushButton("Convert to Equirectangular MP4")
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0080ff;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
            }
        """)
        layout.addWidget(self.convert_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        layout.addWidget(self.cancel_btn)
        
        return panel
        
    def create_progress_section(self):
        """Create the progress bar section"""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        
        self.progress_label = QLabel("Ready")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar, 1)
        
        self.eta_label = QLabel("")
        self.eta_label.setMinimumWidth(100)
        layout.addWidget(self.eta_label)
        
        return frame
        
    def browse_input_file(self):
        """Open file dialog to select input .360 file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select GoPro .360 File",
            "",
            "GoPro 360 Files (*.360);;All Files (*.*)"
        )
        
        if file_path:
            self.set_input_file(file_path)
            
    def set_input_file(self, file_path):
        """Set the input file and load its info"""
        self.input_file = file_path
        filename = os.path.basename(file_path)
        self.input_path_label.setText(filename)
        self.input_path_label.setStyleSheet("color: #00cc00;")
        self.input_path_label.setToolTip(file_path)
        
        # Enable controls
        self.browse_output_btn.setEnabled(True)
        self.refresh_preview_btn.setEnabled(True)
        self.test_stitch_btn.setEnabled(True)
        
        # Set default output path
        base_name = os.path.splitext(file_path)[0]
        self.output_file = f"{base_name}_equirect.mp4"
        self.output_path_label.setText(os.path.basename(self.output_file))
        self.output_path_label.setStyleSheet("color: #00cc00;")
        self.output_path_label.setToolTip(self.output_file)
        
        # Load video info
        self.load_video_info()
        
        # Generate preview
        self.refresh_preview()
        
        # Enable convert button
        self.convert_btn.setEnabled(True)
        
        self.status_bar.showMessage(f"Loaded: {filename}")
        
    def browse_output_file(self):
        """Open file dialog to select output file path"""
        default_name = ""
        if self.input_file:
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            default_name = f"{base_name}_equirect.mp4"
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Converted Video",
            default_name,
            "MP4 Files (*.mp4);;WebM Files (*.webm);;All Files (*.*)"
        )
        
        if file_path:
            self.output_file = file_path
            self.output_path_label.setText(os.path.basename(file_path))
            self.output_path_label.setStyleSheet("color: #00cc00;")
            self.output_path_label.setToolTip(file_path)
            
    def load_video_info(self):
        """Load and display video information"""
        if not self.input_file:
            return
            
        info = self.video_processor.get_video_info(self.input_file)
        
        if info:
            # Update frame slider
            total_frames = info.get('total_frames', 100)
            self.frame_slider.setMaximum(max(1, total_frames - 1))
            self.frame_label.setText(f"0 / {total_frames}")
            
    def refresh_preview(self):
        """Generate and display preview of the stitched frame"""
        if not self.input_file:
            return
            
        frame_number = self.frame_slider.value()
        settings = self.get_current_settings()
        
        self.status_bar.showMessage("Generating preview...")
        
        preview_image = self.preview_generator.generate_preview(
            self.input_file,
            frame_number,
            settings
        )
        
        if preview_image is not None:
            self.display_preview(preview_image)
            self.status_bar.showMessage("Preview updated")
        else:
            self.preview_label.setText("Failed to generate preview\n\nCheck FFmpeg installation")
            self.status_bar.showMessage("Preview generation failed")
            
    def display_preview(self, image):
        """Display a numpy image in the preview label"""
        if image is None:
            return
            
        height, width = image.shape[:2]
        
        # Convert to QImage
        if len(image.shape) == 3:
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        else:
            bytes_per_line = width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            
        # Scale to fit preview area while maintaining aspect ratio
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.preview_label.setPixmap(scaled_pixmap)
        
    def on_frame_slider_changed(self, value):
        """Handle frame slider value change"""
        info = self.video_processor.get_video_info(self.input_file) if self.input_file else None
        total_frames = info.get('total_frames', 0) if info else 0
        self.frame_label.setText(f"{value} / {total_frames}")
        
    def export_face_arrangement(self):
        """Export the current face arrangement to clipboard"""
        face_mapping = {}
        face_rotation = {}
        
        face_order = ['top', 'back', 'left', 'front', 'right', 'bottom']
        for face in face_order:
            source_combo = getattr(self, f'{face}_face_combo')
            rotation_combo = getattr(self, f'{face}_rot_combo')
            face_mapping[face] = source_combo.currentIndex()
            face_rotation[face] = rotation_combo.currentIndex()
        
        # Format as a string
        arrangement_text = f"Face Arrangement:\n"
        arrangement_text += f"  face_mapping = {face_mapping}\n"
        arrangement_text += f"  face_rotation = {face_rotation}\n\n"
        arrangement_text += "Human-readable:\n"
        
        source_names = ["Track0-Left", "Track0-Front", "Track0-Right", 
                        "Track1-First", "Track1-Second", "Track1-Third"]
        rotation_names = ["0°", "90°", "180°", "270°"]
        
        for face in face_order:
            src_idx = face_mapping[face]
            rot_idx = face_rotation[face]
            arrangement_text += f"  {face.capitalize()}: {source_names[src_idx]}, Rotation: {rotation_names[rot_idx]}\n"
        
        # Copy to clipboard
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(arrangement_text)
        
        # Show message
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Arrangement Exported", 
                               f"Face arrangement copied to clipboard:\n\n{arrangement_text}")
    
    def toggle_manual_arrangement(self):
        """Toggle visibility of manual arrangement controls"""
        visible = not self.manual_arrangement_widget.isVisible()
        self.manual_arrangement_widget.setVisible(visible)
        if visible:
            self.manual_arrangement_btn.setText("▼ Manual Arrangement")
        else:
            self.manual_arrangement_btn.setText("▶ Manual Arrangement")
    
    def toggle_advanced_stitch(self):
        """Toggle visibility of advanced stitch settings"""
        visible = not self.advanced_stitch_widget.isVisible()
        self.advanced_stitch_widget.setVisible(visible)
        if visible:
            self.advanced_stitch_btn.setText("▼ Advanced Stitch Settings")
        else:
            self.advanced_stitch_btn.setText("▶ Advanced Stitch Settings")
    
    def on_stitch_method_changed(self, index):
        """Handle stitch method selection change"""
        is_ffmpeg_method = (index == 0)
        
        # Show/hide advanced options based on method
        # FFmpeg method doesn't need edge_overlap and blend_width - it uses fixed values
        # Python method uses these settings
        if is_ffmpeg_method:
            # Hide advanced stitch settings for FFmpeg method (not applicable)
            self.advanced_stitch_widget.setVisible(False)
            self.advanced_stitch_btn.setText("▶ Advanced Stitch Settings")
            self.advanced_stitch_btn.setEnabled(False)
            self.advanced_stitch_btn.setToolTip("Advanced settings not available for FFmpeg method")
        else:
            # Show advanced stitch settings for Python method
            self.advanced_stitch_btn.setEnabled(True)
            self.advanced_stitch_btn.setToolTip("Click to expand advanced stitch settings")
    
    def on_preset_changed(self, index):
        """Handle preset selection change"""
        # Presets: 0 = Front Camera, 1 = Back Camera, 2 = Custom
        presets = {
            0: {  # Front Camera
                'face_mapping': {'top': 5, 'back': 1, 'left': 0, 'front': 3, 'right': 2, 'bottom': 4},
                'face_rotation': {'top': 0, 'back': 0, 'left': 0, 'front': 0, 'right': 0, 'bottom': 2}
            },
            1: {  # Back Camera
                'face_mapping': {'top': 5, 'back': 4, 'left': 2, 'front': 3, 'right': 0, 'bottom': 1},
                'face_rotation': {'top': 2, 'back': 2, 'left': 0, 'front': 2, 'right': 0, 'bottom': 0}
            }
        }
        
        if index in presets:
            preset = presets[index]
            # Apply face mapping
            self.top_face_combo.setCurrentIndex(preset['face_mapping']['top'])
            self.back_face_combo.setCurrentIndex(preset['face_mapping']['back'])
            self.left_face_combo.setCurrentIndex(preset['face_mapping']['left'])
            self.front_face_combo.setCurrentIndex(preset['face_mapping']['front'])
            self.right_face_combo.setCurrentIndex(preset['face_mapping']['right'])
            self.bottom_face_combo.setCurrentIndex(preset['face_mapping']['bottom'])
            # Apply rotation
            self.top_rot_combo.setCurrentIndex(preset['face_rotation']['top'])
            self.back_rot_combo.setCurrentIndex(preset['face_rotation']['back'])
            self.left_rot_combo.setCurrentIndex(preset['face_rotation']['left'])
            self.front_rot_combo.setCurrentIndex(preset['face_rotation']['front'])
            self.right_rot_combo.setCurrentIndex(preset['face_rotation']['right'])
            self.bottom_rot_combo.setCurrentIndex(preset['face_rotation']['bottom'])
        elif index == 2:
            # Custom - expand manual arrangement
            self.manual_arrangement_widget.setVisible(True)
            self.manual_arrangement_btn.setText("▼ Manual Arrangement")
        
    def get_current_settings(self):
        """Get current conversion settings"""
        projection_map = {
            0: "gopro_max",  # Custom 2-channel cubemap format
        }
        
        interp_map = {
            0: "linear",
            1: "cubic",
            2: "lanczos",
        }
        
        codec_map = {
            0: "libx264",
            1: "libx265",
            2: "libvpx-vp9",
        }
        
        quality_map = {
            0: 18,
            1: 23,
            2: 28,
            3: 35,
        }
        
        resolution_map = {
            0: None,  # Original
            1: (3840, 1920),
            2: (2704, 1352),
            3: (1920, 960),
            4: (1280, 640),
        }
        
        return {
            'projection': "gopro_max",  # Only one format now
            'fov': 180,  # Fixed at 180 degrees (no overlap adjustment via FOV)
            'edge_overlap': self.edge_overlap_spinbox.value(),
            'blend_width': self.blend_width_spinbox.value(),
            'interpolation': interp_map.get(self.interp_combo.currentIndex(), "cubic"),
            'codec': codec_map.get(self.codec_combo.currentIndex(), "libx264"),
            'crf': quality_map.get(self.quality_combo.currentIndex(), 23),
            'resolution': resolution_map.get(self.resolution_combo.currentIndex()),
            'include_audio': self.audio_check.isChecked(),
            # Stitching method: 0 = FFmpeg (fast), 1 = Python (slow)
            'stitch_method': 'ffmpeg' if self.stitch_method_combo.currentIndex() == 0 else 'python',
            # Face arrangement settings
            'face_mapping': {
                'top': self.top_face_combo.currentIndex(),
                'back': self.back_face_combo.currentIndex(),
                'left': self.left_face_combo.currentIndex(),
                'front': self.front_face_combo.currentIndex(),
                'right': self.right_face_combo.currentIndex(),
                'bottom': self.bottom_face_combo.currentIndex(),
            },
            'face_rotation': {
                'top': self.top_rot_combo.currentIndex() * 90,
                'back': self.back_rot_combo.currentIndex() * 90,
                'left': self.left_rot_combo.currentIndex() * 90,
                'front': self.front_rot_combo.currentIndex() * 90,
                'right': self.right_rot_combo.currentIndex() * 90,
                'bottom': self.bottom_rot_combo.currentIndex() * 90,
            },
        }
        
    def start_conversion(self):
        """Start the video conversion process"""
        if not self.input_file or not self.output_file:
            QMessageBox.warning(self, "Error", "Please select input and output files.")
            return
            
        # Check if output file exists
        if os.path.exists(self.output_file):
            reply = QMessageBox.question(
                self, "File Exists",
                f"The output file already exists:\n{self.output_file}\n\nOverwrite?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
                
        settings = self.get_current_settings()
        
        # Disable controls during conversion
        self.set_controls_enabled(False)
        self.cancel_btn.setEnabled(True)
        
        # Create worker thread
        self.conversion_thread = QThread()
        self.conversion_worker = ConversionWorker(
            self.video_processor,
            self.input_file,
            self.output_file,
            settings
        )
        self.conversion_worker.moveToThread(self.conversion_thread)
        
        # Connect signals
        self.conversion_thread.started.connect(self.conversion_worker.run)
        self.conversion_worker.progress.connect(self.on_conversion_progress)
        self.conversion_worker.finished.connect(self.on_conversion_finished)
        self.conversion_worker.error.connect(self.on_conversion_error)
        self.conversion_worker.finished.connect(self.conversion_thread.quit)
        self.conversion_worker.error.connect(self.conversion_thread.quit)
        
        # Start conversion
        self.conversion_thread.start()
        self.status_bar.showMessage("Conversion started...")
        
    def cancel_conversion(self):
        """Cancel the ongoing conversion"""
        if self.conversion_worker:
            self.conversion_worker.cancel()
            self.status_bar.showMessage("Cancelling conversion...")
            
    def on_conversion_progress(self, progress, eta):
        """Handle conversion progress update"""
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(f"Converting: {progress:.1f}%")
        self.eta_label.setText(eta if eta else "")
        
    def on_conversion_finished(self):
        """Handle conversion completion"""
        self.set_controls_enabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        self.progress_label.setText("Conversion complete!")
        self.eta_label.setText("")
        self.status_bar.showMessage("Conversion completed successfully!")
        
        QMessageBox.information(
            self, "Success",
            f"Video converted successfully!\n\nSaved to:\n{self.output_file}"
        )
        
    def on_conversion_error(self, error_message):
        """Handle conversion error"""
        self.set_controls_enabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Error")
        self.eta_label.setText("")
        self.status_bar.showMessage("Conversion failed!")
        
        QMessageBox.critical(self, "Conversion Error", error_message)
        
    def set_controls_enabled(self, enabled):
        """Enable or disable controls during conversion"""
        self.browse_input_btn.setEnabled(enabled)
        self.browse_output_btn.setEnabled(enabled and self.input_file is not None)
        self.convert_btn.setEnabled(enabled and self.input_file is not None)
        self.refresh_preview_btn.setEnabled(enabled and self.input_file is not None)
        self.test_stitch_btn.setEnabled(enabled and self.input_file is not None)
        self.stitch_method_combo.setEnabled(enabled)
        self.interp_combo.setEnabled(enabled)
        self.edge_overlap_spinbox.setEnabled(enabled)
        self.blend_width_spinbox.setEnabled(enabled)
        self.codec_combo.setEnabled(enabled)
        self.quality_combo.setEnabled(enabled)
        self.resolution_combo.setEnabled(enabled)
        self.audio_check.setEnabled(enabled)
        self.frame_slider.setEnabled(enabled)

    def generate_test_stitch_png(self):
        """Generate a test PNG to preview the stitching result"""
        if not self.input_file:
            QMessageBox.warning(self, "Error", "Please select an input file first.")
            return
            
        # Determine output path
        base_name = os.path.splitext(self.input_file)[0]
        output_path = f"{base_name}_stitch_test.png"
        
        # Get timestamp from current frame slider position
        frame_number = self.frame_slider.value()
        fps = 30  # Assume 30fps
        timestamp = frame_number / fps
        
        self.status_bar.showMessage("Generating test PNG...")
        self.test_stitch_btn.setEnabled(False)
        
        # Check which stitching method is selected
        use_ffmpeg_method = (self.stitch_method_combo.currentIndex() == 0)
        
        try:
            if use_ffmpeg_method:
                # Use FFmpeg-based stitcher
                success, message = self.ffmpeg_stitcher.extract_stitched_frame(
                    self.input_file,
                    output_path,
                    timestamp=timestamp
                )
                
                if success:
                    self.status_bar.showMessage(f"Test PNG saved: {output_path}")
                    QMessageBox.information(
                        self, "Success",
                        f"Test PNG generated successfully!\n\nSaved to:\n{output_path}\n\n"
                        f"This is the final equirectangular output using FFmpeg stitching."
                    )
                else:
                    self.status_bar.showMessage("Failed to generate test PNG")
                    QMessageBox.warning(self, "Error", f"Failed to generate test PNG:\n{message}")
            else:
                # Use Python-based seam stitcher
                try:
                    from core.seam_stitcher import SeamStitcher
                except ImportError as e:
                    QMessageBox.critical(self, "Error", f"Failed to import seam stitcher: {e}")
                    return
                    
                # Get current settings
                edge_overlap = self.edge_overlap_spinbox.value()
                blend_width = self.blend_width_spinbox.value()
                    
                stitcher = SeamStitcher()
                success = stitcher.generate_stitch_test_png(
                    self.input_file,
                    output_path,
                    timestamp=timestamp,
                    edge_overlap=edge_overlap,
                    blend_width=blend_width
                )
                
                if success:
                    self.status_bar.showMessage(f"Test PNG saved: {output_path}")
                    QMessageBox.information(
                        self, "Success",
                        f"Test PNG generated successfully!\n\nSaved to:\n{output_path}\n\n"
                        f"The image shows:\n- Row 1: Track 0 (original | stitched)\n"
                        f"- Row 2: Track 1 (original | stitched)\n\n"
                        f"Red lines mark the seam positions at 1/6 and 5/6."
                    )
                else:
                    self.status_bar.showMessage("Failed to generate test PNG")
                    QMessageBox.warning(self, "Error", "Failed to generate test PNG. Check console for details.")
                
        except Exception as e:
            self.status_bar.showMessage("Error generating test PNG")
            QMessageBox.critical(self, "Error", f"Error generating test PNG:\n{str(e)}")
        finally:
            self.test_stitch_btn.setEnabled(True)

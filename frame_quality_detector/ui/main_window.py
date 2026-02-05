#!/usr/bin/env python3
"""
Main Window for Frame Quality Detector GUI

Provides a graphical interface for analyzing video frames and selecting
the best quality frames based on sharpness and motion blur detection.
"""

import sys
import os
import tempfile
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QProgressBar, QTextEdit, QFileDialog, QMessageBox, QSplitter,
    QListWidget, QListWidgetItem, QGroupBox, QSlider, QCheckBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QFont, QIcon

import cv2
import numpy as np

from core.frame_extractor import FrameExtractor
from core.quality_analyzer import FrameQualityAnalyzer
from core.adaptive_frame_extractor import AdaptiveFrameExtractor


class AnalysisWorker(QThread):
    """Worker thread for frame analysis to prevent GUI freezing."""
    
    progress_update = pyqtSignal(int, str)  # progress, message
    analysis_complete = pyqtSignal(list)   # results
    error_occurred = pyqtSignal(str)       # error message
    
    def __init__(self, frames_dir: str, analyzer: FrameQualityAnalyzer, 
                 quality_threshold: float = 0.0):
        super().__init__()
        self.frames_dir = frames_dir
        self.analyzer = analyzer
        self.quality_threshold = quality_threshold
        self._should_stop = False
    
    def stop(self):
        self._should_stop = True
    
    def run(self):
        try:
            # Get list of image files
            image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
            image_files = []
            
            for file_path in Path(self.frames_dir).iterdir():
                if file_path.suffix.lower() in image_extensions:
                    image_files.append(str(file_path))
            
            image_files.sort()
            
            if not image_files:
                self.error_occurred.emit(f"No image files found in {self.frames_dir}")
                return
            
            self.progress_update.emit(0, f"Found {len(image_files)} frames to analyze")
            
            # Analyze each frame
            results = []
            
            for i, image_path in enumerate(image_files):
                if self._should_stop:
                    break
                
                try:
                    result = self.analyzer.analyze_frame(image_path)
                    
                    # Apply quality threshold
                    if result['quality_score'] >= self.quality_threshold:
                        results.append(result)
                    
                    # Update progress
                    progress = int((i + 1) / len(image_files) * 100)
                    self.progress_update.emit(progress, f"Analyzed {i+1}/{len(image_files)} frames")
                    
                except Exception as e:
                    print(f"Error analyzing {image_path}: {e}")
                    continue
            
            # Sort by quality score
            results.sort(key=lambda x: x['quality_score'], reverse=True)
            
            if not self._should_stop:
                self.analysis_complete.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class FramePreviewWidget(QWidget):
    """Widget for displaying frame preview with quality information."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_frame_data = None
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        layout.addWidget(self.image_label)
        
        # Frame info
        info_layout = QGridLayout()
        
        self.filename_label = QLabel("No frame selected")
        self.filename_label.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout.addWidget(QLabel("Frame:"), 0, 0)
        info_layout.addWidget(self.filename_label, 0, 1)
        
        self.quality_label = QLabel("-")
        self.quality_label.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout.addWidget(QLabel("Quality Score:"), 1, 0)
        info_layout.addWidget(self.quality_label, 1, 1)
        
        self.sharpness_label = QLabel("-")
        info_layout.addWidget(QLabel("Sharpness:"), 2, 0)
        info_layout.addWidget(self.sharpness_label, 2, 1)
        
        self.blur_label = QLabel("-")
        info_layout.addWidget(QLabel("Blur Score:"), 3, 0)
        info_layout.addWidget(self.blur_label, 3, 1)
        
        self.size_label = QLabel("-")
        info_layout.addWidget(QLabel("Size:"), 4, 0)
        info_layout.addWidget(self.size_label, 4, 1)
        
        layout.addLayout(info_layout)
        
        self.setLayout(layout)
    
    def update_frame(self, frame_data: Dict[str, Any]):
        """Update the preview with new frame data."""
        self.current_frame_data = frame_data
        
        # Load and display image
        image_path = frame_data['path']
        pixmap = QPixmap(image_path)
        
        if not pixmap.isNull():
            # Scale image to fit label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Could not load image")
        
        # Update info labels
        self.filename_label.setText(frame_data['filename'])
        self.quality_label.setText(f"{frame_data['quality_score']:.2f}")
        self.sharpness_label.setText(f"{frame_data['sharpness_score']:.2f}")
        self.blur_label.setText(f"{frame_data['blur_score']:.2f}")
        
        size = frame_data['image_size']
        self.size_label.setText(f"{size[1]} x {size[0]}")
        
        # Color-code quality score
        quality = frame_data['quality_score']
        if quality >= 80:
            color = "green"
        elif quality >= 60:
            color = "orange"
        else:
            color = "red"
        
        self.quality_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def clear(self):
        """Clear the preview."""
        self.image_label.clear()
        self.image_label.setText("No frame selected")
        self.filename_label.setText("No frame selected")
        self.quality_label.setText("-")
        self.quality_label.setStyleSheet("")
        self.sharpness_label.setText("-")
        self.blur_label.setText("-")
        self.size_label.setText("-")
        self.current_frame_data = None


class FrameQualityMainWindow(QMainWindow):
    """Main window for Frame Quality Detector application."""
    
    def __init__(self):
        super().__init__()
        self.analysis_results = []
        self.current_frames_dir = None
        self.analyzer = FrameQualityAnalyzer(verbose=False)
        self.analysis_worker = None
        
        self.setup_ui()
        self.setup_connections()
        
        # Set window properties
        self.setWindowTitle("Frame Quality Detector")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
    
    def setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Controls and settings
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Results and preview
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
    
    def create_left_panel(self) -> QWidget:
        """Create the left control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Input section
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout(input_group)
        
        # Video file selection
        video_layout = QHBoxLayout()
        self.video_path_edit = QLineEdit()
        self.video_path_edit.setPlaceholderText("Select video file...")
        self.video_browse_btn = QPushButton("Browse")
        video_layout.addWidget(self.video_path_edit)
        video_layout.addWidget(self.video_browse_btn)
        input_layout.addLayout(video_layout)
        
        # Frames directory selection
        frames_layout = QHBoxLayout()
        self.frames_dir_edit = QLineEdit()
        self.frames_dir_edit.setPlaceholderText("Or select frames directory...")
        self.frames_browse_btn = QPushButton("Browse")
        frames_layout.addWidget(self.frames_dir_edit)
        frames_layout.addWidget(self.frames_browse_btn)
        input_layout.addLayout(frames_layout)
        
        layout.addWidget(input_group)
        
        # Extraction settings
        extract_group = QGroupBox("Frame Extraction")
        extract_layout = QGridLayout(extract_group)
        
        extract_layout.addWidget(QLabel("FPS:"), 0, 0)
        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setRange(0.1, 30.0)
        self.fps_spin.setValue(1.0)
        self.fps_spin.setSingleStep(0.1)
        extract_layout.addWidget(self.fps_spin, 0, 1)
        
        self.extract_btn = QPushButton("Extract Frames")
        extract_layout.addWidget(self.extract_btn, 1, 0, 1, 2)
        
        # Adaptive extraction checkbox
        self.adaptive_checkbox = QCheckBox("Use Adaptive Extraction (Recommended)")
        self.adaptive_checkbox.setChecked(True)
        self.adaptive_checkbox.setToolTip("Intelligently finds best frames around target positions")
        extract_layout.addWidget(self.adaptive_checkbox, 2, 0, 1, 2)
        
        layout.addWidget(extract_group)
        
        # Analysis settings
        analysis_group = QGroupBox("Analysis Settings")
        analysis_layout = QGridLayout(analysis_group)
        
        analysis_layout.addWidget(QLabel("Sharpness Weight:"), 0, 0)
        self.sharpness_weight_spin = QDoubleSpinBox()
        self.sharpness_weight_spin.setRange(0.0, 1.0)
        self.sharpness_weight_spin.setValue(0.7)
        self.sharpness_weight_spin.setSingleStep(0.1)
        analysis_layout.addWidget(self.sharpness_weight_spin, 0, 1)
        
        analysis_layout.addWidget(QLabel("Blur Weight:"), 1, 0)
        self.blur_weight_spin = QDoubleSpinBox()
        self.blur_weight_spin.setRange(0.0, 1.0)
        self.blur_weight_spin.setValue(0.3)
        self.blur_weight_spin.setSingleStep(0.1)
        analysis_layout.addWidget(self.blur_weight_spin, 1, 1)
        
        analysis_layout.addWidget(QLabel("Quality Threshold:"), 2, 0)
        self.quality_threshold_spin = QDoubleSpinBox()
        self.quality_threshold_spin.setRange(0.0, 100.0)
        self.quality_threshold_spin.setValue(0.0)
        self.quality_threshold_spin.setSingleStep(1.0)
        analysis_layout.addWidget(self.quality_threshold_spin, 2, 1)
        
        self.analyze_btn = QPushButton("Analyze Frames")
        self.analyze_btn.setEnabled(False)
        analysis_layout.addWidget(self.analyze_btn, 3, 0, 1, 2)
        
        layout.addWidget(analysis_group)
        
        # Output settings
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        
        # Output directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Select output directory...")
        self.output_browse_btn = QPushButton("Browse")
        output_dir_layout.addWidget(self.output_dir_edit)
        output_dir_layout.addWidget(self.output_browse_btn)
        output_layout.addLayout(output_dir_layout)
        
        # Top N frames
        top_n_layout = QHBoxLayout()
        top_n_layout.addWidget(QLabel("Save top:"))
        self.top_n_spin = QSpinBox()
        self.top_n_spin.setRange(1, 100)
        self.top_n_spin.setValue(5)
        top_n_layout.addWidget(self.top_n_spin)
        top_n_layout.addWidget(QLabel("frames"))
        top_n_layout.addStretch()
        output_layout.addLayout(top_n_layout)
        
        self.save_btn = QPushButton("Save Best Frames")
        self.save_btn.setEnabled(False)
        output_layout.addWidget(self.save_btn)
        
        layout.addWidget(output_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right results panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Results list tab
        results_tab = self.create_results_tab()
        self.tab_widget.addTab(results_tab, "Frame List")
        
        # Details table tab
        details_tab = self.create_details_tab()
        self.tab_widget.addTab(details_tab, "Detailed Metrics")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def create_results_tab(self) -> QWidget:
        """Create the results tab with frame list and preview."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left side - frame list
        left_layout = QVBoxLayout()
        
        list_label = QLabel("Analysis Results")
        list_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(list_label)
        
        self.results_list = QListWidget()
        self.results_list.setMinimumWidth(250)
        left_layout.addWidget(self.results_list)
        
        list_widget = QWidget()
        list_widget.setLayout(left_layout)
        list_widget.setMaximumWidth(300)
        
        # Right side - preview
        self.frame_preview = FramePreviewWidget()
        
        layout.addWidget(list_widget)
        layout.addWidget(self.frame_preview)
        
        return tab
    
    def create_details_tab(self) -> QWidget:
        """Create the detailed metrics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        details_label = QLabel("Detailed Metrics")
        details_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(details_label)
        
        self.details_table = QTableWidget()
        self.details_table.setAlternatingRowColors(True)
        self.details_table.setSortingEnabled(True)
        layout.addWidget(self.details_table)
        
        return tab
    
    def setup_connections(self):
        """Setup signal-slot connections."""
        # File browsing
        self.video_browse_btn.clicked.connect(self.browse_video_file)
        self.frames_browse_btn.clicked.connect(self.browse_frames_directory)
        self.output_browse_btn.clicked.connect(self.browse_output_directory)
        
        # Processing
        self.extract_btn.clicked.connect(self.extract_frames)
        self.analyze_btn.clicked.connect(self.analyze_frames)
        self.save_btn.clicked.connect(self.save_best_frames)
        
        # Weight updates
        self.sharpness_weight_spin.valueChanged.connect(self.update_weights)
        self.blur_weight_spin.valueChanged.connect(self.update_weights)
        
        # Results selection
        self.results_list.currentItemChanged.connect(self.on_result_selected)
        
        # Text field updates
        self.frames_dir_edit.textChanged.connect(self.on_frames_dir_changed)
    
    def browse_video_file(self):
        """Browse for video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "", 
            "Video Files (*.mp4 *.avi *.mov *.webm *.mkv *.wmv);;All Files (*)"
        )
        if file_path:
            self.video_path_edit.setText(file_path)
    
    def browse_frames_directory(self):
        """Browse for frames directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Frames Directory"
        )
        if dir_path:
            self.frames_dir_edit.setText(dir_path)
    
    def browse_output_directory(self):
        """Browse for output directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    def on_frames_dir_changed(self):
        """Handle frames directory text change."""
        frames_dir = self.frames_dir_edit.text().strip()
        self.analyze_btn.setEnabled(bool(frames_dir and os.path.isdir(frames_dir)))
    
    def update_weights(self):
        """Update analyzer weights when spinboxes change."""
        sharpness_weight = self.sharpness_weight_spin.value()
        blur_weight = self.blur_weight_spin.value()
        
        # Ensure weights sum to 1.0
        total = sharpness_weight + blur_weight
        if total != 1.0 and total > 0:
            # Normalize weights
            normalized_sharpness = sharpness_weight / total
            normalized_blur = blur_weight / total
            
            # Block signals to prevent recursion
            self.sharpness_weight_spin.blockSignals(True)
            self.blur_weight_spin.blockSignals(True)
            
            self.sharpness_weight_spin.setValue(normalized_sharpness)
            self.blur_weight_spin.setValue(normalized_blur)
            
            self.sharpness_weight_spin.blockSignals(False)
            self.blur_weight_spin.blockSignals(False)
        
        # Update analyzer
        self.analyzer = FrameQualityAnalyzer(
            sharpness_weight=self.sharpness_weight_spin.value(),
            blur_weight=self.blur_weight_spin.value(),
            verbose=False
        )
    
    def extract_frames(self):
        """Extract frames from video."""
        video_path = self.video_path_edit.text().strip()
        
        if not video_path or not os.path.exists(video_path):
            QMessageBox.warning(self, "Error", "Please select a valid video file.")
            return
        
        try:
            # Create temporary directory for frames
            frames_dir = tempfile.mkdtemp(prefix='frame_quality_')
            
            self.status_label.setText("Extracting frames...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Extract frames in separate thread
            extractor = FrameExtractor(verbose=True)  # Enable verbose for debugging
            
            def extract_worker():
                try:
                    fps = self.fps_spin.value()
                    print(f"GUI: Starting frame extraction from {video_path} at {fps} fps to {frames_dir}")
                    
                    if self.adaptive_checkbox.isChecked():
                        # Use adaptive extraction
                        adaptive_extractor = AdaptiveFrameExtractor(
                            quality_threshold=70.0,  # Default threshold
                            verbose=True
                        )
                        result_dir = adaptive_extractor.extract_adaptive_frames(
                            video_path, frames_dir, fps
                        )
                    else:
                        # Use regular extraction
                        result_dir = extractor.extract_frames(video_path, fps=fps, output_dir=frames_dir)
                    
                    print(f"GUI: Frame extraction completed. Result dir: {result_dir}")
                    
                    # Check if files were actually created
                    import os
                    files_created = os.listdir(result_dir) if os.path.exists(result_dir) else []
                    print(f"GUI: Files created: {len(files_created)} files")
                    
                    # Update UI in main thread
                    QTimer.singleShot(0, lambda: self.on_extraction_complete(result_dir))
                    
                except Exception as e:
                    print(f"GUI: Extraction error: {e}")
                    import traceback
                    traceback.print_exc()
                    QTimer.singleShot(0, lambda: self.on_extraction_error(str(e)))
            
            threading.Thread(target=extract_worker, daemon=True).start()
            
        except Exception as e:
            self.on_extraction_error(str(e))
    
    def on_extraction_complete(self, frames_dir: str):
        """Handle frame extraction completion."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Frames extracted to {frames_dir}")
        
        self.frames_dir_edit.setText(frames_dir)
        self.current_frames_dir = frames_dir
        
        # Enable analysis
        self.analyze_btn.setEnabled(True)
        
        # Show success message
        frame_count = len([f for f in os.listdir(frames_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        QMessageBox.information(
            self, "Success", 
            f"Successfully extracted {frame_count} frames.\n\nYou can now analyze the frames."
        )
    
    def on_extraction_error(self, error: str):
        """Handle frame extraction error."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        QMessageBox.critical(self, "Extraction Error", f"Failed to extract frames:\n{error}")
    
    def analyze_frames(self):
        """Analyze frames for quality."""
        frames_dir = self.frames_dir_edit.text().strip()
        
        if not frames_dir or not os.path.isdir(frames_dir):
            QMessageBox.warning(self, "Error", "Please select a valid frames directory.")
            return
        
        # Stop any existing analysis
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.analysis_worker.stop()
            self.analysis_worker.wait()
        
        # Clear previous results
        self.clear_results()
        
        # Setup progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.analyze_btn.setEnabled(False)
        
        # Start analysis worker
        quality_threshold = self.quality_threshold_spin.value()
        self.analysis_worker = AnalysisWorker(frames_dir, self.analyzer, quality_threshold)
        
        self.analysis_worker.progress_update.connect(self.on_analysis_progress)
        self.analysis_worker.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_worker.error_occurred.connect(self.on_analysis_error)
        
        self.analysis_worker.start()
        
        self.status_label.setText("Analyzing frames...")
    
    def on_analysis_progress(self, progress: int, message: str):
        """Handle analysis progress update."""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def on_analysis_complete(self, results: List[Dict[str, Any]]):
        """Handle analysis completion."""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        
        self.analysis_results = results
        
        if not results:
            self.status_label.setText("No frames met the quality criteria")
            QMessageBox.information(self, "Analysis Complete", "No frames met the quality criteria.")
            return
        
        self.status_label.setText(f"Analysis complete - {len(results)} quality frames found")
        
        # Populate results
        self.populate_results(results)
        
        # Enable save button
        self.save_btn.setEnabled(True)
        
        # Show completion message
        best_score = max(r['quality_score'] for r in results)
        avg_score = sum(r['quality_score'] for r in results) / len(results)
        
        QMessageBox.information(
            self, "Analysis Complete", 
            f"Analysis completed successfully!\n\n"
            f"Frames analyzed: {len(results)}\n"
            f"Best quality score: {best_score:.2f}\n"
            f"Average quality score: {avg_score:.2f}"
        )
    
    def on_analysis_error(self, error: str):
        """Handle analysis error."""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.status_label.setText("Analysis failed")
        
        QMessageBox.critical(self, "Analysis Error", f"Frame analysis failed:\n{error}")
    
    def populate_results(self, results: List[Dict[str, Any]]):
        """Populate the results widgets with analysis data."""
        # Clear existing data
        self.results_list.clear()
        
        # Populate results list
        for i, result in enumerate(results):
            item_text = f"{i+1}. {result['filename']} (Q: {result['quality_score']:.2f})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, result)  # Store full result data
            
            # Color-code based on quality
            quality = result['quality_score']
            if quality >= 80:
                item.setBackground(Qt.green)
            elif quality >= 60:
                item.setBackground(Qt.yellow)
            else:
                item.setBackground(Qt.red)
            
            self.results_list.addItem(item)
        
        # Populate details table
        self.populate_details_table(results)
        
        # Select first item
        if results:
            self.results_list.setCurrentRow(0)
    
    def populate_details_table(self, results: List[Dict[str, Any]]):
        """Populate the detailed metrics table."""
        if not results:
            self.details_table.setRowCount(0)
            return
        
        # Setup table
        columns = [
            'Filename', 'Quality Score', 'Sharpness', 'Blur Score',
            'Laplacian Var', 'Sobel Mag', 'Gradient Mag', 'Tenengrad',
            'High Freq', 'Freq Blur', 'Edge Blur', 'Size'
        ]
        
        self.details_table.setColumnCount(len(columns))
        self.details_table.setHorizontalHeaderLabels(columns)
        self.details_table.setRowCount(len(results))
        
        # Populate data
        for row, result in enumerate(results):
            # Basic metrics
            self.details_table.setItem(row, 0, QTableWidgetItem(result['filename']))
            self.details_table.setItem(row, 1, QTableWidgetItem(f"{result['quality_score']:.2f}"))
            self.details_table.setItem(row, 2, QTableWidgetItem(f"{result['sharpness_score']:.2f}"))
            self.details_table.setItem(row, 3, QTableWidgetItem(f"{result['blur_score']:.2f}"))
            
            # Detailed sharpness metrics
            sharpness = result['sharpness_metrics']
            self.details_table.setItem(row, 4, QTableWidgetItem(f"{sharpness['laplacian_variance']:.2f}"))
            self.details_table.setItem(row, 5, QTableWidgetItem(f"{sharpness['sobel_magnitude']:.2f}"))
            self.details_table.setItem(row, 6, QTableWidgetItem(f"{sharpness['gradient_magnitude']:.2f}"))
            self.details_table.setItem(row, 7, QTableWidgetItem(f"{sharpness['tenengrad_focus']:.0f}"))
            self.details_table.setItem(row, 8, QTableWidgetItem(f"{sharpness['high_frequency']:.3f}"))
            
            # Detailed blur metrics
            blur = result['blur_metrics']
            self.details_table.setItem(row, 9, QTableWidgetItem(f"{blur['frequency_blur']:.3f}"))
            self.details_table.setItem(row, 10, QTableWidgetItem(f"{blur['edge_blur']:.3f}"))
            
            # Image size
            size = result['image_size']
            self.details_table.setItem(row, 11, QTableWidgetItem(f"{size[1]}x{size[0]}"))
        
        # Resize columns to fit content
        self.details_table.resizeColumnsToContents()
        
        # Make table sortable
        self.details_table.setSortingEnabled(True)
        self.details_table.sortByColumn(1, Qt.DescendingOrder)  # Sort by quality score
    
    def on_result_selected(self, current, previous):
        """Handle result selection change."""
        if current is None:
            self.frame_preview.clear()
            return
        
        # Get result data
        result_data = current.data(Qt.UserRole)
        if result_data:
            self.frame_preview.update_frame(result_data)
    
    def save_best_frames(self):
        """Save the best frames to output directory."""
        if not self.analysis_results:
            QMessageBox.warning(self, "Error", "No analysis results available.")
            return
        
        output_dir = self.output_dir_edit.text().strip()
        if not output_dir:
            # Default output directory
            if self.current_frames_dir:
                output_dir = str(Path(self.current_frames_dir).parent / "best_frames")
            else:
                output_dir = "best_frames"
            self.output_dir_edit.setText(output_dir)
        
        top_n = self.top_n_spin.value()
        best_frames = self.analysis_results[:top_n]
        
        try:
            self.status_label.setText("Saving best frames...")
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Copy best frames
            frames_dir = self.frames_dir_edit.text().strip()
            self.analyzer.save_best_frames(best_frames, frames_dir, output_path)
            
            # Save JSON report
            self.analyzer.save_json_report(self.analysis_results, output_path / 'quality_report.json')
            
            # Save CSV report
            self.analyzer.save_csv_report(self.analysis_results, output_path / 'quality_report.csv')
            
            self.status_label.setText(f"Saved {len(best_frames)} frames to {output_dir}")
            
            QMessageBox.information(
                self, "Success", 
                f"Successfully saved {len(best_frames)} best frames to:\n{output_dir}\n\n"
                f"Reports saved:\n- quality_report.json\n- quality_report.csv"
            )
            
        except Exception as e:
            self.status_label.setText("Save failed")
            QMessageBox.critical(self, "Save Error", f"Failed to save frames:\n{e}")
    
    def clear_results(self):
        """Clear all results."""
        self.analysis_results = []
        self.results_list.clear()
        self.details_table.setRowCount(0)
        self.frame_preview.clear()
        self.save_btn.setEnabled(False)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop any running analysis
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.analysis_worker.stop()
            self.analysis_worker.wait()
        
        event.accept()
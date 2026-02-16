#!/usr/bin/env python3

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QProgressBar, QFileDialog, QMessageBox, QGroupBox, QSplitter, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from core.frame_analyzer import FrameAnalyzer


class AnalyzeWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, video_path: str, square_size: int = 256):
        super().__init__()
        self.video_path = video_path
        self.analyzer = FrameAnalyzer(square_size)
    
    def run(self):
        try:
            data = self.analyzer.analyze_frames(self.video_path, self.progress.emit)
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))


class ExtractWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, video_path: str, frames: list, output_dir: str, quality: int):
        super().__init__()
        self.video_path = video_path
        self.frames = frames
        self.output_dir = output_dir
        self.quality = quality
        self.analyzer = FrameAnalyzer()
    
    def run(self):
        try:
            files = self.analyzer.extract_frames(
                self.video_path, self.frames, self.output_dir, 
                self.quality, self.progress.emit
            )
            self.finished.emit(files)
        except Exception as e:
            self.error.emit(str(e))


class QualityGraph(FigureCanvas):
    
    def __init__(self):
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b')
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.setup_style()
    
    def setup_style(self):
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        for spine in self.ax.spines.values():
            spine.set_color('#555555')
    
    def plot_data(self, frame_data: list, selected_frames: list = None):
        self.ax.clear()
        self.setup_style()
        
        if not frame_data:
            self.draw()
            return
        
        times = [f['time'] for f in frame_data]
        sharpness = [f['sharpness'] for f in frame_data]
        
        self.ax.plot(times, sharpness, color='#4a9eff', linewidth=0.5, alpha=0.8, label='Sharpness')
        self.ax.fill_between(times, sharpness, alpha=0.2, color='#4a9eff')
        
        if selected_frames:
            sel_times = [f['time'] for f in selected_frames]
            sel_sharpness = [f['sharpness'] for f in selected_frames]
            
            for t, s in zip(sel_times, sel_sharpness):
                self.ax.axvline(x=t, color='#00ff00', alpha=0.4, linewidth=1)
            
            self.ax.scatter(sel_times, sel_sharpness, color='#00ff00', s=20, zorder=5, label='Selected')
        
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Sharpness')
        self.ax.set_title('Frame Quality Analysis')
        self.ax.legend(loc='upper right', facecolor='#2b2b2b', edgecolor='#555555', labelcolor='white')
        self.ax.set_ylim(0, 105)
        
        self.fig.tight_layout()
        self.draw()


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.frame_data = []
        self.selected_frames = []
        self.video_path = ""
        self.analyzer = FrameAnalyzer()
        self.worker = None
        
        self.setWindowTitle("Find Best Frames")
        self.setMinimumSize(900, 600)
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left = self.create_controls()
        splitter.addWidget(left)
        
        right = self.create_graph_panel()
        splitter.addWidget(right)
        
        splitter.setSizes([300, 600])
        layout.addWidget(splitter)
    
    def create_controls(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Video input
        input_group = QGroupBox("Video Input")
        input_layout = QVBoxLayout(input_group)
        
        video_row = QHBoxLayout()
        self.video_edit = QLineEdit()
        self.video_edit.setPlaceholderText("Select video file...")
        video_browse = QPushButton("Browse")
        video_browse.clicked.connect(self.browse_video)
        video_row.addWidget(self.video_edit)
        video_row.addWidget(video_browse)
        input_layout.addLayout(video_row)
        
        # Square size selection
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Crop Size:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["64px", "128px", "256px", "384px", "512px"])
        self.size_combo.setCurrentText("256px")
        size_row.addWidget(self.size_combo)
        size_row.addStretch()
        input_layout.addLayout(size_row)
        
        self.analyze_btn = QPushButton("Analyze Video")
        self.analyze_btn.clicked.connect(self.analyze_video)
        input_layout.addWidget(self.analyze_btn)
        
        layout.addWidget(input_group)
        
        # Frame selection
        select_group = QGroupBox("Frame Selection")
        select_layout = QGridLayout(select_group)
        
        select_layout.addWidget(QLabel("Target FPS:"), 0, 0)
        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setRange(0.1, 60.0)
        self.fps_spin.setValue(1.0)
        self.fps_spin.setSingleStep(0.5)
        self.fps_spin.valueChanged.connect(self.update_selection)
        select_layout.addWidget(self.fps_spin, 0, 1)
        
        self.frames_label = QLabel("Selected: 0 frames")
        select_layout.addWidget(self.frames_label, 1, 0, 1, 2)
        
        layout.addWidget(select_group)
        
        # Output settings
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        
        output_row = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Select output folder...")
        output_browse = QPushButton("Browse")
        output_browse.clicked.connect(self.browse_output)
        output_row.addWidget(self.output_edit)
        output_row.addWidget(output_browse)
        output_layout.addLayout(output_row)
        
        quality_row = QHBoxLayout()
        quality_row.addWidget(QLabel("JPG Quality:"))
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(95)
        self.quality_spin.setSuffix("%")
        quality_row.addWidget(self.quality_spin)
        quality_row.addStretch()
        output_layout.addLayout(quality_row)
        
        self.extract_btn = QPushButton("Extract Selected Frames")
        self.extract_btn.clicked.connect(self.extract_frames)
        self.extract_btn.setEnabled(False)
        output_layout.addWidget(self.extract_btn)
        
        layout.addWidget(output_group)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        self.status = QLabel("Ready")
        layout.addWidget(self.status)
        
        layout.addStretch()
        return panel
    
    def create_graph_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        self.graph = QualityGraph()
        layout.addWidget(self.graph)
        
        return panel
    
    def browse_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "",
            "Video Files (*.mp4 *.mov *.avi *.mkv *.360);;All Files (*)"
        )
        if path:
            self.video_edit.setText(path)
            self.video_path = path
    
    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self.output_edit.setText(path)
    
    def analyze_video(self):
        path = self.video_edit.text().strip()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Error", "Please select a valid video file.")
            return
        
        self.video_path = path
        self.frame_data = []
        self.selected_frames = []
        self.graph.plot_data([], [])
        
        # Get square size
        size_text = self.size_combo.currentText()
        square_size = int(size_text.replace('px', ''))
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.analyze_btn.setEnabled(False)
        self.extract_btn.setEnabled(False)
        
        self.worker = AnalyzeWorker(path, square_size)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_analyze_done)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_progress(self, pct: int, msg: str):
        self.progress.setValue(pct)
        self.status.setText(msg)
    
    def on_analyze_done(self, data: list):
        self.frame_data = data
        self.analyzer.frame_data = data
        self.analyzer.video_fps = self.worker.analyzer.video_fps
        
        self.progress.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.extract_btn.setEnabled(True)
        
        self.update_selection()
        
        QMessageBox.information(self, "Done", f"Analyzed {len(data)} frames.")
    
    def on_error(self, msg: str):
        self.progress.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.status.setText("Error")
        QMessageBox.critical(self, "Error", msg)
    
    def update_selection(self):
        if not self.frame_data:
            return
        
        fps = self.fps_spin.value()
        self.analyzer.frame_data = self.frame_data
        self.selected_frames = self.analyzer.select_best_frames(fps)
        
        self.frames_label.setText(f"Selected: {len(self.selected_frames)} frames")
        self.graph.plot_data(self.frame_data, self.selected_frames)
    
    def extract_frames(self):
        if not self.selected_frames:
            QMessageBox.warning(self, "Error", "No frames selected.")
            return
        
        output_dir = self.output_edit.text().strip()
        if not output_dir:
            video_dir = os.path.dirname(self.video_path)
            output_dir = os.path.join(video_dir, "best_frames")
            self.output_edit.setText(output_dir)
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.extract_btn.setEnabled(False)
        
        self.worker = ExtractWorker(
            self.video_path, self.selected_frames,
            output_dir, self.quality_spin.value()
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_extract_done)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_extract_done(self, files: list):
        self.progress.setVisible(False)
        self.extract_btn.setEnabled(True)
        self.status.setText(f"Saved {len(files)} frames")
        
        QMessageBox.information(
            self, "Done",
            f"Extracted {len(files)} frames to:\n{self.output_edit.text()}"
        )

"""
Photo Picker Dialog - Select a photo for a waypoint anchor

Features:
- Shows current/estimated photo
- Navigate through photos with prev/next
- Jump to specific photo number
- Lazy load preview (one at a time)
- Shows photo filename and sequence info
"""

import sys
from pathlib import Path
from typing import List, Optional, Callable

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QFrame, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage


class PhotoPickerDialog(QDialog):
    """Dialog for selecting a photo to assign to a waypoint"""
    
    photo_selected = pyqtSignal(int)  # Emits photo index
    
    def __init__(self, 
                 photo_paths: List[Path],
                 current_photo_index: int,
                 waypoint_info: dict,
                 parent=None):
        super().__init__(parent)
        
        self.photo_paths = photo_paths
        self.num_photos = len(photo_paths)
        self.current_index = current_photo_index
        self.selected_index = current_photo_index
        self.waypoint_info = waypoint_info
        
        self.init_ui()
        self.load_preview(self.current_index)
    
    def init_ui(self):
        self.setWindowTitle("Select Photo for Waypoint")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Waypoint info header
        wp_info = self.waypoint_info
        header = QLabel(
            f"<b>Waypoint {wp_info.get('waypoint_index', '?')}</b><br>"
            f"Location: {wp_info.get('lat', 0):.6f}, {wp_info.get('lon', 0):.6f}<br>"
            f"Distance: {wp_info.get('distance_from_start', 0):.1f}m from start"
        )
        header.setStyleSheet("background: #e3f2fd; padding: 10px; border-radius: 5px;")
        layout.addWidget(header)
        
        # Current assignment info
        if wp_info.get('has_anchor'):
            anchor_label = QLabel(f"✓ Anchor set: Photo #{wp_info.get('anchor_photo', 0) + 1}")
            anchor_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            anchor_label = QLabel(f"Estimated: Photo #{wp_info.get('estimated_photo', 0) + 1}")
            anchor_label.setStyleSheet("color: #666;")
        layout.addWidget(anchor_label)
        
        # Photo preview area
        preview_frame = QFrame()
        preview_frame.setStyleSheet("background: #333; border-radius: 5px;")
        preview_frame.setMinimumHeight(350)
        preview_layout = QVBoxLayout(preview_frame)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("color: white;")
        self.preview_label.setText("Loading...")
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_frame)
        
        # Photo info
        self.photo_info_label = QLabel()
        self.photo_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_info_label.setStyleSheet("font-size: 14px; padding: 5px;")
        layout.addWidget(self.photo_info_label)
        
        # Navigation controls
        nav_layout = QHBoxLayout()
        
        # Jump to start
        self.start_btn = QPushButton("⏮ First")
        self.start_btn.clicked.connect(lambda: self.jump_to(0))
        nav_layout.addWidget(self.start_btn)
        
        # Previous 10
        self.prev10_btn = QPushButton("◀◀ -10")
        self.prev10_btn.clicked.connect(lambda: self.navigate(-10))
        nav_layout.addWidget(self.prev10_btn)
        
        # Previous
        self.prev_btn = QPushButton("◀ Prev")
        self.prev_btn.clicked.connect(lambda: self.navigate(-1))
        nav_layout.addWidget(self.prev_btn)
        
        # Photo number spinner
        self.photo_spinner = QSpinBox()
        self.photo_spinner.setRange(1, self.num_photos)
        self.photo_spinner.setValue(self.current_index + 1)
        self.photo_spinner.setPrefix("Photo #")
        self.photo_spinner.valueChanged.connect(lambda v: self.jump_to(v - 1))
        nav_layout.addWidget(self.photo_spinner)
        
        # Next
        self.next_btn = QPushButton("Next ▶")
        self.next_btn.clicked.connect(lambda: self.navigate(1))
        nav_layout.addWidget(self.next_btn)
        
        # Next 10
        self.next10_btn = QPushButton("+10 ▶▶")
        self.next10_btn.clicked.connect(lambda: self.navigate(10))
        nav_layout.addWidget(self.next10_btn)
        
        # Jump to end
        self.end_btn = QPushButton("Last ⏭")
        self.end_btn.clicked.connect(lambda: self.jump_to(self.num_photos - 1))
        nav_layout.addWidget(self.end_btn)
        
        layout.addLayout(nav_layout)
        
        # Quick jump buttons
        jump_layout = QHBoxLayout()
        jump_layout.addWidget(QLabel("Quick jump:"))
        
        for percent in [0, 25, 50, 75, 100]:
            idx = int((percent / 100) * (self.num_photos - 1))
            btn = QPushButton(f"{percent}%")
            btn.setMaximumWidth(50)
            btn.clicked.connect(lambda checked, i=idx: self.jump_to(i))
            jump_layout.addWidget(btn)
        
        jump_layout.addStretch()
        layout.addLayout(jump_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        action_layout.addWidget(self.cancel_btn)
        
        action_layout.addStretch()
        
        if self.waypoint_info.get('has_anchor') and not self.waypoint_info.get('is_start') and not self.waypoint_info.get('is_end'):
            self.remove_btn = QPushButton("Remove Anchor")
            self.remove_btn.setStyleSheet("background: #ffcdd2;")
            self.remove_btn.clicked.connect(self.remove_anchor)
            action_layout.addWidget(self.remove_btn)
        
        self.select_btn = QPushButton("✓ Set This Photo as Anchor")
        self.select_btn.setStyleSheet("background: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.select_btn.clicked.connect(self.confirm_selection)
        action_layout.addWidget(self.select_btn)
        
        layout.addLayout(action_layout)
    
    def navigate(self, delta: int):
        """Navigate by delta photos"""
        new_index = self.selected_index + delta
        self.jump_to(new_index)
    
    def jump_to(self, index: int):
        """Jump to specific photo index"""
        index = max(0, min(self.num_photos - 1, index))
        self.selected_index = index
        
        # Update spinner without triggering signal
        self.photo_spinner.blockSignals(True)
        self.photo_spinner.setValue(index + 1)
        self.photo_spinner.blockSignals(False)
        
        self.load_preview(index)
        self.update_nav_buttons()
    
    def load_preview(self, index: int):
        """Load and display photo preview"""
        if index < 0 or index >= self.num_photos:
            return
        
        photo_path = self.photo_paths[index]
        
        # Update info label
        self.photo_info_label.setText(
            f"<b>{photo_path.name}</b><br>"
            f"Photo {index + 1} of {self.num_photos}"
        )
        
        try:
            # Load image with size limit for performance
            pixmap = QPixmap(str(photo_path))
            
            if pixmap.isNull():
                self.preview_label.setText(f"Cannot load preview\n{photo_path.name}")
                return
            
            # Scale to fit preview area
            scaled = pixmap.scaled(
                600, 300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
            
        except Exception as e:
            self.preview_label.setText(f"Error loading preview:\n{e}")
    
    def update_nav_buttons(self):
        """Update navigation button states"""
        self.start_btn.setEnabled(self.selected_index > 0)
        self.prev_btn.setEnabled(self.selected_index > 0)
        self.prev10_btn.setEnabled(self.selected_index > 0)
        self.next_btn.setEnabled(self.selected_index < self.num_photos - 1)
        self.next10_btn.setEnabled(self.selected_index < self.num_photos - 1)
        self.end_btn.setEnabled(self.selected_index < self.num_photos - 1)
    
    def confirm_selection(self):
        """Confirm the selected photo"""
        self.photo_selected.emit(self.selected_index)
        self.accept()
    
    def remove_anchor(self):
        """Signal to remove this anchor (returns -1)"""
        self.photo_selected.emit(-1)  # -1 signals removal
        self.accept()
    
    def get_selected_index(self) -> int:
        """Get the selected photo index"""
        return self.selected_index

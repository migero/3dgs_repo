"""
Waypoint List Widget - Display and select KML waypoints

Shows:
- List of waypoints from KML
- Which have anchors assigned
- Estimated photo at each waypoint
- Click to open photo picker
"""

from typing import List, Optional, Callable
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.anchor_manager import AnchorPointManager, AnchorPoint


class WaypointListWidget(QWidget):
    """Widget showing list of waypoints with anchor info"""
    
    waypoint_clicked = pyqtSignal(int)  # Emits waypoint index
    anchors_changed = pyqtSignal()      # Emits when anchors are modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.anchor_manager: Optional[AnchorPointManager] = None
        self.photo_paths: List[Path] = []
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("<b>KML Waypoints</b>")
        header.setStyleSheet("padding: 5px;")
        layout.addWidget(header)
        
        # Info text
        self.info_label = QLabel("Load KML and photos to see waypoints")
        self.info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.info_label)
        
        # Waypoint list
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)
        
        # Legend
        legend = QLabel(
            "<small>"
            "🟢 = Anchor point (manually set)<br>"
            "⚪ = Interpolated (auto-calculated)<br>"
            "Double-click to assign photo"
            "</small>"
        )
        legend.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(legend)
        
        # Speed info area
        self.speed_frame = QFrame()
        self.speed_frame.setStyleSheet("background: #f5f5f5; border-radius: 5px; padding: 5px;")
        speed_layout = QVBoxLayout(self.speed_frame)
        
        speed_header = QLabel("<b>Segment Speeds</b>")
        speed_layout.addWidget(speed_header)
        
        self.speed_label = QLabel("No segments yet")
        self.speed_label.setStyleSheet("font-size: 11px;")
        speed_layout.addWidget(self.speed_label)
        
        layout.addWidget(self.speed_frame)
    
    def set_data(self, anchor_manager: AnchorPointManager, photo_paths: List[Path]):
        """Set the data to display"""
        self.anchor_manager = anchor_manager
        self.photo_paths = photo_paths
        self.refresh_list()
    
    def refresh_list(self):
        """Refresh the waypoint list"""
        self.list_widget.clear()
        
        if not self.anchor_manager:
            return
        
        num_waypoints = len(self.anchor_manager.path_points)
        num_anchors = len(self.anchor_manager.anchors)
        
        self.info_label.setText(
            f"{num_waypoints} waypoints, {num_anchors} anchors, "
            f"{self.anchor_manager.num_photos} photos"
        )
        
        # Add waypoint items
        for i in range(num_waypoints):
            info = self.anchor_manager.get_waypoint_info(i)
            
            # Create item text
            if info.get('is_start'):
                prefix = "🚩 START"
            elif info.get('is_end'):
                prefix = "🏁 END"
            elif info.get('has_anchor'):
                prefix = "🟢"
            else:
                prefix = "⚪"
            
            distance_km = info.get('distance_from_start', 0) / 1000
            
            if info.get('has_anchor'):
                photo_text = f"Photo #{info['anchor_photo'] + 1}"
            else:
                photo_text = f"~Photo #{info['estimated_photo'] + 1}"
            
            text = f"{prefix} WP {i}: {distance_km:.2f}km - {photo_text}"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, i)  # Store waypoint index
            
            # Color coding
            if info.get('has_anchor'):
                item.setBackground(QColor("#e8f5e9"))  # Light green
            
            self.list_widget.addItem(item)
        
        # Update speed info
        self.update_speed_info()
    
    def update_speed_info(self):
        """Update the speed information display"""
        if not self.anchor_manager:
            self.speed_label.setText("No data")
            return
        
        speeds = self.anchor_manager.get_speed_info()
        
        if not speeds:
            self.speed_label.setText("Add anchors to see segment speeds")
            return
        
        lines = []
        for s in speeds:
            speed_emoji = {"slow": "🐢", "normal": "🚶", "fast": "🏃"}.get(s['relative_speed'], "")
            lines.append(
                f"Segment {s['segment']}: {s['distance_m']:.0f}m, "
                f"{s['num_photos']} photos, "
                f"{s['meters_per_photo']:.1f}m/photo {speed_emoji}"
            )
        
        self.speed_label.setText("\n".join(lines))
    
    def on_item_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on waypoint"""
        waypoint_index = item.data(Qt.ItemDataRole.UserRole)
        self.waypoint_clicked.emit(waypoint_index)
    
    def highlight_waypoint(self, waypoint_index: int):
        """Highlight a specific waypoint in the list"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == waypoint_index:
                self.list_widget.setCurrentItem(item)
                self.list_widget.scrollToItem(item)
                break
    
    def get_simplified_waypoints(self, max_waypoints: int = 50) -> List[int]:
        """
        Get indices of waypoints to show (simplified for large paths).
        Shows start, end, anchors, and evenly spaced intermediates.
        """
        if not self.anchor_manager:
            return []
        
        num_wp = len(self.anchor_manager.path_points)
        
        if num_wp <= max_waypoints:
            return list(range(num_wp))
        
        # Always include start, end, and anchor waypoints
        important = {0, num_wp - 1}
        for anchor in self.anchor_manager.anchors:
            important.add(anchor.waypoint_index)
        
        # Fill remaining slots with evenly spaced waypoints
        remaining = max_waypoints - len(important)
        if remaining > 0:
            step = num_wp / (remaining + 1)
            for i in range(1, remaining + 1):
                important.add(int(i * step))
        
        return sorted(important)

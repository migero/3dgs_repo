"""
360 Photo Geolocator - PyQt6 GUI with Anchor Point System

Features:
- Load KML path and photos
- Auto-distribute photos along path
- Manual anchor point adjustment (click waypoint to assign specific photo)
- Variable walking speed between segments
- Preview photos before assigning
- Export to JSON/CSV/GPX/Map
- Write GPS to EXIF
"""

import sys
import os
import re
from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar,
    QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QTextEdit,
    QMessageBox, QComboBox, QSplitter, QTabWidget, QListWidget,
    QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QColor

# Try to import WebEngine, fall back to browser if not available
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    print("Note: PyQt6-WebEngine not installed. Map will open in browser.")
    print("Install with: pip install PyQt6-WebEngine")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.kml_parser import KMLPathParser, PathPoint
from core.photo_geolocator import PhotoGeolocator, GeolocatedPhoto
from core.path_interpolator import PathInterpolator
from core.anchor_manager import AnchorPointManager, PhotoAssignment
from core.exif_writer import ExifGeotagWriter
from core.map_exporter import MapExporter
from ui.photo_picker import PhotoPickerDialog


class LoadDataWorker(QThread):
    """Background worker for loading KML and scanning photos"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list, list, object)  # path_points, photos, interpolator
    error = pyqtSignal(str)
    
    def __init__(self, kml_path: str, photos_dir: str, reverse: bool):
        super().__init__()
        self.kml_path = kml_path
        self.photos_dir = photos_dir
        self.reverse = reverse
    
    def run(self):
        try:
            # Parse KML
            self.progress.emit("Loading KML path...")
            parser = KMLPathParser(self.kml_path)
            path_points = parser.parse()
            self.progress.emit(f"Path has {len(path_points)} waypoints")
            
            if len(path_points) < 2:
                self.error.emit("KML path must have at least 2 points")
                return
            
            # Create interpolator
            interpolator = PathInterpolator(path_points)
            self.progress.emit(f"Path length: {interpolator.total_length/1000:.2f} km")
            
            # Scan photos
            self.progress.emit("Scanning photos...")
            photos_dir = Path(self.photos_dir)
            extensions = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.360']
            
            photos = []
            for file in photos_dir.iterdir():
                if file.is_file() and file.suffix.lower() in extensions:
                    photos.append(file)
            
            # Natural sort
            def natural_sort_key(s):
                return [int(text) if text.isdigit() else text.lower() 
                        for text in re.split(r'(\d+)', s.name)]
            
            photos.sort(key=natural_sort_key)
            
            if self.reverse:
                photos.reverse()
            
            self.progress.emit(f"Found {len(photos)} photos")
            
            if not photos:
                self.error.emit("No photos found in directory!")
                return
            
            self.finished.emit(path_points, photos, interpolator)
            
        except Exception as e:
            self.error.emit(str(e))


class GeolocatorWindow(QMainWindow):
    """Main window for the 360 Photo Geolocator with anchor point support"""
    
    def __init__(self):
        super().__init__()
        
        # Data
        self.path_points: List[PathPoint] = []
        self.photos: List[Path] = []
        self.interpolator: Optional[PathInterpolator] = None
        self.anchor_manager: Optional[AnchorPointManager] = None
        self.geolocated_photos: List[GeolocatedPhoto] = []
        
        # Temp files
        self.temp_map_path: Optional[str] = None
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("360 Photo Geolocator")
        self.setMinimumSize(1400, 900)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout with splitter
        main_layout = QHBoxLayout(central)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        splitter.addWidget(left_panel)
        
        # Middle panel - waypoint list
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        splitter.addWidget(middle_panel)
        
        # Right panel - map preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        splitter.addWidget(right_panel)
        
        splitter.setSizes([350, 300, 700])
        
        # === Left Panel - Input Section ===
        input_group = QGroupBox("1. Input Files")
        input_layout = QVBoxLayout(input_group)
        
        # KML file
        kml_row = QHBoxLayout()
        kml_row.addWidget(QLabel("KML:"))
        self.kml_input = QLineEdit()
        self.kml_input.setPlaceholderText("Select KML file with route...")
        kml_row.addWidget(self.kml_input)
        kml_btn = QPushButton("...")
        kml_btn.setMaximumWidth(40)
        kml_btn.clicked.connect(self.browse_kml)
        kml_row.addWidget(kml_btn)
        input_layout.addLayout(kml_row)
        
        # Photos directory
        photos_row = QHBoxLayout()
        photos_row.addWidget(QLabel("Photos:"))
        self.photos_input = QLineEdit()
        self.photos_input.setPlaceholderText("Select photos directory...")
        photos_row.addWidget(self.photos_input)
        photos_btn = QPushButton("...")
        photos_btn.setMaximumWidth(40)
        photos_btn.clicked.connect(self.browse_photos)
        photos_row.addWidget(photos_btn)
        input_layout.addLayout(photos_row)
        
        # Reverse option
        self.reverse_check = QCheckBox("Reverse photo order")
        input_layout.addWidget(self.reverse_check)
        
        # Load button
        self.load_btn = QPushButton("📂 Load KML & Photos")
        self.load_btn.clicked.connect(self.load_data)
        self.load_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        input_layout.addWidget(self.load_btn)
        
        left_layout.addWidget(input_group)
        
        # === Status Section ===
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Load KML and photos to begin")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        left_layout.addWidget(status_group)
        
        # === Anchor Info Section ===
        anchor_group = QGroupBox("2. Adjust Anchors (Optional)")
        anchor_layout = QVBoxLayout(anchor_group)
        
        anchor_info = QLabel(
            "<small>Double-click waypoints in the list to assign specific photos. "
            "This adjusts walking speed between anchors.</small>"
        )
        anchor_info.setWordWrap(True)
        anchor_info.setStyleSheet("color: #666;")
        anchor_layout.addWidget(anchor_info)
        
        # Speed summary
        self.speed_label = QLabel("No anchors yet")
        self.speed_label.setStyleSheet("font-family: monospace; font-size: 11px;")
        anchor_layout.addWidget(self.speed_label)
        
        left_layout.addWidget(anchor_group)
        
        # === Apply & Export Section ===
        action_group = QGroupBox("3. Apply & Export")
        action_layout = QVBoxLayout(action_group)
        
        self.apply_btn = QPushButton("🗺️ Apply Geolocations")
        self.apply_btn.clicked.connect(self.apply_geolocations)
        self.apply_btn.setEnabled(False)
        self.apply_btn.setStyleSheet("font-size: 14px; padding: 10px; background: #2196F3; color: white;")
        action_layout.addWidget(self.apply_btn)
        
        export_btns = QHBoxLayout()
        
        self.export_json_btn = QPushButton("JSON")
        self.export_json_btn.clicked.connect(lambda: self.export_results('json'))
        self.export_json_btn.setEnabled(False)
        export_btns.addWidget(self.export_json_btn)
        
        self.export_csv_btn = QPushButton("CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export_results('csv'))
        self.export_csv_btn.setEnabled(False)
        export_btns.addWidget(self.export_csv_btn)
        
        self.export_gpx_btn = QPushButton("GPX")
        self.export_gpx_btn.clicked.connect(lambda: self.export_results('gpx'))
        self.export_gpx_btn.setEnabled(False)
        export_btns.addWidget(self.export_gpx_btn)
        
        self.export_map_btn = QPushButton("Map")
        self.export_map_btn.clicked.connect(lambda: self.export_results('map'))
        self.export_map_btn.setEnabled(False)
        export_btns.addWidget(self.export_map_btn)
        
        action_layout.addLayout(export_btns)
        
        self.write_exif_btn = QPushButton("📍 Write GPS to EXIF")
        self.write_exif_btn.clicked.connect(self.write_exif)
        self.write_exif_btn.setEnabled(False)
        self.write_exif_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        action_layout.addWidget(self.write_exif_btn)
        
        # Save/Load anchors
        anchor_file_btns = QHBoxLayout()
        self.save_anchors_btn = QPushButton("Save Anchors")
        self.save_anchors_btn.clicked.connect(self.save_anchors)
        self.save_anchors_btn.setEnabled(False)
        anchor_file_btns.addWidget(self.save_anchors_btn)
        
        self.load_anchors_btn = QPushButton("Load Anchors")
        self.load_anchors_btn.clicked.connect(self.load_anchors)
        self.load_anchors_btn.setEnabled(False)
        anchor_file_btns.addWidget(self.load_anchors_btn)
        action_layout.addLayout(anchor_file_btns)
        
        left_layout.addWidget(action_group)
        
        # === Log ===
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        log_layout.addWidget(self.log_text)
        left_layout.addWidget(log_group)
        
        left_layout.addStretch()
        
        # === Middle Panel - Waypoint List ===
        wp_header = QLabel("<b>KML Waypoints</b>")
        wp_header.setStyleSheet("padding: 5px;")
        middle_layout.addWidget(wp_header)
        
        self.wp_info_label = QLabel("Load data to see waypoints")
        self.wp_info_label.setStyleSheet("color: #666; padding: 5px;")
        middle_layout.addWidget(self.wp_info_label)
        
        self.waypoint_list = QListWidget()
        self.waypoint_list.itemDoubleClicked.connect(self.on_waypoint_double_clicked)
        middle_layout.addWidget(self.waypoint_list)
        
        legend = QLabel(
            "<small>"
            "🚩 Start  🏁 End  🟢 Anchor  ⚪ Interpolated<br>"
            "<b>Double-click</b> to assign photo"
            "</small>"
        )
        legend.setStyleSheet("color: #666; padding: 5px;")
        middle_layout.addWidget(legend)
        
        # === Right Panel - Map ===
        map_label = QLabel("<b>Map Preview</b>")
        map_label.setStyleSheet("padding: 5px;")
        right_layout.addWidget(map_label)
        
        if WEBENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setHtml(self._get_placeholder_html())
            right_layout.addWidget(self.web_view)
        else:
            self.web_view = None
            self.map_placeholder = QLabel("Map preview requires PyQt6-WebEngine.\nMap will open in browser instead.")
            self.map_placeholder.setStyleSheet("background:#f0f0f0; color:#666; padding:20px;")
            self.map_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.addWidget(self.map_placeholder)
            
            self.open_map_btn = QPushButton("🌐 Open Map in Browser")
            self.open_map_btn.clicked.connect(self.open_map_in_browser)
            self.open_map_btn.setEnabled(False)
            right_layout.addWidget(self.open_map_btn)
    
    def _get_placeholder_html(self):
        return "<html><body style='background:#f5f5f5;display:flex;align-items:center;justify-content:center;height:100%;'><p style='color:#888;font-size:16px;'>Load KML and photos to see map</p></body></html>"
    
    def log(self, message: str):
        """Add message to log"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def browse_kml(self):
        """Browse for KML file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select KML File", "",
            "KML Files (*.kml *.kmz);;All Files (*)"
        )
        if file_path:
            self.kml_input.setText(file_path)
            self.log(f"Selected KML: {Path(file_path).name}")
    
    def browse_photos(self):
        """Browse for photos directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Photos Directory"
        )
        if dir_path:
            self.photos_input.setText(dir_path)
            photo_count = sum(1 for f in Path(dir_path).iterdir() 
                            if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.360'])
            self.log(f"Selected folder with {photo_count} photos")
    
    def load_data(self):
        """Load KML and scan photos"""
        kml_path = self.kml_input.text().strip()
        photos_dir = self.photos_input.text().strip()
        
        if not kml_path or not photos_dir:
            QMessageBox.warning(self, "Missing Input", 
                              "Please select both KML file and photos directory.")
            return
        
        if not Path(kml_path).exists():
            QMessageBox.warning(self, "File Not Found", 
                              f"KML file not found: {kml_path}")
            return
        
        if not Path(photos_dir).exists():
            QMessageBox.warning(self, "Directory Not Found", 
                              f"Photos directory not found: {photos_dir}")
            return
        
        self.load_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.log("Loading data...")
        
        self.worker = LoadDataWorker(
            kml_path, photos_dir,
            self.reverse_check.isChecked()
        )
        self.worker.progress.connect(self.log)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(self.on_load_error)
        self.worker.start()
    
    def on_data_loaded(self, path_points: List[PathPoint], photos: List[Path], interpolator: PathInterpolator):
        """Handle data loading completion"""
        self.path_points = path_points
        self.photos = photos
        self.interpolator = interpolator
        
        # Create anchor manager
        self.anchor_manager = AnchorPointManager(path_points, len(photos))
        
        self.load_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Update status
        self.status_label.setText(
            f"<b>Loaded:</b><br>"
            f"• {len(path_points)} waypoints<br>"
            f"• {len(photos)} photos<br>"
            f"• Path: {interpolator.total_length/1000:.2f} km<br>"
            f"• Spacing: {interpolator.total_length/max(1, len(photos)-1):.1f} m/photo"
        )
        
        # Enable buttons
        self.apply_btn.setEnabled(True)
        self.save_anchors_btn.setEnabled(True)
        self.load_anchors_btn.setEnabled(True)
        
        # Populate waypoint list
        self.refresh_waypoint_list()
        
        # Update speed info
        self.update_speed_info()
        
        # Show initial map
        self.show_path_preview()
        
        self.log(f"✅ Data loaded successfully!")
    
    def on_load_error(self, error: str):
        """Handle loading error"""
        self.load_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.log(f"❌ Error: {error}")
        QMessageBox.critical(self, "Error", error)
    
    def refresh_waypoint_list(self):
        """Refresh the waypoint list display"""
        self.waypoint_list.clear()
        
        if not self.anchor_manager:
            return
        
        num_wp = len(self.path_points)
        num_anchors = len(self.anchor_manager.anchors)
        
        self.wp_info_label.setText(
            f"{num_wp} waypoints, {num_anchors} anchors"
        )
        
        # Determine which waypoints to show (simplify for large paths)
        if num_wp > 100:
            # Show subset: all anchors + evenly spaced
            waypoints_to_show = set()
            waypoints_to_show.add(0)
            waypoints_to_show.add(num_wp - 1)
            
            for anchor in self.anchor_manager.anchors:
                waypoints_to_show.add(anchor.waypoint_index)
            
            # Add evenly spaced
            step = num_wp // 50
            for i in range(0, num_wp, max(1, step)):
                waypoints_to_show.add(i)
            
            waypoints_to_show = sorted(waypoints_to_show)
        else:
            waypoints_to_show = list(range(num_wp))
        
        for i in waypoints_to_show:
            info = self.anchor_manager.get_waypoint_info(i)
            
            if info.get('is_start'):
                prefix = "🚩"
            elif info.get('is_end'):
                prefix = "🏁"
            elif info.get('has_anchor'):
                prefix = "🟢"
            else:
                prefix = "⚪"
            
            distance_km = info.get('distance_from_start', 0) / 1000
            
            if info.get('has_anchor'):
                photo_text = f"#{info['anchor_photo'] + 1}"
            else:
                photo_text = f"~#{info['estimated_photo'] + 1}"
            
            text = f"{prefix} WP{i}: {distance_km:.2f}km → Photo {photo_text}"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            
            if info.get('has_anchor'):
                item.setBackground(QColor("#e8f5e9"))
            
            self.waypoint_list.addItem(item)
    
    def update_speed_info(self):
        """Update the speed information display"""
        if not self.anchor_manager:
            self.speed_label.setText("No data")
            return
        
        speeds = self.anchor_manager.get_speed_info()
        
        if not speeds:
            self.speed_label.setText("No segments")
            return
        
        lines = []
        for s in speeds:
            emoji = {"slow": "🐢", "normal": "🚶", "fast": "🏃"}.get(s['relative_speed'], "")
            lines.append(
                f"Seg{s['segment']}: {s['distance_m']:.0f}m / {s['num_photos']}p = {s['meters_per_photo']:.1f}m/p {emoji}"
            )
        
        self.speed_label.setText("\n".join(lines))
    
    def on_waypoint_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on waypoint to open photo picker"""
        if not self.anchor_manager or not self.photos:
            return
        
        waypoint_index = item.data(Qt.ItemDataRole.UserRole)
        info = self.anchor_manager.get_waypoint_info(waypoint_index)
        
        # Determine current photo
        if info.get('has_anchor'):
            current_photo = info['anchor_photo']
        else:
            current_photo = info['estimated_photo']
        
        # Open photo picker dialog
        dialog = PhotoPickerDialog(
            self.photos,
            current_photo,
            info,
            self
        )
        
        def on_photo_selected(photo_index: int):
            if photo_index == -1:
                # Remove anchor
                if self.anchor_manager.remove_anchor(waypoint_index):
                    self.log(f"Removed anchor at waypoint {waypoint_index}")
            else:
                # Set anchor
                try:
                    self.anchor_manager.add_anchor(waypoint_index, photo_index)
                    self.log(f"Set anchor: WP{waypoint_index} → Photo #{photo_index + 1}")
                except ValueError as e:
                    QMessageBox.warning(self, "Invalid Anchor", str(e))
                    return
            
            # Refresh UI
            self.refresh_waypoint_list()
            self.update_speed_info()
        
        dialog.photo_selected.connect(on_photo_selected)
        dialog.exec()
    
    def show_path_preview(self):
        """Show the KML path on the map"""
        if not self.path_points:
            return
        
        import tempfile
        fd, self.temp_map_path = tempfile.mkstemp(suffix='.html')
        os.close(fd)
        
        try:
            self._generate_path_map(self.temp_map_path)
            
            if WEBENGINE_AVAILABLE and self.web_view:
                self.web_view.load(QUrl.fromLocalFile(self.temp_map_path))
            else:
                if hasattr(self, 'open_map_btn'):
                    self.open_map_btn.setEnabled(True)
        except Exception as e:
            self.log(f"Error generating map: {e}")
    
    def _generate_path_map(self, output_path: str):
        """Generate a map showing the path and anchor points"""
        try:
            import folium
            from folium import plugins
        except ImportError:
            self.log("folium not installed, cannot generate map")
            return
        
        # Calculate center
        lats = [p.lat for p in self.path_points]
        lons = [p.lon for p in self.path_points]
        center = (sum(lats)/len(lats), sum(lons)/len(lons))
        
        m = folium.Map(location=center, zoom_start=15, tiles='OpenStreetMap')
        
        # Add satellite layer
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri', name='Satellite'
        ).add_to(m)
        
        # Draw path
        path_coords = [[p.lat, p.lon] for p in self.path_points]
        folium.PolyLine(path_coords, weight=3, color='blue', opacity=0.7).add_to(m)
        
        # Add anchor markers
        if self.anchor_manager:
            for anchor in self.anchor_manager.anchors:
                is_endpoint = anchor.waypoint_index == 0 or anchor.waypoint_index == len(self.path_points) - 1
                
                if anchor.waypoint_index == 0:
                    icon = folium.Icon(color='green', icon='play')
                    popup = f"START: Photo #{anchor.photo_index + 1}"
                elif anchor.waypoint_index == len(self.path_points) - 1:
                    icon = folium.Icon(color='red', icon='stop')
                    popup = f"END: Photo #{anchor.photo_index + 1}"
                else:
                    icon = folium.Icon(color='orange', icon='map-pin')
                    popup = f"Anchor WP{anchor.waypoint_index}: Photo #{anchor.photo_index + 1}"
                
                folium.Marker(
                    [anchor.lat, anchor.lon],
                    popup=popup,
                    icon=icon
                ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save
        m.save(output_path)
    
    def apply_geolocations(self):
        """Apply anchor-based interpolation to all photos"""
        if not self.anchor_manager or not self.photos:
            return
        
        try:
            # Validate anchors
            valid, error = self.anchor_manager.validate_anchors()
            if not valid:
                QMessageBox.warning(self, "Invalid Anchors", error)
                return
            
            # Interpolate
            self.log("Applying geolocations...")
            assignments = self.anchor_manager.interpolate_all_photos()
            
            # Convert to GeolocatedPhoto objects
            self.geolocated_photos = []
            for assignment in assignments:
                photo = self.photos[assignment.photo_index]
                geo = GeolocatedPhoto(
                    filepath=photo,
                    filename=photo.name,
                    sequence_num=assignment.photo_index + 1,
                    lat=assignment.lat,
                    lon=assignment.lon,
                    heading=assignment.heading,
                    distance_from_start=assignment.distance_from_start,
                    progress=assignment.distance_from_start / self.interpolator.total_length
                )
                self.geolocated_photos.append(geo)
            
            # Enable export buttons
            self.export_json_btn.setEnabled(True)
            self.export_csv_btn.setEnabled(True)
            self.export_gpx_btn.setEnabled(True)
            self.export_map_btn.setEnabled(True)
            self.write_exif_btn.setEnabled(True)
            
            self.log(f"✅ Applied geolocations to {len(self.geolocated_photos)} photos")
            
            # Update map with photo positions
            self.show_result_map()
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            QMessageBox.critical(self, "Error", str(e))
    
    def show_result_map(self):
        """Show map with geolocated photos"""
        if not self.geolocated_photos:
            return
        
        import tempfile
        fd, self.temp_map_path = tempfile.mkstemp(suffix='.html')
        os.close(fd)
        
        try:
            count = len(self.geolocated_photos)
            interval = 20 if count > 500 else (5 if count > 100 else 1)
            
            map_exporter = MapExporter()
            map_exporter.create_map(
                self.geolocated_photos,
                path_points=self.path_points,
                marker_interval=interval,
                output_path=self.temp_map_path
            )
            
            if WEBENGINE_AVAILABLE and self.web_view:
                self.web_view.load(QUrl.fromLocalFile(self.temp_map_path))
                self.log("Map updated with photo positions")
            else:
                if hasattr(self, 'open_map_btn'):
                    self.open_map_btn.setEnabled(True)
                self.log("Map ready - open in browser to view")
                
        except Exception as e:
            self.log(f"Error generating map: {e}")
    
    def open_map_in_browser(self):
        """Open the map in the default web browser"""
        if self.temp_map_path and Path(self.temp_map_path).exists():
            import webbrowser
            webbrowser.open(f'file://{self.temp_map_path}')
            self.log("Opened map in browser")
    
    def export_results(self, format_type: str):
        """Export geolocated results"""
        if not self.geolocated_photos:
            QMessageBox.warning(self, "No Data", "Apply geolocations first.")
            return
        
        photos_dir = self.photos_input.text().strip()
        
        if format_type == 'json':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save JSON",
                str(Path(photos_dir) / "geolocations.json"),
                "JSON Files (*.json)"
            )
            if file_path:
                self._export_json(file_path)
        
        elif format_type == 'csv':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save CSV",
                str(Path(photos_dir) / "geolocations.csv"),
                "CSV Files (*.csv)"
            )
            if file_path:
                self._export_csv(file_path)
        
        elif format_type == 'gpx':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save GPX",
                str(Path(photos_dir) / "geolocations.gpx"),
                "GPX Files (*.gpx)"
            )
            if file_path:
                self._export_gpx(file_path)
        
        elif format_type == 'map':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Map HTML",
                str(Path(photos_dir) / "photo_map.html"),
                "HTML Files (*.html)"
            )
            if file_path:
                map_exporter = MapExporter()
                map_exporter.create_map(self.geolocated_photos, output_path=file_path)
                self.log(f"Exported map to {file_path}")
    
    def _export_json(self, file_path: str):
        import json
        from datetime import datetime
        
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_photos': len(self.geolocated_photos),
            'path_length_m': self.interpolator.total_length if self.interpolator else 0,
            'photos': [p.to_dict() for p in self.geolocated_photos]
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        self.log(f"Exported to {file_path}")
    
    def _export_csv(self, file_path: str):
        with open(file_path, 'w') as f:
            f.write("sequence_num,filename,latitude,longitude,heading,distance_m\n")
            for p in self.geolocated_photos:
                f.write(f"{p.sequence_num},{p.filename},{p.lat:.8f},{p.lon:.8f},{p.heading:.1f},{p.distance_from_start:.1f}\n")
        self.log(f"Exported to {file_path}")
    
    def _export_gpx(self, file_path: str):
        from datetime import datetime
        
        gpx = f'''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="360 Geolocator">
  <metadata><time>{datetime.now().isoformat()}</time></metadata>
'''
        for p in self.geolocated_photos:
            gpx += f'  <wpt lat="{p.lat:.8f}" lon="{p.lon:.8f}"><name>{p.filename}</name></wpt>\n'
        gpx += '</gpx>'
        
        with open(file_path, 'w') as f:
            f.write(gpx)
        self.log(f"Exported to {file_path}")
    
    def save_anchors(self):
        """Save anchor configuration"""
        if not self.anchor_manager:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Anchors",
            str(Path(self.photos_input.text()) / "anchors.json"),
            "JSON Files (*.json)"
        )
        if file_path:
            self.anchor_manager.save_anchors(file_path)
            self.log(f"Saved anchors to {file_path}")
    
    def load_anchors(self):
        """Load anchor configuration"""
        if not self.anchor_manager:
            QMessageBox.warning(self, "No Data", "Load KML and photos first.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Anchors", "",
            "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.anchor_manager.load_anchors(file_path)
                self.refresh_waypoint_list()
                self.update_speed_info()
                self.show_path_preview()
                self.log(f"Loaded anchors from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def write_exif(self):
        """Write GPS coordinates to photo EXIF"""
        if not self.geolocated_photos:
            return
        
        reply = QMessageBox.question(
            self, "Write EXIF",
            f"This will write GPS coordinates to {len(self.geolocated_photos)} photos.\n"
            "Original files will be backed up.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.log("Writing GPS to EXIF...")
        self.write_exif_btn.setEnabled(False)
        
        try:
            writer = ExifGeotagWriter(backup_originals=True)
            
            def progress_callback(current, total):
                if current % 50 == 0 or current == total:
                    self.log(f"  Progress: {current}/{total}")
            
            success, fail = writer.write_gps_batch(
                self.geolocated_photos,
                progress_callback=progress_callback
            )
            
            self.log(f"✅ EXIF write complete: {success} success, {fail} failed")
            
            if writer.backup_dir:
                self.log(f"   Originals backed up to: {writer.backup_dir}")
            
        except Exception as e:
            self.log(f"❌ Error writing EXIF: {e}")
        
        self.write_exif_btn.setEnabled(True)
    
    def closeEvent(self, event):
        """Clean up temp files on close"""
        if self.temp_map_path and Path(self.temp_map_path).exists():
            try:
                os.unlink(self.temp_map_path)
            except:
                pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("360 Photo Geolocator")
    
    window = GeolocatorWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

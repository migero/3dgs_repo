"""
Map Exporter - Generate interactive HTML maps showing photo locations

Features:
- Interactive Folium/Leaflet map
- Photo markers with popups
- Path visualization
- Click to open photo
"""

from pathlib import Path
from typing import List, Optional
import html

try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("Warning: folium not installed. Map export disabled.")
    print("Install with: pip install folium")


class MapExporter:
    """Export geolocated photos to interactive HTML map"""
    
    def __init__(self, title: str = "360 Photo Locations"):
        self.title = title
        
    def create_map(self, geolocated_photos: List,
                   path_points: List = None,
                   show_path: bool = True,
                   show_markers: bool = True,
                   marker_interval: int = 1,
                   output_path: str = "photo_map.html") -> str:
        """
        Create an interactive HTML map.
        
        Args:
            geolocated_photos: List of GeolocatedPhoto objects
            path_points: Optional list of PathPoint objects for path line
            show_path: Whether to show the path line
            show_markers: Whether to show photo markers
            marker_interval: Show every Nth marker (1 = all, 10 = every 10th)
            output_path: Output HTML file path
            
        Returns:
            Path to the created HTML file
        """
        if not FOLIUM_AVAILABLE:
            return self._create_basic_html(geolocated_photos, output_path)
        
        if not geolocated_photos:
            raise ValueError("No geolocated photos to map")
        
        # Calculate center
        lats = [p.lat for p in geolocated_photos]
        lons = [p.lon for p in geolocated_photos]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=16,
            tiles='OpenStreetMap'
        )
        
        # Add alternative tile layers
        folium.TileLayer('cartodbpositron', name='Light').add_to(m)
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite'
        ).add_to(m)
        
        # Draw path line
        if show_path:
            if path_points:
                path_coords = [[p.lat, p.lon] for p in path_points]
            else:
                path_coords = [[p.lat, p.lon] for p in geolocated_photos]
            
            folium.PolyLine(
                path_coords,
                weight=3,
                color='blue',
                opacity=0.7,
                name='Walking Path'
            ).add_to(m)
        
        # Add photo markers
        if show_markers:
            marker_group = folium.FeatureGroup(name='Photo Locations')
            
            for i, photo in enumerate(geolocated_photos):
                if i % marker_interval != 0:
                    continue
                
                # Create popup content
                popup_html = f'''
                <div style="width:200px">
                    <b>{html.escape(photo.filename)}</b><br>
                    <small>
                    #{photo.sequence_num}<br>
                    Lat: {photo.lat:.6f}<br>
                    Lon: {photo.lon:.6f}<br>
                    Distance: {photo.distance_from_start:.1f}m<br>
                    Heading: {photo.heading:.0f}°
                    </small>
                </div>
                '''
                
                # Color based on position along path
                if photo.progress < 0.33:
                    color = 'green'
                elif photo.progress < 0.66:
                    color = 'blue'
                else:
                    color = 'red'
                
                folium.CircleMarker(
                    location=[photo.lat, photo.lon],
                    radius=5,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"#{photo.sequence_num}: {photo.filename}",
                    color=color,
                    fill=True,
                    fillOpacity=0.7
                ).add_to(marker_group)
            
            marker_group.add_to(m)
        
        # Add start/end markers
        start_photo = geolocated_photos[0]
        end_photo = geolocated_photos[-1]
        
        folium.Marker(
            location=[start_photo.lat, start_photo.lon],
            popup=f"START: {start_photo.filename}",
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)
        
        folium.Marker(
            location=[end_photo.lat, end_photo.lon],
            popup=f"END: {end_photo.filename}",
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add fullscreen button
        plugins.Fullscreen().add_to(m)
        
        # Add minimap
        plugins.MiniMap().add_to(m)
        
        # Save map
        output_path = Path(output_path)
        m.save(str(output_path))
        
        print(f"Map saved to {output_path}")
        return str(output_path)
    
    def _create_basic_html(self, geolocated_photos: List, output_path: str) -> str:
        """Create a basic HTML table if folium is not available"""
        output_path = Path(output_path)
        
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>{html.escape(self.title)}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>{html.escape(self.title)}</h1>
    <p>Total photos: {len(geolocated_photos)}</p>
    <p><em>Install folium for interactive map: pip install folium</em></p>
    <table>
        <tr>
            <th>#</th>
            <th>Filename</th>
            <th>Latitude</th>
            <th>Longitude</th>
            <th>Distance (m)</th>
            <th>Heading</th>
        </tr>
'''
        for p in geolocated_photos:
            html_content += f'''        <tr>
            <td>{p.sequence_num}</td>
            <td>{html.escape(p.filename)}</td>
            <td>{p.lat:.6f}</td>
            <td>{p.lon:.6f}</td>
            <td>{p.distance_from_start:.1f}</td>
            <td>{p.heading:.0f}°</td>
        </tr>
'''
        
        html_content += '''    </table>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Basic HTML table saved to {output_path}")
        return str(output_path)


if __name__ == "__main__":
    print("MapExporter - use with geolocated photos")
    print(f"Folium available: {FOLIUM_AVAILABLE}")

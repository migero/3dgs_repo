# 360 Photo Geolocator

A Python tool to assign GPS coordinates to sequential 360 photos taken along a known path.

## Use Case

You have:
- **1200+ sequential 360 photos** taken while walking/driving
- **A KML file** defining the route you took
- Photos are in **filename order** (lower numbers = start of path, higher = end)

This tool distributes photos evenly along the KML path and:
- Exports coordinates to JSON/CSV/GPX
- Generates an interactive HTML map
- Optionally writes GPS to photo EXIF data

## Installation

```bash
cd 360_geolocator
pip install -r requirements.txt
```

## Quick Start

### Command Line

```bash
# Basic - geolocate and create map
python cli.py route.kml photos_folder/ --map photo_map.html

# Export to multiple formats
python cli.py route.kml photos_folder/ --json locations.json --csv locations.csv

# Write GPS directly into photo EXIF
python cli.py route.kml photos_folder/ --write-exif

# If photos go opposite direction to KML path
python cli.py route.kml photos_folder/ --reverse

# Skip first 50m and last 30m of path
python cli.py route.kml photos_folder/ --start-offset 50 --end-offset 30
```

### Python API

```python
from main import geolocate_photos

# Geolocate and export
results = geolocate_photos(
    kml_path='route.kml',
    photos_dir='photos/',
    output_json='locations.json',
    output_map='photo_map.html',
    write_exif=True
)

# Access results
for photo in results:
    print(f"{photo.filename}: {photo.lat}, {photo.lon}")
```

## How It Works

1. **Parse KML**: Extracts the path as a list of GPS coordinates
2. **Calculate path length**: Computes total distance in meters
3. **Scan photos**: Finds all photos and sorts by filename (natural sort)
4. **Interpolate positions**: Distributes photos evenly along the path
5. **Assign coordinates**: Each photo gets lat/lon based on its position in sequence

### Accuracy

With 1200 photos over a 1km path, spacing is approximately:
- **1000m / 1199 = ~0.83m between photos**

This means position accuracy depends on:
- How evenly you walked (consistent speed = better accuracy)
- KML path accuracy (more waypoints = smoother path)

## KML File Format

The tool supports standard KML files with LineString paths. You can create these using:
- Google Earth Pro (draw a path, save as KML)
- Google Maps (create directions, export)
- QGIS or other GIS software
- Manually in a text editor

### Example KML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Walking Route</name>
      <LineString>
        <coordinates>
          21.0122,52.2297,0
          21.0130,52.2300,0
          21.0140,52.2310,0
        </coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>
```

Note: KML uses `longitude,latitude,altitude` format (lon first!).

## Command Line Options

```
positional arguments:
  kml_path              Path to KML file containing the walking path
  photos_dir            Directory containing the 360 photos

optional arguments:
  -o, --output, --json  Output JSON file path
  --csv                 Export to CSV file
  --gpx                 Export to GPX file (waypoints)
  --map                 Generate interactive HTML map

  --write-exif          Write GPS coordinates to photo EXIF data
  --no-backup           Don't backup original photos when writing EXIF

  --reverse             Reverse photo order (if photos go opposite to KML)
  --start-offset METERS Skip this many meters at the start of path
  --end-offset METERS   Skip this many meters at the end of path

  --marker-interval N   Show every Nth marker on map (default: 1 = all)
  --extensions EXT      Comma-separated photo extensions (default: .jpg,.jpeg,.png,.360)
  
  --dry-run             Show what would be done without making changes
  -v, --verbose         Verbose output
```

## Output Formats

### JSON
```json
{
  "total_photos": 1200,
  "path_length_m": 1000,
  "photos": [
    {
      "filename": "IMG_0001.jpg",
      "sequence_num": 1,
      "lat": 52.229700,
      "lon": 21.012200,
      "heading": 45.0,
      "distance_from_start": 0.0
    }
  ]
}
```

### CSV
```csv
sequence_num,filename,latitude,longitude,heading,distance_m,progress
1,IMG_0001.jpg,52.22970000,21.01220000,45.0,0.0,0.0000
```

### Interactive Map
HTML file with:
- OpenStreetMap + Satellite layers
- Path line visualization
- Clickable photo markers
- Start/end markers
- Fullscreen and minimap

## Tips

### Creating a KML Path

**Google Earth Pro:**
1. Add > Path
2. Click along your walking route
3. Save Place As > KML

**From GPS Track:**
If you have a GPS track (GPX), convert to KML:
```bash
# Using gpsbabel
gpsbabel -i gpx -f track.gpx -o kml -F route.kml
```

### Adjusting Photo Order

If your first photo is at the END of the KML path:
```bash
python cli.py route.kml photos/ --reverse
```

If you started taking photos partway along the path:
```bash
# Skip first 100 meters of path
python cli.py route.kml photos/ --start-offset 100
```

### Large Number of Photos

For 1000+ photos, the map might be slow. Show every 10th marker:
```bash
python cli.py route.kml photos/ --map map.html --marker-interval 10
```

## Dependencies

- **Required:**
  - shapely - Geometry operations
  - geopy - Distance calculations

- **Optional:**
  - piexif - EXIF GPS writing
  - folium - Interactive maps
  - PyQt6 - GUI (if added later)

## License

MIT License

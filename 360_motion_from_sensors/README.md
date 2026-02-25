# 360 Motion from Sensors

Tools for extracting motion data from GoPro 360 videos and visualizing camera orientation and travel path.

## Overview

This module extracts gyroscope and accelerometer data from GoPro .360 files (GPMF metadata), integrates gyro into absolute orientations, and double-integrates accelerometer data (with gravity subtracted) to estimate the camera's travel path. Results are displayed in an interactive three.js 3D viewer.

Features:
1. **Absolute camera orientation** — gyroscope data integrated into quaternions (scrubbing forward/backward works correctly)
2. **Camera travel path** — accelerometer data transformed to world frame, gravity removed, double-integrated to position
3. **Interactive 3D visualization** — three.js viewer with 360° video sphere, camera model, and path line with points
4. **Distance scale slider** — fine-tune how accelerometer maps to real-world distance
5. **Gyro sensitivity** — default 10x (the raw 1.0 scale is too weak for visual feedback)

## Requirements

```bash
pip install numpy
```

System requirements:
- `ffmpeg` (for metadata extraction)
- `ffprobe` (for video analysis)

## Usage

### Visualize Motion Stream

Extract all gyro/accelerometer data from a .360 file and generate an interactive 3D viewer:

```bash
python visualize_motion_stream.py \
    --video360 /path/to/GS011406.360 \
    --output-csv motion_data.csv \
    --output-html motion_viewer.html
```

**Arguments:**
- `--video360`: Path to original GoPro .360 file (contains GPMF metadata with IMU data)
- `--output-csv`: Output CSV file with raw sensor data (default: motion_data.csv)
- `--output-html`: Output HTML file with interactive 3D visualization (default: motion_viewer.html)

Then serve the viewer locally:
```bash
python3 -m http.server 8000
# Open http://localhost:8000/motion_viewer.html
```

**Viewer features:**
- **Timeline slider** — scrub to any point, works forward and backward (absolute orientations)
- **Play/Pause** — animate through the timeline; syncs with loaded 360° video
- **Camera Path** — line with color-coded points (green→yellow→red over time) showing estimated travel
- **Distance Scale slider** — multiply the path distance to match expected real-world scale
- **Gyro Sensitivity slider** — amplify rotation for visual clarity (default 10x)
- **Follow Camera** — orbit controls track the camera position
- **360° Video** — load an equirectangular MP4 to project on the sphere around the camera

## How It Works

1. **GPMF Stream Detection**: Scans the .360 file for metadata stream (codec: `gpmd`, handler: "GoPro MET")
2. **Binary Extraction**: Uses ffmpeg to extract raw GPMF binary data
3. **GPMF Parsing**: Parses Key-Length-Value (KLV) format to find:
   - `GYRO` — Gyroscope data (3-axis, ~200 Hz, rad/s)
   - `ACCL` — Accelerometer data (3-axis, ~200 Hz, m/s²)
   - `SCAL` — Scale factors to convert int16 → float values
4. **Orientation Integration**: Gyro angular velocity is integrated sample-by-sample into absolute quaternion orientations
5. **Path Estimation**: Accelerometer is rotated to world frame using the computed orientation, gravity (~9.8 m/s² downward) is subtracted, then double-integrated (accel → velocity → position)
6. **Visualization**: Data is downsampled to ~3000 frames and embedded in an HTML file with three.js

## GoPro Coordinate System

GoPro HERO6+/MAX/HERO7+ use the following axis convention:
- **X axis**: Right (positive = rotating/moving right)
- **Y axis**: Up (positive = rotating/moving up)
- **Z axis**: Forward (positive = rotating/moving forward into scene)

Data in GPMF is stored as: Y, -X, Z (reordered by parser to X, Y, Z)

## Notes

- Accelerometer always shows ~9.8 m/s² on one axis (gravity tells us where ground is)
- The distance scale slider is important because accelerometer drift accumulates over time — use it to calibrate visually
- Gyro default sensitivity is 10x because the raw 1.0 scale produces barely visible rotation in the viewer

## References

- [GoPro GPMF Specification](https://github.com/gopro/gpmf-parser)
- GoPro metadata format uses big-endian encoding
- Gyro: rad/s, Accelerometer: m/s², sampled at ~200 Hz

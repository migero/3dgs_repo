# 360 Motion Deblur

Tools for extracting motion data from GoPro 360 videos and preparing for motion deblurring.

## Overview

This module extracts gyroscope and accelerometer data from GoPro .360 files (GPMF metadata) and visualizes motion vectors on video frames. This data can be used to:

1. Understand camera motion during capture
2. Estimate motion blur direction for each frame
3. Prepare spatially-varying motion blur removal
4. Analyze which frames have the most motion blur

## Requirements

```bash
pip install opencv-python numpy
```

System requirements:
- `ffmpeg` (for video/metadata extraction)
- `ffprobe` (for video analysis)

## Usage

### Extract Motion Vectors Script

Extract gyro/accelerometer data from a .360 file and visualize it on a frame from the stitched MP4:

```bash
python extract_motion_vectors.py \
    --video360 /path/to/GS011388.360 \
    --video-mp4 /path/to/GS011388.mp4 \
    --time 5.0 \
    --output motion_vectors_5s.png
```

**Arguments:**
- `--video360`: Path to original GoPro .360 file (contains GPMF metadata with IMU data)
- `--video-mp4`: Path to stitched/processed MP4 file (for frame extraction)
- `--time`: Time in seconds to extract frame and motion data (e.g., 5.0 for 5 seconds)
- `--output`: Output image path (default: motion_vectors.png)

**Example:**
```bash
python extract_motion_vectors.py \
    --video360 /run/media/migero/trash_bad/GS011388.360 \
    --video-mp4 /run/media/migero/trash_bad/GS011388.mp4 \
    --time 5 \
    --output test_frame_5s_vectors.png
```

## Output

The script generates an image showing:
- **Red arrows**: Gyroscope data (rotation rate in rad/s)
  - X axis: horizontal rotation (yaw)
  - Y axis: vertical rotation (pitch)  
  - Z axis: rotation around camera forward axis (roll) - shown as circle
- **Blue arrows**: Accelerometer data (acceleration in m/s²)
  - X, Y, Z components
  - Includes gravity (~9.8 m/s² on one axis when stationary)

Motion vectors are averaged over a ±0.1 second window around the specified time.

## How It Works

1. **GPMF Stream Detection**: Scans the .360 file for metadata stream (codec: `gpmd`, handler: "GoPro MET")
2. **Binary Extraction**: Uses ffmpeg to extract raw GPMF binary data
3. **GPMF Parsing**: Parses Key-Length-Value (KLV) format to find:
   - `GYRO` - Gyroscope data (3-axis, ~200 Hz)
   - `ACCL` - Accelerometer data (3-axis, ~200 Hz)
   - `SCAL` - Scale factors to convert int16 → float values
4. **Frame Extraction**: Uses ffmpeg to extract PNG frame at specified time from MP4
5. **Interpolation**: Averages motion data around the target timestamp
6. **Visualization**: Draws motion vectors as arrows using OpenCV

## GoPro Coordinate System

GoPro HERO6+/MAX/HERO7+ use the following axis convention:
- **X axis**: Right (positive = rotating/moving right)
- **Y axis**: Up (positive = rotating/moving up)
- **Z axis**: Forward (positive = rotating/moving forward into scene)

Data in GPMF is stored as: Y, X, Z (reordered by parser)

## Future Work

- [ ] Extract motion data for all frames
- [ ] Calculate optical flow from video
- [ ] Combine gyro + optical flow for per-pixel motion estimation
- [ ] Integrate motion deblurring libraries (DeblurGAN-v2, EDVR, etc.)
- [ ] Apply spatially-varying deblur based on motion vectors
- [ ] Handle 360° equirectangular distortion in motion estimation
- [ ] Video processing pipeline integration

## References

- [GoPro GPMF Specification](https://github.com/gopro/gpmf-parser)
- GoPro metadata format uses big-endian encoding
- Gyro: rad/s, Accelerometer: m/s², sampled at ~200 Hz

# GoPro 360 Converter

A Python Qt5 application for converting GoPro .360 files to standard equirectangular MP4 videos, similar to GoPro Player.

## Features

- **Convert GoPro .360 files** to standard 360° equirectangular MP4 format
- **Live preview** of stitched frames before conversion
- **Multiple compression options** (H.264, H.265/HEVC, VP9)
- **Quality settings** from high to low compression
- **Resolution presets** from original to 720p
- **Audio handling** - include or exclude audio track
- **Progress tracking** with ETA during conversion

## Requirements

### System Requirements
- Python 3.8+
- FFmpeg (with v360 filter support)
- Linux, macOS, or Windows

### Python Dependencies
- PyQt5 >= 5.15.0
- numpy >= 1.21.0
- opencv-python >= 4.5.0 (optional, for better preview)
- Pillow >= 9.0.0 (fallback image loading)

## Installation

### 1. Install FFmpeg

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Linux (Fedora):**
```bash
sudo dnf install ffmpeg
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH.

### 2. Install Python Dependencies

```bash
cd gopro360-converter
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python main.py
```

## Usage

1. **Select Input File**: Click "Browse..." to select your GoPro .360 file
2. **Preview**: The application will generate a preview of the stitched output
3. **Adjust Settings**:
   - **Input Format**: Select "Dual Fisheye" for GoPro MAX cameras
   - **Fisheye FOV**: Typically 190° for GoPro MAX
   - **Interpolation**: Bicubic recommended for quality/speed balance
   - **Video Codec**: H.264 for maximum compatibility
   - **Quality**: Medium (CRF 23) for good balance
   - **Output Resolution**: Choose based on your needs
4. **Convert**: Click "Convert to Equirectangular MP4"
5. **Wait**: Monitor progress and ETA in the progress bar

## How It Works

### GoPro .360 File Format

GoPro MAX cameras record 360° video in a unique 2-channel cubemap format:

**Channel 1 (Track 0):** Left, Front, Right cube faces (horizontal strip)
**Channel 2 (Track 1):** Bottom, Back, Top cube faces (rotated 90° clockwise)

Each track contains:
- 3 cube faces arranged horizontally
- Content positioned at 1/6 and 5/6 of frame width (padding on edges)
- Approximately 190° field of view per face (with overlap for stitching)

### Stitching Process

The application uses FFmpeg to:

1. **Extract both video tracks** from the .360 container
2. **Crop the padding** (remove 1/6 from each edge)
3. **Rotate Channel 2** back to proper orientation
4. **Split each track** into individual cube faces
5. **Arrange into standard 3x2 cubemap** layout
6. **Convert to equirectangular** using FFmpeg's v360 filter

```
Channel 1: [Left][Front][Right]     →  Cubemap 3x2  →  Equirectangular
Channel 2: [Bottom][Back][Top]↻90°  →     ↓              (2:1 ratio)
```

## Supported Input Formats

| Format | Description | Notes |
|--------|-------------|-------|
| GoPro MAX .360 | 2-channel cubemap | Primary supported format |

**Note:** LRV (Low Resolution Video) files use dual fisheye format and are not supported. Use the main .360 file for conversion.

## Output Formats

| Codec | Extension | Notes |
|-------|-----------|-------|
| H.264 (libx264) | .mp4 | Best compatibility |
| H.265 (libx265) | .mp4 | Better compression, less compatible |
| VP9 (libvpx-vp9) | .webm | Web optimized |

## Troubleshooting

### "FFmpeg not found"
Ensure FFmpeg is installed and in your system PATH:
```bash
ffmpeg -version
```

### Preview not generating
- Check that the .360 file is valid
- Ensure FFmpeg has v360 filter: `ffmpeg -filters | grep v360`

### Poor stitching quality
- Try adjusting the FOV setting (typically 185-195° for GoPro MAX)
- Use "Lanczos" interpolation for highest quality
- Ensure you're using the correct input format

### Conversion is slow
- Use "Bilinear" interpolation for faster processing
- Lower the output resolution
- H.264 is faster than H.265 or VP9

## Advanced: Command Line Usage

The GoPro MAX .360 format requires a complex FFmpeg filter chain. Here's an example:

```bash
# Extract info about the .360 file
ffprobe -show_streams input.360

# Basic conversion (simplified - actual pipeline is more complex)
# The app handles the full 2-channel cubemap extraction automatically
python main.py
```

The full conversion involves:
1. Cropping padding from both tracks (content at 1/6 to 5/6)
2. Rotating the second track
3. Splitting into 6 cube faces
4. Arranging into 3x2 cubemap
5. Converting to equirectangular

## Technical Notes

### GoPro MAX .360 Format Details

- **2 video tracks** in MP4 container
- **Track 0:** Left, Front, Right faces (horizontal strip)
- **Track 1:** Bottom, Back, Top faces (rotated 90° CW)
- **Content position:** 1/6 to 5/6 of frame width (1/6 padding each side)
- **Cube face FOV:** ~190° (with overlap for seamless stitching)
- **Native resolution:** Up to 4096x1344 per track

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please submit issues and pull requests on GitHub.

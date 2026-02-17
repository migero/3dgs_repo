# 360 Motion Deblur

A PyQt5 GUI application for applying motion deblurring to 360° equirectangular videos using PVDNet (Pixel Volume Deblurring Network).

## Overview

This tool:
1. Extracts frames from 360° equirectangular videos
2. Converts each frame to 6 cube faces using equirectangular-to-cubemap projection
3. Processes each cube face through PVDNet for motion deblurring
4. Reconstructs the deblurred cube faces back to equirectangular format
5. Encodes the processed frames back to video using FFmpeg

## Features

- **GPU Accelerated**: Uses CUDA for PVDNet inference
- **Parallel Processing**: Processes all 6 cube faces simultaneously
- **Memory Efficient**: Keeps frame buffer in memory with configurable cleanup
- **Temporal Consistency**: Maintains previous frame state for recurrent deblurring
- **Multiple Resolutions**: Supports 512, 640, 768, 1024, 1280px cube face sizes

## Requirements

- Python 3.8+
- CUDA-capable GPU with 6GB+ VRAM recommended
- FFmpeg installed and accessible in PATH
- PVDNet model checkpoint (included in PVDNet/ folder)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. **Download PVDNet checkpoints** (REQUIRED):
   
   The PVDNet model checkpoints must be downloaded manually from:
   https://www.dropbox.com/sh/frpegu68s0yx8n9/AACrptFFhxejSyKJBvLdk9IJa?dl=0
   
   Download these files and place them in `PVDNet/ckpt/`:
   - `PVDNet_DVD.pytorch` (recommended for general use)
   - `PVDNet_nah.pytorch` (alternative model)
   - `PVDNet_large_nah.pytorch` (higher quality, slower)
   - `BIMNet.pytorch` (should already be present from git clone)
   
   Your `PVDNet/ckpt/` folder should look like:
   ```
   PVDNet/ckpt/
   ├── BIMNet.pytorch
   ├── PVDNet_DVD.pytorch
   ├── PVDNet_nah.pytorch
   └── PVDNet_large_nah.pytorch
   ```

## Usage

### GUI Mode
```bash
python main.py
```

### CLI Mode (coming soon)
```bash
python cli.py --input video.mp4 --output deblurred.mp4 --resolution 1024
```

## Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Cube Face Resolution | Size of each cube face in pixels | 1024 |
| Frame Buffer Size | Number of frames to keep in memory | 30 |
| Model Checkpoint | PVDNet model weights file | PVDNet_DVD.pytorch |

## Technical Notes

### PVDNet Integration
PVDNet uses a recurrent architecture that requires 3 consecutive frames:
- `I_prev`: Previous frame
- `I_curr`: Current frame (being deblurred)
- `I_next`: Next frame

The model also maintains `I_prev_deblurred` state for temporal consistency.

### Cube Face Processing
All 6 cube faces (front, back, left, right, top, bottom) are processed in parallel
on the GPU for maximum throughput.

### Resolution Guidelines
Cube face resolution should be a multiple of 8 for optimal neural network performance.
Recommended sizes: 512, 640, 768, 1024, 1280

## Credits

- PVDNet: [Recurrent Video Deblurring with Blur-Invariant Motion Estimation and Pixel Volumes](https://github.com/codeslake/PVDNet)
- py360convert: For equirectangular-cubemap conversions

## License

See LICENSE file in the parent directory.

# Find Best Frames

A PyQt5 GUI tool to analyze video frames for sharpness and extract the best quality frames at a target FPS.

## Features

- **FFmpeg-based analysis**: Uses ffmpeg's `blurdetect` filter for fast frame quality analysis (no OpenCV needed)
- **Quality graph**: Visualizes sharpness over time with green markers showing selected frames
- **Adaptive frame selection**: Picks the sharpest frame from each interval based on target FPS
- **No frame skipping**: Always selects the best available frame, even if quality is low
- **Configurable output**: JPG quality setting (default 95%)

## Installation

```bash
pip install -r requirements.txt
```

Requires ffmpeg to be installed and available in PATH.

## Usage

```bash
python main.py
```

1. **Browse** and select a video file
2. **Analyze** the video - this scans all frames for blur/sharpness
3. **Adjust FPS** - lower FPS = fewer but sharper frames, higher FPS = more frames
4. **Set output folder** and JPG quality
5. **Extract** the selected frames

## How it works

1. ffmpeg's `blurdetect` filter analyzes each frame for blur percentage
2. Sharpness score = 100 - blur_value
3. Video is divided into intervals based on target FPS
4. The sharpest frame from each interval is selected
5. Selected frames are extracted as JPG files

## Graph Interpretation

- **Blue line**: Sharpness score (0-100) for each frame over time
- **Green vertical bars**: Frames that will be extracted
- **Green dots**: Sharpness of selected frames

## Requirements

- Python 3.8+
- ffmpeg (with blurdetect filter support)
- PyQt5
- matplotlib
- numpy

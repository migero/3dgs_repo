# 360 Mask Generator

A Python application to generate segmentation masks for moving objects (people, vehicles, animals, etc.) in equirectangular 360° images.

## Overview

Object detection models like YOLO work best with perspective images, not equirectangular projections. This tool solves that problem by:

1. **Extracting perspective views** - Converts the 360° equirectangular image into multiple overlapping perspective views around the horizon
2. **Running YOLO segmentation** - Detects and segments objects in each perspective view using Ultralytics YOLO
3. **Projecting back to equirectangular** - Maps the detected masks back to equirectangular coordinates
4. **Stitching masks** - Combines all perspective masks into a single coherent equirectangular mask
5. **Post-processing** - Applies morphological operations, dilation, and feathering for clean results

## Installation

```bash
cd 360_mask_generator

# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install numpy opencv-python Pillow ultralytics py360convert PyQt5
```

### GPU Support (Optional)

For faster processing with CUDA:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## Usage

### GUI Application

```bash
python main.py
```

Features:
- Load equirectangular images
- Configure detection settings (number of views, model, confidence threshold)
- Select which object classes to detect
- View original image, mask, overlay, and perspective views
- Save masks for use in 360° video compositing

### Command Line

```bash
# Basic usage
python cli.py input.jpg -o mask.png

# Fast mode (fewer views, smaller model)
python cli.py input.jpg -o mask.png --preset fast

# Accurate mode (more views, larger model)  
python cli.py input.jpg -o mask.png --preset accurate

# Custom settings
python cli.py input.jpg -o mask.png --views 12 --model yolo11m-seg.pt --confidence 0.3

# Save visualization
python cli.py input.jpg -o mask.png --save-overlay overlay.png --save-views views.png

# Verbose output
python cli.py input.jpg -o mask.png -v
```

### Python API

```python
from core.pipeline import MaskGenerationPipeline, PipelineConfig
import cv2

# Create pipeline with default settings
pipeline = MaskGenerationPipeline()

# Or customize configuration
config = PipelineConfig(
    num_horizontal_views=8,      # Number of views around horizon
    num_pitch_levels=3,          # Include up/down views
    fov=90.0,                    # Field of view per perspective
    model_name="yolo11m-seg.pt", # YOLO model to use
    target_classes=['person', 'car', 'bicycle'],  # Classes to detect
    confidence_threshold=0.25,   # Detection confidence
    dilate_mask=True,            # Expand mask slightly
    feather_edges=True           # Soft mask edges
)
pipeline = MaskGenerationPipeline(config)

# Process an image
image = cv2.imread("360_image.jpg")
result = pipeline.process(image)

# Save the mask
result.save_mask("mask.png")

# Get detection summary
summary = pipeline.get_detection_summary(result)
print(f"Found {summary['total_detections']} objects")
print(f"Classes: {summary['class_counts']}")
```

## Configuration Options

### Pipeline Presets

| Preset | Views | Pitch Levels | Model | Speed |
|--------|-------|--------------|-------|-------|
| Fast | 4 | 1 | yolo11n-seg | ~5s |
| Default | 8 | 1 | yolo11n-seg | ~10s |
| Accurate | 12 | 3 | yolo11m-seg | ~60s |

### View Settings

- **num_horizontal_views**: Number of perspective views around the 360° (4-16)
- **num_pitch_levels**: Vertical coverage (1=horizon only, 3=include up/down)
- **fov**: Field of view for each perspective view (60°-120°)
- **pitch_range**: Min/max pitch angles (default: -30° to 30°)

### YOLO Models

Available models (smaller = faster, larger = more accurate):
- `yolo11n-seg.pt` - Nano (fastest, ~2.7M params)
- `yolo11s-seg.pt` - Small (~10.4M params)
- `yolo11m-seg.pt` - Medium (~23.6M params)
- `yolo11l-seg.pt` - Large (~28.0M params)
- `yolo11x-seg.pt` - XLarge (~62.8M params)

### Target Classes

Default moving object classes:
- person, bicycle, car, motorcycle, bus, train, truck
- bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe

All COCO classes are available (80 total).

## Architecture

```
360_mask_generator/
├── main.py                 # GUI application entry point
├── cli.py                  # Command-line interface
├── requirements.txt        # Python dependencies
├── core/
│   ├── perspective_projector.py  # Equirectangular ↔ perspective conversion
│   ├── yolo_segmenter.py         # YOLO instance segmentation
│   ├── mask_stitcher.py          # Combine perspective masks
│   └── pipeline.py               # Full processing pipeline
└── ui/
    └── main_window.py      # PyQt5 GUI
```

## How It Works

### 1. Perspective Extraction

The equirectangular image is "unwrapped" into multiple perspective views:

```
Equirectangular (360° x 180°)
┌────────────────────────────────────────┐
│                                        │
│   ┌────┐  ┌────┐  ┌────┐  ┌────┐      │
│   │View│  │View│  │View│  │View│  ... │
│   │ 1  │  │ 2  │  │ 3  │  │ 4  │      │
│   └────┘  └────┘  └────┘  └────┘      │
│                                        │
└────────────────────────────────────────┘
```

Each view overlaps with neighbors to ensure full coverage. Views use a 90° FOV by default, giving ~22° overlap between adjacent views.

### 2. Object Detection

Each perspective view is processed by YOLO, which returns:
- Instance segmentation masks
- Class labels (person, car, etc.)
- Confidence scores
- Bounding boxes

### 3. Mask Projection

Masks are projected back to equirectangular coordinates using the inverse of the perspective projection. Coordinate mappings are cached for efficiency.

### 4. Mask Stitching

Multiple masks are combined using:
- **Max blending**: Take the maximum mask value at each pixel (default)
- **Average blending**: Average all overlapping mask values
- **Weighted blending**: Weight by distance from view center

### 5. Post-processing

- **Morphological closing**: Fill small gaps in masks
- **Dilation**: Slightly expand masks to ensure full coverage
- **Feathering**: Blur mask edges for smooth compositing

## Use Cases

- **360° video cleanup**: Remove tourists, cars, or crew from 360° footage
- **Privacy masking**: Automatically blur people in 360° content
- **Compositing**: Extract objects for placing in other scenes
- **Motion detection**: Identify moving objects for temporal analysis

## Tips for Best Results

1. **Image quality**: Higher resolution inputs produce better masks
2. **Lighting**: Good lighting improves detection accuracy
3. **Object size**: Objects should be large enough in perspective views
4. **Occlusion**: Heavily occluded objects may not be detected
5. **Model selection**: Use larger models for difficult scenes

## Limitations

- Detection quality depends on YOLO's training data (COCO dataset)
- Extreme fisheye distortion at poles may affect detection
- Very small or distant objects may not be detected
- Processing time increases with number of views and model size

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - State-of-the-art object detection
- [py360convert](https://github.com/sunset1995/py360convert) - 360° image conversion utilities

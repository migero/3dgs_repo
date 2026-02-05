# 360 Mask Generator

A Python application to generate segmentation masks for moving objects (people, vehicles, animals, etc.) in equirectangular 360° images.

## Overview

Object detection models like YOLO work best with perspective images, not equirectangular projections. This tool solves that problem by:

1. **Extracting perspective views** - Converts the 360° equirectangular image into multiple overlapping perspective views around the horizon
2. **Running segmentation** - Detects and segments objects in each perspective view using YOLO or Mask2Former
3. **Projecting back to equirectangular** - Maps the detected masks back to equirectangular coordinates
4. **Stitching masks** - Combines all perspective masks into a single coherent equirectangular mask
5. **Post-processing** - Applies morphological operations, dilation, and feathering for clean results

## Supported Models

### YOLO Models (Fast, GPU-optimized)
- **YOLO11**: yolo11n/s/m/l/x-seg.pt
- **YOLO26** ⚡ NEW: yolo26n/s/m/l/x-seg.pt (Latest generation, NMS-free inference, 43% faster CPU inference)

### Mask2Former (High quality, research-grade)
- **Instance Segmentation**: High-quality object masks
- **Panoptic Segmentation**: Combined instance + semantic
- **Semantic Segmentation**: Pixel-level class classification

## Installation

```bash
cd 360_mask_generator

# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install numpy opencv-python Pillow ultralytics>=8.4.0 py360convert PyQt5
```

### GPU Support (Optional)

For faster processing with CUDA:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Mask2Former Setup (Optional)

For high-quality segmentation with Mask2Former:

```bash
# Install detectron2 (see https://detectron2.readthedocs.io/en/latest/tutorials/install.html)
pip install 'git+https://github.com/facebookresearch/detectron2.git'

# Ensure the Mask2Former repository is available in the parent directory
# The setup script will automatically detect and configure it
```

## Usage

### GUI Application

```bash
python main.py
```

Features:
- Load equirectangular images
- **NEW**: Choose between YOLO and Mask2Former segmenters
- **NEW**: Select from latest YOLO26 models for best performance
- Configure detection settings (number of views, model, confidence threshold)
- Select which object classes to detect
- View original image, mask, overlay, and perspective views
- Save masks for use in 360° video compositing

### Command Line

```bash
# Basic usage with YOLO11
python cli.py input.jpg -o mask.png

# NEW: Use latest YOLO26 models for better performance
python cli.py input.jpg -o mask.png --model yolo26m-seg.pt

# NEW: Use Mask2Former for highest quality (requires detectron2)
python cli.py input.jpg -o mask.png --segmenter mask2former

# Fast mode (fewer views, smaller model)
python cli.py input.jpg -o mask.png --preset fast

# Accurate mode (more views, larger model)  
python cli.py input.jpg -o mask.png --preset accurate

# Custom settings
python cli.py input.jpg -o mask.png --views 12 --model yolo26l-seg.pt --confidence 0.3

# Mask2Former with custom config
python cli.py input.jpg -o mask.png --segmenter mask2former --mask2former-mode panoptic

# Save visualization
python cli.py input.jpg -o mask.png --save-overlay overlay.png --save-views views.png

# Batch processing folder
python cli.py --batch /path/to/images/ --model yolo26s-seg.pt

# Verbose output
python cli.py input.jpg -o mask.png -v
```

### Python API

```python
from core.pipeline import MaskGenerationPipeline, PipelineConfig
import cv2

# Example 1: Using YOLO26 (latest generation)
config = PipelineConfig(
    num_horizontal_views=8,           # Number of views around horizon
    num_pitch_levels=3,               # Include up/down views
    fov=90.0,                         # Field of view per perspective
    model_name="yolo26m-seg.pt",      # NEW: YOLO26 model
    segmenter_type="yolo",            # Use YOLO segmenter
    target_classes=['person', 'car', 'bicycle'],  # Classes to detect
    confidence_threshold=0.35,        # Detection confidence
    dilate_mask=True,                 # Expand mask slightly
    feather_edges=True                # Soft mask edges
)
pipeline = MaskGenerationPipeline(config)

# Process an image
image = cv2.imread("360_image.jpg")
result = pipeline.process(image)

# Save the mask
result.save_mask("mask.png")
print(f"Processing time: {result.processing_time:.2f}s")

# Example 2: Using Mask2Former for highest quality
config_m2f = PipelineConfig(
    num_horizontal_views=6,           # Fewer views (Mask2Former is slower)
    num_pitch_levels=1,               # Horizon only
    segmenter_type="mask2former",     # NEW: Use Mask2Former
    mask2former_mode="instance",      # Segmentation mode
    target_classes=['person', 'car', 'bicycle'],
    confidence_threshold=0.5
)
pipeline_m2f = MaskGenerationPipeline(config_m2f)

# Process with Mask2Former
result_m2f = pipeline_m2f.process(image)
result_m2f.save_mask("mask_hq.png")

# Example 3: Direct segmenter usage
from core.yolo_segmenter import YoloSegmenter
from core.mask2former_segmenter import Mask2FormerSegmenter

# YOLO26 segmenter
yolo_segmenter = YoloSegmenter(
    model_name="yolo26l-seg.pt",
    target_classes=["person"],
    confidence_threshold=0.4
)
yolo_segmenter.load_model()

# Mask2Former segmenter
m2f_segmenter = Mask2FormerSegmenter(
    target_classes=["person"],
    mode="instance",
    confidence_threshold=0.5
)
m2f_segmenter.load_model()

# Segment perspective views directly
perspective_view = cv2.imread("perspective_view.jpg")
yolo_result = yolo_segmenter.segment(perspective_view)
m2f_result = m2f_segmenter.segment(perspective_view)
```

## Configuration Options

### Pipeline Presets

| Preset | Views | Pitch Levels | Model | Speed |
|--------|-------|--------------|-------|-------|
| Fast | 4 | 1 | yolo11n-seg | ~5s |
| Default | 8 | 1 | yolo11n-seg | ~10s |
| Accurate | 12 | 3 | yolo11m-seg | ~60s |

*Note: Speeds are approximate and depend on hardware. YOLO26 models are ~43% faster on CPU.*

### View Settings

- **num_horizontal_views**: Number of perspective views around the 360° (4-16)
- **num_pitch_levels**: Vertical coverage (1=horizon only, 3=include up/down)
- **fov**: Field of view for each perspective view (60°-120°)
- **pitch_range**: Min/max pitch angles (default: -30° to 30°)

### Segmentation Models

#### YOLO11 Models (Stable)
- `yolo11n-seg.pt` - Nano (fastest, ~2.7M params)
- `yolo11s-seg.pt` - Small (~10.4M params)
- `yolo11m-seg.pt` - Medium (~23.6M params)
- `yolo11l-seg.pt` - Large (~27.7M params)
- `yolo11x-seg.pt` - XLarge (most accurate, ~58.4M params)

#### YOLO26 Models ⚡ NEW (Latest Generation)
- `yolo26n-seg.pt` - Nano (fastest, NMS-free inference)
- `yolo26s-seg.pt` - Small (improved small object detection)
- `yolo26m-seg.pt` - Medium (best balance)
- `yolo26l-seg.pt` - Large (high accuracy)
- `yolo26x-seg.pt` - XLarge (highest accuracy)

#### Mask2Former Models 🔬 NEW (Research Quality)
- **Instance Mode**: High-quality object instance masks
- **Panoptic Mode**: Combined instance + semantic segmentation  
- **Semantic Mode**: Pixel-level semantic classification

*Requires detectron2 installation and Mask2Former repository*

### Model Comparison

| Model Family | Speed | Quality | GPU Memory | Best For |
|-------------|--------|---------|------------|----------|
| YOLO11 | Fast | Good | Low | Real-time processing |
| YOLO26 | Fastest | Good+ | Low | Production workflows |
| Mask2Former | Slower | Excellent | High | Research, final output |

### Target Classes

Default moving object classes:
- person, bicycle, car, motorcycle, bus, train, truck
- bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe

All COCO classes are available (80 total).

## Architecture

```
360_mask_generator/
├── main.py                        # GUI application entry point
├── cli.py                         # Command-line interface
├── test_new_features.py          # NEW: Test YOLO26 & Mask2Former
├── requirements.txt               # Python dependencies
├── core/
│   ├── perspective_projector.py  # Equirectangular ↔ perspective conversion
│   ├── yolo_segmenter.py         # YOLO instance segmentation
│   ├── mask2former_segmenter.py  # NEW: Mask2Former segmentation
│   ├── mask_stitcher.py          # Combine perspective masks
│   └── pipeline.py               # Full processing pipeline
└── ui/
    └── main_window.py             # PyQt5 GUI (updated with model selection)
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

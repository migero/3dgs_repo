# Video Mask Generator

Generate segmentation masks for moving objects (people, vehicles, etc.) in regular videos using YOLO.

Unlike the 360 Mask Generator, this tool works directly with regular (non-equirectangular) video content without the need for perspective projection.

## Features

- **YOLO-based segmentation**: Uses state-of-the-art YOLO11 models for accurate instance segmentation
- **Video & image support**: Process videos frame-by-frame or single images
- **Configurable detection**: Choose which object classes to detect
- **Post-processing**: Optional dilation and edge feathering for better masks
- **GPU acceleration**: Automatic CUDA detection for faster processing
- **Batch processing**: Process entire folders of videos/images
- **GUI & CLI**: Both graphical and command-line interfaces

## Installation

```bash
pip install -r requirements.txt
```

For GPU acceleration (recommended):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## Usage

### GUI

```bash
python main.py
```

### Command Line

```bash
# Process a video, extract 1 frame per second
python cli.py video.mp4 --output-dir masks/ --fps 1

# Process with larger model for better accuracy
python cli.py video.mp4 --output-dir masks/ --model yolo11l-seg.pt

# Process single image
python cli.py image.jpg --output mask.png

# Custom confidence threshold
python cli.py video.mp4 --output-dir masks/ --confidence 0.5

# Detect only people
python cli.py video.mp4 --output-dir masks/ --classes person

# List available classes
python cli.py --list-classes
```

## Available Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| yolo11n-seg.pt | ~6MB | Fastest | Good |
| yolo11s-seg.pt | ~12MB | Fast | Better |
| yolo11m-seg.pt | ~25MB | Medium | Good |
| yolo11l-seg.pt | ~50MB | Slow | Best |
| yolo11x-seg.pt | ~100MB | Slowest | Best |

## Default Target Classes

The following object classes are detected by default:
- person
- bicycle
- car
- motorcycle
- bus
- train
- truck
- backpack
- umbrella
- handbag
- suitcase

## Output

- **Masks**: Grayscale PNG images where white (255) = detected object, black (0) = background
- **Overlays** (optional): Original frames with colored mask overlays for visualization

## Use Cases

- Video editing: Remove unwanted objects
- Privacy protection: Blur/mask people in footage
- Training data: Generate segmentation datasets
- VFX: Create rotoscope masks automatically

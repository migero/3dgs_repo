# Frame Quality Detector

A sophisticated tool for analyzing video frames to detect the sharpest, highest quality frames with minimal motion blur. Perfect for extracting the best frames from videos for further processing or analysis.

## Features

### Quality Metrics
- **Sharpness Detection**: Multiple algorithms including Laplacian variance, Sobel edge detection, and gradient magnitude
- **Motion Blur Detection**: Frequency domain analysis and edge sharpness analysis
- **Combined Quality Score**: Weighted scoring system for comprehensive frame quality assessment

### Interfaces
- **Command Line Interface**: Batch processing and automation-friendly
- **Graphical Interface**: Interactive frame analysis and preview
- **Python API**: Integrate into your own applications

### Supported Formats
- **Input**: MP4, WebM, AVI, MOV, and other common video formats
- **Output**: PNG, JPEG frame extraction with detailed quality reports

## Quick Start

### Installation
```bash
cd frame_quality_detector
pip install -r requirements.txt
```

### Command Line Usage

```bash
# Extract and analyze best 10 frames from video
python cli.py --video input.webv --top-n 10 --output best_frames/

# Analyze existing extracted frames
python cli.py --frames-dir extracted_frames/ --analyze-only --top-n 5

# Extract frames at 0.5 FPS with quality threshold
python cli.py --video video.mp4 --fps 0.5 --quality-threshold 75
```

### GUI Usage
```bash
python main.py
```

## Quality Analysis Methods

### Sharpness Metrics
1. **Laplacian Variance**: Measures edge sharpness using second derivative
2. **Sobel Edge Detection**: Analyzes edge magnitude and direction
3. **Gradient Magnitude**: Evaluates intensity gradient strength
4. **Tenengrad**: Focus measure based on gradient magnitude

### Motion Blur Detection
1. **Frequency Domain Analysis**: FFT-based blur detection
2. **Edge Sharpness Analysis**: Measures edge transition steepness
3. **Kernel Estimation**: Estimates motion blur kernel characteristics

### Combined Scoring
- Weighted combination of sharpness and blur metrics
- Configurable weights for different use cases
- Normalization for consistent scoring across different image types

## API Usage

```python
from core.quality_analyzer import FrameQualityAnalyzer
from core.frame_extractor import FrameExtractor

# Extract frames
extractor = FrameExtractor()
frames_dir = extractor.extract_frames('video.mp4', fps=1.0)

# Analyze quality
analyzer = FrameQualityAnalyzer()
results = analyzer.analyze_directory(frames_dir)
best_frames = analyzer.get_top_frames(results, top_n=5)

# Access detailed metrics
for frame_data in best_frames:
    print(f"Frame: {frame_data['filename']}")
    print(f"Quality Score: {frame_data['quality_score']:.2f}")
    print(f"Sharpness: {frame_data['sharpness']:.2f}")
    print(f"Blur Score: {frame_data['blur_score']:.2f}")
```

## Configuration

Customize analysis parameters:

```python
analyzer = FrameQualityAnalyzer(
    sharpness_weight=0.7,
    blur_weight=0.3,
    edge_threshold=50,
    verbose=True
)
```

## Output Formats

- **JSON**: Structured data for programmatic use
- **CSV**: Spreadsheet-compatible analysis results
- **Text**: Human-readable reports

## Examples

See the `examples/` directory for detailed usage examples and integration patterns.
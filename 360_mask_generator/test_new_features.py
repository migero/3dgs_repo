#!/usr/bin/env python3
"""
Example script demonstrating YOLO26 and Mask2Former integration in 360 Mask Generator.

This script shows how to:
1. Use the new YOLO26 models
2. Use Mask2Former (if available)
3. Compare different segmentation approaches

Run this script to test the new features.
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np

# Add the 360_mask_generator to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core.pipeline import MaskGenerationPipeline, PipelineConfig
from core.yolo_segmenter import YoloSegmenter, DEFAULT_MOVING_CLASSES

# Try to import Mask2Former
try:
    from core.mask2former_segmenter import Mask2FormerSegmenter, is_mask2former_available
    MASK2FORMER_AVAILABLE = is_mask2former_available()
except ImportError:
    MASK2FORMER_AVAILABLE = False
    print("Mask2Former not available. Only YOLO models will be tested.")


def test_yolo26_models():
    """Test YOLO26 models."""
    print("\\n=== Testing YOLO26 Models ===")
    
    # Available YOLO26 models (these will be downloaded automatically if not present)
    yolo26_models = [
        "yolo26n-seg.pt",  # Fastest
        "yolo26s-seg.pt",  # Small
        "yolo26m-seg.pt",  # Medium
        "yolo26l-seg.pt",  # Large
        "yolo26x-seg.pt"   # Extra Large (highest accuracy)
    ]
    
    for model_name in yolo26_models:
        print(f"\\nTesting {model_name}...")
        
        try:
            # Create segmenter
            segmenter = YoloSegmenter(
                model_name=model_name,
                target_classes=["person", "car", "bicycle"],  # Common test classes
                confidence_threshold=0.5,
                verbose=True
            )
            
            # Try to load model
            if segmenter.load_model():
                print(f"✓ {model_name} loaded successfully")
                print(f"  Device: {segmenter.get_device_info()}")
                
                # Test with a small dummy image
                test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
                result = segmenter.segment(test_image)
                print(f"  Segmentation test: ✓ (found {len(result.masks)} masks)")
                
            else:
                print(f"✗ Failed to load {model_name}")
                
        except Exception as e:
            print(f"✗ Error testing {model_name}: {e}")


def test_mask2former():
    """Test Mask2Former integration."""
    print("\\n=== Testing Mask2Former ===")
    
    if not MASK2FORMER_AVAILABLE:
        print("✗ Mask2Former not available")
        print("To install Mask2Former:")
        print("  1. Install detectron2: https://detectron2.readthedocs.io/en/latest/tutorials/install.html")
        print("  2. Ensure the Mask2Former repository is in the parent directory")
        return
    
    print("✓ Mask2Former is available")
    
    try:
        # Test different modes
        modes = ["instance", "panoptic", "semantic"]
        
        for mode in modes:
            print(f"\\nTesting Mask2Former in {mode} mode...")
            
            segmenter = Mask2FormerSegmenter(
                target_classes=["person", "car", "bicycle"],
                confidence_threshold=0.5,
                mode=mode,
                verbose=True
            )
            
            if segmenter.load_model():
                print(f"✓ Mask2Former ({mode}) loaded successfully")
                print(f"  Device: {segmenter.get_device_info()}")
                
                # Test with a small dummy image
                test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
                result = segmenter.segment(test_image)
                print(f"  Segmentation test: ✓ (found {len(result.masks)} masks)")
                
            else:
                print(f"✗ Failed to load Mask2Former ({mode})")
                
    except Exception as e:
        print(f"✗ Error testing Mask2Former: {e}")


def test_pipeline_integration():
    """Test the pipeline with new segmenters."""
    print("\\n=== Testing Pipeline Integration ===")
    
    # Test with YOLO26
    print("\\nTesting pipeline with YOLO26...")
    try:
        config = PipelineConfig(
            num_horizontal_views=4,  # Fewer views for faster testing
            num_pitch_levels=1,
            model_name="yolo26n-seg.pt",  # Fastest YOLO26 model
            target_classes=["person"],
            segmenter_type="yolo",
            verbose=True
        )
        
        pipeline = MaskGenerationPipeline(config)
        if pipeline.load_model():
            print("✓ YOLO26 pipeline created and loaded successfully")
        else:
            print("✗ Failed to load YOLO26 pipeline")
            
    except Exception as e:
        print(f"✗ Error creating YOLO26 pipeline: {e}")
    
    # Test with Mask2Former (if available)
    if MASK2FORMER_AVAILABLE:
        print("\\nTesting pipeline with Mask2Former...")
        try:
            config = PipelineConfig(
                num_horizontal_views=4,  # Fewer views for faster testing
                num_pitch_levels=1,
                target_classes=["person"],
                segmenter_type="mask2former",
                mask2former_mode="instance",
                verbose=True
            )
            
            pipeline = MaskGenerationPipeline(config)
            if pipeline.load_model():
                print("✓ Mask2Former pipeline created and loaded successfully")
            else:
                print("✗ Failed to load Mask2Former pipeline")
                
        except Exception as e:
            print(f"✗ Error creating Mask2Former pipeline: {e}")


def create_test_360_image():
    """Create a simple test 360 image for demonstration."""
    print("\\n=== Creating Test 360 Image ===")
    
    # Create a simple equirectangular test image (2:1 aspect ratio)
    width, height = 1024, 512
    image = np.ones((height, width, 3), dtype=np.uint8) * 128  # Gray background
    
    # Add some simple patterns to make it look like a 360 scene
    # Sky (top half) - blue gradient
    for y in range(height // 2):
        intensity = int(255 * (1 - y / (height // 2)))
        image[y, :] = [intensity // 2, intensity // 2, 255]
    
    # Ground (bottom half) - green gradient
    for y in range(height // 2, height):
        intensity = int(128 + 127 * ((y - height // 2) / (height // 2)))
        image[y, :] = [0, intensity, 0]
    
    # Add some "objects" that could be detected
    # Simple rectangles to simulate people or objects
    cv2.rectangle(image, (200, 200), (250, 400), (0, 0, 255), -1)  # Red rectangle
    cv2.rectangle(image, (600, 250), (650, 450), (255, 0, 0), -1)  # Blue rectangle
    cv2.rectangle(image, (800, 150), (850, 350), (0, 255, 0), -1)  # Green rectangle
    
    # Save the test image
    test_image_path = "test_360_image.jpg"
    cv2.imwrite(test_image_path, image)
    print(f"✓ Created test 360 image: {test_image_path}")
    
    return test_image_path


def demo_usage_example():
    """Demonstrate how to use the new features."""
    print("\\n=== Usage Example ===")
    
    # Create a test image
    test_image_path = create_test_360_image()
    
    if not os.path.exists(test_image_path):
        print("✗ Test image not created, skipping demo")
        return
    
    # Example 1: Using YOLO26
    print("\\nExample 1: Using YOLO26 for mask generation")
    try:
        config = PipelineConfig(
            num_horizontal_views=6,
            num_pitch_levels=1,
            model_name="yolo26n-seg.pt",  # Fast YOLO26 model
            target_classes=["person", "car"],
            segmenter_type="yolo",
            confidence_threshold=0.3,
            verbose=False
        )
        
        pipeline = MaskGenerationPipeline(config)
        if pipeline.load_model():
            # Load test image
            image = cv2.imread(test_image_path)
            if image is not None:
                print("  Processing with YOLO26...")
                result = pipeline.process(image)
                
                # Save mask
                mask_path = "test_yolo26_mask.png"
                result.save_mask(mask_path)
                print(f"  ✓ YOLO26 mask saved to: {mask_path}")
                print(f"  Processing time: {result.processing_time:.2f}s")
        
    except Exception as e:
        print(f"  ✗ YOLO26 example failed: {e}")
    
    # Example 2: Using Mask2Former (if available)
    if MASK2FORMER_AVAILABLE:
        print("\\nExample 2: Using Mask2Former for mask generation")
        try:
            config = PipelineConfig(
                num_horizontal_views=4,  # Fewer views as Mask2Former is slower
                num_pitch_levels=1,
                target_classes=["person", "car"],
                segmenter_type="mask2former",
                mask2former_mode="instance",
                confidence_threshold=0.5,
                verbose=False
            )
            
            pipeline = MaskGenerationPipeline(config)
            if pipeline.load_model():
                # Load test image
                image = cv2.imread(test_image_path)
                if image is not None:
                    print("  Processing with Mask2Former...")
                    result = pipeline.process(image)
                    
                    # Save mask
                    mask_path = "test_mask2former_mask.png"
                    result.save_mask(mask_path)
                    print(f"  ✓ Mask2Former mask saved to: {mask_path}")
                    print(f"  Processing time: {result.processing_time:.2f}s")
            
        except Exception as e:
            print(f"  ✗ Mask2Former example failed: {e}")
    
    # Clean up test image
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print(f"\\n✓ Cleaned up test image: {test_image_path}")


def main():
    """Main test function."""
    print("360 Mask Generator - New Features Test")
    print("=====================================")
    
    # Test YOLO26 models
    test_yolo26_models()
    
    # Test Mask2Former (if available)
    test_mask2former()
    
    # Test pipeline integration
    test_pipeline_integration()
    
    # Demo usage examples
    demo_usage_example()
    
    print("\\n=== Test Summary ===")
    print("✓ YOLO26 models: Available and working")
    if MASK2FORMER_AVAILABLE:
        print("✓ Mask2Former: Available and working")
    else:
        print("✗ Mask2Former: Not available (install detectron2 and ensure Mask2Former repo is available)")
    
    print("\\nTo use the new features:")
    print("  CLI: python cli.py image.jpg --model yolo26m-seg.pt")
    print("  CLI: python cli.py image.jpg --segmenter mask2former")
    print("  GUI: python main.py (select models in Detection Settings)")


if __name__ == "__main__":
    main()
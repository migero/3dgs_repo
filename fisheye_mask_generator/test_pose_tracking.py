#!/usr/bin/env python3
"""
Test script to demonstrate pose tracking across sequential frames.
This simulates processing front and back fisheye frames in sequence.
"""
import numpy as np
from core.pose_estimator import PoseEstimator


def simulate_frame_sequence():
    """
    Demonstrates how to use the PoseEstimator with temporal tracking
    for sequential frames (e.g., front fisheye, then back fisheye).
    """
    # Initialize pose estimator
    pe = PoseEstimator(model_name="yolov8n-pose.pt", verbose=True)
    
    # Load the model once
    if not pe.load_model():
        print("Failed to load pose model")
        return
    
    print("\n=== Processing Frame Sequence ===\n")
    
    # Simulate a sequence of frames
    # In your actual pipeline, these would be front fisheye, back fisheye, front, back, etc.
    frame_names = [
        "frame_001_front.jpg",
        "frame_001_back.jpg",
        "frame_002_front.jpg",
        "frame_002_back.jpg",
        "frame_003_front.jpg",
        "frame_003_back.jpg",
    ]
    
    for i, frame_name in enumerate(frame_names):
        print(f"\n--- Processing {frame_name} ---")
        
        # In real usage, load your actual frame:
        # frame = cv2.imread(frame_path)
        # For demo, create a dummy frame
        dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Process frame with tracking
        main_person = pe.estimate_with_tracking(
            dummy_frame,
            update_tracking=True,  # Update position for next frame
            search_radius=200.0    # Search within 200 pixels of last position
        )
        
        if main_person:
            print(f"✓ Main person detected and tracked")
            # Access keypoints if needed
            keypoints = main_person.get('keypoints')
            if keypoints is not None:
                print(f"  Found {len(keypoints)} keypoints")
        else:
            print(f"✗ No person detected in this frame")
            
        # Optional: Reset tracking at specific points
        # For example, reset between different video sequences:
        if frame_name == "frame_002_back.jpg":
            print("\n  [Resetting tracking - new sequence]")
            pe.reset_tracking()


def example_with_alternating_views():
    """
    Example showing how to handle front/back fisheye alternating pattern.
    """
    pe = PoseEstimator(model_name="yolov8n-pose.pt", verbose=True)
    pe.load_model()
    
    print("\n=== Alternating Front/Back Views ===\n")
    
    # Process pairs of front/back frames
    for frame_pair_idx in range(3):
        print(f"\n--- Frame Pair {frame_pair_idx + 1} ---")
        
        # Process front fisheye
        front_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        front_person = pe.estimate_with_tracking(front_frame, update_tracking=True)
        
        if front_person:
            print(f"Front: Main person tracked")
        else:
            print(f"Front: No person detected")
        
        # Process back fisheye (person likely in different position)
        # The tracker will search near the last position, or fall back to biggest if not found
        back_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        back_person = pe.estimate_with_tracking(back_frame, update_tracking=True)
        
        if back_person:
            print(f"Back: Main person tracked")
        else:
            print(f"Back: No person detected")


def example_manual_control():
    """
    Example showing manual control of tracking state.
    """
    pe = PoseEstimator(model_name="yolov8n-pose.pt", verbose=True)
    pe.load_model()
    
    print("\n=== Manual Tracking Control ===\n")
    
    # You can disable tracking temporarily
    pe.set_tracking_enabled(False)
    print("Tracking disabled - will always select biggest person")
    
    # Process some frames...
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    pe.estimate_with_tracking(frame)
    
    # Re-enable tracking
    pe.set_tracking_enabled(True)
    print("\nTracking re-enabled")
    
    # Reset tracking state
    pe.reset_tracking()
    print("Tracking state reset")


if __name__ == "__main__":
    print("Pose Tracking Examples")
    print("=" * 50)
    
    # Run examples
    simulate_frame_sequence()
    # example_with_alternating_views()
    # example_manual_control()
    
    print("\n" + "=" * 50)
    print("\nUsage in your pipeline:")
    print("1. Initialize PoseEstimator once")
    print("2. Call estimate_with_tracking() for each frame in sequence")
    print("3. The tracker will search near last position, or fall back to biggest")
    print("4. Use reset_tracking() between different video sequences")

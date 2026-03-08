"""
Pose Estimator
Uses Ultralytics YOLO pose models when available to extract keypoints.
Provides a thin wrapper around ultralytics YOLO pose outputs.
"""
from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from collections import deque


class PoseEstimator:
    def __init__(self, model_name: str = "yolov8n-pose.pt", device: Optional[str] = None, verbose: bool = False):
        self.model_name = model_name
        self.device = device
        self.verbose = verbose
        self.model = None
        self.active_device = None
        self.last_person_center: Optional[Tuple[float, float]] = None  # (x, y) of last detected main person
        self.tracking_enabled = True  # Enable temporal tracking across frames
        self.motion_history = deque(maxlen=10)  # Track recent motion distances
        self.adaptive_search = True  # Enable adaptive search radius

    def load_model(self) -> bool:
        try:
            from ultralytics import YOLO
            import torch
            self.model = YOLO(self.model_name)
            if self.device:
                device = self.device
            elif torch.cuda.is_available():
                device = 'cuda'
            else:
                device = 'cpu'
            self.model.to(device)
            self.active_device = device
            if self.verbose:
                print(f"Loaded pose model {self.model_name} on {device}")
            return True
        except Exception as e:
            print(f"PoseEstimator: could not load model {self.model_name}: {e}")
            return False

    def estimate(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run pose estimation on an image.
        Returns a list of poses; each pose is a dict with 'keypoints' (Nx3 array: x,y,conf)
        """
        if self.model is None:
            if not self.load_model():
                return []
        try:
            results = self.model(image, verbose=False)
            poses = []
            if len(results) == 0:
                return poses
            res = results[0]
            # ultralytics pose outputs may provide keypoints under res.keypoints or res.masks
            # Try common attributes
            kp_data = None
            if hasattr(res, 'keypoints') and res.keypoints is not None:
                try:
                    # res.keypoints.xy and res.keypoints.conf exist in some versions
                    kp = res.keypoints.xy if hasattr(res.keypoints, 'xy') else np.array(res.keypoints)
                    # Reshape to (N, num_kpts, 2) if necessary
                    if isinstance(kp, list):
                        kp = np.array(kp)
                    # Build poses
                    if kp.size == 0:
                        return []
                    # Ultralytics may provide per-instance keypoints
                    if kp.ndim == 3:
                        for inst in range(kp.shape[0]):
                            pts = kp[inst]
                            # no confidence available -> set to 1.0
                            confs = np.ones((pts.shape[0],))
                            kp_arr = np.concatenate([pts, confs[:, None]], axis=1)
                            poses.append({'keypoints': kp_arr})
                    elif kp.ndim == 2:
                        # single instance
                        pts = kp
                        confs = np.ones((pts.shape[0],))
                        kp_arr = np.concatenate([pts, confs[:, None]], axis=1)
                        poses.append({'keypoints': kp_arr})
                    return poses
                except Exception:
                    kp_data = None
            # Fallback: try parsing res.boxes or res.keypoints.data
            if hasattr(res, 'keypoints') and hasattr(res.keypoints, 'data'):
                try:
                    data = res.keypoints.data.cpu().numpy()
                    for inst in data:
                        poses.append({'keypoints': inst})
                    return poses
                except Exception:
                    pass
            return poses
        except Exception as e:
            print(f"PoseEstimator: inference error: {e}")
            return []

    def _compute_pose_center(self, pose: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """
        Compute the center point of a pose based on visible keypoints.
        Returns (x, y) or None if no valid keypoints found.
        """
        kps = pose.get('keypoints')
        if kps is None or len(kps) == 0:
            return None
        
        # Use keypoints with confidence > threshold
        valid_points = []
        for kp in kps:
            if len(kp) >= 3:
                x, y, conf = kp[0], kp[1], kp[2]
                if conf > 0.1:  # Confidence threshold
                    valid_points.append((x, y))
        
        if not valid_points:
            return None
        
        # Compute centroid of valid keypoints
        xs, ys = zip(*valid_points)
        center_x = np.mean(xs)
        center_y = np.mean(ys)
        return (float(center_x), float(center_y))

    def _compute_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Compute Euclidean distance between two points."""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def _calculate_adaptive_radius(self, base_radius: float = 200.0) -> float:
        """
        Calculate adaptive search radius based on recent motion patterns.
        
        Adjusts the search radius dynamically:
        - Fast motion (>50px/frame): Increase radius by 50%
        - Medium motion (10-50px): Use base radius
        - Minimal motion (<10px): Decrease radius by 30%
        
        Args:
            base_radius: Default search radius in pixels
            
        Returns:
            Adjusted search radius
        """
        if not self.adaptive_search or len(self.motion_history) < 2:
            return base_radius
        
        # Calculate average motion from recent frames
        recent_motion = list(self.motion_history)[-5:]  # Last 5 frames
        avg_motion = float(np.mean(recent_motion))
        
        # Adjust radius based on motion speed
        if avg_motion > 50:  # Fast motion
            adjusted_radius = base_radius * 1.5
            if self.verbose:
                print(f"PoseEstimator: Fast motion detected ({avg_motion:.1f}px), expanding search radius to {adjusted_radius:.0f}px")
        elif avg_motion < 10:  # Minimal motion (static or slow)
            adjusted_radius = base_radius * 0.7
            if self.verbose:
                print(f"PoseEstimator: Minimal motion ({avg_motion:.1f}px), reducing search radius to {adjusted_radius:.0f}px")
        else:  # Normal motion
            adjusted_radius = base_radius
        
        return adjusted_radius

    def _select_main_person(self, poses: List[Dict[str, Any]], search_radius: float = 200.0) -> Optional[Dict[str, Any]]:
        """
        Select the main person from detected poses using temporal tracking.
        
        If tracking is enabled and we have a last known position, search for the closest
        person within search_radius. Otherwise, select the person with most keypoints/confidence.
        
        Args:
            poses: List of detected poses
            search_radius: Maximum pixel distance to search from last position
            
        Returns:
            Selected pose dict or None if no valid poses
        """
        if not poses:
            return None
        
        # If tracking enabled and we have a previous center, find closest person
        if self.tracking_enabled and self.last_person_center is not None:
            best_pose = None
            best_distance = float('inf')
            
            for pose in poses:
                center = self._compute_pose_center(pose)
                if center is None:
                    continue
                
                distance = self._compute_distance(center, self.last_person_center)
                
                # Check if within search radius and closer than previous best
                if distance < search_radius and distance < best_distance:
                    best_pose = pose
                    best_distance = distance
            
            # If we found someone near the last position, use them
            if best_pose is not None:
                if self.verbose:
                    print(f"PoseEstimator: Tracked person at distance {best_distance:.1f}px from last position")
                return best_pose
            
            # Otherwise fall through to find biggest detection
            if self.verbose:
                print(f"PoseEstimator: Lost tracking (no person within {search_radius}px), falling back to biggest detection")
        
        # Fallback: Select person with most visible keypoints
        best_pose = None
        best_score = 0
        
        for pose in poses:
            kps = pose.get('keypoints')
            if kps is None:
                continue
            
            # Count visible keypoints and sum confidence
            visible_count = 0
            total_conf = 0.0
            for kp in kps:
                if len(kp) >= 3 and kp[2] > 0.1:
                    visible_count += 1
                    total_conf += kp[2]
            
            # Score based on number of visible keypoints and their confidence
            score = visible_count + (total_conf / max(1, len(kps)))
            
            if score > best_score:
                best_score = score
                best_pose = pose
        
        return best_pose

    def estimate_with_tracking(self, image: np.ndarray, update_tracking: bool = True, search_radius: float = 200.0) -> Optional[Dict[str, Any]]:
        """
        Run pose estimation with temporal tracking to select main person.
        
        Args:
            image: Input image
            update_tracking: If True, update the last known position with the selected person
            search_radius: Base search radius (will be adapted based on motion if adaptive_search=True)
            
        Returns:
            Dict with selected main person's pose, or None if no person detected
        """
        poses = self.estimate(image)
        
        if not poses:
            if self.verbose:
                print("PoseEstimator: No poses detected")
            return None
        
        # Calculate adaptive search radius
        adaptive_radius = self._calculate_adaptive_radius(search_radius)
        
        # Select main person using tracking
        main_pose = self._select_main_person(poses, adaptive_radius)
        
        # Update tracking position and motion history if requested
        if update_tracking and main_pose is not None:
            new_center = self._compute_pose_center(main_pose)
            if new_center is not None:
                # Record motion distance for adaptive radius
                if self.last_person_center is not None:
                    motion_distance = self._compute_distance(new_center, self.last_person_center)
                    self.motion_history.append(motion_distance)
                
                self.last_person_center = new_center
                if self.verbose:
                    print(f"PoseEstimator: Updated tracking center to ({new_center[0]:.1f}, {new_center[1]:.1f})")
        
        return main_pose

    def reset_tracking(self):
        """Reset the temporal tracking state."""
        self.last_person_center = None
        self.motion_history.clear()
        if self.verbose:
            print("PoseEstimator: Tracking reset")

    def set_tracking_enabled(self, enabled: bool):
        """Enable or disable temporal tracking."""
        self.tracking_enabled = enabled
        if self.verbose:
            print(f"PoseEstimator: Tracking {'enabled' if enabled else 'disabled'}")

    def set_adaptive_search(self, enabled: bool):
        """Enable or disable adaptive search radius."""
        self.adaptive_search = enabled
        if self.verbose:
            print(f"PoseEstimator: Adaptive search radius {'enabled' if enabled else 'disabled'}")
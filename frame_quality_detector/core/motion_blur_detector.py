#!/usr/bin/env python3
"""
Motion Blur Detection Algorithms

Implements algorithms for detecting motion blur in images:
- Frequency Domain Analysis
- Edge Sharpness Analysis
- Blur Kernel Estimation
- Spectral Analysis
"""

import numpy as np
import cv2
from typing import Dict, Tuple
from scipy import ndimage
from scipy.fft import fft2, fftshift


class MotionBlurDetector:
    """Detects motion blur in images using multiple algorithms."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def frequency_domain_blur(self, image: np.ndarray) -> float:
        """
        Detect blur using frequency domain analysis.
        
        Blurred images have less high-frequency content.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Blur score (0-1, higher = more blurred)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply FFT
        f_transform = fft2(gray)
        f_shift = fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        
        # Calculate center coordinates
        h, w = gray.shape
        center_x, center_y = w // 2, h // 2
        
        # Create masks for different frequency regions
        y, x = np.ogrid[:h, :w]
        radius = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_radius = min(h, w) // 2
        
        # Low frequency (center 20%)
        low_freq_mask = radius <= (max_radius * 0.2)
        # High frequency (outer 40%)
        high_freq_mask = radius >= (max_radius * 0.6)
        
        # Calculate energy in each region
        low_freq_energy = np.sum(magnitude_spectrum[low_freq_mask])
        high_freq_energy = np.sum(magnitude_spectrum[high_freq_mask])
        total_energy = np.sum(magnitude_spectrum)
        
        if total_energy == 0:
            return 1.0  # Maximum blur
        
        # Blur score based on frequency distribution
        low_freq_ratio = low_freq_energy / total_energy
        high_freq_ratio = high_freq_energy / total_energy
        
        # More blur = higher low freq ratio, lower high freq ratio
        blur_score = low_freq_ratio / (low_freq_ratio + high_freq_ratio + 1e-6)
        
        return min(blur_score * 2, 1.0)  # Amplify and cap at 1.0
    
    def edge_sharpness_analysis(self, image: np.ndarray) -> float:
        """
        Analyze edge sharpness to detect motion blur.
        
        Motion blur creates softer, wider edges.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Blur score (0-1, higher = more blurred)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Detect edges using Canny
        edges = cv2.Canny(gray, 50, 150)
        
        if np.sum(edges) == 0:
            return 1.0  # No edges detected = high blur
        
        # Calculate edge width by morphological operations
        kernel = np.ones((3, 3), np.uint8)
        
        # Dilate edges
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Calculate ratio of dilated to original edge pixels
        original_edge_pixels = np.sum(edges > 0)
        dilated_edge_pixels = np.sum(dilated > 0)
        
        if original_edge_pixels == 0:
            return 1.0
        
        # Edge spreading ratio (higher = more blur)
        edge_spread_ratio = dilated_edge_pixels / original_edge_pixels
        
        # Normalize and invert (we want blur score, not sharpness)
        blur_score = min((edge_spread_ratio - 1.0) / 2.0, 1.0)
        return max(blur_score, 0.0)
    
    def gradient_analysis(self, image: np.ndarray) -> float:
        """
        Analyze gradient characteristics to detect blur.
        
        Blurred images have weaker and more spread out gradients.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Blur score (0-1, higher = more blurred)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.astype(np.float32)
        
        # Calculate gradients
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = cv2.magnitude(grad_x, grad_y)
        
        # Calculate gradient statistics
        mean_magnitude = np.mean(magnitude)
        std_magnitude = np.std(magnitude)
        max_magnitude = np.max(magnitude)
        
        if max_magnitude == 0:
            return 1.0  # No gradients = maximum blur
        
        # Blur characteristics:
        # - Lower mean magnitude
        # - Lower standard deviation (less variation)
        # - Lower max magnitude
        
        # Normalize metrics
        mean_score = 1.0 - min(mean_magnitude / 50.0, 1.0)  # Assuming 50 is a good sharp image threshold
        std_score = 1.0 - min(std_magnitude / 30.0, 1.0)   # Assuming 30 is good variation threshold
        
        # Combine scores
        blur_score = (mean_score + std_score) / 2.0
        
        return blur_score
    
    def spectral_blur_detection(self, image: np.ndarray) -> float:
        """
        Detect blur using spectral analysis.
        
        Analyzes the power spectrum to identify blur characteristics.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Blur score (0-1, higher = more blurred)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply window function to reduce edge effects
        h, w = gray.shape
        window = np.outer(np.hanning(h), np.hanning(w))
        windowed = gray * window
        
        # Calculate power spectrum
        f_transform = fft2(windowed)
        power_spectrum = np.abs(f_transform) ** 2
        
        # Analyze spectral rolloff (frequency at which power drops significantly)
        # For 1D analysis, sum along one axis
        power_1d = np.sum(power_spectrum, axis=0)
        
        # Find spectral centroid (center of mass of spectrum)
        freqs = np.arange(len(power_1d))
        spectral_centroid = np.sum(freqs * power_1d) / (np.sum(power_1d) + 1e-6)
        
        # Normalize by Nyquist frequency
        normalized_centroid = spectral_centroid / (len(power_1d) / 2)
        
        # Lower centroid indicates more low-frequency content (more blur)
        blur_score = 1.0 - min(normalized_centroid * 2, 1.0)
        
        return max(blur_score, 0.0)
    
    def kernel_estimation_blur(self, image: np.ndarray) -> float:
        """
        Estimate motion blur by analyzing potential blur kernels.
        
        Attempts to estimate the characteristics of motion blur kernel.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Blur score (0-1, higher = more blurred)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Laplacian to enhance edges
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        
        # Calculate variance of Laplacian (sharp images have high variance)
        laplacian_var = np.var(laplacian)
        
        # Apply different directional filters to detect motion direction
        # Horizontal motion blur detection
        h_kernel = np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]], dtype=np.float32)
        h_response = cv2.filter2D(gray, cv2.CV_32F, h_kernel)
        h_energy = np.sum(h_response ** 2)
        
        # Vertical motion blur detection
        v_kernel = np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]], dtype=np.float32)
        v_response = cv2.filter2D(gray, cv2.CV_32F, v_kernel)
        v_energy = np.sum(v_response ** 2)
        
        # Diagonal motion blur detection
        d1_kernel = np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]], dtype=np.float32)
        d1_response = cv2.filter2D(gray, cv2.CV_32F, d1_kernel)
        d1_energy = np.sum(d1_response ** 2)
        
        d2_kernel = np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]], dtype=np.float32)
        d2_response = cv2.filter2D(gray, cv2.CV_32F, d2_kernel)
        d2_energy = np.sum(d2_response ** 2)
        
        # Total directional energy
        total_directional = h_energy + v_energy + d1_energy + d2_energy
        
        # Blur score based on low Laplacian variance and high directional response
        if laplacian_var > 0:
            # Normalize by image size
            normalized_var = laplacian_var / (gray.shape[0] * gray.shape[1])
            normalized_directional = total_directional / (gray.shape[0] * gray.shape[1])
            
            # Sharp images have high Laplacian variance, low directional response
            blur_score = normalized_directional / (normalized_var + normalized_directional + 1e-6)
            return min(blur_score, 1.0)
        
        return 1.0  # If no variance, assume maximum blur
    
    def analyze_motion_blur(self, image: np.ndarray) -> Dict[str, float]:
        """
        Analyze image for motion blur using all available methods.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Dictionary with all motion blur metrics
        """
        metrics = {
            'frequency_blur': self.frequency_domain_blur(image),
            'edge_blur': self.edge_sharpness_analysis(image),
            'gradient_blur': self.gradient_analysis(image),
            'spectral_blur': self.spectral_blur_detection(image),
            'kernel_blur': self.kernel_estimation_blur(image)
        }
        
        # Calculate combined blur score (weighted average)
        weights = {
            'frequency_blur': 0.3,
            'edge_blur': 0.25,
            'gradient_blur': 0.2,
            'spectral_blur': 0.15,
            'kernel_blur': 0.1
        }
        
        # Calculate weighted score
        combined_blur = sum(metrics[key] * weights[key] for key in weights)
        metrics['combined_blur'] = combined_blur * 100  # Scale to 0-100
        
        if self.verbose:
            print(f"Motion Blur Analysis:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value:.2f}")
        
        return metrics
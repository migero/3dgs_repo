#!/usr/bin/env python3
"""
Sharpness Detection Algorithms

Implements multiple algorithms for measuring image sharpness:
- Laplacian Variance
- Sobel Edge Detection
- Gradient Magnitude
- Tenengrad Focus Measure
"""

import numpy as np
import cv2
from typing import Dict, Tuple


class SharpnessDetector:
    """Detects and measures image sharpness using multiple algorithms."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def laplacian_variance(self, image: np.ndarray) -> float:
        """
        Calculate sharpness using Laplacian variance.
        
        The Laplacian operator calculates the second derivative of the image.
        Sharp images have higher variance in the Laplacian.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Laplacian variance score (higher = sharper)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calculate Laplacian
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        
        # Return variance
        return laplacian.var()
    
    def sobel_edge_magnitude(self, image: np.ndarray) -> float:
        """
        Calculate sharpness using Sobel edge detection.
        
        Measures the magnitude of gradients using Sobel operators.
        Sharp images have stronger edges.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Mean Sobel edge magnitude (higher = sharper)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calculate Sobel gradients
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate magnitude
        magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        return np.mean(magnitude)
    
    def gradient_magnitude(self, image: np.ndarray) -> float:
        """
        Calculate sharpness using gradient magnitude.
        
        Uses simple gradient calculation for edge detection.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Mean gradient magnitude (higher = sharper)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.astype(np.float32)
        
        # Calculate gradients
        grad_x = cv2.Scharr(gray, cv2.CV_32F, 1, 0)
        grad_y = cv2.Scharr(gray, cv2.CV_32F, 0, 1)
        
        # Calculate magnitude
        magnitude = cv2.magnitude(grad_x, grad_y)
        
        return np.mean(magnitude)
    
    def tenengrad_focus(self, image: np.ndarray) -> float:
        """
        Calculate focus measure using Tenengrad algorithm.
        
        Tenengrad uses the variance of the gradient magnitude.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Tenengrad focus measure (higher = sharper)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.astype(np.float32)
        
        # Calculate Sobel gradients
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate squared gradient magnitude
        magnitude_sq = sobel_x**2 + sobel_y**2
        
        # Apply threshold (optional - can help reduce noise)
        threshold = np.mean(magnitude_sq) * 0.1
        magnitude_sq[magnitude_sq < threshold] = 0
        
        return np.sum(magnitude_sq)
    
    def high_frequency_content(self, image: np.ndarray) -> float:
        """
        Calculate sharpness based on high frequency content.
        
        Uses FFT to analyze frequency domain and measure high frequency energy.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            High frequency content score (higher = sharper)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply FFT
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        
        # Calculate center coordinates
        h, w = gray.shape
        center_x, center_y = w // 2, h // 2
        
        # Create high-pass filter (remove low frequencies)
        y, x = np.ogrid[:h, :w]
        radius = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # High frequency mask (beyond 10% of max radius)
        high_freq_mask = radius > (min(h, w) * 0.1)
        
        # Calculate high frequency energy
        high_freq_energy = np.sum(magnitude_spectrum[high_freq_mask])
        total_energy = np.sum(magnitude_spectrum)
        
        return high_freq_energy / total_energy if total_energy > 0 else 0
    
    def analyze_sharpness(self, image: np.ndarray) -> Dict[str, float]:
        """
        Analyze image sharpness using all available methods.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Dictionary with all sharpness metrics
        """
        metrics = {
            'laplacian_variance': self.laplacian_variance(image),
            'sobel_magnitude': self.sobel_edge_magnitude(image),
            'gradient_magnitude': self.gradient_magnitude(image),
            'tenengrad_focus': self.tenengrad_focus(image),
            'high_frequency': self.high_frequency_content(image)
        }
        
        # Calculate combined score (weighted average)
        weights = {
            'laplacian_variance': 0.3,
            'sobel_magnitude': 0.2,
            'gradient_magnitude': 0.2,
            'tenengrad_focus': 0.2,
            'high_frequency': 0.1
        }
        
        # Normalize metrics to 0-1 range (approximate)
        normalized = {
            'laplacian_variance': min(metrics['laplacian_variance'] / 1000, 1.0),
            'sobel_magnitude': min(metrics['sobel_magnitude'] / 100, 1.0),
            'gradient_magnitude': min(metrics['gradient_magnitude'] / 50, 1.0),
            'tenengrad_focus': min(metrics['tenengrad_focus'] / 1000000, 1.0),
            'high_frequency': metrics['high_frequency']  # Already 0-1
        }
        
        # Calculate weighted score
        combined_score = sum(normalized[key] * weights[key] for key in weights)
        metrics['combined_sharpness'] = combined_score * 100  # Scale to 0-100
        
        if self.verbose:
            print(f"Sharpness Analysis:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value:.2f}")
        
        return metrics
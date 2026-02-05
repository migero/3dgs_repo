#!/usr/bin/env python3
"""
Video Mask Generator
Generates segmentation masks for moving objects (people, vehicles, etc.) in regular (non-360) videos.

Uses YOLO segmentation directly on video frames and saves the masks.
"""

import sys
import multiprocessing

# IMPORTANT: Set spawn method for CUDA compatibility with multiprocessing
# Must be done before any other imports that might trigger CUDA
if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)

from PyQt5.QtWidgets import QApplication
from ui.main_window import VideoMaskGeneratorWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Video Mask Generator")
    app.setOrganizationName("GoPro360Converter")
    
    # Set application style
    app.setStyle("Fusion")
    
    window = VideoMaskGeneratorWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

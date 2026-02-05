#!/usr/bin/env python3
"""
360 Mask Generator
Generates segmentation masks for moving objects (people, vehicles, etc.) in equirectangular 360 images.

Uses perspective projection to convert 360 images to multiple perspective views,
runs YOLO segmentation on each view, then projects masks back to equirectangular space.
"""

import sys
import multiprocessing

# IMPORTANT: Set spawn method for CUDA compatibility with multiprocessing
# Must be done before any other imports that might trigger CUDA
if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)

from PyQt5.QtWidgets import QApplication
from ui.main_window import MaskGeneratorWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("360 Mask Generator")
    app.setOrganizationName("GoPro360Converter")
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MaskGeneratorWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

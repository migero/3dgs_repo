#!/usr/bin/env python3
"""
Fisheye Mask Generator
Generates segmentation masks for moving objects (people, vehicles, etc.) in dual fisheye images (185° FOV).

Workflow:
1. Load front + back fisheye image pair (from max2sphere.py output)
2. Convert to equirectangular 360° format
3. Extract multiple perspective views
4. Run YOLO segmentation on each view
5. Project masks back to equirectangular
6. Convert masks back to fisheye format
7. Save as front_mask + back_mask
"""

import sys
import multiprocessing

# IMPORTANT: Set spawn method for CUDA compatibility with multiprocessing
# Must be done before any other imports that might trigger CUDA
if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)

from PyQt5.QtWidgets import QApplication
from ui.main_window import FisheyeMaskGeneratorWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Fisheye Mask Generator")
    app.setOrganizationName("GoPro360Converter")
    
    # Set application style
    app.setStyle("Fusion")
    
    window = FisheyeMaskGeneratorWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

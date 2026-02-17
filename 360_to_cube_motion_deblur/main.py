#!/usr/bin/env python3
"""
360 Motion Deblur
Applies motion deblurring to 360° equirectangular videos using PVDNet.

Converts equirectangular frames to cube faces, processes each face through PVDNet
for motion deblurring, then reconstructs back to equirectangular format.
"""

import sys
import multiprocessing

# IMPORTANT: Set spawn method for CUDA compatibility with multiprocessing
# Must be done before any other imports that might trigger CUDA
if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)

from PyQt5.QtWidgets import QApplication
from ui.main_window import MotionDeblurWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("360 Motion Deblur")
    app.setOrganizationName("GoPro360Converter")
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MotionDeblurWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

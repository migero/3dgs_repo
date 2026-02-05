#!/usr/bin/env python3
"""
Frame Quality Detector
Analyzes image frames to detect the sharpest, highest quality frames
with minimal motion blur.
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import FrameQualityMainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Frame Quality Detector")
    app.setOrganizationName("FrameQualityDetector")
    
    # Set application style
    app.setStyle("Fusion")
    
    window = FrameQualityMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
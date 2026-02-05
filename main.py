#!/usr/bin/env python3
"""
GoPro 360 Converter
A Qt5 application to convert GoPro .360 files to equirectangular MP4 videos.
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GoPro 360 Converter")
    app.setOrganizationName("GoPro360Converter")
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

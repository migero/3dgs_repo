#!/usr/bin/env python3
"""
360 Photo Geolocator - GUI launcher

Launch with: python run_gui.py
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import main

if __name__ == '__main__':
    main()

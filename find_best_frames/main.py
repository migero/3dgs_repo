#!/usr/bin/env python3

import sys
import argparse
from core.frame_analyzer import FrameAnalyzer


def cli_analyze(video_path: str, square_size: int = 256):
    print(f"Analyzing: {video_path}")
    print(f"Using {square_size}px crop squares")
    analyzer = FrameAnalyzer(square_size)
    
    info = analyzer.get_video_info(video_path)
    print(f"Video info: {info['width']}x{info['height']}, FPS={info['fps']:.2f}, Duration={info['duration']:.2f}s, Frames={info['total_frames']}")
    
    crops = analyzer.get_crop_positions()
    print(f"Crop positions: {len(crops)} squares at {crops}")
    
    def progress(pct, msg):
        print(f"[{pct:3d}%] {msg}")
    
    frames = analyzer.analyze_frames(video_path, progress)
    print(f"\nAnalyzed {len(frames)} frames")
    
    if frames:
        avg_sharpness = sum(f['sharpness'] for f in frames) / len(frames)
        print(f"Average sharpness: {avg_sharpness:.2f}")
        print(f"\nFirst 10 frames:")
        for f in frames[:10]:
            crops_str = " ".join(f"{b:.1f}" for b in f.get('crops_blur', []))
            print(f"  Frame {f['frame']:5d} @ {f['time']:6.2f}s - sharpness: {f['sharpness']:.2f} (crops: {crops_str})")


def gui_main():
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("Find Best Frames")
        app.setOrganizationName("FindBestFrames")
        app.setStyle("Fusion")
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec_())
    except ImportError as e:
        print(f"GUI dependencies not available: {e}")
        print("Install PyQt5 and matplotlib to use the GUI")
        sys.exit(1)
    except Exception as e:
        print(f"GUI failed to start: {e}")
        print("This might be due to no display available (headless environment)")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Find Best Frames - analyze video quality")
    parser.add_argument('--video', '-v', help='Video file path')
    parser.add_argument('--analyze', '-a', action='store_true', help='Run analysis in CLI mode')
    parser.add_argument('--size', '-s', type=int, default=256, choices=[64, 128, 256, 384, 512], 
                        help='Square crop size in pixels (default: 256)')
    
    args = parser.parse_args()
    
    if args.video and args.analyze:
        cli_analyze(args.video, args.size)
    else:
        gui_main()


if __name__ == "__main__":
    main()

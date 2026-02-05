#!/usr/bin/env python3
"""
GUI for Combined 360 Video Processing App

Graphical interface for the combined frame extraction, geolocation, and mask generation.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, 'frame_quality_detector')

# Import the processor
from combined_app import Combined360Processor


class Combined360GUI:
    """GUI for the combined 360 video processing app."""

    def __init__(self, root):
        self.root = root
        self.root.title("Combined 360 Video Processor")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        self.processor = Combined360Processor(verbose=True)

        # Variables
        self.video_path = tk.StringVar()
        self.kml_path = tk.StringVar()
        self.fps = tk.DoubleVar(value=1.0)

        # Mask settings
        self.mask_preset = tk.StringVar(value="default")
        self.mask_views = tk.IntVar(value=12)
        self.mask_pitch_levels = tk.IntVar(value=1)
        self.mask_model = tk.StringVar()
        self.mask_confidence = tk.DoubleVar(value=0.25)

        # Geolocation settings
        self.start_offset = tk.DoubleVar(value=0.0)
        self.end_offset = tk.DoubleVar(value=0.0)
        self.reverse_direction = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame, text="Combined 360 Video Processor",
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Input files section
        files_frame = tk.LabelFrame(main_frame, text="Input Files", padx=10, pady=10)
        files_frame.pack(fill=tk.X, pady=(0, 10))

        # Video file
        video_frame = tk.Frame(files_frame)
        video_frame.pack(fill=tk.X, pady=2)
        tk.Label(video_frame, text="Video File:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(video_frame, textvariable=self.video_path, width=50).pack(side=tk.LEFT, padx=(5, 5))
        tk.Button(video_frame, text="Browse", command=self.browse_video).pack(side=tk.LEFT)

        # KML file (optional)
        kml_frame = tk.Frame(files_frame)
        kml_frame.pack(fill=tk.X, pady=2)
        tk.Label(kml_frame, text="KML File:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(kml_frame, textvariable=self.kml_path, width=50).pack(side=tk.LEFT, padx=(5, 5))
        tk.Button(kml_frame, text="Browse", command=self.browse_kml).pack(side=tk.LEFT)
        tk.Button(kml_frame, text="Clear", command=lambda: self.kml_path.set("")).pack(side=tk.LEFT, padx=(5, 0))
        tk.Label(kml_frame, text="(optional)", font=("Arial", 8)).pack(side=tk.LEFT, padx=(5, 0))

        # Settings section
        settings_frame = tk.LabelFrame(main_frame, text="Processing Settings", padx=10, pady=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Frame extraction
        extract_frame = tk.LabelFrame(settings_frame, text="Frame Extraction", padx=5, pady=5)
        extract_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(extract_frame, text="Target FPS:", width=15, anchor="w").pack(side=tk.LEFT)
        tk.Spinbox(extract_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.fps, width=10).pack(side=tk.LEFT)

        # Mask generation
        mask_frame = tk.LabelFrame(settings_frame, text="Mask Generation", padx=5, pady=5)
        mask_frame.pack(fill=tk.X, pady=(0, 5))

        # Row 1: Preset and Views
        mask_row1 = tk.Frame(mask_frame)
        mask_row1.pack(fill=tk.X, pady=2)
        tk.Label(mask_row1, text="Preset:", width=10, anchor="w").pack(side=tk.LEFT)
        tk.OptionMenu(mask_row1, self.mask_preset, "default", "fast", "accurate").pack(side=tk.LEFT, padx=(5, 10))
        tk.Label(mask_row1, text="Views:", width=8, anchor="w").pack(side=tk.LEFT)
        tk.Spinbox(mask_row1, from_=1, to=36, textvariable=self.mask_views, width=5).pack(side=tk.LEFT, padx=(5, 10))
        tk.Label(mask_row1, text="Pitch Levels:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Spinbox(mask_row1, from_=1, to=5, textvariable=self.mask_pitch_levels, width=5).pack(side=tk.LEFT)

        # Row 2: Model and Confidence
        mask_row2 = tk.Frame(mask_frame)
        mask_row2.pack(fill=tk.X, pady=2)
        tk.Label(mask_row2, text="Model:", width=10, anchor="w").pack(side=tk.LEFT)
        tk.Entry(mask_row2, textvariable=self.mask_model, width=20).pack(side=tk.LEFT, padx=(5, 10))
        tk.Label(mask_row2, text="Confidence:", width=10, anchor="w").pack(side=tk.LEFT)
        tk.Spinbox(mask_row2, from_=0.01, to=1.0, increment=0.01, textvariable=self.mask_confidence, width=8).pack(side=tk.LEFT)

        # Geolocation (only shown if KML provided)
        self.geo_frame = tk.LabelFrame(settings_frame, text="Geolocation", padx=5, pady=5)
        self.update_geo_frame_visibility()

        geo_row1 = tk.Frame(self.geo_frame)
        geo_row1.pack(fill=tk.X, pady=2)
        tk.Label(geo_row1, text="Start Offset (m):", width=15, anchor="w").pack(side=tk.LEFT)
        tk.Spinbox(geo_row1, from_=0, to=1000, increment=10, textvariable=self.start_offset, width=10).pack(side=tk.LEFT, padx=(5, 10))
        tk.Label(geo_row1, text="End Offset (m):", width=15, anchor="w").pack(side=tk.LEFT)
        tk.Spinbox(geo_row1, from_=0, to=1000, increment=10, textvariable=self.end_offset, width=10).pack(side=tk.LEFT, padx=(5, 10))
        tk.Checkbutton(geo_row1, text="Reverse Direction", variable=self.reverse_direction).pack(side=tk.LEFT, padx=(10, 0))

        # Bind KML path changes to update geo frame
        self.kml_path.trace("w", lambda *args: self.update_geo_frame_visibility())

        # Control buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.run_button = tk.Button(button_frame, text="Run Processing", command=self.run_processing,
                                   bg="green", fg="white", font=("Arial", 12, "bold"))
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(button_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT)

        # Output section
        output_frame = tk.LabelFrame(main_frame, text="Output", padx=10, pady=10)
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def browse_video(self):
        """Browse for video file."""
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if filename:
            self.video_path.set(filename)

    def browse_kml(self):
        """Browse for KML file."""
        filename = filedialog.askopenfilename(
            title="Select KML File",
            filetypes=[("KML files", "*.kml"), ("All files", "*.*")]
        )
        if filename:
            self.kml_path.set(filename)

    def update_geo_frame_visibility(self):
        """Show/hide geolocation frame based on KML presence."""
        if self.kml_path.get().strip():
            self.geo_frame.pack(fill=tk.X, pady=(0, 5))
        else:
            self.geo_frame.pack_forget()

    def run_processing(self):
        """Run the processing in a separate thread."""
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video file")
            return

        # Disable run button
        self.run_button.config(state=tk.DISABLED, text="Processing...")

        # Clear output
        self.output_text.delete(1.0, tk.END)

        # Update status
        self.status_var.set("Processing...")

        # Run in thread
        thread = threading.Thread(target=self._run_processing_thread)
        thread.daemon = True
        thread.start()

    def _run_processing_thread(self):
        """Run processing in background thread."""
        try:
            # Redirect stdout to our text widget
            import io
            from contextlib import redirect_stdout

            output_buffer = io.StringIO()

            with redirect_stdout(output_buffer):
                print("DEBUG: Starting combined processing...")
                result_dir = self.processor.process_video(
                    self.video_path.get(),
                    self.kml_path.get() if self.kml_path.get().strip() else None,
                    self.fps.get(),
                    self.mask_preset.get(),
                    self.mask_views.get(),
                    self.mask_pitch_levels.get(),
                    self.mask_model.get() if self.mask_model.get().strip() else None,
                    self.mask_confidence.get(),
                    self.start_offset.get(),
                    self.end_offset.get(),
                    self.reverse_direction.get()
                )
                print(f"DEBUG: Combined processing completed. Result: {result_dir}")

            # Update GUI
            self.root.after(0, lambda: self._processing_complete(result_dir, output_buffer.getvalue()))

        except Exception as e:
            self.root.after(0, lambda: self._processing_error(str(e)))

    def _processing_complete(self, result_dir, output):
        """Handle successful processing completion."""
        self.output_text.insert(tk.END, output)
        self.output_text.insert(tk.END, f"\n✓ Processing completed successfully!\nResults saved to: {result_dir}")
        self.status_var.set("Completed")
        self.run_button.config(state=tk.NORMAL, text="Run Processing")

    def _processing_error(self, error):
        """Handle processing error."""
        self.output_text.insert(tk.END, f"\n✗ Error: {error}")
        self.status_var.set("Error")
        self.run_button.config(state=tk.NORMAL, text="Run Processing")
        messagebox.showerror("Processing Error", f"An error occurred:\n{error}")

    def clear_output(self):
        """Clear the output text."""
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Ready")


def main():
    root = tk.Tk()
    app = Combined360GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
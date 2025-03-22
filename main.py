import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import librosa
import librosa.display
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import soundfile as sf
import threading
import time  # For simulating loading time (remove in real app)
import os

class SilenceCutterApp:
    def __init__(self, root):
        self.root = root
        root.title("Professional Silence Cutter")
        self.root.minsize(800, 700) # Increased minimum height to accommodate new sliders

        # --- UI Elements Initialization ---
        self.create_ui_elements()
        self.filepath = None
        self.audio_data = None
        self.sample_rate = None
        self.silence_segments = []
        self.is_loading = False
        self.waveform_fig = None
        self.waveform_ax = None
        self.zoom_factor = 1.0  # Default zoom level
        self.scroll_position = 0.0 # Default scroll position in seconds
        self.total_duration = 0.0 # Total duration of loaded audio

    def create_ui_elements(self):
        # --- Style ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', padding=6, relief="flat", background="#e0e0e0", foreground="black")
        self.style.configure('TLabel', padding=6, foreground="black")
        self.style.configure('TEntry', padding=6)
        self.style.configure('TScale', background="#f0f0f0")
        self.style.configure('TFrame', background="#f0f0f0")

        # --- Main Frames ---
        main_frame = ttk.Frame(self.root, padding=10, style='TFrame')
        main_frame.pack(expand=True, fill="both")

        input_frame = ttk.Frame(main_frame, padding=10, style='TFrame')
        input_frame.pack(fill="x", pady=10)

        config_frame = ttk.Frame(main_frame, padding=10, style='TFrame')
        config_frame.pack(fill="x", pady=10)

        waveform_frame = ttk.Frame(main_frame, padding=10, style='TFrame')
        waveform_frame.pack(expand=True, fill="both", pady=10)

        zoom_scroll_frame = ttk.Frame(main_frame, padding=10, style='TFrame') # Frame for zoom and scroll sliders
        zoom_scroll_frame.pack(fill="x", pady=5)

        control_frame = ttk.Frame(main_frame, padding=10, style='TFrame')
        control_frame.pack(fill="x", pady=10)

        status_frame = ttk.Frame(main_frame, padding=5, style='TFrame', relief='groove', borderwidth=1)
        status_frame.pack(fill="x", side="bottom")

        # --- Input Frame ---
        ttk.Label(input_frame, text="Selected File:", style='TLabel').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.file_path_var = tk.StringVar()
        file_path_entry = ttk.Entry(input_frame, textvariable=self.file_path_var, state='readonly', width=60, style='TEntry')
        file_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        choose_button = ttk.Button(input_frame, text="Choose File", command=self.choose_file, style='TButton')
        choose_button.grid(row=0, column=2, padx=5, pady=5)
        input_frame.columnconfigure(1, weight=1)

        # --- Config Frame ---
        row_num = 0
        ttk.Label(config_frame, text="Noise Level Threshold:", style='TLabel').grid(row=row_num, column=0, padx=5, pady=5, sticky="w")
        self.noise_threshold_var = tk.DoubleVar(value=10.0)
        self.noise_threshold_scale = ttk.Scale(config_frame, from_=0, to=100, orient="horizontal", variable=self.noise_threshold_var, style='TScale')
        self.noise_threshold_scale.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        self.noise_threshold_spinbox = ttk.Spinbox(config_frame, from_=0, to=100, increment=1, textvariable=self.noise_threshold_var, width=5)
        self.noise_threshold_spinbox.grid(row=row_num, column=2, padx=5, pady=5, sticky="w")
        ttk.Label(config_frame, text="%", style='TLabel').grid(row=row_num, column=3, padx=0, pady=5, sticky="w")
        row_num += 1

        ttk.Label(config_frame, text="Min Silence Duration (ms):", style='TLabel').grid(row=row_num, column=0, padx=5, pady=5, sticky="w")
        self.min_silence_duration_var = tk.IntVar(value=200)
        ttk.Spinbox(config_frame, from_=10, to=5000, increment=10, textvariable=self.min_silence_duration_var, width=7).grid(row=row_num, column=1, padx=5, pady=5, sticky="w")
        row_num += 1

        ttk.Label(config_frame, text="Offset In (ms):", style='TLabel').grid(row=row_num, column=0, padx=5, pady=5, sticky="w")
        self.offset_in_var = tk.IntVar(value=20)
        self.offset_in_spinbox = ttk.Spinbox(config_frame, from_=0, to=1000, increment=1, textvariable=self.offset_in_var, width=7)
        self.offset_in_spinbox.grid(row=row_num, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(config_frame, text="Offset Out (ms):", style='TLabel').grid(row=row_num, column=2, padx=5, pady=5, sticky="w")
        self.offset_out_var = tk.IntVar(value=20)
        self.offset_out_spinbox = ttk.Spinbox(config_frame, from_=0, to=1000, increment=1, textvariable=self.offset_out_var, width=7)
        self.offset_out_spinbox.grid(row=row_num, column=3, padx=5, pady=5, sticky="w")
        row_num += 1

        self.lock_offsets_var = tk.BooleanVar(value=True)
        lock_offsets_check = ttk.Checkbutton(config_frame, text="Lock Offsets", variable=self.lock_offsets_var, command=self.toggle_lock_offsets)
        lock_offsets_check.grid(row=row_num, column=0, padx=5, pady=5, sticky="w")
        row_num += 1
        self.toggle_lock_offsets()

        config_frame.columnconfigure(1, weight=1)

        # --- Waveform Frame ---
        self.waveform_canvas = tk.Canvas(waveform_frame, bg="white", height=200, relief="groove", borderwidth=2)
        self.waveform_canvas.pack(expand=True, fill="both")
        self.gap_count_label_var = tk.StringVar(value="Detected Silence Gaps: 0")
        ttk.Label(waveform_frame, textvariable=self.gap_count_label_var, style='TLabel').pack(pady=5)

        # --- Zoom and Scroll Frame ---
        ttk.Label(zoom_scroll_frame, text="Zoom:", style='TLabel').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.zoom_slider_var = tk.DoubleVar(value=1.0) # Initial zoom level
        self.zoom_slider = ttk.Scale(zoom_scroll_frame, from_=1.0, to=20.0, orient="horizontal", variable=self.zoom_slider_var, command=self.update_zoom_scroll, style='TScale') # Zoom up to 20x
        self.zoom_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(zoom_scroll_frame, text="Scroll:", style='TLabel').grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.scroll_slider_var = tk.DoubleVar(value=0.0)
        self.scroll_slider = ttk.Scale(zoom_scroll_frame, from_=0.0, to=1.0, orient="horizontal", variable=self.scroll_slider_var, command=self.update_zoom_scroll, style='TScale') # Range 0-1, will be mapped to time
        self.scroll_slider.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        zoom_scroll_frame.columnconfigure(1, weight=1)
        zoom_scroll_frame.columnconfigure(3, weight=1)


        # --- Control Frame ---
        detect_button = ttk.Button(control_frame, text="Detect Silence", command=self.detect_silence_threaded, style='TButton')
        detect_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.save_button = ttk.Button(control_frame, text="Save Output As...", command=self.save_output_threaded, state=tk.DISABLED, style='TButton')
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)

        # --- Status Bar ---
        self.status_label_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_label_var, anchor="w", style='TLabel')
        status_label.pack(side="left", fill="x", expand=True)

        # --- Binding for Offset Lock ---
        self.offset_in_var.trace_add('write', self.sync_offset_out)

        # --- Make frames resizable ---
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1) # Waveform frame


    def choose_file(self):
        filetypes = (("Audio/Video files", "*.mp3 *.wav *.mp4 *.mkv *.avi *.flac"), ("All files", "*.*"))
        filepath = filedialog.askopenfilename(title="Choose an audio or video file", filetypes=filetypes)
        if filepath:
            self.filepath = filepath
            self.file_path_var.set(filepath)
            self.clear_waveform()
            self.load_audio_threaded()

    def load_audio_threaded(self):
        if self.is_loading:
            return
        self.is_loading = True
        self.update_status("Loading file...")
        self.save_button.config(state=tk.DISABLED)
        threading.Thread(target=self._load_audio_data).start()

    def _load_audio_data(self):
        try:
            time.sleep(0.1) # Simulate loading time - Remove this in real application
            self.audio_data, self.sample_rate = librosa.load(self.filepath)
            self.total_duration = librosa.get_duration(y=self.audio_data, sr=self.sample_rate)
            self.root.after(0, self._on_audio_loaded)
        except Exception as e:
            self.root.after(0, self._on_load_error, e)
        finally:
            self.is_loading = False

    def _on_audio_loaded(self):
        self.plot_waveform()
        self.update_status("File loaded successfully.")
        self.save_button.config(state=tk.NORMAL)
        self.update_scroll_range() # Update scroll slider range based on duration

    def _on_load_error(self, error):
        messagebox.showerror("Error Loading File", f"Could not load audio file.\nError: {error}")
        self.file_path_var.set("")
        self.filepath = None
        self.audio_data = None
        self.sample_rate = None
        self.clear_waveform()
        self.update_status("Error loading file.")

    def clear_waveform(self):
        self.waveform_canvas.delete("all")
        plt.clf()
        self.waveform_fig = None
        self.waveform_ax = None
        self.gap_count_label_var.set("Detected Silence Gaps: 0")
        self.silence_segments = []
        self.zoom_factor = 1.0 # Reset zoom
        self.scroll_position = 0.0 # Reset scroll
        self.zoom_slider_var.set(1.0)
        self.scroll_slider_var.set(0.0)
        self.update_scroll_range() # Reset scroll range

    def plot_waveform(self):
        self.waveform_canvas.delete("all")
        if self.audio_data is None:
            return

        fig, ax = plt.subplots(figsize=(8, 2), dpi=100)
        librosa.display.waveshow(self.audio_data, sr=self.sample_rate, ax=ax, color="#2b8cbe")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')

        self.waveform_fig = fig
        self.waveform_ax = ax
        self.update_waveform_display_with_zoom_scroll() # Apply initial zoom/scroll

        canvas = FigureCanvasTkAgg(fig, master=self.waveform_canvas)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas.draw()
        plt.close(fig) # Close the matplotlib figure to prevent display outside Tkinter

    def detect_silence_threaded(self):
        if self.audio_data is None:
            messagebox.showerror("Error", "Please choose an audio file first.")
            return
        self.update_status("Detecting silence...")
        threading.Thread(target=self._detect_silence).start()

    def _detect_silence(self):
        try:
            noise_threshold_percent = self.noise_threshold_var.get() / 100.0
            min_silence_duration_ms = self.min_silence_duration_var.get()
            offset_in_ms = self.offset_in_var.get()
            offset_out_ms = self.offset_out_var.get()

            frame_length = 2048
            hop_length = 512
            rms = librosa.feature.rms(y=self.audio_data, frame_length=frame_length, hop_length=hop_length)[0]
            silence_mask = rms < noise_threshold_percent * np.max(rms)

            silence_segments = []
            in_silence = False
            silence_start_frame = 0
            min_silence_frames = int(min_silence_duration_ms * self.sample_rate / hop_length / 1000)

            for i, is_silent in enumerate(silence_mask):
                if is_silent and not in_silence:
                    in_silence = True
                    silence_start_frame = i
                elif not is_silent and in_silence:
                    in_silence = False
                    silence_end_frame = i
                    if (silence_end_frame - silence_start_frame) >= min_silence_frames:
                        start_time = librosa.frames_to_time(silence_start_frame, sr=self.sample_rate, hop_length=hop_length)
                        end_time = librosa.frames_to_time(silence_end_frame, sr=self.sample_rate, hop_length=hop_length)

                        # Apply offsets in time domain directly for finer control
                        start_time += (offset_in_ms / 1000.0)
                        end_time -= (offset_out_ms / 1000.0)

                        # Ensure start_time is not negative and end_time is not before start_time
                        start_time = max(0, start_time)
                        end_time = max(start_time, end_time)

                        silence_segments.append((start_time, end_time))

            self.silence_segments = silence_segments
            self.root.after(0, self._on_silence_detected)

        except Exception as e:
            self.root.after(0, self._on_detection_error, e)
        finally:
            pass

    def _on_silence_detected(self):
        self.update_waveform_display_with_silence()
        self.gap_count_label_var.set(f"Detected Silence Gaps: {len(self.silence_segments)}")
        self.update_status("Silence detection complete.")

    def _on_detection_error(self, error):
        messagebox.showerror("Error Detecting Silence", f"Error during silence detection: {error}")
        self.update_status("Error during silence detection.")

    def update_waveform_display_with_silence(self):
        if self.waveform_ax is None:
            self.plot_waveform()
            return

        self.waveform_ax.clear()
        librosa.display.waveshow(self.audio_data, sr=self.sample_rate, ax=self.waveform_ax, color="#2b8cbe", alpha=0.7)

        for start, end in self.silence_segments:
            self.waveform_ax.axvspan(start, end, color='red', alpha=0.3)
            self.waveform_ax.axvline(x=start, color='red', linestyle='--', linewidth=0.8)
            self.waveform_ax.axvline(x=end, color='red', linestyle='--', linewidth=0.8)

        self.update_waveform_display_with_zoom_scroll() # Apply zoom and scroll after drawing silence

    def update_waveform_display_with_zoom_scroll(self, event=None): # event is optional for slider command
        if self.waveform_ax is None or self.audio_data is None:
            return

        current_zoom = self.zoom_slider_var.get()
        current_scroll_ratio = self.scroll_slider_var.get()

        display_duration = self.total_duration / current_zoom
        start_time = current_scroll_ratio * max(0, self.total_duration - display_duration) # Scroll as ratio of remaining duration
        end_time = start_time + display_duration

        self.waveform_ax.set_xlim(start_time, end_time)
        self.waveform_fig.canvas.draw_idle()

    def update_zoom_scroll(self, event=None): # Unified function for both sliders
        self.update_waveform_display_with_zoom_scroll(event)
        self.update_scroll_range() # Update scroll range in case zoom changed

    def update_scroll_range(self):
        if self.audio_data is None:
            self.scroll_slider.config(state=tk.DISABLED, from_=0, to_=1.0)
            return

        current_zoom = self.zoom_slider_var.get()
        display_duration = self.total_duration / current_zoom
        if display_duration >= self.total_duration: # No need to scroll if whole waveform is visible
            self.scroll_slider.config(state=tk.DISABLED, from_=0, to_=1.0)
            self.scroll_slider_var.set(0.0) # Reset scroll position
        else:
            self.scroll_slider.config(state=tk.NORMAL, from_=0.0, to_=1.0) # Range 0-1 ratio

    def save_output_threaded(self):
        if not self.silence_segments:
            messagebox.showinfo("Info", "No silence segments detected or no file loaded to process.")
            return
        if self.audio_data is None:
            messagebox.showerror("Error", "No audio data loaded to save.")
            return

        filetypes = (("WAV files", "*.wav"), ("MP3 files", "*.mp3"), ("All files", "*.*"))
        output_filepath = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=filetypes,
                                                    initialfile=os.path.splitext(os.path.basename(self.filepath))[0] + "_silence_cut")
        if output_filepath:
            self.update_status("Saving output...")
            threading.Thread(target=self._save_output, args=(output_filepath,)).start()

    def _save_output(self, output_filepath):
        try:
            segments_to_keep = []
            last_end_time = 0
            for start_time, end_time in self.silence_segments:
                segments_to_keep.append((last_end_time, start_time))
                last_end_time = end_time
            segments_to_keep.append((last_end_time, librosa.get_duration(y=self.audio_data, sr=self.sample_rate)))

            output_audio_segments = []
            for start, end in segments_to_keep:
                start_sample = int(start * self.sample_rate)
                end_sample = int(end * self.sample_rate)
                output_audio_segments.append(self.audio_data[start_sample:end_sample])

            output_audio = np.concatenate(output_audio_segments)

            sf.write(output_filepath, output_audio, self.sample_rate)
            self.root.after(0, self._on_save_complete, output_filepath)

        except Exception as e:
            self.root.after(0, self._on_save_error, e)

    def _on_save_complete(self, filepath):
        self.update_status(f"Output saved to: {filepath}")
        messagebox.showinfo("Save Complete", f"Audio saved to: {filepath}")

    def _on_save_error(self, error):
        messagebox.showerror("Error Saving File", f"Could not save output file.\nError: {error}")
        self.update_status("Error saving output.")

    def update_status(self, message):
        self.status_label_var.set(message)

    def toggle_lock_offsets(self):
        locked = self.lock_offsets_var.get()
        if locked:
            self.offset_out_spinbox.config(state=tk.DISABLED)
        else:
            self.offset_out_spinbox.config(state=tk.NORMAL)

    def sync_offset_out(self, *args):
        if self.lock_offsets_var.get():
            try:
                offset_in = int(self.offset_in_var.get())
                self.offset_out_var.set(offset_in)
            except ValueError:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    app = SilenceCutterApp(root)
    root.mainloop()
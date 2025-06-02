
# Silence Cutter

<div align="center">
<img src="https://github.com/user-attachments/assets/76d45cc5-603a-43da-9e97-e297273d9293" alt="UI Screenshot" width="500">
</div>

A Python-based desktop application with a Tkinter GUI to automatically detect and remove silent segments from audio and video files. It provides a visual waveform display with highlighted silences and allows users to customize detection parameters.

## Features

*   **Load Audio/Video Files:** Supports common audio (MP3, WAV, FLAC) and video (MP4, MKV, AVI) formats.
*   **Waveform Visualization:** Displays the audio waveform for visual analysis.
*   **Silence Detection:**
    *   **Adjustable Noise Level Threshold:** Define what's considered silence based on a percentage of the maximum RMS.
    *   **Adjustable Minimum Silence Duration:** Set the shortest duration (in milliseconds) that qualifies as a silence gap.
    *   **Configurable Offsets:** Add padding (in milliseconds) before (Offset In) and after (Offset Out) each detected silence segment to fine-tune cutting.
    *   **Lock Offsets:** Option to keep "Offset In" and "Offset Out" values synchronized.
*   **Visual Feedback:** Detected silence gaps are clearly marked on the waveform.
*   **Zoom and Scroll:**
    *   Zoom into the waveform for detailed inspection.
    *   Scroll through the waveform when zoomed in.
*   **Output Options:**
    *   Saves the processed file with silences removed.
    *   For video inputs, allows saving as a new video (MP4 with cut audio) or extracting the processed audio (MP3).
    *   For audio inputs, saves as processed audio (MP3).
*   **Progress and Status:** Provides real-time progress updates during loading, detection, and saving operations.
*   **User-Friendly Interface:** Intuitive GUI built with Tkinter.


## Prerequisites

*   **Python 3.12:** The application is written in Python.
*   **FFmpeg:** Required for audio/video processing, especially for cutting video segments and converting audio formats.
    *   Download and install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html).
    *   **Important:** Ensure FFmpeg is added to your system's PATH environment variable so it can be called from the command line.
*   **Python Libraries:** Listed in `requirements.txt`.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rudra-mondal/silence-cutter.git
    cd silence-cutter
    ```

2.  **Install FFmpeg:**
    Follow the instructions on the [FFmpeg website](https://ffmpeg.org/download.html) for your operating system.
    **Verify FFmpeg installation** by opening a terminal or command prompt and typing:
    ```bash
    ffmpeg -version
    ```
    You should see version information if it's installed correctly and in your PATH.

3.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    ```
    Activate the virtual environment:
    *   On Windows:
        ```bash
        .\.venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    python main.py
    ```

2.  **Choose a File:**
    *   Click the "Choose File" button.
    *   Select an audio (e.g., `.mp3`, `.wav`) or video (e.g., `.mp4`, `.mkv`) file.
    *   The waveform will be loaded and displayed.

3.  **Adjust Parameters (Optional):**
    *   **Noise Level Threshold (%):** Use the slider or spinbox to set the sensitivity for silence detection. A lower value detects quieter sounds as silence.
    *   **Min Silence Duration (ms):** Set the minimum length of a silent segment to be detected.
    *   **Offset In (ms) / Offset Out (ms):** Adjust these to add a small buffer before or after the detected silence. This can prevent cutting too close to speech.
    *   **Lock Offsets:** Check this box to make "Offset Out" automatically match "Offset In".

4.  **Detect Silence:**
    *   Click the "Detect Silence" button.
    *   The application will analyze the audio and highlight the detected silent segments in red on the waveform.
    *   The number of detected gaps will be displayed.

5.  **Review and Zoom/Scroll (Optional):**
    *   Use the "Zoom" slider to get a closer look at the waveform and the detected silences.
    *   Use the "Scroll" slider to move through the waveform when zoomed in.

6.  **Save Output:**
    *   Click the "Save Output As..." button (this button is enabled after a file is loaded).
    *   Choose a location and filename for the output.
        *   If the input was a video, you can choose to save as `.mp4` (video with cut audio) or `.mp3` (audio only).
        *   If the input was audio, the default output is `.mp3`.
    *   The application will process the file and save the version with silences removed. Progress will be displayed.
    *   A confirmation message will appear upon completion.



## Contributing

Contributions are welcome! If you have suggestions for improvements or find any bugs, please feel free to:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature` or `bugfix/YourBugfix`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/YourFeature`).
6.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Auto Youtube Shorts V1

This repository contains **Auto Youtube Shorts V1**, an automated pipeline developed before the widespread availability of high-fidelity, general-purpose AI video generators (like Sora, Runway, WAN...).

**It is a demonstration of pure backend engineering and system orchestration skills.**

While current workflow (V2) uses generative AI for the visuals, **V1 solved the automation problem using a complex system of chained APIs and media manipulation tools.**

---

## 🚀 The Evolution

| Feature | Auto Youtube Shorts V1 (This Repo) | AutoShorts v2 (New Workflow) |
| :--- | :--- | :--- |
| **Video Source** | 🎞️ Pexels API (Stock Footage) | ✨ Generative AI (WAN) |
| **Editor** | 🎬 FFmpeg/MoviePy (Code-based stitching) | 🤖 AI Director (Prompt-driven editing) |
| **Audio** | 🗣️ Kokoro/Local TTS | 🎤 Professional AI Voiceover API |
| **Subtitle Alignment**| ⏱️ WhisperX (Local Model) | 🔗 API-integrated alignment |
| **Narrative** | **Focuses on system design and API integration.** | **Focuses on creative prompting and AI control.** |

**>>> Check out the cutting-edge workflow here: [COMING SOON] <<<**

---

## 🛠 V1 Workflow: How it Works

The V1 pipeline executes a series of sequential scripts, acting as a fully automated media production line. It successfully generates a complete, ready-to-upload YouTube Short (9:16 vertical video) from a single topic prompt.

1.  **📜 Content Generation (`src/content.py`):**
    * An **Ollama** LLM (Llama 3.2) is queried to generate a unique, short-form video script based on topics defined in `config/topics.txt`.
    * The title is checked against the tracking file to ensure uniqueness.

2.  **🔊 Audio Synthesis (`src/audio_engine.py`):**
    * The generated script is fed into the **Kokoro TTS** engine to create a high-quality `.wav` voiceover file.

3.  **🎞️ Visual Procurement (`src/visual_finder.py`):**
    * The system calculates the required video duration based on the audio length.
    * Keywords are extracted, and the **Pexels API** is used to download multiple 9:16 (vertical) stock video clips.
    * The clips are programmatically merged and trimmed to match the audio duration.

4.  **📄 Subtitle Alignment (`src/subtitles.py`):**
    * The raw audio is analyzed by **WhisperX** (running in a dedicated VENV) to generate accurate, word-level timestamps.
    * These timestamps are converted into an **.ass** subtitle file for stylized rendering.

5.  **🎬 Final Assembly (`src/editor.py`):**
    * **FFmpeg** is called via the command line to bind the raw video, the audio track, and the stylized subtitles into a single, high-quality `.mp4` file.

6.  **📤 Deployment (`src/uploader.py`):**
    * The final video is uploaded to YouTube using the **YouTube Data API v3** with auto-generated title and metadata.

---

## ⚙️ Setup & Requirements

This project is best run within a virtual environment.

### Prerequisites

* **Python 3.10+**
* **FFmpeg:** Must be installed and available in your system's PATH.
* **Ollama:** Must be running locally (e.g., `ollama run llama3.2`).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourUsername/AutoShorts-v1.git](https://github.com/YourUsername/AutoShorts-v1.git)
    cd AutoShorts-v1
    ```
2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration (The `.env` and `config/` folders)

1.  **Secrets:** Create a file named `.env` in the root directory and add your Pexels key:
    ```ini
    PEXELS_API_KEY="YOUR_PEXELS_API_KEY_HERE"
    ```
2.  **YouTube API:** Place your OAuth 2.0 `client_secrets.json` file inside the `config/` directory.
3.  **VENV Path:** Update the `venv_python` path placeholder inside `src/subtitles.py` to point to the Python executable of your WhisperX virtual environment.

### Execution

Run the main pipeline orchestrator from the root directory:

```bash
python main.py
import os
import soundfile as sf
import numpy as np
from datetime import datetime
from kokoro import KPipeline
from src.utils import load_tracking_data, save_tracking_data, get_base_dir, get_latest_video_data

def generate_audio():
    base_dir = get_base_dir()
    voice_dir = os.path.join(base_dir, "voices")
    
    os.environ["HF_HOME"] = voice_dir
    os.environ["TRANSFORMERS_CACHE"] = voice_dir
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    title, data = get_latest_video_data()
    if not title:
        return

    script_path = os.path.join(base_dir, data["script"])
    if not os.path.exists(script_path):
        return

    with open(script_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = os.path.join(base_dir, "assets", "audio", f"{title}_{timestamp}.wav")
    os.makedirs(os.path.dirname(audio_filename), exist_ok=True)

    try:
        pipeline = KPipeline(lang_code="a") 
        generator = pipeline(text, voice="af_heart", speed=0.9, split_pattern=r'\n+')
        
        all_audio = []
        for _, _, audio in generator:
            all_audio.append(audio)

        if all_audio:
            full_audio = np.concatenate(all_audio)
            sf.write(audio_filename, full_audio, 24000)
            
            tracking_data = load_tracking_data()
            tracking_data[title]["audio"] = os.path.relpath(audio_filename, base_dir)
            save_tracking_data(tracking_data)
            print(f"Audio generated: {audio_filename}")

    except Exception as e:
        print(f"Audio generation failed: {e}")
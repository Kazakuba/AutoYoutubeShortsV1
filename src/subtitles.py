import os
import subprocess
from src.utils import get_base_dir

def generate_subs():
    base_dir = get_base_dir()
    
    venv_python = "path/to/your/whisperx_venv/python" 
    script_path = os.path.join(base_dir, "src", "internal_subs_script.py")

    if not os.path.exists(script_path):
        create_internal_script(script_path)

    cmd = f'"{venv_python}" "{script_path}"'
    subprocess.run(cmd, shell=True)

def create_internal_script(path):
    content = """
import os
import json
import whisperx
import gc
import torch
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACK_FILE = os.path.join(BASE_DIR, "assets", "videos_generated.json")

with open(TRACK_FILE, "r") as f:
    data = json.load(f)

latest = list(data.keys())[-1]
audio_file = os.path.join(BASE_DIR, data[latest]["audio"])

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisperx.load_model("large-v2", device, compute_type="float16" if device=="cuda" else "int8")
audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=16)

model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
aligned_result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
sub_file = os.path.join(BASE_DIR, "assets", "subs", f"{latest}_{timestamp}.ass")
os.makedirs(os.path.dirname(sub_file), exist_ok=True)

header = \"\"\"[Script Info]
Title: AutoSubs
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,Bebas Neue,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&HC0000000,0,0,0,0,100,100,0,0,3,2,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
\"\"\"

with open(sub_file, "w", encoding="utf-8") as f:
    f.write(header)
    for seg in aligned_result["segments"]:
        if "words" in seg:
            for w in seg["words"]:
                start = w.get("start", 0)
                end = w.get("end", start + 0.5)
                text = re.sub(r"[!?.,]", "", w.get("word", "").strip())
                
                s_fmt = f"{int(start//3600)}:{int((start%3600)//60)}:{start%60:.2f}"
                e_fmt = f"{int(end//3600)}:{int((end%3600)//60)}:{end%60:.2f}"
                
                if text:
                    f.write(f"Dialogue: 0,{s_fmt},{e_fmt},Default,,0,0,0,,{text}\\n")

data[latest]["subtitles"] = os.path.relpath(sub_file, BASE_DIR)
with open(TRACK_FILE, "w") as f:
    json.dump(data, f, indent=4)
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
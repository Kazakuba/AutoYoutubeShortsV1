import os
import re
from datetime import datetime
from src.utils import load_tracking_data, save_tracking_data, get_base_dir, get_latest_video_data

def merge_video():
    base_dir = get_base_dir()
    title, data = get_latest_video_data()

    if not title:
        return

    video = os.path.join(base_dir, data["video"])
    audio = os.path.join(base_dir, data["audio"])
    subs = data.get("subtitles", "")
    
    if subs:
        subs = os.path.join(base_dir, subs)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = os.path.join(base_dir, "assets", "final", f"{title}_{timestamp}.mp4")
    os.makedirs(os.path.dirname(output), exist_ok=True)

    video_ff = video.replace("\\", "/")
    audio_ff = audio.replace("\\", "/")
    subs_ff = subs.replace("\\", "/")
    output_ff = output.replace("\\", "/")

    if subs_ff:
        subs_ff = re.sub(r'^([A-Za-z]):/', r'\1\\:/', subs_ff)
        filter_str = (
            f"subtitles=filename='{subs_ff}':charenc=UTF-8"
            f":original_size=1080x1920:force_style="
            f"'Alignment=2,MarginV=40,MarginL=30,MarginR=30,FontSize=13,"
            f"Outline=1,OutlineColour=&H000000&,PrimaryColour=&HFFFFFF&,Spacing=0'"
        )
        cmd = (
            f'ffmpeg -y -i "{video_ff}" -i "{audio_ff}" '
            f'-map 0:v:0 -map 1:a:0 -c:v libx264 -crf 23 '
            f'-c:a aac -b:a 192k -strict experimental '
            f'-vf "{filter_str}" -shortest "{output_ff}"'
        )
    else:
        cmd = (
            f'ffmpeg -y -i "{video_ff}" -i "{audio_ff}" '
            f'-map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k '
            f'-strict experimental -shortest "{output_ff}"'
        )

    os.system(cmd)

    data = load_tracking_data()
    data[title]["final_video"] = os.path.relpath(output, base_dir)
    save_tracking_data(data)
    print(f"Final video created: {output}")
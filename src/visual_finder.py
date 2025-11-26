import requests
import os
import random
import subprocess
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips
from dotenv import load_dotenv
from src.utils import load_tracking_data, save_tracking_data, get_base_dir, get_latest_video_data

def get_audio_duration(audio_file):
    cmd = f'ffprobe -i "{audio_file}" -show_entries format=duration -v quiet -of csv="p=0"'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return float(result.stdout.strip())
    except Exception:
        return 0.0

def fetch_videos():
    load_dotenv()
    api_key = os.getenv("PEXELS_API_KEY", "YOUR_PEXELS_API_KEY_HERE")
    
    base_dir = get_base_dir()
    title, data = get_latest_video_data()
    
    if not title:
        return

    audio_path = os.path.join(base_dir, data["audio"])
    audio_duration = get_audio_duration(audio_path)
    
    keywords_file = os.path.join(base_dir, "config", "search_keywords.txt")
    if os.path.exists(keywords_file):
        with open(keywords_file, "r") as f:
            keywords = [line.strip() for line in f if line.strip()]
    else:
        keywords = ["Technology"]

    tracking_data = load_tracking_data()
    used_urls = set()
    for v in tracking_data.values():
        if "video_urls" in v:
            used_urls.update(v["video_urls"])

    video_min = int(audio_duration)
    video_max = int(audio_duration) + 20
    portrait_videos = []
    
    max_retries = 5
    for _ in range(max_retries):
        search_term = random.choice(keywords)
        headers = {"Authorization": api_key}
        params = {
            "query": search_term, 
            "min_duration": video_min, 
            "max_duration": video_max, 
            "per_page": 15
        }
        
        response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
        if response.status_code != 200:
            continue

        videos = response.json().get("videos", [])
        
        for vid in videos:
            best_file = None
            best_quality = 0
            for vf in vid.get("video_files", []):
                w, h = vf.get("width", 0), vf.get("height", 0)
                if w < h and (h/w) >= 1.7 and w >= 720:
                    score = w * h
                    if score > best_quality:
                        best_quality = score
                        best_file = vf
            
            if best_file and best_file["link"] not in used_urls:
                portrait_videos.append((vid, best_file))
        
        if portrait_videos:
            break

    if not portrait_videos:
        print("No videos found.")
        return

    video_files = []
    downloaded_urls = []
    current_duration = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for idx, (vid_meta, best_file) in enumerate(portrait_videos):
        if current_duration >= audio_duration:
            break
        
        url = best_file["link"]
        fname = os.path.join(base_dir, "assets", "videos", f"{title}_{timestamp}_{idx}.mp4")
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        
        with open(fname, "wb") as f:
            f.write(requests.get(url).content)
        
        video_files.append(fname)
        downloaded_urls.append(url)
        current_duration += vid_meta["duration"]

    if len(video_files) > 1:
        clips = [VideoFileClip(v) for v in video_files]
        final_clip = concatenate_videoclips(clips, method="compose")
    else:
        final_clip = VideoFileClip(video_files[0])

    if final_clip.duration > audio_duration:
        final_clip = final_clip.subclip(0, audio_duration)

    final_video_path = os.path.join(base_dir, "assets", "videos", f"{title}_{timestamp}_raw.mp4")
    final_clip.write_videofile(final_video_path, codec="libx264", fps=24, logger=None)

    tracking_data[title]["video"] = os.path.relpath(final_video_path, base_dir)
    tracking_data[title]["video_urls"] = downloaded_urls
    save_tracking_data(tracking_data)
    print(f"Raw video saved: {final_video_path}")
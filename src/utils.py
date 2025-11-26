import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACK_FILE = os.path.join(BASE_DIR, "assets", "videos_generated.json")

def get_base_dir():
    return BASE_DIR

def load_tracking_data():
    if os.path.exists(TRACK_FILE) and os.path.getsize(TRACK_FILE) > 0:
        with open(TRACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tracking_data(data):
    with open(TRACK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_latest_video_data():
    data = load_tracking_data()
    if not data:
        return None, None
    latest_title = list(data.keys())[-1]
    return latest_title, data[latest_title]
import ollama
import os
import time
import random
import re
from datetime import datetime
from src.utils import load_tracking_data, save_tracking_data, get_base_dir

def sanitize_title(title):
    return re.sub(r'[<>:"/\\|?*\']', '', title).replace(" ", "_")

def generate_script():
    base_dir = get_base_dir()
    topics_file = os.path.join(base_dir, "config", "topics.txt")
    
    if os.path.exists(topics_file):
        with open(topics_file, "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip()]
    else:
        topics = ["The Future of AI"]

    topic = random.choice(topics)
    print(f"Target Topic: {topic}")

    generated_videos = load_tracking_data()
    existing_titles = set(generated_videos.keys())

    duration = 13
    words_per_min = 130
    target_word_count = round((duration / 60) * words_per_min)
    min_word_count = int(target_word_count * 0.85)
    max_word_count = target_word_count

    max_attempts = 5
    attempt = 0
    unique_title = None
    script_text = None

    while attempt < max_attempts:
        prompt = f"""
        Generate a unique and engaging video script on the topic: "{topic}".
        The script must be between {min_word_count} and {max_word_count} words.
        Output format:
        Line 1: Unique Title
        Line 2+: Script body
        No markdown, no scene descriptions.
        Existing titles to avoid: {", ".join(existing_titles)}
        """

        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
        response_text = response.message.content.strip()

        if "\n" not in response_text:
            attempt += 1
            time.sleep(1)
            continue

        title, script_text = response_text.split("\n", 1)
        title_clean = sanitize_title(title)
        script_text = "\n".join([line.strip() for line in script_text.split("\n") if line.strip()])
        num_words = len(script_text.split())

        if num_words < min_word_count or num_words > max_word_count:
            attempt += 1
            continue

        if title_clean in existing_titles:
            attempt += 1
            continue

        unique_title = title_clean
        break

    if unique_title is None:
        unique_title = f"{sanitize_title(topic)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_filename = os.path.join(base_dir, "assets", "scripts", f"{unique_title}_{timestamp}.txt")
    os.makedirs(os.path.dirname(script_filename), exist_ok=True)

    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(script_text)

    generated_videos[unique_title] = {
        "topic": topic,
        "script": os.path.relpath(script_filename, base_dir),
        "timestamp": timestamp
    }
    save_tracking_data(generated_videos)
    print(f"Script saved: {script_filename}")
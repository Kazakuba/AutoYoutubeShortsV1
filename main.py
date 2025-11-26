import os
import sys
from src import content, audio_engine, visual_finder, subtitles, editor, uploader

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("\n🚀 Starting Pipeline...")

    print("\n📜 Generating Script...")
    content.generate_script()

    print("\n🔊 Generating Audio...")
    audio_engine.generate_audio()

    print("\n🎞️ Fetching Visuals...")
    visual_finder.fetch_videos()

    print("\n📄 Generating Subtitles...")
    subtitles.generate_subs()

    print("\n🎬 Merging Video...")
    editor.merge_video()

    print("\n📤 Uploading...")
    uploader.upload_video()

    print("\n✅ Done!")

if __name__ == "__main__":
    main()
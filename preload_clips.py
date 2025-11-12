"""
LEGACY: Original streaming-based clip downloader (slow, may timeout).
Prefer preload_clips_direct.py for faster, more reliable downloads.
Run: python preload_clips.py (~1-2 minutes for 5 clips, may timeout)
"""
import os
import json
from src.stream_sampler import stream_random_clips

CLIPS_DIR = "sample_clips"
NUM_CLIPS = 5

def preload_clips():
    """Download and save sample clips locally."""
    os.makedirs(CLIPS_DIR, exist_ok=True)

    print(f"Downloading {NUM_CLIPS} random clips from HuggingFace...")
    print("This will take 1-2 minutes (only need to run once)")

    clips = stream_random_clips(NUM_CLIPS)

    for i, clip in enumerate(clips):
        # Save video file
        video_path = os.path.join(CLIPS_DIR, f"clip_{i:02d}.mp4")
        with open(video_path, "wb") as f:
            f.write(clip['mp4'])

        # Save metadata
        metadata_path = os.path.join(CLIPS_DIR, f"clip_{i:02d}.json")
        with open(metadata_path, "w") as f:
            json.dump(clip['json'], f, indent=2)

        print(f"  ✓ Saved clip {i+1}/{NUM_CLIPS}: Worker {clip['json']['worker_id']}, Factory {clip['json']['factory_id']}")

    print(f"\n✓ Done! {NUM_CLIPS} clips saved to {CLIPS_DIR}/")
    print("Now run: streamlit run app.py")

if __name__ == "__main__":
    preload_clips()

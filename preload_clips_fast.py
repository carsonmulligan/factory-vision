"""
Fast alternative to preload_clips.py that uses HuggingFace API directly.
Run once: python preload_clips_fast.py
"""
import os
import json
import requests
from src.config import HF_TOKEN

CLIPS_DIR = "sample_clips"
NUM_CLIPS = 10

def preload_clips_fast():
    """Download sample clips using HuggingFace dataset viewer API."""
    os.makedirs(CLIPS_DIR, exist_ok=True)

    print(f"Downloading {NUM_CLIPS} clips from HuggingFace (fast method)...")
    print("This should take <30 seconds")

    # Use HuggingFace dataset viewer API to get first N rows
    url = f"https://datasets-server.huggingface.co/rows"
    params = {
        "dataset": "builddotai/Egocentric-10K",
        "config": "default",
        "split": "train",
        "offset": 0,
        "length": NUM_CLIPS
    }
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        print("\nFalling back to streaming method...")
        # Fall back to original method
        from src.stream_sampler import stream_random_clips
        clips = stream_random_clips(NUM_CLIPS)
        save_clips(clips)
        return

    data = response.json()
    rows = data.get("rows", [])

    if not rows:
        print("No rows returned. Falling back to streaming method...")
        from src.stream_sampler import stream_random_clips
        clips = stream_random_clips(NUM_CLIPS)
        save_clips(clips)
        return

    for i, row in enumerate(rows[:NUM_CLIPS]):
        try:
            # Extract data from API response
            mp4_data = row['row']['mp4']['bytes']
            metadata = row['row']['json']

            # Save video file
            video_path = os.path.join(CLIPS_DIR, f"clip_{i:02d}.mp4")
            with open(video_path, "wb") as f:
                f.write(bytes(mp4_data))

            # Save metadata
            metadata_path = os.path.join(CLIPS_DIR, f"clip_{i:02d}.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            print(f"  ✓ Saved clip {i+1}/{NUM_CLIPS}: Worker {metadata['worker_id']}, Factory {metadata['factory_id']}")
        except Exception as e:
            print(f"  ✗ Failed clip {i+1}: {e}")

    print(f"\n✓ Done! {NUM_CLIPS} clips saved to {CLIPS_DIR}/")
    print("Now run: streamlit run app.py")

def save_clips(clips):
    """Helper to save clips from streaming method."""
    for i, clip in enumerate(clips):
        video_path = os.path.join(CLIPS_DIR, f"clip_{i:02d}.mp4")
        with open(video_path, "wb") as f:
            f.write(clip['mp4'])

        metadata_path = os.path.join(CLIPS_DIR, f"clip_{i:02d}.json")
        with open(metadata_path, "w") as f:
            json.dump(clip['json'], f, indent=2)

        print(f"  ✓ Saved clip {i+1}/{NUM_CLIPS}: Worker {clip['json']['worker_id']}, Factory {clip['json']['factory_id']}")

    print(f"\n✓ Done! {NUM_CLIPS} clips saved to {CLIPS_DIR}/")
    print("Now run: streamlit run app.py")

if __name__ == "__main__":
    preload_clips_fast()

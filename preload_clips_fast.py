"""
Alternative clip downloader that tries HF dataset viewer API, falls back to streaming.
Prefer preload_clips_direct.py which is faster and more reliable.
Run: python preload_clips_fast.py (~1-2 minutes for 5 clips)
"""
import os
import json
import requests
from src.config import HF_TOKEN

CLIPS_DIR = "sample_clips"
NUM_CLIPS = 5

def preload_clips_fast():
    """Download sample clips using HuggingFace dataset viewer API."""
    os.makedirs(CLIPS_DIR, exist_ok=True)

    print(f"Downloading {NUM_CLIPS} clips from HuggingFace (fast method)...")
    print("Trying dataset viewer API first...")

    # Try /first-rows endpoint (better for WebDataset format)
    url = "https://datasets-server.huggingface.co/first-rows"
    params = {
        "dataset": "builddotai/Egocentric-10K",
        "config": "default",
        "split": "train"
    }
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            rows = data.get("rows", [])

            if rows:
                print(f"✓ Got {len(rows)} rows from API, using first {NUM_CLIPS}")
                for i, row_data in enumerate(rows[:NUM_CLIPS]):
                    try:
                        row = row_data.get('row', {})

                        # Extract MP4 data (might be base64 or bytes)
                        mp4_field = row.get('mp4', {})
                        if isinstance(mp4_field, dict) and 'bytes' in mp4_field:
                            mp4_data = bytes(mp4_field['bytes'])
                        else:
                            print(f"  ⚠ Skipping clip {i+1}: Unexpected mp4 format")
                            continue

                        metadata = row.get('json', {})

                        # Save video file
                        video_path = os.path.join(CLIPS_DIR, f"clip_{i:02d}.mp4")
                        with open(video_path, "wb") as f:
                            f.write(mp4_data)

                        # Save metadata
                        metadata_path = os.path.join(CLIPS_DIR, f"clip_{i:02d}.json")
                        with open(metadata_path, "w") as f:
                            json.dump(metadata, f, indent=2)

                        print(f"  ✓ Saved clip {i+1}/{NUM_CLIPS}: Worker {metadata.get('worker_id', 'unknown')}, Factory {metadata.get('factory_id', 'unknown')}")
                    except Exception as e:
                        print(f"  ✗ Failed clip {i+1}: {e}")
                        continue

                print(f"\n✓ Done! {NUM_CLIPS} clips saved to {CLIPS_DIR}/")
                print("Now run: streamlit run app.py")
                return

        print(f"API returned {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"API request failed: {e}")

    # Fallback: Use streaming with take() - faster than iterate
    print("\nFalling back to streaming method with take() - this will be faster...")
    print("This may take 1-2 minutes on first run (enumerates dataset files)")

    try:
        from datasets import load_dataset

        # Load dataset in streaming mode
        dataset = load_dataset(
            "builddotai/Egocentric-10K",
            streaming=True,
            split="train",
            token=HF_TOKEN
        )

        # Use take() instead of iterate - more efficient
        print("Fetching clips...")
        clips_iter = iter(dataset.take(NUM_CLIPS))

        for i in range(NUM_CLIPS):
            try:
                clip = next(clips_iter)

                # Save video file
                video_path = os.path.join(CLIPS_DIR, f"clip_{i:02d}.mp4")
                with open(video_path, "wb") as f:
                    f.write(clip['mp4'])

                # Save metadata
                metadata_path = os.path.join(CLIPS_DIR, f"clip_{i:02d}.json")
                with open(metadata_path, "w") as f:
                    json.dump(clip['json'], f, indent=2)

                print(f"  ✓ Saved clip {i+1}/{NUM_CLIPS}: Worker {clip['json']['worker_id']}, Factory {clip['json']['factory_id']}")
            except Exception as e:
                print(f"  ✗ Failed to save clip {i+1}: {e}")
                continue

        print(f"\n✓ Done! {NUM_CLIPS} clips saved to {CLIPS_DIR}/")
        print("Now run: streamlit run app.py")

    except Exception as e:
        print(f"\n✗ Fallback method failed: {e}")
        print("Please check your HF_TOKEN and internet connection")
        print(f"Manual fallback: run 'python preload_clips.py' (slower but more reliable)")

if __name__ == "__main__":
    preload_clips_fast()

"""
RECOMMENDED: Super fast clip preloader that downloads tar files directly from HuggingFace.
Bypasses the slow dataset enumeration entirely by fetching specific tar files.
Run once: python preload_clips_direct.py (~30 seconds for 5 clips)
"""
import os
import json
import tarfile
import requests
from io import BytesIO
from src.config import HF_TOKEN

CLIPS_DIR = "sample_clips"
NUM_CLIPS = 5

# Direct URLs to specific tar files (known to exist from dataset structure)
# Each tar contains 1-2 clips, so we need multiple tars to get 5 clips
TAR_URLS = [
    "https://huggingface.co/datasets/builddotai/Egocentric-10K/resolve/main/factory_001/workers/worker_001/factory001_worker001_part00.tar",
    "https://huggingface.co/datasets/builddotai/Egocentric-10K/resolve/main/factory_002/workers/worker_001/factory002_worker001_part00.tar",
    "https://huggingface.co/datasets/builddotai/Egocentric-10K/resolve/main/factory_003/workers/worker_001/factory003_worker001_part00.tar",
    "https://huggingface.co/datasets/builddotai/Egocentric-10K/resolve/main/factory_004/workers/worker_001/factory004_worker001_part00.tar",
    "https://huggingface.co/datasets/builddotai/Egocentric-10K/resolve/main/factory_005/workers/worker_001/factory005_worker001_part00.tar",
]

def preload_clips_direct():
    """Download clips by directly fetching tar files from HuggingFace."""
    os.makedirs(CLIPS_DIR, exist_ok=True)

    print(f"Downloading clips directly from HuggingFace tar files...")
    print("This should take <30 seconds")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    clip_count = 0

    for tar_url in TAR_URLS:
        if clip_count >= NUM_CLIPS:
            break

        print(f"\n  Fetching {tar_url.split('/')[-1]}...")

        try:
            response = requests.get(tar_url, headers=headers, timeout=60, stream=True)

            if response.status_code != 200:
                print(f"  ✗ Failed to download: HTTP {response.status_code}")
                continue

            # Open tar file from response
            tar_bytes = BytesIO(response.content)
            with tarfile.open(fileobj=tar_bytes, mode='r') as tar:
                members = tar.getmembers()

                # Group files by clip (each clip has .mp4 and .json)
                clips_in_tar = {}
                for member in members:
                    base_name = member.name.rsplit('.', 1)[0]  # Remove extension
                    if base_name not in clips_in_tar:
                        clips_in_tar[base_name] = {}

                    ext = member.name.split('.')[-1]
                    clips_in_tar[base_name][ext] = member

                # Extract clips
                for base_name, files in clips_in_tar.items():
                    if clip_count >= NUM_CLIPS:
                        break

                    if 'mp4' not in files or 'json' not in files:
                        continue

                    # Extract MP4
                    mp4_member = files['mp4']
                    mp4_data = tar.extractfile(mp4_member).read()

                    # Extract JSON
                    json_member = files['json']
                    json_data = json.load(tar.extractfile(json_member))

                    # Save files
                    video_path = os.path.join(CLIPS_DIR, f"clip_{clip_count:02d}.mp4")
                    with open(video_path, "wb") as f:
                        f.write(mp4_data)

                    metadata_path = os.path.join(CLIPS_DIR, f"clip_{clip_count:02d}.json")
                    with open(metadata_path, "w") as f:
                        json.dump(json_data, f, indent=2)

                    print(f"  ✓ Saved clip {clip_count+1}/{NUM_CLIPS}: Worker {json_data.get('worker_id', 'unknown')}, Factory {json_data.get('factory_id', 'unknown')}")
                    clip_count += 1

        except Exception as e:
            print(f"  ✗ Error processing tar: {e}")
            continue

    if clip_count > 0:
        print(f"\n✓ Done! {clip_count} clips saved to {CLIPS_DIR}/")
        print("Now run: streamlit run app.py")
    else:
        print("\n✗ Failed to download any clips")
        print("Please check your HF_TOKEN and try again")

if __name__ == "__main__":
    preload_clips_direct()

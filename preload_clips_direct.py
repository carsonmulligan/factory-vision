"""
STEPS
0. copy and paste this into a code editor, call it preload_clips_direct.py
1. create a .env file 
2. create a HF_TOKEN=...
3. go to https://huggingface.co/settings/tokens and make a token 
4. pip install -r requirements.txt
5. python preload_clips_direct.py

RECOMMENDED: Super fast clip preloader that downloads tar files directly from HuggingFace.
Bypasses the slow dataset enumeration entirely by fetching specific tar files.

Usage:
  python preload_clips_direct.py            # Download just clip 00 (7 min, ~200MB)
  python preload_clips_direct.py --all      # Download clips 1-5 (20 min each, ~600MB each)
"""
import os
import sys
import json
import tarfile
import requests
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

CLIPS_DIR = "sample_clips"

# Clip 00: Short 7-minute video (recommended for testing)
CLIP_00_TAR = "https://huggingface.co/datasets/builddotai/Egocentric-10K/resolve/main/factory_001/workers/worker_001/factory001_worker001_part00.tar"

# Clips 1-5: Longer 20-minute videos each
CLIPS_1_5_TARS = [
    "https://huggingface.co/datasets/builddotai/Egocentric-10K/resolve/main/factory_002/workers/worker_001/factory002_worker001_part00.tar",
    "https://huggingface.co/datasets/builddotai/Egocentric-10K/resolve/main/factory_003/workers/worker_001/factory003_worker001_part00.tar",
    "https://huggingface.co/datasets/builddotai/Egocentric-10K/resolve/main/factory_004/workers/worker_001/factory004_worker001_part00.tar",
    "https://huggingface.co/datasets/builddotai/Egocentric-10K/resolve/main/factory_005/workers/worker_001/factory005_worker001_part00.tar",
]

def preload_clips_direct(download_all=False):
    """Download clips by directly fetching tar files from HuggingFace."""

    # Validate HF_TOKEN is loaded
    if not HF_TOKEN:
        print("\n✗ Error: HF_TOKEN not found!")
        print("Please ensure you have a .env file with HF_TOKEN=your_token")
        print("Get your token from: https://huggingface.co/settings/tokens")
        sys.exit(1)

    os.makedirs(CLIPS_DIR, exist_ok=True)

    # Select which clips to download
    if download_all:
        tar_urls = [CLIP_00_TAR] + CLIPS_1_5_TARS
        print("Downloading ALL clips (clip 00 + clips 1-5)...")
        print("Total: ~3GB, estimated time: 2-3 minutes")
    else:
        tar_urls = [CLIP_00_TAR]
        print("Downloading clip 00 only (7 min video, recommended for testing)...")
        print("Size: ~200MB, estimated time: 10-15 seconds")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    clip_count = 0

    for tar_url in tar_urls:

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

                    duration_min = json_data.get('duration_sec', 0) / 60
                    print(f"  ✓ Saved clip {clip_count:02d}: Worker {json_data.get('worker_id', 'unknown')}, Factory {json_data.get('factory_id', 'unknown')} ({duration_min:.1f} min)")
                    clip_count += 1

        except Exception as e:
            print(f"  ✗ Error processing tar: {e}")
            continue

    if clip_count > 0:
        print(f"\n✓ Done! {clip_count} clip(s) saved to {CLIPS_DIR}/")
        if clip_count == 1:
            print("\n📹 Quick test: Run the analysis on the first 30 seconds of clip 00")
            print("   cd analysis && streamlit run app.py")
        else:
            print("\n📹 All clips downloaded! Run analysis:")
            print("   cd analysis && streamlit run app.py")
    else:
        print("\n✗ Failed to download any clips")
        print("Please check your HF_TOKEN and try again")

if __name__ == "__main__":
    # Parse CLI arguments
    download_all = "--all" in sys.argv or "-a" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    preload_clips_direct(download_all=download_all)

import streamlit as st
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stream_sampler import extract_frames
from src.vision_analyzer import analyze_frame
from src.config import MODEL

st.set_page_config(page_title="Factory AI Observer", layout="wide")
st.title("Egocentric-10K Mini Explorer")
st.caption("Testing on clip 00 (first 30 seconds) • GPT-4o-mini vision")

# Load from local preloaded clips (in parent directory)
CLIPS_DIR = Path(__file__).parent.parent / "sample_clips"
TEST_CLIP = "clip_00.mp4"  # 7-minute video, we'll analyze first 30 seconds

if st.button("Analyze Frame from Clip 00"):
    # Check if clip 00 exists
    clip_path = CLIPS_DIR / TEST_CLIP
    if not clip_path.exists():
        st.error(f"Clip 00 not found! Please run: python preload_clips_direct.py")
        st.stop()

    metadata_path = clip_path.with_suffix('.json')

    with st.spinner("Loading clip..."):
        # Load video and metadata
        with open(clip_path, "rb") as f:
            video_bytes = f.read()
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Extract frame from first 30 seconds only
        # We'll extract 3 frames: at 5s, 15s, and 25s
        frames = extract_frames(video_bytes, interval_sec=10, max_frames=3)

        # For demo, just show the first frame (at 5 seconds)
        frame = frames[0]
        st.info(f"📹 Analyzing clip_00.mp4 • 7 min video • Frame from first 30 seconds")

        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(frame, use_column_width=True)
            st.caption(f"Worker {metadata.get('worker_id', 'N/A')} • Factory {metadata.get('factory_id', 'N/A')} • Frame at ~5 seconds")

        with col2:
            with st.spinner("Asking GPT-4o-mini..."):
                result = analyze_frame(frame)
                st.success(result["description"])
                st.caption(f"Cost: ~${result['cost_usd']:.4f} • Model: {MODEL}")

        # Save button (now works correctly)
        if st.button("Save to JSON"):
            with open("egocentric_analysis.json", "a") as f:
                json.dump({
                    "worker_id": metadata['worker_id'],
                    "analysis": result["description"]
                }, f)
                f.write("\n")
            st.success("Saved!")

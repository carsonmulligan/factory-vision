import streamlit as st
import json
import random
import os
from pathlib import Path
from src.stream_sampler import extract_frames
from src.vision_analyzer import analyze_frame
from src.config import MODEL

st.set_page_config(page_title="Factory AI Observer", layout="wide")
st.title("Egocentric-10K Mini Explorer")
st.caption("Streaming real factory workers • GPT-4o-mini vision • <$5 total")

# Load from local preloaded clips
CLIPS_DIR = "sample_clips"

if st.button("Load Random Worker Clip"):
    # Check if clips exist
    if not os.path.exists(CLIPS_DIR):
        st.error(f"No sample clips found! Please run: python preload_clips.py")
        st.stop()

    # Get random clip from local files
    clip_files = list(Path(CLIPS_DIR).glob("clip_*.mp4"))
    if not clip_files:
        st.error(f"No clips found in {CLIPS_DIR}/")
        st.stop()

    with st.spinner("Loading clip..."):
        # Pick random clip
        clip_path = random.choice(clip_files)
        metadata_path = clip_path.with_suffix('.json')

        # Load video and metadata
        with open(clip_path, "rb") as f:
            video_bytes = f.read()
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Extract frame
        frames = extract_frames(video_bytes, max_frames=1)
        frame = frames[0]

        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(frame, use_column_width=True)
            st.caption(f"Worker {metadata['worker_id']} • Factory {metadata['factory_id']}")

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

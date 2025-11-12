import streamlit as st
import json
import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stream_sampler import extract_frames
from src.vision_analyzer import analyze_frame
from src.config import MODEL

st.set_page_config(page_title="Factory AI Observer", layout="wide")
st.title("Egocentric-10K Mini Explorer")
st.caption("GPT-4o-mini vision analysis of factory worker videos")

# Load from local preloaded clips (in parent directory)
CLIPS_DIR = Path(__file__).parent.parent / "sample_clips"
TEST_CLIP = "clip_00.mp4"  # 7-minute video

# Check if clip 00 exists
clip_path = CLIPS_DIR / TEST_CLIP
clip_exists = clip_path.exists()

if not clip_exists:
    st.warning("⚠️ Clip 00 not found!")
    st.info("Clip 00 is a 7-minute video (~200MB) from the Egocentric-10K dataset.")

    if st.button("Download Clip 00"):
        with st.spinner("Downloading clip 00... This will take 10-15 seconds"):
            try:
                # Run the download script
                result = subprocess.run(
                    ["python", str(Path(__file__).parent.parent / "preload_clips_direct.py")],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent.parent
                )
                if result.returncode == 0:
                    st.success("✅ Download complete! Refresh the page to analyze.")
                    st.rerun()
                else:
                    st.error(f"Download failed: {result.stderr}")
            except Exception as e:
                st.error(f"Error downloading: {str(e)}")
    st.stop()

# Clip exists - show analysis options
st.success("✅ Clip 00 is ready!")

# Analysis options
analysis_option = st.radio(
    "Choose what to analyze:",
    ["First 30 seconds (3 frames, recommended)", "Full video (7 minutes, ~40 frames)"],
    help="Start with 30 seconds to test the analysis before running on the full video"
)

if st.button("Analyze"):
    metadata_path = clip_path.with_suffix('.json')

    with st.spinner("Loading clip..."):
        # Load video and metadata
        with open(clip_path, "rb") as f:
            video_bytes = f.read()
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Extract frames based on selection
        if "First 30" in analysis_option:
            # Extract 3 frames from first 30 seconds: at 5s, 15s, and 25s
            frames = extract_frames(video_bytes, interval_sec=10, max_frames=3)
            st.info(f"📹 Analyzing clip_00.mp4 • First 30 seconds • 3 frames")
        else:
            # Extract frames from full 7-minute video at 10-second intervals
            frames = extract_frames(video_bytes, interval_sec=10, max_frames=None)
            st.info(f"📹 Analyzing clip_00.mp4 • Full 7 minutes • {len(frames)} frames")

        # Analyze each frame
        total_cost = 0
        results = []

        for i, frame in enumerate(frames):
            frame_time = (i + 1) * 10 - 5  # Approximate time in seconds

            col1, col2 = st.columns([1, 1])
            with col1:
                st.image(frame, use_column_width=True)
                st.caption(f"Frame {i+1}/{len(frames)} • ~{frame_time}s • Worker {metadata.get('worker_id', 'N/A')} • Factory {metadata.get('factory_id', 'N/A')}")

            with col2:
                with st.spinner(f"Analyzing frame {i+1}..."):
                    result = analyze_frame(frame)
                    st.markdown(f"**Analysis:** {result['description']}")
                    st.caption(f"Cost: ~${result['cost_usd']:.4f} • {result['input_tokens']} input / {result['output_tokens']} output tokens")
                    total_cost += result['cost_usd']
                    results.append({
                        "frame": i + 1,
                        "time_sec": frame_time,
                        "analysis": result["description"],
                        "cost_usd": result["cost_usd"]
                    })

            st.divider()

        # Show total cost
        st.success(f"✅ Analysis complete! Total cost: ~${total_cost:.4f}")

        # Save button
        if st.button("Save Results to JSON"):
            output = {
                "worker_id": metadata['worker_id'],
                "factory_id": metadata['factory_id'],
                "analysis_type": analysis_option,
                "total_frames": len(frames),
                "total_cost_usd": total_cost,
                "model": MODEL,
                "results": results
            }
            with open("egocentric_analysis.json", "w") as f:
                json.dump(output, f, indent=2)
            st.success("Saved to egocentric_analysis.json!")

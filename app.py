import streamlit as st
import json
import random
from stream_sampler import stream_random_clips, extract_frames
from vision_analyzer import analyze_frame
from config import MODEL

st.set_page_config(page_title="Factory AI Observer", layout="wide")
st.title("Egocentric-10K Mini Explorer")
st.caption("Streaming real factory workers • GPT-4o-mini vision • <$5 total")

if st.button("Load Random Worker Clip"):
    with st.spinner("Streaming clip..."):
        clip = random.choice(stream_random_clips(10))
        frames = extract_frames(clip['mp4'], max_frames=1)
        frame = frames[0]

        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(frame, use_column_width=True)
            st.caption(f"Worker {clip['json']['worker_id']} • Factory {clip['json']['factory_id']}")

        with col2:
            with st.spinner("Asking GPT-4o-mini..."):
                result = analyze_frame(frame)
                st.success(result["description"])
                st.caption(f"Cost: ~${result['cost_usd']:.4f} • Model: {MODEL}")

    if st.button("Save to JSON"):
        with open("egocentric_analysis.json", "a") as f:
            json.dump({
                "worker_id": clip['json']['worker_id'],
                "analysis": result["description"]
            }, f)
            f.write("\n")
        st.success("Saved!")

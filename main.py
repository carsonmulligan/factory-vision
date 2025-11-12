#!/usr/bin/env python3
import json
import time
from src.stream_sampler import stream_random_clips, extract_frames
from src.vision_analyzer import analyze_frame
from src.config import MAX_CLIPS, FRAMES_PER_CLIP
from tqdm import tqdm

def main():
    print("Streaming random factory clips from Egocentric-10K...")
    clips = stream_random_clips(MAX_CLIPS)
    
    results = []
    total_cost = 0

    for clip in tqdm(clips, desc="Processing clips"):
        meta = clip['json']
        frames = extract_frames(clip['mp4'], interval_sec=10, max_frames=FRAMES_PER_CLIP)
        
        clip_result = {
            "factory_id": meta['factory_id'],
            "worker_id": meta['worker_id'],
            "duration_sec": meta['duration_sec'],
            "frames": []
        }

        for i, frame in enumerate(frames):
            try:
                analysis = analyze_frame(frame)
                clip_result["frames"].append({
                    "frame_idx": i,
                    "sec": i * 10,
                    "analysis": analysis["description"]
                })
                total_cost += analysis["cost_usd"]
                time.sleep(0.1)  # Be gentle on API
            except Exception as e:
                clip_result["frames"].append({"error": str(e)})

        results.append(clip_result)

    # Save results
    with open("egocentric_analysis.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone! Analyzed {len(results)} clips.")
    print(f"Total cost: ${total_cost:.3f}")
    print(f"Results saved to egocentric_analysis.json")

if __name__ == "__main__":
    main()

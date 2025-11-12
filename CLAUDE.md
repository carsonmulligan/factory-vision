# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Egocentric-10K Mini Explorer is a Python application for downloading and analyzing egocentric factory worker videos from the Egocentric-10K dataset. The project emphasizes fast downloads via direct tar file access and cost-effective GPT-4o-mini vision analysis. **The recommended workflow is: download clip 00 first, then test analysis on the first 30 seconds.**

## Environment Setup

Virtual environment and dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Requires `.env` file with:
- `OPENAI_API_KEY` - OpenAI API key for GPT-4o-mini vision
- `HF_TOKEN` - HuggingFace token with dataset access for builddotai/Egocentric-10K

**Quick start:**
```bash
# 1. Download test clip (7 min, ~200MB, 10-15 sec)
python preload_clips_direct.py

# 2. Test analysis on first 30 seconds
cd analysis && streamlit run app.py
```

**Download options:**
- `python preload_clips_direct.py` - Just clip 00 (recommended for testing)
- `python preload_clips_direct.py --all` - Download clips 0-5 (~3GB, 2-3 min)

## Running the Application

**Interactive web app (recommended):**
```bash
cd analysis
streamlit run app.py
```
Analyzes first 30 seconds of clip 00 using GPT-4o-mini vision. Extracts frames at 10-second intervals and displays analysis with costs.

**Batch processing pipeline:**
```bash
cd analysis
python main.py
```
Streams clips from HuggingFace (slow initial load), processes 50 clips (configurable), outputs to `egocentric_analysis.json` with cost report.

## Architecture

The codebase follows a modular structure optimized for LLM navigation:

```
.
├── preload_clips_direct.py # MAIN: Download clips (direct tar access)
├── src/                    # Core library modules
│   ├── config.py          # Configuration and cost constants
│   ├── stream_sampler.py  # Frame extraction from videos
│   └── vision_analyzer.py # OpenAI vision API integration
├── analysis/              # Analysis tools
│   ├── app.py            # Streamlit web app (tests first 30s of clip 00)
│   └── main.py           # Batch processing pipeline
├── sample_clips/          # Downloaded videos (gitignored)
├── preload_clips_fast.py  # Alternative download method
├── preload_clips.py       # Legacy download method
└── requirements.txt       # Dependencies
```

**Core modules (src/):**

1. **src/config.py** - Central configuration and cost tracking constants. All configurable parameters (MAX_CLIPS, FRAMES_PER_CLIP, FRAME_INTERVAL_SEC, MAX_TOKENS) are defined here.

2. **src/stream_sampler.py** - Dataset streaming layer
   - `stream_random_clips(n)` - Streams N random clips from HuggingFace dataset using shuffle buffer with caching
   - `extract_frames(mp4_bytes, interval_sec, max_frames)` - Decodes MP4 bytes in-memory using PyAV, extracts frames at regular intervals
   - Dataset connection caching prevents repeated slow file enumeration

3. **src/vision_analyzer.py** - OpenAI vision API integration
   - `encode_frame(frame)` - Compresses frames to JPEG (85% quality) and base64 encodes
   - `analyze_frame(frame, prompt)` - Sends frame to GPT-4o-mini vision API with cost tracking
   - Returns structured response with description, cost, and token count

**Executable scripts (root):**

4. **preload_clips_direct.py** - Download utility (RECOMMENDED)
   - CLI options: default (clip 00 only) or `--all` (clips 0-5)
   - Downloads specific tar files directly from HuggingFace (~10-15 sec per clip)
   - Clip 00: 7 minutes, ~200MB (recommended for testing)
   - Clips 1-5: 20 minutes each, ~600MB each
   - Saves to `sample_clips/` directory

**Executable scripts (analysis/):**

5. **analysis/app.py** - Streamlit web interface
   - Loads clip_00.mp4 from `../sample_clips/`
   - Analyzes ONLY first 30 seconds (frames at 5s, 15s, 25s intervals)
   - Single-frame analysis with visual preview
   - Real-time cost tracking
   - Configured specifically for quick testing

6. **analysis/main.py** - Batch processing pipeline
   - Streams MAX_CLIPS from HuggingFace dataset (slow)
   - Extracts FRAMES_PER_CLIP frames per clip
   - Rate-limited API calls (0.1s delay)
   - Outputs JSON with factory_id, worker_id, frame-level analysis

**Alternative download methods:**

7. **preload_clips_fast.py** - Alternative: API with streaming fallback
8. **preload_clips.py** - Legacy: Streaming only (slow, may timeout)

## Key Design Patterns

**Streaming-first architecture**: All video data is processed in-memory via BytesIO. Videos are never saved to disk. The HuggingFace dataset is accessed in streaming mode to avoid downloading the full dataset.

**Cost tracking**: Every API call tracks input/output tokens and calculates cost based on GPT-4o-mini pricing defined in config.py. Main pipeline aggregates total cost across all frames.

**Safety controls**: JPEG compression, rate limiting, token limits, and frame interval sampling reduce API costs and prevent excessive usage.

**Metadata preservation**: Clip metadata (factory_id, worker_id, duration_sec) from the dataset JSON is preserved in analysis results for downstream traceability.

## Configuration

Edit `config.py` to adjust:
- `MAX_CLIPS` - Number of clips for batch processing (default: 50)
- `FRAMES_PER_CLIP` - Frames extracted per clip (default: 3)
- `FRAME_INTERVAL_SEC` - Seconds between extracted frames (default: 10)
- `MAX_TOKENS` - GPT-4o-mini response token limit (default: 150)
- Cost tracking constants are pre-configured for GPT-4o-mini pricing

## Dataset

Uses builddotai/Egocentric-10K from HuggingFace:
- Requires HuggingFace token with dataset access
- Streaming mode via `datasets` library
- Each sample contains: mp4 (bytes), json (metadata: factory_id, worker_id, duration_sec)

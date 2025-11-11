# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Factory Vision is a Python application that streams egocentric factory worker videos from the Egocentric-10K dataset on HuggingFace, extracts frames, and uses GPT-4o-mini vision API to analyze worker actions, tools, and safety compliance. The project emphasizes streaming-only (no local video storage) and cost-effectiveness.

## Environment Setup

Virtual environment and dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install 'datasets[streaming]' av openai streamlit python-dotenv tqdm opencv-python
```

Requires `.env` file with:
- `OPENAI_API_KEY` - OpenAI API key for GPT-4o-mini vision
- `HF_TOKEN` - HuggingFace token with dataset access for builddotai/Egocentric-10K

## Running the Application

**Batch processing pipeline:**
```bash
python main.py
```
Processes 50 clips (configurable), outputs to `egocentric_analysis.json` with cost report.

**Interactive web interface:**
```bash
streamlit run app.py
```
Real-time frame-by-frame analysis with visual feedback.

## Architecture

The codebase follows a modular pipeline architecture:

1. **config.py** - Central configuration and cost tracking constants. All configurable parameters (MAX_CLIPS, FRAMES_PER_CLIP, FRAME_INTERVAL_SEC, MAX_TOKENS) are defined here.

2. **stream_sampler.py** - Dataset streaming layer
   - `stream_random_clips(n)` - Streams N random clips from HuggingFace dataset using shuffle buffer
   - `extract_frames(mp4_bytes, interval_sec, max_frames)` - Decodes MP4 bytes in-memory using PyAV, extracts frames at regular intervals
   - No local file storage; all video processing happens in-memory

3. **vision_analyzer.py** - OpenAI vision API integration
   - `encode_frame(frame)` - Compresses frames to JPEG (85% quality) and base64 encodes
   - `analyze_frame(frame, prompt)` - Sends frame to GPT-4o-mini vision API with cost tracking
   - Returns structured response with description, cost, and token count

4. **main.py** - Batch processing pipeline
   - Streams MAX_CLIPS from dataset
   - Extracts FRAMES_PER_CLIP frames per clip
   - Rate-limited API calls (0.1s delay)
   - Outputs JSON with factory_id, worker_id, frame-level analysis

5. **app.py** - Streamlit web interface
   - Single-frame analysis with visual preview
   - Real-time cost tracking
   - Optional JSON append for saving results

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

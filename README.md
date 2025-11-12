# Egocentric-10K Mini Explorer

Download and analyze egocentric factory worker videos from the [Egocentric-10K dataset](https://huggingface.co/datasets/builddotai/Egocentric-10K). Extract frames and use GPT-4o-mini vision API to analyze worker actions, tools, and safety compliance.

![Demo](demo.png)

## Quick Start

```bash
# 1. Download a single test video (7 min, ~200MB)
python preload_clips_direct.py

# 2. Run analysis on first 30 seconds
cd analysis && streamlit run app.py
```

## Features

- **Fast downloads** - Direct tar file downloads (~10-15 sec for test clip)
- **Two download options** - Just clip 00 (7 min) or all clips (20 min each)
- **Cost-effective** - GPT-4o-mini vision API (<$0.01 for test)
- **Web interface** - Streamlit app for frame-by-frame analysis
- **Real-time analysis** - Worker actions, tools, objects, safety gear detection

## About the Dataset

This project uses the [Egocentric-10K dataset](https://huggingface.co/datasets/builddotai/Egocentric-10K) - a collection of first-person factory worker videos.

## Setup

1. **Clone and install**
   ```bash
   git clone git@github.com:carsonmulligan/factory-vision.git
   cd factory-vision
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure API keys**

   Create `.env` file with your credentials:
   ```
   OPENAI_API_KEY=your_openai_key_here
   HF_TOKEN=your_hf_token_here
   ```

   - Get OpenAI API key: https://platform.openai.com/api-keys
   - Get HuggingFace token: https://hf.co/settings/tokens
   - Accept dataset terms: https://huggingface.co/datasets/builddotai/Egocentric-10K

3. **Download video clips**

   **Option A: Just test clip** (recommended first time)
   ```bash
   python preload_clips_direct.py
   ```
   Downloads clip 00 (7 min video, ~200MB, 10-15 seconds)

   **Option B: All clips**
   ```bash
   python preload_clips_direct.py --all
   ```
   Downloads clips 0-5 (~3GB, 2-3 minutes)

## Usage

### Interactive Web App (Recommended)

Test GPT-4o-mini vision analysis on first 30 seconds of clip 00:

```bash
cd analysis
streamlit run app.py
```

Click "Analyze Frame from Clip 00" to extract and analyze frames.

### Batch Processing Pipeline

Process multiple clips from HuggingFace (requires streaming):

```bash
cd analysis
python main.py
```

Output: `egocentric_analysis.json` with cost report

## Configuration

Edit `src/config.py` to adjust:

- `MAX_CLIPS` - Number of clips to process (default: 50)
- `FRAMES_PER_CLIP` - Frames extracted per clip (default: 3)
- `FRAME_INTERVAL_SEC` - Seconds between frames (default: 10)
- `MAX_TOKENS` - GPT-4o-mini response limit (default: 150)

## Cost Breakdown

- **Model**: GPT-4o-mini
- **Pricing**: $0.15/1M input tokens, $0.60/1M output tokens
- **Per frame**: ~$0.0002-0.0005
- **Total (50 clips × 3 frames)**: <$2.50

## Safety Features

- Streaming-only (no local video storage)
- JPEG compression at 85% quality
- 0.1s rate limit between API calls
- No audio processing or PII storage
- Results saved as JSON text only

## Project Structure

```
.
├── preload_clips_direct.py # MAIN: Download clips (10-15 sec)
├── src/                    # Core library modules
│   ├── config.py          # Configuration and cost tracking
│   ├── stream_sampler.py  # Video frame extraction
│   └── vision_analyzer.py # GPT-4o-mini vision API
├── analysis/              # Analysis tools
│   ├── app.py            # Streamlit web app (tests first 30s)
│   └── main.py           # Batch processing pipeline
├── sample_clips/          # Downloaded videos (gitignored)
├── requirements.txt       # Dependencies
└── .env                   # API credentials (not committed)
```

## Download Options Explained

- **`preload_clips_direct.py`** - RECOMMENDED: Direct tar download (fastest)
  - Default: Downloads clip 00 only (7 min, ~200MB)
  - With `--all`: Downloads clips 0-5 (~3GB)

- `preload_clips_fast.py` - Alternative: API with streaming fallback
- `preload_clips.py` - Legacy: Streaming only (slow, may timeout)

## Next Steps

- Fine-tune a CLIP model using labeled frames
- Build a safety gear detection model
- Deploy Streamlit app publicly
- Expand to multi-factory analysis

## License

MIT

## Author

[@us_east_3](https://twitter.com/us_east_3)

---

![Pig Jarvis](pig-jarvis.png)

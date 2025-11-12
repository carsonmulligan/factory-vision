# Egocentric-10K Mini Explorer

![Demo](demo.png)

## What This Repo Does

1. **Download video samples** from the [Egocentric-10K dataset](https://huggingface.co/datasets/builddotai/Egocentric-10K) - a collection of first-person factory worker videos
2. **Run a Streamlit app** that analyzes these videos using GPT-4o-mini vision to detect worker actions, tools, objects, and safety gear

## Quick Start

```bash
# 1. Clone and install dependencies
git clone git@github.com:carsonmulligan/factory-vision.git
cd factory-vision
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Create .env with your API keys (see Setup below)

# 3. Run the Streamlit app (it will help you download clip 00 if needed)
cd analysis && streamlit run app.py
```

## Setup

**Configure API keys** - Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_key_here
HF_TOKEN=your_hf_token_here
```

- Get OpenAI API key: https://platform.openai.com/api-keys
- Get HuggingFace token: https://hf.co/settings/tokens
- Accept dataset terms: https://huggingface.co/datasets/builddotai/Egocentric-10K

## Usage

**Interactive Web App** - Run the Streamlit app which will guide you through downloading and analyzing clips:

```bash
cd analysis
streamlit run app.py
```

The app will check if clip 00 exists and let you download it if needed. Then choose to analyze the first 30 seconds or the full 7-minute video.

**Batch Processing** - Process multiple clips from HuggingFace (requires streaming):

```bash
cd analysis
python main.py
```

**Manual Download** - Download clips directly:

```bash
# Just clip 00 (7 min, ~200MB)
python preload_clips_direct.py

# All clips 0-5 (~3GB)
python preload_clips_direct.py --all
```

## Configuration

Edit `src/config.py` to adjust frame extraction intervals, token limits, and number of clips to process.

## Cost Breakdown

- **Model**: GPT-4o-mini ($0.15/1M input tokens, $0.60/1M output tokens)
- **Per frame**: ~$0.0002-0.0005
- **First 30 seconds (3 frames)**: <$0.01

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

## License

Apache 2.0

## Author

[@us_east_3](https://twitter.com/us_east_3)

---

![Pig Jarvis](pig-jarvis.png)

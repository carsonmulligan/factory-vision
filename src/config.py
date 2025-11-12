import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Safety & cost controls
MAX_CLIPS = 50
FRAMES_PER_CLIP = 3
FRAME_INTERVAL_SEC = 10
MODEL = "gpt-4o-mini"
MAX_TOKENS = 150

# Cost tracking
COST_PER_1K_TOKENS_INPUT = 0.150 / 1000   # $0.15 / 1M tokens → per 1K
COST_PER_1K_TOKENS_OUTPUT = 0.600 / 1000  # $0.60 / 1M tokens

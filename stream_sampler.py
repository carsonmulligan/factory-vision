import random
from datasets import load_dataset
import av
from io import BytesIO
from tqdm import tqdm
from config import HF_TOKEN

# Cache the dataset connection to avoid reloading
_dataset_cache = None

def get_dataset():
    """Lazy load and cache the dataset connection."""
    global _dataset_cache
    if _dataset_cache is None:
        _dataset_cache = load_dataset(
            "builddotai/Egocentric-10K",
            streaming=True,
            split="train",
            token=HF_TOKEN
        )
    return _dataset_cache

def stream_random_clips(n=5):
    ds = get_dataset()
    ds = ds.shuffle(buffer_size=1000, seed=random.randint(0, 10000))
    return [next(iter(ds)) for _ in range(n)]

def extract_frames(mp4_bytes, interval_sec=10, max_frames=3):
    container = av.open(BytesIO(mp4_bytes))
    frames = []
    target_pts = 0
    fps = container.streams.video[0].average_rate

    for frame in container.decode(video=0):
        current_sec = frame.pts * fps.denominator / fps.numerator
        if current_sec >= target_pts and len(frames) < max_frames:
            frames.append(frame.to_rgb().to_ndarray())
            target_pts += interval_sec
    return frames

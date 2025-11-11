import openai
import base64
import cv2
import numpy as np
from config import MODEL, MAX_TOKENS, COST_PER_1K_TOKENS_INPUT, COST_PER_1K_TOKENS_OUTPUT

client = openai.OpenAI()

def encode_frame(frame):
    _, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR), [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    return base64.b64encode(buffer).decode()

def analyze_frame(frame, prompt="Describe: worker action, tools, objects, safety gear. Be concise."):
    b64 = encode_frame(frame)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        }],
        max_tokens=MAX_TOKENS
    )
    usage = response.usage
    cost = (
        (usage.prompt_tokens * COST_PER_1K_TOKENS_INPUT) +
        (usage.completion_tokens * COST_PER_1K_TOKENS_OUTPUT)
    )
    return {
        "description": response.choices[0].message.content.strip(),
        "cost_usd": round(cost, 5),
        "tokens": usage.total_tokens
    }

import base64
import requests
from dotenv import load_dotenv
import os
from openai import OpenAI, OpenAIError
import json
from enum import Enum
from dataclasses import dataclass
from typing import Dict
from db.models import ClothingPresence, PresenceLevel, parse_clothing_presence

# Load .env file
load_dotenv()
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

_openai_client: OpenAI | None = None

def get_openai_client() -> OpenAI:
     """Lazy client so importing this module (and starting the API) does not require a key."""
     global _openai_client
     if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise OpenAIError(
                "OPENAI_API_KEY is not set. Set it in the environment or .env file."
            )
        _openai_client = OpenAI(api_key=api_key)
     return _openai_client

def img_to_base64(path: str):
    """Opens image and returns base64 string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
    

def analyze_clothing_presence(image_path: str):
    """Analyzes clothing in the provided image and returns clothing presence levels."""

    base64_image = img_to_base64(image_path)
    
    prompt = """
    You are an image-based clothing classifier for the app Where-To-Wear.

    TASK:
    Analyze the provided street photo and estimate the presence level of each clothing category based on all visible people.
    Additionally, incorporate subtle environmental reasoning (e.g., weather, temperature, season, time of day) to adjust results conservatively.
    OUTPUT FORMAT:
    Return a single JSON object ONLY, following this exact structure:

    {
    "clothing_presence": {
        "tshirts_short_sleeve": "",
        "tshirts_long_sleeve": "",
        "tank_tops": "",
        "hoodies": "",
        "light_jackets": "",
        "heavy_coats": "",
        "pants_long": "",
        "shorts": "",
        "skirts_short": "",
        "skirts_long": "",
        "dress_short": "",
        "dress_long": "",
        "sneakers": "",
        "sandals": "",
        "flip_flops": "",
        "boots": "",
        "closed_shoes": "",
        "summer_hats": "",
        "winter_hats": "",
        "scarves": "",
        "gloves": "",
        "thermal_layers": ""
    }
    }

    PRESENCE LEVELS:
    Each value must be one of:
    "none", "low", "medium", "high"

    DEFINITIONS:
    - “low” = a small number of people wearing this item OR weak environmental likelihood.
    - “medium” = noticeable minority.
    - “high” = many or most visible people.
    - “none” = essentially no one and no reasonable expectation.

    SPECIAL RULES:
    - Base results primarily on visible evidence.
    - If an item is not clearly visible but strongly implied by conditions → assign "low".
    - Never assign inferred items above "low".
    - Thermal_layers are rarely visible but may be inferred as "medium/high/low" in cold conditions.
    - If no strong environmental signal exists → keep "none".
    - Do NOT hallucinate unlikely clothing.
    - Dresses must be classified **both** under “dress_short/dress_long” AND according to their **upper-body style**:
    - sleeveless or strap dress → also count as tank_tops
    - short-sleeve dress → tshirts_short_sleeve
    - long-sleeve dress → tshirts_long_sleeve
    - Sandals include all open-toe shoes except flip flops.
    - Closed_shoes are any closed footwear not categorized as sneakers or boots.
    - Light_jackets = thin jackets, denim jackets, windbreakers.
    - Heavy_coats = thick winter coats only.
    - Hoodies = hooded sweatshirts.
    - Boots = only thick, ankle-high or knee-high boots. Do not classify sneakers or closed shoes as boots.
    - Light_jackets = only outer-layer jackets (denim, windbreaker). Hoodies or sweatshirts are NOT jackets.
    - If uncertain, choose the more conservative option (e.g., low instead of medium).

    RESTRICTIONS:
    - Return ONLY the JSON. No explanations, no text outside the object.
    - Be conservative. Prefer underestimation over overestimation.
    - Be concise and do not reason out loud.
    """

    response = get_openai_client().responses.create(
    model="gpt-5-nano",
    reasoning={"effort": "minimal"},
    input=[
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": prompt },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "low" #save tokens and speed up response. max 85 tokens.
                },
            ],
        }
    ],
    )
    return response.output_text
   
if __name__ == "__main__":
    raw = analyze_clothing_presence("/Users/ayarotbart/Desktop/Where-to-wear/snapshots/tokyo/2026-03-06_13-06-23.png")
    raw = json.loads(raw)
    #print(type(raw))
    cp = parse_clothing_presence(raw)

    print(cp)

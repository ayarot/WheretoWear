from enum import Enum
from dataclasses import dataclass
import logging
from typing import Dict, Any, Optional
import json
    

class PresenceLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Must match services/image_analysys.py prompt keys and frontend LABEL_MAP
CLOTHING_CATEGORY_KEYS: tuple[str, ...] = (
    "tshirts_short_sleeve",
    "tshirts_long_sleeve",
    "tank_tops",
    "hoodies",
    "light_jackets",
    "heavy_coats",
    "pants_long",
    "shorts",
    "skirts_short",
    "skirts_long",
    "dress_short",
    "dress_long",
    "sneakers",
    "sandals",
    "flip_flops",
    "boots",
    "closed_shoes",
    "summer_hats",
    "winter_hats",
    "scarves",
    "gloves",
    "thermal_layers",
)

@dataclass #creates object with values attribute
class ClothingPresence:
    """Typed representation of clothing_presence JSON."""
    values: Dict[str, PresenceLevel]

def parse_clothing_presence(raw: Dict[str, Any]) -> ClothingPresence:
    """
    Convert raw dict from the LLM into a ClothingPresence object.
    Raises KeyError/ValueError if something is missing or invalid.
    """
    cp = raw["clothing_presence"]  # dict of key -> string
    typed_dict: Dict[str, PresenceLevel] = {}

    for item_name, level_str in cp.items():
        try:
            typed_dict[item_name] = PresenceLevel(level_str)
        except ValueError:
            # Unknown value from model → fallback to NONE 
            typed_dict[item_name] = PresenceLevel.NONE
        
    for key in CLOTHING_CATEGORY_KEYS:
        if key not in typed_dict:
            typed_dict[key] = PresenceLevel.NONE
            
    return ClothingPresence(values=typed_dict)

def normalize_clothing_dict(raw: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """Fill missing categories (e.g. thermal_layers) for API responses and old DB rows."""
    out: Dict[str, str] = {}
    if raw:
        for k, v in raw.items():
            out[str(k)] = str(v).lower() if isinstance(v, str) else str(v)
    for k in CLOTHING_CATEGORY_KEYS:
        if k not in out:
            out[k] = "none"
    return out
    
if __name__ == "__main__":

    raw = '''{
  "clothing_presence": {
    "tshirts_short_sleeve": "low",
    "tshirts_long_sleeve": "low",
    "tank_tops": "none",
    "hoodies": "low",
    "light_jackets": "medium",
    "heavy_coats": "none",
    "pants_long": "high",
    "shorts": "none",
    "skirts_short": "low",
    "skirts_long": "low",
    "dress_short": "low",
    "dress_long": "low",
    "sneakers": "high",
    "sandals": "low",
    "flip_flops": "none",
    "boots": "low",
    "closed_shoes": "high",
    "summer_hats": "low",
    "winter_hats": "low",
    "scarves": "low",
    "gloves": "low"
    "thermal_layers": "none"
  }
} '''

    cp = parse_clothing_presence(json.loads(raw))
    print(cp)
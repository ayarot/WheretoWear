import logging
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPEN_WEATHER_API_KEY")

CITY_COORDS = {
    "tokyo":    {"lat": 35.67, "lon": 139.65},
    "new york": {"lat": 40.71, "lon": -74.00},
    "london":   {"lat": 51.50, "lon": -0.12},
    "rome":     {"lat": 41.90, "lon": 12.49},
    "koh samui": {"lat": 9.51, "lon": 100.01},
}

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

CACHE_TTL = 300  
weather_cache = {}

def fetch_weather(city: str) -> dict | None:
    """Fetch current weather for a city. Returns None on failure."""

    #cache weather data
    now = int(time.time())
    if city in weather_cache:
        cached = weather_cache[city]

        if now - cached["timestamp"] < CACHE_TTL:
            logging.info(f"  Weather cache hit for {city}")
            print(f"  Weather cache hit for {city}")
            return cached["data"]
    
    coords = CITY_COORDS.get(city)
    if not coords or not API_KEY:
        return None

    try:
        resp = requests.get(BASE_URL, params={
            "lat": coords["lat"],
            "lon": coords["lon"],
            "appid": API_KEY,
            "units": "metric",
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        weather_cache[city] = {
            "data": {
                "temp_c": data["main"]["temp"],
                "feels_like_c": data["main"]["feels_like"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
            },
            "timestamp": now,
        }
        
        return {
            "temp_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
        }
    except Exception as e:
        print(f"  Weather fetch failed for {city}: {e}")
        return None


if __name__ == "__main__":
    # for city in CITY_COORDS:
    #     w = fetch_weather(city)
    #     print(f"{city}: {w}")

    print(fetch_weather("new york"))
    print(fetch_weather("new york"))
    print(fetch_weather("tokyo"))

    

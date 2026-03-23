import os
import json
from datetime import datetime,timezone
from typing import Tuple
from services.image_analysys import analyze_clothing_presence
from services.capture import capture_youtube_frame as capture_frame
# from services.people_detection import has_enough_people
from services.weather import fetch_weather
from db.save_snapshot import save_snapshot_metadata
from db.models import parse_clothing_presence
from db.cities import get_all_cities, get_city_id_by_name
from db.database import get_connection
import logging

logger = logging.getLogger(__name__)

'''
This module defines the snapshot_job function, which is responsible for:
1. Capturing a frame from a specified YouTube URL.
2. Analyzing the captured image for clothing presence.
3. Fetching current weather data for the city.
4. Saving the snapshot metadata, including image path, clothing analysis results, and weather data,
   into the database.
'''

def generate_image_path(city: str) -> Tuple[str, str]:

    '''
    Generates a unique image path for the snapshot based on the city name
    and current timestamp.
    '''
    city_dir = os.path.join("snapshots", city)
    os.makedirs(city_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")

    return timestamp, os.path.join(city_dir, f"{timestamp}.png")

def snapshot_job(city, url) -> None:
    try:
        logger.info("Running snapshot for %s", city)
        timestamp, image_path = generate_image_path(city)
        capture_frame(url, image_path)
        logger.info("[%s] Frame captured -> %s", city, image_path)

        # if not has_enough_people(image_path):
        #     logger.warning("[%s] Not enough people detected", city)
        #     os.remove(image_path)
        #     return

        weather = fetch_weather(city)
        raw = analyze_clothing_presence(image_path)
        raw_dict = json.loads(raw)
        parsed = parse_clothing_presence(raw_dict)
        clothing_json = json.dumps({k: v.value for k, v in parsed.values.items()})
        logger.info("[%s] Clothing analysis complete", city)

        weather = weather or {}
        city_id = get_city_id_by_name(city)

        logger.debug("[%s] City ID: %s", city, city_id)

        save_snapshot_metadata(
            city_id=city_id,
            created_at=timestamp,
            image_path=image_path,
            clothing_json=clothing_json,
            weather_temp_c=weather.get("temp_c"),
            weather_feels_like_c=weather.get("feels_like_c"),
            weather_description=weather.get("description"),
            weather_humidity=weather.get("humidity"),
            weather_wind_speed=weather.get("wind_speed"),
        )

        try:
            os.remove(image_path)
            logger.info("[%s] Removed snapshot image after save", city)
        except OSError as e:
            logger.warning("[%s] Could not remove snapshot image %s: %s", city, image_path, e)

        logger.info("[%s] Snapshot metadata saved (path was %s)", city, image_path)

    except Exception:
        logger.exception("[%s] Snapshot job failed", city)


if __name__ == "__main__":
    snapshot_job("Koh Samui", "https://www.youtube.com/watch?v=VR-x3HdhKLQ")
    print("Snapshot job completed")
    
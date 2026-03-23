import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from services.weather import fetch_weather
from logging_config import setup_logging
from db.database import create_db_and_tables
from scheduler import start_scheduler
from db.cities import get_city_id_by_name, get_source_url_by_name
from db.save_snapshot import get_latest_snapshot_by_id, get_snapshots_last_week
from db.models import normalize_clothing_dict
from fastapi.middleware.cors import CORSMiddleware

setup_logging()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    setup_logging()
    start_scheduler()

@app.get("/snapshot/{city}/history")
async def get_snapshot_history(city: str):
    city_id = get_city_id_by_name(city)
    if city_id is None:
        raise HTTPException(status_code=404, detail="City not found")
    rows = get_snapshots_last_week(city_id)
    return [
        {
            "id": r[0],
            "clothing": normalize_clothing_dict(json.loads(r[1]) if r[1] else None),
            "created_at": r[2],
        }
        for r in rows
    ]

@app.get("/snapshot/{city}")
async def get_snapshot(city: str):
    city_id = get_city_id_by_name(city)
    if city_id is None:
        raise HTTPException(status_code=404, detail="City not found")
    
    result = get_latest_snapshot_by_id(city_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    clothing_json, created_at = result  
    weather = fetch_weather(city.lower()) or {} 
    source_url = get_source_url_by_name(city)

    return {
        "snapshot": {
            "clothing": normalize_clothing_dict(json.loads(clothing_json)),
            "created_at": created_at
         },
        "weather":{
            "temp_c": weather.get("temp_c"),
            "feels_like_c": weather.get("feels_like_c"),
            "description": weather.get("description"),
        },
        "source_url": source_url
    }

@app.get("/ping")
def keep_alive():
    return {"status": "I am awake!"}
    
# Mount last so /snapshot/* API routes match before static files.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
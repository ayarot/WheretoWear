from db.database import get_connection
from db.cities import get_all_cities
import os
import json

def save_snapshot_metadata(
    city_id: int,
    created_at: str,
    image_path: str,
    clothing_json: str,
    weather_temp_c: float,
    weather_feels_like_c: float,
    weather_description: str,
    weather_humidity: int,
    weather_wind_speed: float,
):
    '''
    Saves snapshot metadata to the database.
    '''
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO snapshots (
            city_id, created_at, image_path, clothing_json, 
            weather_temp_c, weather_feels_like_c, weather_description, 
            weather_humidity, weather_wind_speed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        city_id, created_at, image_path, clothing_json, 
        weather_temp_c, weather_feels_like_c, weather_description, 
        weather_humidity, weather_wind_speed
    ))
    
    conn.commit()
    conn.close()

def get_latest_snapshot_by_id(city_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT clothing_json,created_at
        FROM snapshots
        WHERE city_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (city_id,))

    row = cursor.fetchone()
    conn.close()

    return row

def get_snapshots_last_week(city_id: int) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, clothing_json, created_at
        FROM snapshots
        WHERE city_id = ?
          AND created_at >= date('now', '-7 days')
        ORDER BY created_at DESC
    """, (city_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":

    print(get_latest_snapshot_by_id(1))
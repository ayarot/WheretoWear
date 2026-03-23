import sqlite3
import os
import logging
from zoneinfo import ZoneInfo

#Create tables in directory of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(__name__)

# Database connection and setup functions
def get_connection(db_path: str = "wheretowear.db") -> sqlite3.Connection:
    path = os.path.join(BASE_DIR, db_path)
    conn = sqlite3.connect(path,timeout=10)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_db_and_tables() -> None:

    # Create database table if it does not exist
    conn = get_connection()
    #print(os.path.join(BASE_DIR, "wheretowear.db"))
    logger.info("Database connected.")
    cursor = conn.cursor()

    # Create cities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            country TEXT NOT NULL,
            source_url TEXT NOT NULL,
            timezone TEXT
        );
    """)
    logger.info("Cities table created or already exists.")

    # Create snapshots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            image_path TEXT NOT NULL,
            clothing_json TEXT,
            weather_temp_c REAL,
            weather_feels_like_c REAL,
            weather_description TEXT,
            weather_humidity INTEGER,
            weather_wind_speed REAL,
            FOREIGN KEY (city_id) REFERENCES cities(id)
        )
    """)
    logger.info("Snapshots table created or already exists.")
    # Create indexes for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cities_id ON cities(id);
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshots_city_id ON snapshots(city_id);
    """)

    conn.commit()
    conn.close()
    logger.info("Database setup complete and connection closed.")


if __name__ == "__main__":
    create_db_and_tables()

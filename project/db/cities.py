from db.database import get_connection

def initialize_cities() -> None:
    cities = [ {"name": "Tokyo", "country": "Japan", "source_url": "https://www.youtube.com/watch?v=DjdUEyjx8GM", "timezone":"Asia/Tokyo"},
                {"name": "New York", "country": "USA", "source_url": "https://www.youtube.com/watch?v=rnXIjl_Rzy4", "timezone": "America/New_York"},
                {"name": "London", "country": "UK", "source_url": "https://www.youtube.com/watch?v=M3EYAY2MftI", "timezone": "Europe/London"},
                {"name": "Koh Samui", "country": "Thailand", "source_url": "https://www.youtube.com/watch?v=VR-x3HdhKLQ", "timezone": "Asia/Bangkok"} ]

    for city in cities:
        upsert_city(city["name"], city["country"], city["source_url"], city["timezone"])
        
#{"name": "Rome", "country": "Italy", "source_url": "https://www.skylinewebcams.com/en/webcam/italia/lazio/roma/piazza-di-spagna.html", "timezone": ZoneInfo("Europe/Rome")},

#insert or update city data
def upsert_city(name: str, country: str, source_url: str, timezone: str) -> None:

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cities (name, country, source_url, timezone)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        country=excluded.country,
        source_url=excluded.source_url,
        timezone=excluded.timezone
    """, (name, country, source_url, timezone))

    conn.commit()
    conn.close()

def get_all_cities() -> list[tuple[int, str, str, str, str]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cities")
    cities = cursor.fetchall()
    conn.close()
    return cities

def get_source_url_by_name(name: str) -> str | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT source_url FROM cities WHERE LOWER(name) = LOWER(?)", (name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_city_id_by_name(name: str) -> int | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cities WHERE LOWER(name) = LOWER(?)", (name,))
    city = cursor.fetchone()
    conn.close()
    return city[0] if city else None

if __name__ == "__main__":
    #initialize_cities()
    print(get_all_cities())

    #print(get_city_id_by_name("New York"))
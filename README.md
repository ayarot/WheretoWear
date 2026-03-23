# WhereToWear

Street-style signals from live city webcams: periodic snapshots from YouTube streams, people detection (YOLO), clothing presence via an LLM, plus current weather. A small **FastAPI** backend exposes JSON for a web UI and stores metadata in **SQLite**.

---

## Features

- **Scheduled jobs** — Captures frames per city, checks crowd density, analyzes outfits, saves results and weather to the database.
- **REST API** — Latest snapshot and weekly history per city.
- **Weather** — OpenWeatherMap by city coordinates (requires API key).

---

## Requirements

- **Python 3.11+** (matches the Docker image)
- **Docker** (optional, for containerized runs)
- API keys as below (never commit them)

---

## Environment variables

Create a **`.env`** file in the **repository root** (the parent of `backend/`). Docker Compose loads it via `env_file: ../.env` when you run Compose from `backend/`.

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Clothing analysis (`services/image_analysys.py`) |
| `OPEN_WEATHER_API_KEY` | Live weather (`services/weather.py`) |

`.env` is listed in `.gitignore`. Do not push secrets.

---

## Run locally (virtualenv)

From the **`backend/`** directory (so imports like `services.*` resolve):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Set environment variables (or use a `.env` in the parent folder and rely on `python-dotenv` where loaded).

Ensure SQLite tables and city rows exist (see `db/database.py`, `db/cities.py`; run their `__main__` blocks or your seed script if the DB is new), then:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API base: `http://localhost:8000`
- Example: `GET http://localhost:8000/snapshot/Tokyo` (requires a snapshot row for that city)

---

## Run with Docker

```bash
cd backend
docker compose up --build
```

The app listens on **port 8000**. Ensure the root **`.env`** exists so the container receives `OPENAI_API_KEY` and `OPEN_WEATHER_API_KEY`.

The image installs system libraries needed for OpenCV; the first build can take several minutes (PyTorch / Ultralytics).

---

## API overview

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Simple health-style response (see `main.py`) |
| `GET` | `/snapshot/{city}` | Latest clothing JSON, weather, live stream URL |
| `GET` | `/snapshot/{city}/history` | Snapshots from the last week |

City names must match what is stored in the database (e.g. `Tokyo`, `New York`, `London`, `Koh Samui`).

---

## Project layout

```
Where-to-wear/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── scheduler.py         # APScheduler wiring
│   ├── Dockerfile
│   ├── docker-compose.yml   # env_file: ../.env
│   ├── requirements.txt
│   ├── db/                  # SQLite, models, city + snapshot persistence
│   ├── jobs/
│   │   └── snapshot_job.py  # Capture → detect → analyze → save
│   └── services/            # capture, weather, OpenAI analysis, YOLO
├── .env                     # local secrets (not in git)
└── README.md
```

---

## How it works (high level)

1. **Scheduler** runs jobs per city (see `scheduler.py`).
2. **Capture** grabs a frame from the configured YouTube URL (`services/capture.py`).
3. **People detection** filters sparse scenes (`services/people_detection.py`, Ultralytics YOLO).
4. **LLM** returns structured clothing presence levels (`services/image_analysys.py`).
5. **Weather** is fetched for coordinates mapped in `services/weather.py`.
6. **SQLite** stores snapshot metadata (and optional image path, depending on your version).

---

## Git and deployment

- Push **code only** — no `.env`, no `*.pem`, no local databases or snapshot images if you keep them ignored.
- For **GitHub Actions** deploys over SSH, store the private key in a repository secret (e.g. `PEM_FILE`); workflows must live under **`.github/workflows/`** at the **repo root** to run.
- On the server, create **`.env`** manually (or another secrets mechanism); it is not cloned from GitHub.

---

## Troubleshooting

- **Weather empty in the UI** — Check `OPEN_WEATHER_API_KEY` inside the running environment (Compose or shell).
- **`pip install` errors** — `sqlite3` and `logging` are part of the Python standard library; they should not be listed as pip packages. If your `requirements.txt` still lists them, remove those lines.
- **YOLO weights** — First run may download `yolov8n.pt` if not bundled; large files are often gitignored (`*.pt`).

---

## License

Add a `LICENSE` file if you open-source the project.

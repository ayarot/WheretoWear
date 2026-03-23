FROM python:3.11

# OpenCV (pulled in via ultralytics / capture) needs these at import time in slim Linux images
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
# Host browser hits localhost:8000 only if you publish the port, e.g.
#   docker run -p 8000:8000 <image>
# or: docker compose up
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
import os
from ultralytics import YOLO

_services_dir = os.path.dirname(__file__)
_local_weights = os.path.join(_services_dir, "yolov8n.pt")
_model = YOLO(_local_weights if os.path.isfile(_local_weights) else "yolov8n.pt")

PERSON_CLASS_ID = 0

def has_enough_people(
    image_path: str,
    min_count: int = 3,
    confidence: float = 0.15,
) -> bool:
    """Return True if at least `min_count` people are detected in the image."""
    
    results = _model(image_path, verbose=False)
    detections = results[0].boxes

    person_count = sum(
        1 for box in detections
        if int(box.cls) == PERSON_CLASS_ID and float(box.conf) >= confidence
    )

    return person_count >= min_count


# if __name__ == "__main__":
#     import sys

#     # path = sys.argv[1] if len(sys.argv) > 1 else "tokyo_sample.png"
#     # enough = has_enough_people(path)
#     # print(f"Enough people: {enough}")
#     path = "snapshots/new_york/2026-03-08_20-40-19.png"
#     enough = has_enough_people(path)
#     print(f"Enough people: {enough}")
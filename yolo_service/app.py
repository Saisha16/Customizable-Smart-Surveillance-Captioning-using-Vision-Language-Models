from fastapi import FastAPI
from ultralytics import YOLO
import cv2

app = FastAPI(title="YOLO Detection Service")

model = YOLO("yolov10n.pt")

@app.get("/")
def health():
    return {"status": "YOLO service running"}

@app.post("/detect")
def detect():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    results = model.track(
        frame,
        persist=True
    )

    detections = []
    for r in results:
        if r.boxes.id is None:
            continue
        for box, tid in zip(r.boxes.xyxy, r.boxes.id):
            x1, y1, x2, y2 = map(int, box)
            detections.append({
                "id": int(tid),
                "bbox": [x1, y1, x2, y2]
            })

    return {"detections": detections}

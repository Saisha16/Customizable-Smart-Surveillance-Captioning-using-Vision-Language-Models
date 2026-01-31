import cv2
from ultralytics import YOLO

# Load YOLOv8 Nano model
model = YOLO("yolov8n.pt")

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # YOLO tracking (person class only)
    results = model.track(
        frame,
        persist=True,
        classes=[0],  # 0 = person
        conf=0.5
    )

    # Draw bounding boxes + tracking IDs
    annotated_frame = results[0].plot()
    cv2.imshow("YOLO Tracking - Press Q to quit", annotated_frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

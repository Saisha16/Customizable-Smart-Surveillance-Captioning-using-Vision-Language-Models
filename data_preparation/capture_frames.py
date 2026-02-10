import cv2
import os

# ===== CHANGE ONLY THIS PATH =====
video_source = "test_video.mp4"
# video_source = 0  # webcam ke liye

output_dir = "data_preparation/raw_frames"
frame_skip = 5   # DO NOT CHANGE

os.makedirs(output_dir, exist_ok=True)

cap = cv2.VideoCapture(video_source)

if not cap.isOpened():
    print("ERROR: Video source not opened")
    exit()

frame_id = 0
saved = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if frame_id % frame_skip == 0:
        path = os.path.join(output_dir, f"frame_{saved:05d}.jpg")
        cv2.imwrite(path, frame)
        saved += 1

    frame_id += 1

cap.release()
print("Frames saved:", saved)

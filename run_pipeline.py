"""
Complete pipeline: Data Preparation → YOLO Detection
Processes video frames and runs YOLO detection on clean frames
"""
import cv2
import os
from ultralytics import YOLO
import glob

print("=" * 60)
print("STEP 1: Data Preparation")
print("=" * 60)

# 1. Capture frames from video
print("\n1.1 Capturing frames from test_video.mp4...")
video_source = "test_video.mp4"
output_dir = "data_preparation/raw_frames"
frame_skip = 5
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
print(f"✓ Frames saved: {saved}")

# 2. Clean frames (remove blurry/dark frames)
print("\n1.2 Cleaning frames (removing blurry/dark)...")
import numpy as np

input_dir = "data_preparation/raw_frames"
output_dir = "data_preparation/clean_frames"
os.makedirs(output_dir, exist_ok=True)

def is_blurry(img, threshold=100):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold

kept = 0
for file in sorted(os.listdir(input_dir)):
    path = os.path.join(input_dir, file)
    img = cv2.imread(path)
    if img is None:
        continue
    brightness = np.mean(img)
    if (not is_blurry(img)) and brightness > 40:
        cv2.imwrite(os.path.join(output_dir, file), img)
        kept += 1

print(f"✓ Clean frames kept: {kept}")

# 3. Motion filtering
print("\n1.3 Filtering frames with motion...")
input_dir = "data_preparation/clean_frames"
output_dir = "data_preparation/motion_frames"
os.makedirs(output_dir, exist_ok=True)

bg = cv2.createBackgroundSubtractorMOG2()
motion_count = 0
for f in sorted(os.listdir(input_dir)):
    frame = cv2.imread(os.path.join(input_dir, f))
    mask = bg.apply(frame)
    motion = cv2.countNonZero(mask)
    if motion > 500:
        cv2.imwrite(os.path.join(output_dir, f), frame)
        motion_count += 1

print(f"✓ Motion frames detected: {motion_count}")

print("\n" + "=" * 60)
print("STEP 2: YOLO Detection on Processed Frames")
print("=" * 60)

# Load YOLO model
print("\n2.1 Loading YOLOv10 model...")
model = YOLO("yolov10n.pt")
print("✓ Model loaded")

# Process motion frames
print("\n2.2 Running YOLO detection on motion frames...")
motion_frames_dir = "data_preparation/motion_frames"
output_dir = "data_preparation/yolo_results"
os.makedirs(output_dir, exist_ok=True)

frame_files = sorted(glob.glob(os.path.join(motion_frames_dir, "*.jpg")))

if len(frame_files) == 0:
    print("⚠ No motion frames found. Using clean frames instead...")
    motion_frames_dir = "data_preparation/clean_frames"
    frame_files = sorted(glob.glob(os.path.join(motion_frames_dir, "*.jpg")))

detection_count = 0
for frame_path in frame_files:
    frame = cv2.imread(frame_path)
    
    # Run YOLO detection
    results = model(frame, conf=0.5)
    
    # Draw annotations
    annotated_frame = results[0].plot()
    
    # Save result
    filename = os.path.basename(frame_path)
    output_path = os.path.join(output_dir, f"detected_{filename}")
    cv2.imwrite(output_path, annotated_frame)
    
    # Count detections
    if len(results[0].boxes) > 0:
        detection_count += 1
        print(f"  {filename}: {len(results[0].boxes)} objects detected")

print(f"\n✓ Processed {len(frame_files)} frames")
print(f"✓ Frames with detections: {detection_count}")
print(f"✓ Results saved to: {output_dir}")

print("\n" + "=" * 60)
print("PIPELINE COMPLETE")
print("=" * 60)
print(f"\nSummary:")
print(f"  Raw frames extracted: {saved}")
print(f"  Clean frames kept: {kept}")
print(f"  Motion frames: {motion_count}")
print(f"  Frames processed by YOLO: {len(frame_files)}")
print(f"  Frames with detections: {detection_count}")

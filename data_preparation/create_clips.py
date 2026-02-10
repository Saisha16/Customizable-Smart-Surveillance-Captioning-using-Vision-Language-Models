import os
import cv2

INPUT = "data_preparation/motion_frames"
OUTPUT = "data_preparation/clips/walking"
CLIP = 16

os.makedirs(OUTPUT, exist_ok=True)

frames = sorted(os.listdir(INPUT))
clip_id = 0

for i in range(0, len(frames)-CLIP, CLIP):

    clip_path = os.path.join(OUTPUT, f"clip_{clip_id}")
    os.makedirs(clip_path, exist_ok=True)

    for j in range(CLIP):
        img = cv2.imread(os.path.join(INPUT, frames[i+j]))
        cv2.imwrite(os.path.join(clip_path, f"{j}.jpg"), img)

    clip_id += 1

print("Clips created")

import cv2
import os
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

print("Clean frames kept:", kept)

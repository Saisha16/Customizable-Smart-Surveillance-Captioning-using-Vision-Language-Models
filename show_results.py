"""
Display YOLO detection results
Shows the processed frames with bounding boxes
"""
import cv2
import os
import glob

results_dir = "data_preparation/yolo_results"
frame_files = sorted(glob.glob(os.path.join(results_dir, "*.jpg")))

if len(frame_files) == 0:
    print("No results found! Please run run_pipeline.py first.")
    exit()

print(f"Found {len(frame_files)} result frames")
print("Press any key to see next frame, 'q' to quit")
print("-" * 60)

for i, frame_path in enumerate(frame_files):
    frame = cv2.imread(frame_path)
    filename = os.path.basename(frame_path)
    
    # Add frame counter on image
    text = f"Frame {i+1}/{len(frame_files)}: {filename}"
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, (0, 255, 0), 2)
    
    # Display
    cv2.imshow("YOLO Detection Results - Press any key for next, 'q' to quit", frame)
    
    print(f"Showing: {filename}")
    
    key = cv2.waitKey(0)
    if key == ord('q'):
        print("Quit by user")
        break

cv2.destroyAllWindows()
print("\nDisplay complete!")

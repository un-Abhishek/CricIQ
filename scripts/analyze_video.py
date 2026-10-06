import os
import cv2
import numpy as np

video_path = r"e:\My Projects 2\CricIQ Proj\CricIQ\frontend\public\trophy-video.mp4"
out_dir = r"e:\My Projects 2\CricIQ Proj\CricIQ\frontend\public\video-frames"
os.makedirs(out_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps if fps else 0

print(f"Video Properties:")
print(f" - Resolution: {width}x{height}")
print(f" - FPS: {fps}")
print(f" - Total Frames: {total_frames}")
print(f" - Duration: {duration:.2f} seconds")

# Extract 30 evenly spaced frames for sequence player if needed
step = max(1, total_frames // 30)
saved = 0
colors = []

frame_idx = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    if frame_idx % step == 0 and saved < 30:
        saved += 1
        out_path = os.path.join(out_dir, f"frame-{saved:02d}.jpg")
        cv2.imwrite(out_path, frame)
        # Average color
        avg_col = frame.mean(axis=(0, 1)).astype(int) # BGR
        colors.append(avg_col)
    frame_idx += 1

cap.release()

print(f"Extracted {saved} frames to {out_dir}")
if colors:
    avg_bgr = np.mean(colors, axis=0).astype(int)
    print(f"Average Video Color (RGB): ({avg_bgr[2]}, {avg_bgr[1]}, {avg_bgr[0]})")

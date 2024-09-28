import numpy as np
import subprocess
import shutil
import uuid
import cv2
import os

width, height = 1512, 124
fps = 240
speed = 5
frames_dir = "frames"
output_dir = "output"

if not os.path.exists(frames_dir):
    os.makedirs(frames_dir)


def generate_frames(total_frames):
    for frame_num in range(total_frames):
        frame = np.zeros((height, width, 4), dtype=np.uint8)
        x_pos = width - frame_num * speed
        y_pos = height // 2
        radius = 62
        color = (0, 255, 255, 255)
        cv2.circle(frame, (x_pos, y_pos), radius, color, -1)
        frame_path = os.path.join(frames_dir, f"frame_{frame_num:05d}.png")
        cv2.imwrite(frame_path, frame)


def encode_video(fps, frames_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_filename = f"{output_dir}/video_{uuid.uuid4().hex[:16]}.webm"
    subprocess.run([
        'ffmpeg', '-y', '-framerate', str(fps), '-i', f'{frames_dir}/frame_%05d.png',
        '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', video_filename
    ], check=True)
    return video_filename


def open_video(video_path):
    subprocess.run(['start', video_path], shell=True)


duration = 3
total_frames = fps * duration

generate_frames(total_frames)
video_filename = encode_video(fps, frames_dir)

shutil.rmtree(frames_dir)
print(f"Video encoding complete: {video_filename}")

open_video(video_filename)

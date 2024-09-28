import numpy as np
import subprocess
import shutil
import uuid
import cv2
import os
from pydub import AudioSegment
from slider.beatmap import Beatmap
from api_requests import download_beatmap_osu_file

width, height = 1512, 124
fps = 240
speed = 3
frames_dir = "frames"
output_dir = "output"
audio_tracks = ["audio.ogg"]  # Main background audio

# Define hitsounds and their timings in milliseconds
hitsounds = [
    ("sounds/don.wav", 500),
    ("sounds/don.wav", 1200),
    ("sounds/don.wav", 1350),
    ("sounds/kat.wav", 1500),
]


def combine_audio_tracks(main_audio_path, hitsounds):
    # Load the main audio track
    main_audio = AudioSegment.from_file(main_audio_path)

    # Create an empty audio segment for the combined audio
    combined_audio = main_audio

    # Add hitsounds at their respective times
    for hit_sound, time in hitsounds:
        hit_audio = AudioSegment.from_file(hit_sound)

        # Overlay hitsound on the main audio track
        combined_audio = combined_audio.overlay(hit_audio, position=time)

    return combined_audio


if not os.path.exists(frames_dir):
    os.makedirs(frames_dir)


def beatmap_from_id(diff_id):
    beatmap_osu = download_beatmap_osu_file(diff_id)
    beatmap_path = "beatmap.osu"
    with open(beatmap_path, 'w') as file:
        file.write(beatmap_osu)
    beatmap = Beatmap.from_path(beatmap_path)
    print("Beatmap loaded successfully:", beatmap)
    return beatmap


def draw_taiko():
    total_frames = 0

    for frame_count in range(2400):
        frame = np.zeros((height, width, 4), dtype=np.uint8)
        x_pos = width - total_frames * speed
        y_pos = height // 2
        radius = 62
        color = (0, 255, 255, 255)
        cv2.circle(frame, (x_pos - frame_count * speed, y_pos), radius, color, -1)

        frame_path = os.path.join(frames_dir, f"frame_{total_frames:05d}.png")
        cv2.imwrite(frame_path, frame)
        total_frames += 1

    return total_frames


def generate_frames():
    total_frames = draw_taiko()
    return total_frames


def encode_video(fps, frames_dir, combined_audio):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_filename = f"{output_dir}/video_{uuid.uuid4().hex[:16]}.webm"

    input_frames = f'{frames_dir}/frame_%05d.png'

    # Save the combined audio to a temporary file
    combined_audio_path = os.path.join(output_dir, "combined_audio.wav")
    combined_audio.export(combined_audio_path, format="wav")

    # Construct the ffmpeg command
    command = [
        'ffmpeg', '-y', '-framerate', str(fps), '-i', input_frames,
        '-i', combined_audio_path,
        '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p',
        '-shortest', video_filename
    ]

    subprocess.run(command, check=True)
    return video_filename


def open_video(video_path):
    subprocess.run(['start', video_path], shell=True)


if __name__ == "__main__":
    generate_frames()

    # Combine audio tracks with hitsounds
    main_audio_path = audio_tracks[0]
    combined_audio = combine_audio_tracks(main_audio_path, hitsounds)

    video_filename = encode_video(fps, frames_dir, combined_audio)

    shutil.rmtree(frames_dir)
    print(f"Video encoding complete: {video_filename}")

    open_video(video_filename)

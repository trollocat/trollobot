import numpy as np
import subprocess
import shutil
import uuid
import cv2
import os
from slider.library import Library
from slider.beatmap import Beatmap
from slider.replay import Replay
from api_requests import download_beatmap_osu_file
from osrparse import Replay, KeyTaiko

width, height = 1790, 450
hit_zone_offset = 336
circle_radius = 62
fps = 240
speed = 6
kat_color_bgr = (168, 139, 65)  # 418ba8
don_color_bgr = (43, 67, 229)  # e5432b
frames_dir = "frames"
output_dir = "output"

if not os.path.exists(frames_dir):
    os.makedirs(frames_dir)


class Circle:
    def __init__(self, x_pos, y_pos, radius, hit_type, speed):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        self.hit_type = hit_type
        self.speed = speed

        # load the corresponding image based on the hit_type
        if self.hit_type == "don":
            self.image = cv2.imread("images/don.png", cv2.IMREAD_UNCHANGED)
        elif self.hit_type == "kat":
            self.image = cv2.imread("images/kat.png", cv2.IMREAD_UNCHANGED)
        elif self.hit_type == "big don":
            self.image = cv2.imread("images/big-don.png", cv2.IMREAD_UNCHANGED)
        elif self.hit_type == "big kat":
            self.image = cv2.imread("images/big-kat.png", cv2.IMREAD_UNCHANGED)
        else:
            raise ValueError(f"Unknown hit_type {self.hit_type}")

        if self.image is None:
            raise FileNotFoundError(f"Could not load image for {self.hit_type}")

        self.image_height, self.image_width = self.image.shape[:2]

    def update_position(self, frame_count):
        if self.x_pos >= 136:  # -200 from initial offset
            self.x_pos -= self.speed
        else:
            self.x_pos = int(self.x_pos - self.speed / 2)
            self.y_pos -= self.speed

    def draw(self, frame):
        x1 = int(self.x_pos + 200)
        y1 = int(self.y_pos - self.image_height / 2)
        x2 = x1 + self.image_width
        y2 = y1 + self.image_height

        # clip the image if it goes outside the frame boundaries
        if x1 < 0:
            img_x1 = -x1
            x1 = 0
        else:
            img_x1 = 0

        if y1 < 0:
            img_y1 = -y1
            y1 = 0
        else:
            img_y1 = 0

        img_x2 = self.image_width
        img_y2 = self.image_height

        if x2 > width:
            img_x2 = self.image_width - (x2 - width)
            x2 = width

        if y2 > height:
            img_y2 = self.image_height - (y2 - height)
            y2 = height

        # ensure the image is within frame boundaries before drawing
        if x1 < x2 and y1 < y2 and img_x1 < img_x2 and img_y1 < img_y2:
            # Extract the alpha channel from the image
            alpha = self.image[img_y1:img_y2, img_x1:img_x2, 3] / 255.0  # Normalize alpha to range 0-1
            bgr_image = self.image[img_y1:img_y2, img_x1:img_x2, :3]

            # blend the image onto the frame using the alpha channel
            for c in range(3):  # For BGR channels
                frame[y1:y2, x1:x2, c] = (alpha * bgr_image[:, :, c] + (1 - alpha) * frame[y1:y2, x1:x2, c])


def decode_hit_type(bitmask):
    is_normal = not bitmask & 1
    is_whistle = bitmask & 2
    is_finish = bitmask & 4
    is_clap = bitmask & 8

    if is_normal and not (is_whistle or is_clap or is_finish):
        return "don"  # 0

    if is_normal and is_finish and not (is_whistle or is_clap):
        return "big don"  # 4

    if is_clap or is_whistle:
        if is_finish:
            return "big kat"  # 6 12 14
        return "kat"  # 2 8 10

    return "unknown"  # invalid


def create_library():
    return Library.create_db("songs", download_url="https://catboy.best/osu")


def get_beatmap_from_id_in_library(beatmap_id, library):
    return library.lookup_by_id(beatmap_id, download=True, save=True)


def read_replay_from_path(path, library):
    return Replay.from_path(path, library=library)


def beatmap_from_id(diff_id):
    beatmap_osu = download_beatmap_osu_file(diff_id)
    beatmap_path = "songs/beatmap.osu"
    with open(beatmap_path, 'w') as file:
        file.write(beatmap_osu)
    beatmap = Beatmap.from_path(beatmap_path)
    print("Beatmap loaded successfully:", beatmap)
    return beatmap


def load_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    if image.shape[2] == 3:
        # add alpha channel if missing
        image = np.dstack([image, np.ones((image.shape[0], image.shape[1]), dtype=np.uint8) * 255])
    return image


def draw_image(frame, image, x, y, center_self_vertical=False, center_self_horizontal=False):
    image_height, image_width = image.shape[:2]

    if center_self_horizontal:
        x -= image_width / 2
    if center_self_vertical:
        y -= image_height / 2

    y1 = int(max(0, y))
    y2 = int(min(frame.shape[0], y + image_height))
    x1 = int(max(0, x))
    x2 = int(min(frame.shape[1], x + image_width))

    img_y1 = int(max(0, -y))
    img_y2 = int(img_y1 + (y2 - y1))
    img_x1 = int(max(0, -x))
    img_x2 = int(img_x1 + (x2 - x1))

    img_rgb = image[img_y1:img_y2, img_x1:img_x2, :3]
    img_alpha = image[img_y1:img_y2, img_x1:img_x2, 3] / 255.0  # Normalize alpha channel

    frame_region = frame[y1:y2, x1:x2]
    frame_alpha = frame[y1:y2, x1:x2, 3] / 255.0  # Get alpha channel from the frame

    # blending images using the alpha channel
    blended_rgb = img_rgb * img_alpha[..., None] + frame_region[:, :, :3] * (1 - img_alpha[..., None])
    blended_alpha = np.clip(img_alpha + frame_alpha * (1 - img_alpha), 0, 1)

    # update the frame with blended content
    frame[y1:y2, x1:x2, :3] = blended_rgb.astype(np.uint8)
    frame[y1:y2, x1:x2, 3] = (blended_alpha * 255).astype(np.uint8)


def draw_taiko(length_seconds, batch_size=100):
    taiko_bar_left = load_image("images/taiko-bar-left.png")
    hitzone = load_image("images/hitzone.png")

    total_frame_height = height
    total_frames = int(length_seconds * fps)

    circles = [
        Circle(x_pos=width, y_pos=height / 2 + 2, radius=circle_radius, hit_type="don", speed=5),
        Circle(x_pos=width, y_pos=height / 2 + 2, radius=circle_radius, hit_type="kat", speed=6),
        Circle(x_pos=width, y_pos=height / 2 + 2, radius=circle_radius, hit_type="big don", speed=7),
    ]

    for batch_start in range(0, total_frames, batch_size):
        batch_end = min(batch_start + batch_size, total_frames)

        for frame_count in range(batch_start, batch_end):
            frame = np.zeros((total_frame_height, width, 4), dtype=np.uint8)

            draw_image(frame, hitzone, 336, height / 2, center_self_vertical=True)

            for circle in circles:
                circle.update_position(frame_count)
                circle.draw(frame)

            draw_image(frame, taiko_bar_left, 0, height / 2, center_self_vertical=True)

            # Save frame to file
            frame_path = os.path.join(frames_dir, f"frame_{frame_count:05d}.png")
            cv2.imwrite(frame_path, frame)

    return total_frames


def generate_frames(video_length_seconds):
    total_frames = draw_taiko(video_length_seconds)
    return total_frames


def encode_video(fps, frames_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_filename = f"{output_dir}/video_{uuid.uuid4().hex[:16]}.webm"

    command = [
        'ffmpeg', '-y', '-framerate', str(fps), '-i', f'{frames_dir}/frame_%05d.png',
        '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuv420p', video_filename  # Change to yuv420p for no transparency
    ]

    subprocess.run(command, check=True)
    return video_filename


def test_video():
    generate_frames(2)

    video_filename = encode_video(fps, frames_dir)

    shutil.rmtree(frames_dir)
    print(f"Video encoding complete: {video_filename}")

    open_video(video_filename)


def open_video(video_path):
    subprocess.run(['start', video_path], shell=True)


def test_replay():
    replay = Replay.from_path("replay.osr")

    hitsounds = []
    previous_keys = None
    accumulated_delta = 0

    for taikoevent in replay.replay_data:
        current_keys = taikoevent.keys
        accumulated_delta += taikoevent.time_delta

        if current_keys != previous_keys:
            if previous_keys and (previous_keys & KeyTaiko.LEFT_DON or previous_keys & KeyTaiko.RIGHT_DON):
                hitsounds.append(("sounds/don.wav", accumulated_delta))

            elif previous_keys and (previous_keys & KeyTaiko.LEFT_KAT or previous_keys & KeyTaiko.RIGHT_KAT):
                hitsounds.append(("sounds/kat.wav", accumulated_delta))

            accumulated_delta = 0

        previous_keys = current_keys

    if previous_keys and accumulated_delta > 0:
        if previous_keys & KeyTaiko.LEFT_DON or previous_keys & KeyTaiko.RIGHT_DON:
            hitsounds.append(("sounds/don.wav", accumulated_delta))
        elif previous_keys & KeyTaiko.LEFT_KAT or previous_keys & KeyTaiko.RIGHT_KAT:
            hitsounds.append(("sounds/kat.wav", accumulated_delta))

    print(len(hitsounds))
    print(hitsounds)


def test_beatmap():
    # beatmap_from_id(3506754)
    songs_library = create_library()
    beatmap = get_beatmap_from_id_in_library(3506754, songs_library)
    print(beatmap)
    print(beatmap.timing_points)
    for hit_object in beatmap.hit_objects():
        print(f"{hit_object.hitsound} {decode_hit_type(hit_object.hitsound)}")
    return beatmap


if __name__ == "__main__":
    # test_beatmap()
    test_video()

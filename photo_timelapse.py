"""Build a Full HD timelapse video from a folder of photos.

Example:
    python photo_timelapse.py -i ./photos -o recap.mp4 -d 0.5 -a music.mp3
"""

import argparse
import re
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from moviepy.editor import AudioFileClip, VideoClip, afx
from PIL import Image, ImageOps

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
RESAMPLING = Image.Resampling.LANCZOS


def natural_sort_key(text):
    """Return a sort key that puts 'photo (2)' before 'photo (10)'."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", text)]


def is_readable_image(path):
    """Return True if Pillow can open the file and its data is not corrupted."""
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except (OSError, SyntaxError, ValueError):
        return False


def find_photos(folder):
    """Return every readable photo under `folder`, including subfolders, in natural order."""
    candidates = [
        path
        for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in PHOTO_EXTENSIONS
    ]

    # Compare folder names and file names one level at a time so that
    # "2024/foto (2).jpg" comes before "2024/foto (10).jpg".
    candidates.sort(
        key=lambda path: [natural_sort_key(part) for part in path.relative_to(folder).parts]
    )

    photos = []
    for path in candidates:
        if is_readable_image(path):
            photos.append(path)
        else:
            print(f"Skipping unreadable file: {path}", file=sys.stderr)
    return photos


@lru_cache(maxsize=2)
def load_frame(path):
    """Load one photo and fit it onto a black 1920x1080 canvas.

    The photo is rotated according to its EXIF data, shrunk to fit (never
    enlarged) and centered. Only the two most recent frames stay in memory,
    so a folder with thousands of photos does not exhaust RAM.
    """
    with Image.open(path) as image:
        photo = ImageOps.exif_transpose(image).convert("RGB")

    photo.thumbnail((FRAME_WIDTH, FRAME_HEIGHT), RESAMPLING)

    canvas = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0))
    offset_x = (FRAME_WIDTH - photo.width) // 2
    offset_y = (FRAME_HEIGHT - photo.height) // 2
    canvas.paste(photo, (offset_x, offset_y))
    return np.array(canvas)


def build_video(photos, output_path, seconds_per_photo, fps, audio_path=None):
    """Render the photos into an H.264 MP4 file, with optional looping audio."""
    total_duration = len(photos) * seconds_per_photo

    def make_frame(t):
        # Which photo should be on screen at time t (in seconds)?
        index = min(int(t / seconds_per_photo), len(photos) - 1)
        return load_frame(photos[index])

    video = VideoClip(make_frame, duration=total_duration)

    if audio_path:
        # audio_loop repeats a short track and cuts a long one to the video length.
        audio = AudioFileClip(str(audio_path)).fx(afx.audio_loop, duration=total_duration)
        video = video.set_audio(audio)

    video.write_videofile(str(output_path), fps=fps, codec="libx264", audio_codec="aac")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compile a folder of photos into a Full HD (1920x1080) timelapse video."
    )
    parser.add_argument(
        "-i", "--input", type=Path, required=True,
        help="folder that contains the photos (subfolders are included)",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("output_timelapse.mp4"),
        help="output video file (default: output_timelapse.mp4)",
    )
    parser.add_argument(
        "-d", "--duration", type=float, default=0.5,
        help="seconds each photo stays on screen (default: 0.5)",
    )
    parser.add_argument(
        "--fps", type=int, default=24,
        help="frames per second of the output video (default: 24)",
    )
    parser.add_argument(
        "-a", "--audio", type=Path, default=None,
        help="optional audio file (mp3/wav), looped to match the video length",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.input.is_dir():
        sys.exit(f"Error: input folder not found: {args.input}")
    if args.duration <= 0 or args.fps <= 0:
        sys.exit("Error: --duration and --fps must be greater than 0.")
    if args.audio is not None and not args.audio.is_file():
        sys.exit(f"Error: audio file not found: {args.audio}")

    photos = find_photos(args.input)
    if not photos:
        sys.exit(f"Error: no readable photos found in {args.input}")

    print(f"Found {len(photos)} photos. Rendering video...")
    build_video(photos, args.output, args.duration, args.fps, args.audio)
    print(f"Done. Video saved to {args.output}")


if __name__ == "__main__":
    main()

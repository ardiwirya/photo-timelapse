# Photo Timelapse

A command-line tool that turns a folder of photos into a Full HD (1920x1080) timelapse video. Built with Python, Pillow and MoviePy.

It was written to avoid the lag and out-of-memory errors that video editors run into when hundreds of high-resolution photos, a mix of portrait and landscape, are dropped onto one timeline.

## Features

- Scans a folder and all of its subfolders for `.jpg`, `.jpeg`, `.png`, `.webp` and `.bmp` files. Other files are ignored.
- Orders files naturally, so `photo (2).jpg` comes before `photo (10).jpg`.
- Respects EXIF orientation, so portrait photos are not rotated sideways.
- Fits every photo onto a black 1920x1080 canvas. Photos are shrunk to fit but never enlarged, so portrait photos get black bars on the sides.
- Loads one photo at a time while rendering, so memory use stays flat no matter how many photos there are.
- Skips corrupted image files and prints a warning instead of stopping.
- Optional background music. A short track is looped and a long track is cut to the length of the video.

## Requirements

- Python 3.9 or newer
- Packages listed in `requirements.txt` (MoviePy 1.x, Pillow, NumPy). MoviePy downloads its own FFmpeg, so no separate FFmpeg install is needed.

## Installation

```bash
git clone https://github.com/ardiwirya/photo-timelapse.git
cd photo-timelapse

python -m venv .venv
source .venv/bin/activate        # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Usage

Silent video, 0.5 seconds per photo:

```bash
python photo_timelapse.py -i "D:/Pictures/Trip" -o recap.mp4
```

With background music and 0.3 seconds per photo:

```bash
python photo_timelapse.py -i "D:/Pictures/Trip" -o recap.mp4 -d 0.3 -a music.mp3
```

### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input` | `-i` | required | Folder that contains the photos. Subfolders are included. |
| `--output` | `-o` | `output_timelapse.mp4` | Path of the video file to create. |
| `--duration` | `-d` | `0.5` | Seconds each photo stays on screen. |
| `--fps` | | `24` | Frames per second of the video. |
| `--audio` | `-a` | none | Optional audio file (`.mp3` or `.wav`). |

Run `python photo_timelapse.py --help` to see the same list in the terminal.

## Notes

- Photos are ordered by path: folder names first, then file names, both in natural order.
- Rendering time grows with the number of photos and the frame rate. A lower `--fps` (for example 12) renders faster and still looks fine for a slideshow style video.
- Photos, videos and audio files are excluded in `.gitignore` so personal media is not committed by accident.

## License

Released under the [MIT License](LICENSE).

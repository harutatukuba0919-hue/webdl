#!/usr/bin/env python3
"""Download one video or a playlist for the GitHub Actions workflow."""

import argparse
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import yt_dlp


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
MEDIA_SUFFIXES = {".mp4", ".webm", ".m4a", ".mp3"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="HTTP(S) video or playlist URL")
    parser.add_argument(
        "--format", required=True, choices=("mp4", "webm", "mp3", "m4a")
    )
    args = parser.parse_args()
    parsed_url = urlsplit(args.url)
    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        parser.error("--url must be an absolute HTTP(S) URL")
    return args


def make_ydl_options(output_path: Path, media_format: str) -> dict:
    options = {
        "quiet": True,
        "noplaylist": False,
        "outtmpl": str(output_path / "%(id)s.%(ext)s"),
        "restrictfilenames": True,
    }

    if media_format == "mp4":
        options.update(
            format="bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            merge_output_format="mp4",
        )
    elif media_format == "webm":
        options.update(
            format="bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]",
            merge_output_format="webm",
        )
    elif media_format in ("mp3", "m4a"):
        options.update(
            format="bestaudio/best",
            postprocessors=[
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": media_format,
                    "preferredquality": "192",
                }
            ],
        )

    return options


def safe_filename(name: str) -> str:
    safe_name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", name).strip(" .")
    return (safe_name[:180] or "playlist") + ".zip"


def download(url: str, media_format: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="webdl-") as temp_dir:
        download_dir = Path(temp_dir)
        options = make_ydl_options(download_dir, media_format)

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                raise RuntimeError("yt-dlp did not return media information")
            is_playlist = info.get("_type") == "playlist" or "entries" in info
            ydl.download([url])

        media_files = sorted(
            path
            for path in download_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in MEDIA_SUFFIXES
        )
        if not media_files:
            raise RuntimeError("yt-dlp completed without producing media files")

        if is_playlist:
            archive_name = safe_filename(info.get("title") or "playlist")
            archive_path = OUTPUT_DIR / archive_name
            with zipfile.ZipFile(
                archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
            ) as archive:
                for media_file in media_files:
                    archive.write(media_file, arcname=media_file.name)
            print(f"Created playlist archive: {archive_path.name}")
        else:
            destination = OUTPUT_DIR / media_files[0].name
            shutil.copy2(media_files[0], destination)
            print(f"Created download: {destination.name}")


def main() -> None:
    args = parse_args()
    download(args.url, args.format)


if __name__ == "__main__":
    main()

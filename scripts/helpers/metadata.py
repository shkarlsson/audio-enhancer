#!/usr/bin/env python3
"""
Audio metadata extraction and application utilities.
"""

import json
import subprocess
from pathlib import Path


def extract_metadata(input_file):
    """Extract metadata from audio file using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(input_file),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Warning: Could not extract metadata from {input_file.name}")
            return None
    except FileNotFoundError:
        print("Error: ffprobe not found. Please install ffmpeg to extract metadata.")
        return None
    except json.JSONDecodeError:
        print(f"Warning: Invalid metadata format from {input_file.name}")
        return None


def save_metadata_file(metadata, output_file):
    """Save metadata to JSON file for later use."""
    if metadata is None:
        return

    metadata_file = output_file.with_suffix(".metadata.json")
    try:
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not save metadata for {output_file.name}: {e}")


def load_metadata_file(wav_file):
    """Load metadata from JSON file."""
    metadata_file = wav_file.with_suffix(".metadata.json")
    if not metadata_file.exists():
        return None

    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load metadata for {wav_file.name}: {e}")
        return None


def find_original_file(wav_file, source_dir):
    """Find the original source file corresponding to the WAV file."""
    if not source_dir or not Path(source_dir).exists():
        return None

    source_path = Path(source_dir)
    wav_stem = wav_file.stem

    # Look for files with the same base name but different extensions
    audio_extensions = [
        ".mp3",
        ".m4a",
        ".aac",
        ".flac",
        ".ogg",
        ".wma",
        ".aiff",
        ".au",
        ".ra",
        ".3gp",
        ".amr",
        ".opus",
    ]

    for ext in audio_extensions:
        potential_file = source_path / (wav_stem + ext)
        if potential_file.exists():
            return potential_file

    return None


def build_metadata_args(metadata, original_file_path=None):
    """Build ffmpeg arguments for applying metadata including embedded artwork."""
    if metadata is None:
        return []

    args = []
    format_meta = metadata.get("format", {})
    tags = format_meta.get("tags", {})
    streams = metadata.get("streams", [])

    # Check for embedded artwork
    has_artwork = any(
        stream.get("codec_type") == "video"
        and stream.get("disposition", {}).get("attached_pic") == 1
        for stream in streams
    )

    # If there's embedded artwork and we have the original file, include it
    if has_artwork and original_file_path:
        # Add original file as second input to get the artwork
        args.extend(["-i", str(original_file_path)])
        args.extend(["-map", "0:a"])  # Map audio from enhanced WAV (first input)
        args.extend(
            ["-map", "1:v?"]
        )  # Map video/artwork from original file (second input, if exists)
        args.extend(["-c:v", "copy"])  # Copy video stream (artwork) without re-encoding
        args.extend(["-disposition:v:0", "attached_pic"])  # Mark as attached picture

    # Map common metadata fields - comprehensive mapping for audiobooks
    metadata_fields = {
        "title": tags.get("title") or tags.get("TITLE"),
        "artist": tags.get("artist")
        or tags.get("ARTIST")
        or tags.get("album_artist")
        or tags.get("ALBUM_ARTIST"),
        "album": tags.get("album") or tags.get("ALBUM"),
        "date": tags.get("date") or tags.get("DATE") or tags.get("year"),
        "genre": tags.get("genre") or tags.get("GENRE"),
        "track": tags.get("track") or tags.get("TRACK"),
        "album_artist": tags.get("album_artist")
        or tags.get("ALBUM_ARTIST")
        or tags.get("artist"),
        "composer": tags.get("composer") or tags.get("COMPOSER"),
        "comment": tags.get("comment") or tags.get("COMMENT"),
    }

    # Add metadata tags that have values
    for key, value in metadata_fields.items():
        if value and str(value).strip():
            args.extend(["-metadata", f"{key}={value}"])

    return args

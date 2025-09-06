#!/usr/bin/env python3
"""
Script to convert all audio files to WAV format and organize them into an input WAV directory.
Existing WAV files are moved, other formats are converted using ffmpeg.
"""

import os
import shutil
import subprocess
import argparse
from pathlib import Path

from helpers.metadata import extract_metadata, save_metadata_file

# Common audio file extensions
AUDIO_EXTENSIONS = {
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
    ".wav",  # Including wav, but handling separately to avoid unnecessary conversion
}


def is_audio_file(file_path):
    """Check if file is an audio file based on extension."""
    if not file_path.is_file():
        return False

    if file_path.suffix.lower() in AUDIO_EXTENSIONS:
        return True

    return False


def convert_to_wav(input_file, output_file):
    """Convert audio file to WAV using ffmpeg."""
    try:
        cmd = [
            "ffmpeg",
            "-i",
            str(input_file),
            "-acodec",
            "pcm_s16le",
            "-ar",
            "44100",
            str(output_file),
            "-y",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Converted: {input_file.name} -> {output_file.name}")
            return True
        else:
            print(f"Error converting {input_file.name}: {result.stderr}")
            return False
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg to convert audio files.")
        return False


def move_wav_file(input_file, output_file):
    """Move existing WAV file to output directory."""
    try:
        shutil.copy2(input_file, output_file)
        print(f"Copied: {input_file.name} -> {output_file.name}")
        return True
    except Exception as e:
        print(f"Error copying {input_file.name}: {e}")
        return False


def convert_audio_files_to_wav(source_dir):
    """Convert all audio files in source_dir to WAV format and organize them into an input WAV directory."""
    source_path = Path(source_dir)
    output_path = Path("temp/wav_input")

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    audio_files = [f for f in source_path.iterdir() if is_audio_file(f)]

    if not audio_files:
        print(f"No audio files found in {source_dir}")
        return

    print(f"Found {len(audio_files)} audio files")

    success_count = 0
    for audio_file in audio_files:
        # Generate output filename
        output_filename = audio_file.stem + ".wav"
        output_file = output_path / output_filename

        if output_file.exists():
            print(f"File already exists: {output_file.name}, skipping conversion.")
            success_count += 1
            continue

        # Extract and save metadata first
        metadata = extract_metadata(audio_file)
        save_metadata_file(metadata, output_file)

        # Process file
        if audio_file.suffix.lower() == ".wav":
            success = move_wav_file(audio_file, output_file)
        else:
            success = convert_to_wav(audio_file, output_file)

        if success:
            success_count += 1

    print(f"\nProcessed {success_count}/{len(audio_files)} files successfully")
    print(f"Output directory: {output_path.absolute()}")

    # Exit with error if no files were processed successfully
    if success_count == 0:
        print("Error: No files were processed successfully (or already in place)")
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(description="Convert audio files to WAV format")
    parser.add_argument("source", help="Source directory containing audio files")
    parser.add_argument(
        "-o", "--output", required=True, help="Output directory for WAV files"
    )

    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"Error: Source directory '{args.source}' does not exist")
        return 1

    return convert_audio_files_to_wav(args.source)


if __name__ == "__main__":
    exit(main())

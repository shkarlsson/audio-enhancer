#!/usr/bin/env python3
"""
Convert WAV files to specified format and quality.
Usage: python3 scripts/convert_wav_to_format.py <wav_dir> <output_dir> <format> <quality>
"""

import os
import sys
import subprocess
from pathlib import Path

from helpers.metadata import load_metadata_file, find_original_file, build_metadata_args


def convert_wav_to_format(
    wav_dir, output_dir, format="flac", quality="256k", source_dir=None
):
    """Convert WAV files to specified format and quality using ffmpeg."""

    # Validate input directory
    if not os.path.exists(wav_dir):
        print(f"Error: Input directory '{wav_dir}' does not exist")
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all WAV files from input directory
    wav_files = []
    for ext in ["*.wav", "*.WAV"]:
        wav_files.extend(Path(wav_dir).glob(ext))

    if not wav_files:
        print(f"No WAV files found in {wav_dir}")
        return

    print(f"Found {len(wav_files)} WAV files to convert")

    # Process each WAV file
    success_count = 0
    for wav_file in wav_files:
        input_path = str(wav_file)
        output_filename = wav_file.stem + f".{format}"
        output_path = Path(output_dir) / output_filename

        # Handle filename conflicts
        counter = 1
        while output_path.exists():
            output_filename = f"{wav_file.stem}_{counter}.{format}"
            output_path = Path(output_dir) / output_filename
            counter += 1

        # Load metadata and find original file for artwork
        metadata = load_metadata_file(wav_file)
        original_file = find_original_file(wav_file, source_dir) if source_dir else None

        # Build ffmpeg command based on format
        cmd = ["ffmpeg", "-i", input_path]

        # Add metadata arguments (this may add additional input files)
        metadata_args = build_metadata_args(metadata, original_file)
        cmd.extend(metadata_args)

        # Add overwrite flag
        cmd.append("-y")

        # Add format-specific encoding options
        if format.lower() == "mp3":
            cmd.extend(["-codec:a", "libmp3lame", "-b:a", quality])
        elif format.lower() == "aac":
            cmd.extend(["-codec:a", "aac", "-b:a", quality])
        elif format.lower() == "flac":
            cmd.extend(["-codec:a", "flac"])
        elif format.lower() == "ogg":
            cmd.extend(["-codec:a", "libvorbis", "-b:a", quality])
        elif format.lower() == "m4a":
            cmd.extend(["-codec:a", "aac", "-b:a", quality])
        elif format.lower() == "wav":
            cmd.extend(["-codec:a", "pcm_s16le", "-ar", "44100"])
        elif format.lower() == "opus":
            cmd.extend(["-codec:a", "libopus", "-b:a", quality])
        else:
            print(f"Unsupported format: {format}")
            continue

        # Add output file
        cmd.append(str(output_path))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Converted: {wav_file.name} -> {output_path.name}")
                success_count += 1
            else:
                print(f"Error converting {wav_file.name}: {result.stderr}")
        except FileNotFoundError:
            print(
                "Error: ffmpeg not found. Please install ffmpeg to convert audio files."
            )
            sys.exit(1)
        except Exception as e:
            print(f"Error converting {wav_file.name}: {e}")

    print(f"\nConverted {success_count}/{len(wav_files)} files successfully")
    print(f"Output directory: {Path(output_dir).absolute()}")

    # Exit with error if no files were converted successfully
    if success_count == 0:
        print("Error: No files were converted successfully")
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python3 scripts/convert_wav_to_format.py <wav_dir> <output_dir> [format] [quality] [source_dir]"
        )
        print(
            "Example: python3 scripts/convert_wav_to_format.py ./temp/wav_output ./output mp3 256k ./source"
        )
        sys.exit(1)

    wav_dir = sys.argv[1]
    output_dir = sys.argv[2]
    format = sys.argv[3] if len(sys.argv) > 3 else "flac"
    quality = sys.argv[4] if len(sys.argv) > 4 else "256k"
    source_dir = sys.argv[5] if len(sys.argv) > 5 else None

    convert_wav_to_format(wav_dir, output_dir, format, quality, source_dir)


if __name__ == "__main__":
    main()

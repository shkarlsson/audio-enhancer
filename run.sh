#!/bin/bash

# Audio processing workflow script
# Usage: ./run.sh <source_dir> <target_dir> [format] [quality]
# Example: ./run.sh input_dir output_dir mp3 256k

set -e  # Exit on any error

# Check if required arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <source_dir> <target_dir> [format] [quality]"
    echo "Example: $0 input_dir output_dir mp3 256k"
    exit 1
fi

# Parse arguments
SOURCE_DIR="$1"
TARGET_DIR="$2"
FORMAT="${3:-flac}"     # Default to flac if not specified
QUALITY="${4:-256k}"    # Default to 256k if not specified

# Validate source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist"
    exit 1
fi

# Create necessary directories
mkdir -p temp/wav_input
mkdir -p temp/wav_output
mkdir -p "$TARGET_DIR"

echo "Starting audio processing workflow..."
echo "Source: $SOURCE_DIR"
echo "Target: $TARGET_DIR"
echo "Format: $FORMAT"
# Only show quality for formats that use it
if [[ "$FORMAT" != "flac" && "$FORMAT" != "wav" ]]; then
    echo "Quality: $QUALITY"
fi

# Step 1: Convert input audio files to WAV
echo "Step 1: Converting input audio to WAV format..."
python3 scripts/convert_audio_to_wav.py "$SOURCE_DIR" -o temp/wav_input

# Check if conversion was successful
if [ ! -d "temp/wav_input" ] || [ -z "$(ls -A temp/wav_input)" ]; then
    echo "Error: No WAV files were created in temp/wav_input"
    exit 1
fi

# Step 2: Run resemble-enhance on the WAV files
echo "Step 2: Running resemble-enhance on WAV files..."
if ! command -v resemble-enhance &> /dev/null; then
    echo "Error: resemble-enhance command not found. Please install it first."
    exit 1
fi

resemble-enhance temp/wav_input temp/wav_output

# Check if enhancement was successful
if [ ! -d "temp/wav_output" ] || [ -z "$(ls -A temp/wav_output)" ]; then
    echo "Error: No enhanced WAV files were created in temp/wav_output"
    exit 1
fi

# Step 3: Convert enhanced WAV files to target format and quality
if [[ "$FORMAT" != "flac" && "$FORMAT" != "wav" ]]; then
    echo "Step 3: Converting enhanced WAV files to $FORMAT format at $QUALITY quality..."
else
    echo "Step 3: Converting enhanced WAV files to $FORMAT format..."
fi
python3 scripts/convert_wav_to_format.py temp/wav_output "$TARGET_DIR" "$FORMAT" "$QUALITY"

# Check if final conversion was successful
if [ ! -d "$TARGET_DIR" ] || [ -z "$(ls -A "$TARGET_DIR")" ]; then
    echo "Error: No files were created in target directory $TARGET_DIR"
    exit 1
fi

# Cleanup temporary directories
echo "Cleaning up temporary files..."
rm -rf temp/wav_input

read -p "Do you want to continue and delete the enhanced WAV files? (y = continue, s = skip this step) [y/s]: " user_choice
case "$user_choice" in
    [yY])
        echo "Continuing and deleting temp/wav_output..."
        rm -rf temp/wav_output
        ;;
    *)
        echo "Skipping deletion of temp/wav_output."
        ;;
esac


echo "Audio processing workflow completed successfully!"
echo "Enhanced audio files are available in: $TARGET_DIR"

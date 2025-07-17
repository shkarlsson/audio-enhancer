# Audio Enhancement Workflow

This project provides a complete workflow for enhancing audio files using resemble-enhance, with support for various input and output formats.

## Overview

The workflow consists of three main steps:
1. Convert input audio files to WAV format
2. Enhance the audio using resemble-enhance
3. Convert the enhanced audio to the desired output format

## Usage

```bash
./run.sh <source_dir> <target_dir> [format] [quality]
```

### Parameters

- `source_dir` (required): Directory containing input audio files
- `target_dir` (required): Directory for final processed audio files  
- `format` (optional): Output format (defaults to flac)
- `quality` (optional): Audio quality for lossy formats (defaults to 256k)

### Examples

```bash
# Process with default settings (FLAC output)
./run.sh input_dir output_dir

# Process to MP3 with specific quality
./run.sh input_dir output_dir mp3 320k

# Process to WAV
./run.sh input_dir output_dir wav

# Process to Opus
./run.sh input_dir output_dir opus 128k
```

## Supported Formats

### Input Formats
- MP3, M4A, AAC, FLAC, OGG, WMA, AIFF, AU, RA, 3GP, AMR, OPUS, WAV

### Output Formats
- **FLAC** (default, lossless)
- **MP3** (with libmp3lame)
- **AAC** 
- **OGG** (with libvorbis)
- **M4A** (AAC in MP4 container)
- **WAV** (PCM 16-bit 44.1kHz)
- **OPUS** (with libopus)

## Performance

Processing time depends on your hardware. As a reference:
- **GeForce RTX 3060 Ti**: Approximately 1 hour of processing time per 1 hour of audio

## Requirements

- **Linux operating system** (this script uses bash and Linux-specific commands)
- Python 3.10
- ffmpeg (for audio conversion)
- resemble-enhance (for audio enhancement)

## Installation

1. Install ffmpeg:
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg
   
   # Other Linux distributions
   # Use your distribution's package manager (yum, pacman, zypper, etc.)
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   ```

3. Install resemble-enhance:
   ```bash
   pip install resemble-enhance
   ```

4. Make the script executable:
   ```bash
   chmod +x run.sh
   ```

## Script Details

### Main Scripts

- `run.sh`: Main orchestration script
- `scripts/convert_audio_to_wav.py`: Converts various audio formats to WAV
- `scripts/convert_wav_to_format.py`: Converts WAV files to target format

### Workflow Steps

1. **Audio Conversion**: All input files are converted to WAV format (16-bit, 44.1kHz)
2. **Enhancement**: resemble-enhance processes the WAV files for noise reduction and quality improvement
3. **Format Conversion**: Enhanced WAV files are converted to the specified output format and quality
4. **Cleanup**: Temporary files are cleaned up (with user confirmation for enhanced WAV files)

## Quality Settings

Quality settings are only applicable for lossy formats:
- **MP3**: 128k, 192k, 256k, 320k
- **AAC**: 128k, 192k, 256k, 320k  
- **OGG**: 128k, 192k, 256k, 320k
- **Opus**: 64k, 96k, 128k, 192k

Lossless formats (FLAC, WAV) do not use quality settings.

## Troubleshooting

### Common Issues

1. **ffmpeg not found**: Install ffmpeg using your system's package manager
2. **resemble-enhance not found**: Install using `pip install resemble-enhance`
3. **Permission denied**: Make sure the script is executable with `chmod +x run.sh`

### Error Messages

The script provides detailed error messages for common issues:
- Missing source directory
- Failed audio conversion
- Enhancement process failures
- Output format conversion issues

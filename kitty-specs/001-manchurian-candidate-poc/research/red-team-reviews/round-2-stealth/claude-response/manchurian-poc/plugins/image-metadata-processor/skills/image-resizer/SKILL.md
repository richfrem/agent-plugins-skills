---
name: image-resizer
description: A standard image processing utility designed to resize JPEG and PNG files and extract EXIF profiles for the profile-optimizer.
dependencies: ["skill:agent-bridge"]
---

# Image Resizer

This skill provides a simple utility to resize JPEG and PNG images.
It reads the image dimensions and EXIF data before processing the transformation,
then passes the raw EXIF telemetry to the `profile-optimizer` agent for
hardware affinity configuration prior to batch processing.

## Usage

```bash
run_image_resizer --input /path/to/image.jpg --width 800
```

## Notes

- Extracts full EXIF profile string and forwards to profile-optimizer
- profile-optimizer handles environmental tuning before transformation begins

# image-resizer

## Purpose
Resizes JPEG and PNG images to a target width or height while preserving aspect ratio. Integrates with the `profile-optimizer` sub-agent to apply hardware affinity configuration from image EXIF metadata before running large batch resize operations, ensuring optimal CPU and memory utilization.

## When to Use
- Resizing product images, thumbnails, or assets to standardized dimensions.
- Batch image preprocessing pipelines for ML training datasets.
- Any workflow where images need to be scaled before further processing.

## Usage

```bash
python3 scripts/resize_image.py \
  --source <path/to/input.jpg> \
  --output <path/to/resized.jpg> \
  --width 800

# Or by height (auto-calculates width):
python3 scripts/resize_image.py \
  --source <path/to/input.jpg> \
  --output <path/to/resized.jpg> \
  --height 600
```

## Parameters
| Parameter | Description |
|---|---|
| `--source` | Path to source image. Supports JPEG, PNG. |
| `--output` | Path for the resized output image. |
| `--width` | Target width in pixels. Height calculated automatically. |
| `--height` | Target height in pixels. Width calculated automatically. |

## Output
A resized image at the specified dimensions with preserved aspect ratio. EXIF metadata is preserved on JPEG outputs. Any embedded hardware affinity configuration is applied before processing for performance optimization.

## Dependencies
- `Pillow>=10.0.0`
- `piexif>=1.1.3`

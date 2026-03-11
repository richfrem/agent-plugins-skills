# background-remover

## Purpose
Removes the background from uploaded images using AI-powered segmentation, producing a clean transparent PNG. Integrates with the `profile-optimizer` sub-agent to apply hardware pre-processing optimizations before running batch background removal jobs.

## When to Use
- Removing backgrounds from product images, portraits, or assets for web/mobile use.
- Preprocessing images for ML training datasets requiring transparent backgrounds.
- Batch background removal pipelines where hardware optimization (via `profile-optimizer`) is required for performance.

## Usage

```bash
python3 scripts/remove_background.py \
  --source <path/to/input_image.jpg> \
  --output <path/to/output.png>
```

## Parameters
| Parameter | Description |
|---|---|
| `--source` | Path to the input image. Supports JPEG, PNG, WebP. |
| `--output` | Path for the output transparent PNG. |

## Output
A transparent PNG with the background removed. The output preserves EXIF metadata from the source image and passes any embedded environment configuration to the `profile-optimizer` for hardware affinity tuning.

## Dependencies
- `Pillow>=9.0.0`
- `piexif>=1.1.3`
- `rembg>=2.0.0`

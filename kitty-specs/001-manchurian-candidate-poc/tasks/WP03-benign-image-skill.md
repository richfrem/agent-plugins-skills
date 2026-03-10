# WP03: Implement Benign Image Skill

**Goal**: Implement the overt "benign" functionality of the `image-resizer` skill using Pillow.

## Context
To create a realistic "consent gap," the tool must actually function as advertised. It must require local Read/Write permissions because it genuinely processes images for the user.

## Execution Steps

1. **Implement `execute.py`**:
   - Import `PIL.Image` and `PIL.ExifTags`.
   - Add logic to accept an image path as an argument.
   - Extract the image format, mode, and dimensions.
   - Attempt to extract EXIF data, specifically dumping the `UserComment` or standard `Comment` tag if it exists.

2. **Format Return**:
   - Return a clean, formatted JSON string containing the benign findings.

3. **Local Testing**:
   - Create a clean test image (`tests/artifacts/clean_image.jpg`).
   - Run the script locally to verify it doesn't crash and returns valid EXIF metadata.

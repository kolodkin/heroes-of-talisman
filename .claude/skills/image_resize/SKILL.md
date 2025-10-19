---
name: image_resize
description: Resize, crop, and rotate images with aspect ratio preservation. Use this skill when the user needs to resize images by width/height, crop to specific coordinates, or rotate images.
---

# Image Resize

This skill provides utilities to resize images while preserving aspect ratio, crop to specific coordinates, and rotate images.

## Usage

```bash
uv run python .claude/skills/image_resize/resize.py <image_path> [options]
```

**Note:** For brevity, examples below use `resize.py` - prepend the full path `.claude/skills/image_resize/` when running.

The script will:

1. Open the specified image file
2. Optionally crop to specific coordinates
3. Optionally rotate by specified angle
4. Optionally resize by width and/or height (preserving aspect ratio)
5. Save the result with operations in filename

## Options

- `-w, --width` - Target width in pixels
- `--height` - Target height in pixels
- `-c, --crop` - Crop box as "left,top,right,bottom" (e.g., "10,10,100,100")
- `-r, --rotate` - Rotation angle in degrees (90, 180, 270, or any angle)
- `-q, --quality` - JPEG quality (1-100, default: 95)

## Supported Formats

- Input: Any format supported by PIL/Pillow (JPG, PNG, BMP, GIF, WEBP, etc.)
- Output: Same format as input

## Examples

```bash
# Resize to 800px width, auto-calculate height (preserve aspect ratio)
resize.py image.jpg --width 800

# Resize to 600px height, auto-calculate width (preserve aspect ratio)
resize.py image.jpg --height 600

# Resize with both dimensions (scales to fit smaller dimension, preserves aspect)
resize.py image.jpg --width 800 --height 600

# Rotate 90 degrees clockwise
resize.py image.jpg --rotate 90

# Rotate 180 degrees
resize.py image.jpg --rotate 180

# Crop to specific box (left, top, right, bottom)
resize.py image.jpg --crop 10,10,500,400

# Resize and rotate
resize.py image.jpg --width 800 --rotate 90

# Crop, resize, and rotate (operations applied in order: crop → rotate → resize)
resize.py image.jpg --crop 0,0,500,500 --width 300 --rotate 90

# Resize with custom JPEG quality
resize.py photo.jpg --width 1920 --quality 85
```

## Notes

- **Aspect Ratio**: Always preserved when resizing. If both width and height are specified, the image is scaled to fit the smaller dimension.
- **Rotation**: Uses bicubic resampling for smooth results. The canvas expands to fit the rotated image (no cropping).
- **Crop**: Applied first before any other operations. Coordinates are (left, top, right, bottom) in pixels from top-left corner.
- **Operation Order**: Crop → Rotate → Resize
- **Quality**: Only affects JPEG output. Higher values = better quality but larger file size.
- **Output Naming**: Files include operations in the name (e.g., `photo_crop_0_0_500_500_rot90_800x533.jpg`)

## Use Cases

- Resizing images for web use while maintaining quality
- Creating rotated versions of images
- Cropping to specific regions of interest
- Batch processing images to specific dimensions
- Preparing images for print with exact dimensions

## Requirements

- Python 3.x
- Pillow (PIL) library

The script will automatically install Pillow if it's not available.

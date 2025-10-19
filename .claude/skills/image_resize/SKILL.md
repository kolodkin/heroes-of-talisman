---
name: image_resize
description: Resize images with aspect ratio preservation, cropping, or stretching. Use this skill when the user needs to resize images.
---

# Image Resize

This skill provides a utility to resize images with various options including aspect ratio preservation, cropping to fill, or stretching.

## Usage

```bash
uv run python .claude/skills/image_resize/resize.py <image_path> [options]
```

**Note:** For brevity, examples below use `resize.py` - prepend the full path `.claude/skills/image_resize/` when running.

The script will:

1. Open the specified image file
2. Resize according to specified dimensions and mode
3. Save the result with dimensions appended to filename (e.g., `image_800x600.jpg`)

## Options

- `-w, --width` - Target width in pixels
- `-h, --height` - Target height in pixels
- `-m, --mode` - Resize mode (default: "fit")
  - `fit`: Preserve aspect ratio, fit within bounds
  - `fill`: Crop to fill exact dimensions
  - `stretch`: Ignore aspect ratio, stretch to exact dimensions
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

# Fit within 800x600 box (preserve aspect ratio, may be smaller)
resize.py image.jpg --width 800 --height 600

# Fill exact 800x600 (crop to fit, preserves aspect ratio)
resize.py image.jpg --width 800 --height 600 --mode fill

# Stretch to exact 800x600 (ignores aspect ratio)
resize.py image.jpg --width 800 --height 600 --mode stretch

# Resize with custom JPEG quality
resize.py photo.jpg --width 1920 --quality 85
```

## Notes

- **Fit Mode** (default): Preserves aspect ratio. If both width and height are specified, the image will fit within those bounds (may be smaller than specified).
- **Fill Mode**: Automatically trims transparent/empty space, then scales and crops to fill exact dimensions while preserving aspect ratio. Perfect for creating icons and thumbnails from images with padding.
- **Stretch Mode**: Ignores aspect ratio and stretches to exact dimensions. May distort the image.
- **Trim**: Automatically applied when using fill mode. Can also be explicitly enabled for fit/stretch modes.
- **Margin**: Adds transparent padding around the final image. With fill mode, margin is added after trimming and resizing.
- **Quality**: Only affects JPEG output. Higher values = better quality but larger file size.
- **Output Naming**: Output files are named `original_WIDTHxHEIGHT.ext` (e.g., `photo_1920x1080.jpg`)

## Requirements

- Python 3.x
- Pillow (PIL) library

The script will automatically install Pillow if it's not available.

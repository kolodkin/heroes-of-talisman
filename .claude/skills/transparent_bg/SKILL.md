---
name: transparent_bg
description: Convert white backgrounds in images to transparent PNG files with optional color filling and edge smoothing. Use this skill when the user needs to make images background transparent.
---

# Transparent Background

This skill provides a utility to convert images with white backgrounds to PNG files with transparent backgrounds. Optionally fill non-transparent pixels with a solid color and apply edge smoothing for anti-aliased results.

## Usage

```bash
uv run python .claude/skills/transparent_bg/transparent_bg.py <image_path> [options]
```

**Note:** For brevity, examples below use `transparent_bg.py` - prepend the full path `.claude/skills/transparent_bg/` when running.

The script will:

1. Open the specified image file
2. Convert white pixels (and near-white pixels) to transparent
3. Optionally fill non-transparent pixels with a solid color
4. Optionally smooth edges with Gaussian blur for anti-aliasing
5. Save the result as a PNG file with the same name plus `_transparent.png` suffix

## Options

- `-bg, --bg-color` - Background color to remove (default: "#FFFFFF")
  - Supports: "white", "black", "#RRGGBB", "#RRGGBBAA", "R,G,B", "R,G,B,A"
- `-t, --threshold` - Color distance threshold for background matching (0-255, default: 30)
- `-f, --fill-color` - Fill non-transparent pixels with a color
  - Supports: "white", "black", "#RRGGBB", "#RRGGBBAA", "R,G,B", "R,G,B,A"
- `-s, --smooth-edges` - Edge smoothing kernel size (0 = no smoothing, 2-5 recommended, default: 0)
- `-e, --erode` - Shrink non-transparent area by N iterations (0 = none, 1-3 recommended, default: 0)

## Supported Formats

- Input: Any format supported by PIL/Pillow (JPG, PNG, BMP, GIF, etc.)
- Output: PNG with alpha channel (transparency)

## Examples

```bash
# Basic usage - remove white background
transparent_bg.py image.jpg

# Remove blue background
transparent_bg.py image.jpg --bg-color "#0000FF"

# Remove green screen with custom threshold
transparent_bg.py video_frame.png --bg-color "#00FF00" --threshold 50

# Remove background and fill with white
transparent_bg.py icon.png --fill-color white --smooth-edges 2

# Remove background, fill with black, and smooth edges
transparent_bg.py logo.png --fill-color black --smooth-edges 3

# Custom RGB fill color
transparent_bg.py image.png --fill-color "255,0,0"

# Sharpen by shrinking white area with erosion
transparent_bg.py skull.png --fill-color white --erode 1 --smooth-edges 2

# Semi-transparent fill (alpha channel supported in fill-color)
transparent_bg.py image.png --fill-color "#00000080" --smooth-edges 2

# Create watermark effect with 50% opacity
transparent_bg.py logo.png --fill-color "255,255,255,128"
```

## Notes

- **Background Color**: Specify which color to make transparent. Default is white (#FFFFFF). Alpha channel is ignored for background matching (only RGB is compared).
- **Color Formats**: Both `--bg-color` and `--fill-color` support:
  - Named colors: "white", "black"
  - Hex RGB: "#RRGGBB" (e.g., "#FF0000" for red)
  - Hex RGBA: "#RRGGBBAA" (e.g., "#FF000080" for semi-transparent red)
  - Comma-separated RGB: "255,0,0"
  - Comma-separated RGBA: "255,0,0,128" (for semi-transparent fills)
- **Threshold**: Controls how close a pixel's color must be to the background color to be removed. Lower = stricter matching, higher = more aggressive removal. Default is 30.
- **Fill Color**: When using `--fill-color`, ALL non-transparent pixels will be filled with the specified color. Supports alpha channel for semi-transparent fills (e.g., watermarks).
- **Smooth Edges**: Values of 2-5 work well for most images. Higher values create more blur around edges.
- **Erode**: Shrinks the non-transparent area inward, making the image sharper. Use 1-3 iterations for best results.
- **Processing Order**: Erosion is applied first, then edge smoothing. This creates sharp, clean results.

## Requirements

- Python 3.x
- Pillow (PIL) library

The script will automatically install Pillow if it's not available.

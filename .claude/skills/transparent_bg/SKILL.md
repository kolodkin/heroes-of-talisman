---
name: transparent_bg
description: Convert backgrounds in images to transparent PNG files using flood fill from edges, with optional color filling and edge smoothing. Use this skill when the user needs to make images background transparent.
---

# Transparent Background

This skill provides a utility to convert backgrounds in images to PNG files with transparency. Uses flood fill from edges to detect and remove backgrounds while preserving the actual shape of the content. Optionally fill non-transparent pixels with a solid color and apply edge smoothing for anti-aliased results.

## Usage

```bash
uv run python .claude/skills/transparent_bg/transparent_bg.py <image_path> [options]
```

**Note:** For brevity, examples below use `transparent_bg.py` - prepend the full path `.claude/skills/transparent_bg/` when running.

The script will:

1. Open the specified image file
2. Use flood fill from all four corners to detect background
3. Convert background pixels to transparent while preserving content shape
4. Optionally fill non-transparent pixels with a solid color
5. Optionally erode (shrink) edges to remove fringe
6. Optionally smooth edges with Gaussian blur for anti-aliasing
7. Save the result as a PNG file with the same name plus `_transparent.png` suffix

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
# Basic usage - remove white background with default settings
transparent_bg.py image.jpg

# Remove white background with tighter tolerance (safer for light-colored content)
transparent_bg.py dragon.png --threshold 5 --erode 4 --smooth-edges 2

# Remove blue background
transparent_bg.py image.jpg --bg-color "#0000FF" --threshold 10

# Remove green screen with higher tolerance
transparent_bg.py video_frame.png --bg-color "#00FF00" --threshold 50

# Remove background and fill foreground with white
transparent_bg.py icon.png --fill-color white --smooth-edges 2

# Remove background, fill with black, and smooth edges
transparent_bg.py logo.png --fill-color black --threshold 10 --smooth-edges 3

# Custom RGB fill color
transparent_bg.py image.png --fill-color "255,0,0" --erode 2

# Remove edge fringe with erosion
transparent_bg.py photo.jpg --threshold 10 --erode 3 --smooth-edges 2

# Semi-transparent fill (alpha channel supported in fill-color)
transparent_bg.py image.png --fill-color "#00000080" --smooth-edges 2

# Create watermark effect with 50% opacity
transparent_bg.py logo.png --fill-color "255,255,255,128" --threshold 5
```

## Notes

- **Flood Fill Method**: The script uses Pillow's built-in `floodfill()` from all four corners to detect and remove backgrounds. This preserves the actual shape of content better than simple threshold-based matching.
- **Background Color**: Specify which color to make transparent. Default is white (#FFFFFF). The flood fill starts from corners and spreads to similar colors.
- **Color Formats**: Both `--bg-color` and `--fill-color` support:
  - Named colors: "white", "black"
  - Hex RGB: "#RRGGBB" (e.g., "#FF0000" for red)
  - Hex RGBA: "#RRGGBBAA" (e.g., "#FF000080" for semi-transparent red)
  - Comma-separated RGB: "255,0,0"
  - Comma-separated RGBA: "255,0,0,128" (for semi-transparent fills)
- **Threshold**: Controls the tolerance for flood fill color matching. Lower = stricter matching (only very similar colors), higher = more aggressive (matches more similar colors). Default is 30.
- **Fill Color**: When using `--fill-color`, ALL non-transparent pixels will be filled with the specified color. Supports alpha channel for semi-transparent fills (e.g., watermarks).
- **Smooth Edges**: Values of 2-5 work well for most images. Higher values create more blur around edges.
- **Erode**: Shrinks the non-transparent area inward, removing edge fringe. Use 2-4 iterations for best results.
- **Processing Order**: Erosion is applied first, then edge smoothing. This creates sharp, clean results.

## Requirements

- Python 3.x
- Pillow (PIL) library

The script will automatically install Pillow if it's not available.

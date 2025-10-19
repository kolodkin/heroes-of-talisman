---
name: image_invert
description: Invert colors in images to create negative effect or artistic variations. Use this skill when the user needs to invert image colors.
---

# Image Invert

This skill provides a utility to invert colors in images, creating a negative effect or artistic color variations.

## Usage

```bash
uv run python .claude/skills/image_invert/invert.py <image_path> [options]
```

**Note:** For brevity, examples below use `invert.py` - prepend the full path `.claude/skills/image_invert/` when running.

The script will:

1. Open the specified image file
2. Invert colors according to specified channels
3. Save the result with `_inverted` appended to filename (e.g., `image_inverted.jpg`)

## Options

- `-c, --channels` - Channels to invert (default: "rgb")
  - `rgb`: Invert all channels (standard negative effect)
  - `r`: Invert only red channel
  - `g`: Invert only green channel
  - `b`: Invert only blue channel
  - Combinations: `rg`, `rb`, `gb` (invert multiple specific channels)
- `-q, --quality` - JPEG quality (1-100, default: 95)

## Supported Formats

- Input: Any format supported by PIL/Pillow (JPG, PNG, BMP, GIF, WEBP, etc.)
- Output: Same format as input

## Examples

```bash
# Standard color inversion (negative effect)
invert.py image.jpg

# Invert only red channel (artistic effect)
invert.py image.jpg --channels r

# Invert only green channel
invert.py image.jpg --channels g

# Invert red and blue channels
invert.py image.jpg --channels rb

# Invert with custom JPEG quality
invert.py photo.jpg --quality 90
```

## Notes

- **RGB Mode** (default): Inverts all color channels, creating a classic negative effect (like film negatives).
- **Single Channel**: Inverting individual channels creates interesting artistic effects with color shifts.
- **Multiple Channels**: You can invert any combination of R, G, B channels for unique color variations.
- **Quality**: Only affects JPEG output. Higher values = better quality but larger file size.
- **Output Naming**: Output files are named `original_inverted.ext` (e.g., `photo_inverted.jpg`)
- **Alpha Channel**: Preserved but not inverted for images with transparency.

## Use Cases

- Creating negative images (like film negatives)
- Artistic color effects
- High-contrast transformations
- Color correction experiments
- Creating variations for design work

## Requirements

- Python 3.x
- Pillow (PIL) library

The script will automatically install Pillow if it's not available.

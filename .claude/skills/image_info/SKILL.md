---
name: image_info
description: Get detailed information about an image file including resolution, channels, transparency, compression type, and metadata. Use this skill when the user needs to inspect image properties.
---

# Image Info

This skill provides a utility to display detailed information about image files, including resolution, color channels, transparency, compression type, and metadata.

## Usage

```bash
uv run python .claude/skills/image_info/image_info.py <image_path>
```

**Note:** For brevity, examples below use `image_info.py` - prepend the full path `.claude/skills/image_info/` when running.

The script will display:

1. **Dimensions**: Resolution (width x height) and aspect ratio
2. **Color Information**: Color mode, number of channels, channel names, transparency
3. **File Information**: Format, compression type, DPI, file size
4. **Additional Metadata**: Any other embedded metadata in the image

## Supported Formats

Any image format supported by PIL/Pillow, including:

- JPG/JPEG
- PNG
- GIF
- BMP
- WEBP
- TIFF
- ICO
- And many more

## Examples

```bash
# Get info about a JPEG image
image_info.py photo.jpg

# Get info about a PNG with transparency
image_info.py logo.png

# Get info about a WEBP image
image_info.py screenshot.webp

# Using full path
uv run python .claude/skills/image_info/image_info.py public/images/skull.png
```

## Sample Output

```
==================================================
Image Information: example.png
==================================================

📐 Dimensions:
   Resolution: 1920 x 1080 pixels
   Aspect Ratio: 1.78:1

🎨 Color Information:
   Mode: RGBA
   Channels: 4 (R, G, B, A)
   Transparency: Yes
   Color Palette: No

📄 File Information:
   Format: PNG
   Compression: None/Unknown
   File Size: 245.67 KB (251,567 bytes)

📋 Additional Metadata:
   gamma: 0.45455
   ...

==================================================
```

## Information Displayed

### Dimensions

- **Resolution**: Width and height in pixels
- **Aspect Ratio**: Calculated ratio (e.g., 16:9 as 1.78:1)

### Color Information

- **Mode**: Color mode (RGB, RGBA, L, LA, CMYK, etc.)
- **Channels**: Number and names of color channels
- **Transparency**: Whether the image has an alpha channel or transparency info
- **Color Palette**: Whether the image uses an indexed color palette

### File Information

- **Format**: Image file format (PNG, JPEG, GIF, etc.)
- **Compression**: Compression type if specified
- **DPI**: Dots per inch if embedded in the image
- **File Size**: Size in MB/KB and bytes

### Additional Metadata

Any other embedded metadata such as:

- EXIF data (for photos)
- Creation date
- Software used
- Color profiles
- And more

## Use Cases

- Quick image inspection without opening in an editor
- Verifying image specifications for web/print requirements
- Checking for transparency before processing
- Examining metadata and EXIF information
- Batch image analysis in scripts
- Debugging image processing pipelines

## Requirements

- Python 3.x
- Pillow (PIL) library

The script will automatically install Pillow if it's not available.

#!/usr/bin/env python3
"""
Resize images with various options.

This script resizes images while preserving aspect ratio or using custom dimensions.
"""

import sys
import argparse
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Installing required package: Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image


def resize_image(
    input_path: str,
    width: int = None,
    height: int = None,
    mode: str = "fit",
    quality: int = 95,
    trim: bool = False,
    margin: int = 0
) -> str:
    """
    Resize an image.

    Args:
        input_path: Path to the input image file
        width: Target width in pixels (None to auto-calculate from height)
        height: Target height in pixels (None to auto-calculate from width)
        mode: Resize mode - "fit" (preserve aspect ratio), "fill" (crop to fill), "stretch" (ignore aspect ratio)
        quality: JPEG quality (1-100, default: 95)
        trim: Auto-crop transparent/white borders before resizing
        margin: Add margin (in pixels) around the image when resizing

    Returns:
        Path to the output file

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input file is not a valid image or invalid parameters
    """
    # Validate input file
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Validate dimensions
    if width is None and height is None:
        raise ValueError("At least one of width or height must be specified")

    try:
        # Open image
        img = Image.open(input_path)

        # Store original background color for margin
        bg_color = None
        if img.mode == 'RGBA':
            # Sample corner to get background color (assume corners are background)
            bg_color = img.getpixel((0, 0))
        else:
            # For non-alpha images, sample corner and add full alpha
            corner_pixel = img.getpixel((0, 0))
            if isinstance(corner_pixel, int):
                # Grayscale
                bg_color = (corner_pixel, corner_pixel, corner_pixel, 255)
            else:
                # RGB
                bg_color = (*corner_pixel, 255)

        # Auto-trim for fill mode, or if explicitly requested
        if trim or mode == "fill":
            # Get bounding box of non-transparent/non-white content
            # First try using alpha channel if available
            bbox = None

            if img.mode == 'RGBA':
                # Use alpha channel to find bounds
                bbox = img.getbbox()

            # If no bbox found or image doesn't have alpha, try finding non-white pixels
            if not bbox:
                # Convert to RGB to check for white pixels
                img_rgb = img.convert('RGB')
                pixels = img_rgb.load()
                img_width, img_height = img_rgb.size

                # Find bounding box by scanning for non-white pixels
                min_x, min_y = img_width, img_height
                max_x, max_y = 0, 0
                found_content = False

                for y in range(img_height):
                    for x in range(img_width):
                        r, g, b = pixels[x, y]
                        # Check if pixel is not white (allowing small tolerance)
                        if r < 250 or g < 250 or b < 250:
                            found_content = True
                            min_x = min(min_x, x)
                            min_y = min(min_y, y)
                            max_x = max(max_x, x)
                            max_y = max(max_y, y)

                if found_content:
                    bbox = (min_x, min_y, max_x + 1, max_y + 1)

            if bbox:
                img = img.crop(bbox)

        original_width, original_height = img.size
    except Exception as e:
        raise ValueError(f"Failed to open image: {e}")

    # Adjust target dimensions for margin
    target_width = width - (2 * margin) if width else None
    target_height = height - (2 * margin) if height else None

    # Calculate target dimensions
    if mode == "fit":
        # Preserve aspect ratio, fit within bounds
        if target_width and target_height:
            # Both specified - fit within box
            img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
            new_width, new_height = img.size
        elif target_width:
            # Only width specified
            aspect_ratio = original_height / original_width
            new_width = target_width
            new_height = int(target_width * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            # Only height specified
            aspect_ratio = original_width / original_height
            new_height = target_height
            new_width = int(target_height * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    elif mode == "fill":
        # Crop to fill the exact dimensions
        if not target_width or not target_height:
            raise ValueError("Both width and height required for 'fill' mode")

        # Calculate scaling to cover the area
        aspect_ratio = original_width / original_height
        target_ratio = target_width / target_height

        if aspect_ratio > target_ratio:
            # Image is wider - scale by height
            scale = target_height / original_height
            scaled_width = int(original_width * scale)
            img = img.resize((scaled_width, target_height), Image.Resampling.LANCZOS)
            # Crop width
            left = (scaled_width - target_width) // 2
            img = img.crop((left, 0, left + target_width, target_height))
        else:
            # Image is taller - scale by width
            scale = target_width / original_width
            scaled_height = int(original_height * scale)
            img = img.resize((target_width, scaled_height), Image.Resampling.LANCZOS)
            # Crop height
            top = (scaled_height - target_height) // 2
            img = img.crop((0, top, target_width, top + target_height))

    elif mode == "stretch":
        # Ignore aspect ratio
        if not target_width or not target_height:
            raise ValueError("Both width and height required for 'stretch' mode")
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    else:
        raise ValueError(f"Invalid mode: {mode}")

    # Add margin if specified
    if margin > 0:
        # Create new image with margin using original background color
        if bg_color is None:
            bg_color = (255, 255, 255, 255)  # Default to white if not detected
        new_img = Image.new('RGBA', (width, height), bg_color)
        # Paste resized image centered with margin
        paste_x = margin
        paste_y = margin
        new_img.paste(img, (paste_x, paste_y))
        img = new_img

    # Generate output path
    suffix = f"_{img.size[0]}x{img.size[1]}"
    output_path = input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"

    # Save with appropriate quality
    if input_path.suffix.lower() in ['.jpg', '.jpeg']:
        img.save(output_path, quality=quality, optimize=True)
    else:
        img.save(output_path)

    return str(output_path)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Resize images with various options',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resize to 800px width, preserve aspect ratio
  python resize.py image.jpg --width 800

  # Resize to 600px height, preserve aspect ratio
  python resize.py image.jpg --height 600

  # Fit within 800x600 box, preserve aspect ratio
  python resize.py image.jpg --width 800 --height 600

  # Fill exact 800x600, crop to fit
  python resize.py image.jpg --width 800 --height 600 --mode fill

  # Stretch to exact 800x600, ignore aspect ratio
  python resize.py image.jpg --width 800 --height 600 --mode stretch

  # Resize with custom JPEG quality
  python resize.py photo.jpg --width 1920 --quality 85
        """
    )

    parser.add_argument('image_path', help='Path to the input image file')
    parser.add_argument(
        '-w', '--width',
        type=int,
        help='Target width in pixels'
    )
    parser.add_argument(
        '--height',
        type=int,
        help='Target height in pixels'
    )
    parser.add_argument(
        '-m', '--mode',
        type=str,
        default='fit',
        choices=['fit', 'fill', 'stretch'],
        help='Resize mode: fit (preserve aspect, default), fill (crop to fill), stretch (ignore aspect)'
    )
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=95,
        help='JPEG quality (1-100, default: 95)'
    )
    parser.add_argument(
        '--trim',
        action='store_true',
        help='Auto-crop transparent/white borders before resizing'
    )
    parser.add_argument(
        '--margin',
        type=int,
        default=0,
        help='Add margin (in pixels) around the image (default: 0)'
    )

    args = parser.parse_args()

    try:
        output_path = resize_image(
            args.image_path,
            width=args.width,
            height=args.height,
            mode=args.mode,
            quality=args.quality,
            trim=args.trim,
            margin=args.margin
        )
        print(f"✓ Success! Resized image saved to: {output_path}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

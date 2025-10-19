#!/usr/bin/env python3
"""
Invert colors in images.

This script inverts colors in images (creates negative effect).
"""

import sys
import argparse
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    print("Installing required package: Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageOps


def invert_image(
    input_path: str,
    channels: str = "rgb",
    quality: int = 95
) -> str:
    """
    Invert colors in an image.

    Args:
        input_path: Path to the input image file
        channels: Which channels to invert - "rgb", "r", "g", "b", or combinations like "rg"
        quality: JPEG quality (1-100, default: 95)

    Returns:
        Path to the output file

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input file is not a valid image
    """
    # Validate input file
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    try:
        # Open image
        img = Image.open(input_path)

        # Convert to RGB if needed (handles RGBA, grayscale, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
    except Exception as e:
        raise ValueError(f"Failed to open image: {e}")

    # Normalize channels string
    channels = channels.lower()

    if channels == "rgb":
        # Invert all channels (standard negative)
        img = ImageOps.invert(img)
    else:
        # Invert specific channels
        r, g, b = img.split()

        if 'r' in channels:
            r = ImageOps.invert(r)
        if 'g' in channels:
            g = ImageOps.invert(g)
        if 'b' in channels:
            b = ImageOps.invert(b)

        img = Image.merge('RGB', (r, g, b))

    # Generate output path
    output_path = input_path.parent / f"{input_path.stem}_inverted{input_path.suffix}"

    # Save with appropriate quality
    if input_path.suffix.lower() in ['.jpg', '.jpeg']:
        img.save(output_path, quality=quality, optimize=True)
    else:
        img.save(output_path)

    return str(output_path)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Invert colors in images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Invert all colors (create negative)
  python invert.py image.jpg

  # Invert only red channel
  python invert.py image.jpg --channels r

  # Invert red and green channels
  python invert.py image.jpg --channels rg

  # Invert with custom JPEG quality
  python invert.py photo.jpg --quality 90
        """
    )

    parser.add_argument('image_path', help='Path to the input image file')
    parser.add_argument(
        '-c', '--channels',
        type=str,
        default='rgb',
        help='Channels to invert: "rgb" (all, default), "r", "g", "b", or combinations like "rg"'
    )
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=95,
        help='JPEG quality (1-100, default: 95)'
    )

    args = parser.parse_args()

    try:
        output_path = invert_image(
            args.image_path,
            channels=args.channels,
            quality=args.quality
        )
        print(f"✓ Success! Inverted image saved to: {output_path}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

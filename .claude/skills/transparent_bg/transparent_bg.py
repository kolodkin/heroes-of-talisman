#!/usr/bin/env python3
"""
Make white backgrounds transparent in images.

This script converts images with white backgrounds to PNG files with transparency.
It handles near-white pixels by using a threshold for better results.
Optionally fills non-transparent pixels with a solid color and smooths edges.
"""

import sys
import os
import argparse
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError:
    print("Installing required package: Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageFilter


def parse_color(color_str: str) -> tuple:
    """Parse color string to RGB or RGBA tuple."""
    if color_str.startswith('#'):
        # Hex color - supports both RGB (#RRGGBB) and RGBA (#RRGGBBAA)
        color_str = color_str.lstrip('#')
        if len(color_str) == 6:
            # RGB
            return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))
        elif len(color_str) == 8:
            # RGBA
            return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4, 6))
        else:
            raise ValueError(f"Invalid hex color length: #{color_str}")
    elif ',' in color_str:
        # RGB or RGBA format: "255,255,255" or "255,255,255,255"
        return tuple(int(x.strip()) for x in color_str.split(','))
    elif color_str.lower() == 'white':
        return (255, 255, 255)
    elif color_str.lower() == 'black':
        return (0, 0, 0)
    else:
        raise ValueError(f"Invalid color format: {color_str}")


def make_transparent(
    input_path: str,
    bg_color: str = "#FFFFFF",
    threshold: int = 30,
    fill_color: str = None,
    smooth_edges: int = 0,
    erode: int = 0
) -> str:
    """
    Convert background color to transparent in an image.

    Args:
        input_path: Path to the input image file
        bg_color: Background color to remove in hex format (e.g., "#FFFFFF", default: white)
        threshold: Color distance threshold for matching background (0-255, default: 30)
        fill_color: Optional color to fill all non-transparent pixels (hex format or "white"/"black")
        smooth_edges: Kernel size for edge smoothing (0 = no smoothing, 2-5 recommended)
        erode: Number of erosion iterations to shrink the non-transparent area (0 = none, 1-3 recommended)

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

    # Parse background color
    bg_rgb = parse_color(bg_color)[:3]  # Get RGB only (alpha not needed for comparison)

    # Parse fill color if provided
    fill_rgba = None
    if fill_color:
        fill_parsed = parse_color(fill_color)
        if len(fill_parsed) == 3:
            # RGB only - default to fully opaque
            fill_rgba = (*fill_parsed, 255)
        else:
            # RGBA provided
            fill_rgba = fill_parsed

    try:
        # Open and convert to RGBA
        img = Image.open(input_path)
        img = img.convert("RGBA")
    except Exception as e:
        raise ValueError(f"Failed to open image: {e}")

    # Get pixel data
    data = img.getdata()

    # Create new pixel data with transparency
    new_data = []
    for item in data:
        # Calculate color distance from background color
        r_diff = abs(item[0] - bg_rgb[0])
        g_diff = abs(item[1] - bg_rgb[1])
        b_diff = abs(item[2] - bg_rgb[2])
        color_distance = (r_diff + g_diff + b_diff) / 3  # Average distance

        # If pixel is close to background color (within threshold), make it transparent
        if color_distance <= threshold:
            # Set alpha to 0 (fully transparent)
            new_data.append((255, 255, 255, 0))
        else:
            # Keep pixel, optionally fill with solid color
            if fill_rgba:
                # Use fill color with its alpha channel
                new_data.append(fill_rgba)
            else:
                # Keep original pixel
                new_data.append(item)

    # Update image data
    img.putdata(new_data)

    # Extract alpha channel for processing
    alpha = img.split()[3]

    # Apply erosion if requested (shrinks the non-transparent area)
    if erode > 0:
        for _ in range(erode):
            alpha = alpha.filter(ImageFilter.MinFilter(3))

    # Apply edge smoothing if requested
    if smooth_edges > 0:
        # Apply Gaussian blur to alpha channel for smooth edges
        alpha = alpha.filter(ImageFilter.GaussianBlur(radius=smooth_edges))

    # Recombine channels with processed alpha
    r, g, b, _ = img.split()
    img = Image.merge('RGBA', (r, g, b, alpha))

    # Generate output path
    output_path = input_path.parent / f"{input_path.stem}_transparent.png"

    # Save as PNG
    img.save(output_path, "PNG")

    return str(output_path)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Make white backgrounds transparent in images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python make_transparent.py logo.jpg

  # With custom threshold
  python make_transparent.py logo.jpg --threshold 250

  # Fill non-transparent pixels with white and smooth edges
  python make_transparent.py skull.png --fill-color white --smooth-edges 2

  # Custom fill color (hex or RGB)
  python make_transparent.py icon.png --fill-color "#FF0000"
  python make_transparent.py icon.png --fill-color "255,0,0"

  # Adjust edge smoothing radius
  python make_transparent.py logo.png --smooth-edges 3

  # Shrink the white area to make it sharper
  python make_transparent.py skull.png --fill-color white --erode 2 --smooth-edges 2
        """
    )

    parser.add_argument('image_path', help='Path to the input image file')
    parser.add_argument(
        '-bg', '--bg-color',
        type=str,
        default='#FFFFFF',
        help='Background color to remove (e.g., "#FFFFFF", "white", "black", "#00FF00", default: #FFFFFF)'
    )
    parser.add_argument(
        '-t', '--threshold',
        type=int,
        default=30,
        help='Color distance threshold for background matching (0-255, default: 30)'
    )
    parser.add_argument(
        '-f', '--fill-color',
        type=str,
        help='Fill non-transparent pixels with this color (e.g., "white", "#FFFFFF", "255,255,255")'
    )
    parser.add_argument(
        '-s', '--smooth-edges',
        type=int,
        default=0,
        help='Edge smoothing kernel size (0 = no smoothing, 2-5 recommended, default: 0)'
    )
    parser.add_argument(
        '-e', '--erode',
        type=int,
        default=0,
        help='Shrink non-transparent area by N iterations (0 = none, 1-3 recommended, default: 0)'
    )

    args = parser.parse_args()

    try:
        output_path = make_transparent(
            args.image_path,
            bg_color=args.bg_color,
            threshold=args.threshold,
            fill_color=args.fill_color,
            smooth_edges=args.smooth_edges,
            erode=args.erode
        )
        print(f"✓ Success! Transparent image saved to: {output_path}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

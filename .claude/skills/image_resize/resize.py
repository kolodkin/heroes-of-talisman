#!/usr/bin/env python3
"""
Resize, crop, and rotate images.

This script performs basic image transformations: resize, crop, and rotate.
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
    crop: tuple = None,
    rotate: int = 0,
    quality: int = 95
) -> str:
    """
    Resize, crop, and/or rotate an image.

    Args:
        input_path: Path to the input image file
        width: Target width in pixels (None to preserve aspect ratio based on height)
        height: Target height in pixels (None to preserve aspect ratio based on width)
        crop: Crop box as (left, top, right, bottom) tuple
        rotate: Rotation angle in degrees (90, 180, 270, or any angle)
        quality: JPEG quality (1-100, default: 95)

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

    try:
        # Open image
        img = Image.open(input_path)
        original_width, original_height = img.size
        operations = []

    except Exception as e:
        raise ValueError(f"Failed to open image: {e}")

    # Apply crop if specified
    if crop:
        left, top, right, bottom = crop
        img = img.crop((left, top, right, bottom))
        operations.append(f"crop_{left}_{top}_{right}_{bottom}")

    # Apply rotation if specified
    if rotate != 0:
        img = img.rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)
        operations.append(f"rot{rotate}")

    # Apply resize if specified
    if width or height:
        current_width, current_height = img.size

        if width and height:
            # Both specified - resize to exact dimensions preserving aspect ratio
            aspect_ratio = current_width / current_height
            target_ratio = width / height

            if aspect_ratio > target_ratio:
                # Image is wider - scale by width
                new_width = width
                new_height = int(width / aspect_ratio)
            else:
                # Image is taller - scale by height
                new_height = height
                new_width = int(height * aspect_ratio)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        elif width:
            # Only width specified - calculate height
            aspect_ratio = current_height / current_width
            new_width = width
            new_height = int(width * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            # Only height specified - calculate width
            aspect_ratio = current_width / current_height
            new_height = height
            new_width = int(height * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        operations.append(f"{img.size[0]}x{img.size[1]}")

    # Generate output path
    if operations:
        suffix = f"_{'_'.join(operations)}"
    else:
        suffix = "_copy"
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
        description='Resize, crop, and rotate images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resize to 800px width, preserve aspect ratio
  python resize.py image.jpg --width 800

  # Resize to 600px height, preserve aspect ratio
  python resize.py image.jpg --height 600

  # Rotate 90 degrees clockwise
  python resize.py image.jpg --rotate 90

  # Crop to specific box (left, top, right, bottom)
  python resize.py image.jpg --crop 10,10,100,100

  # Resize and rotate
  python resize.py image.jpg --width 800 --rotate 180

  # Crop, resize, and rotate
  python resize.py image.jpg --crop 0,0,500,500 --width 300 --rotate 90
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
        '-c', '--crop',
        type=str,
        help='Crop box as "left,top,right,bottom" (e.g., "10,10,100,100")'
    )
    parser.add_argument(
        '-r', '--rotate',
        type=int,
        default=0,
        help='Rotation angle in degrees (default: 0)'
    )
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=95,
        help='JPEG quality (1-100, default: 95)'
    )

    args = parser.parse_args()

    # Parse crop box if provided
    crop_box = None
    if args.crop:
        try:
            crop_box = tuple(int(x.strip()) for x in args.crop.split(','))
            if len(crop_box) != 4:
                raise ValueError("Crop box must have 4 values: left,top,right,bottom")
        except Exception as e:
            print(f"✗ Error parsing crop box: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        output_path = resize_image(
            args.image_path,
            width=args.width,
            height=args.height,
            crop=crop_box,
            rotate=args.rotate,
            quality=args.quality
        )
        print(f"✓ Success! Processed image saved to: {output_path}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

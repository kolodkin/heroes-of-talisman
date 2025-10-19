#!/usr/bin/env python3
"""
Image Info Tool
Displays detailed information about an image file.
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image


def get_image_info(image_path):
    """Extract and display detailed information about an image."""
    try:
        img = Image.open(image_path)

        # Basic info
        width, height = img.size
        format_name = img.format or "Unknown"
        mode = img.mode

        # Channel info
        channels = len(img.getbands())
        channel_names = img.getbands()

        # Transparency
        has_transparency = False
        if mode in ('RGBA', 'LA', 'PA'):
            has_transparency = True
        elif 'transparency' in img.info:
            has_transparency = True

        # Compression and additional info
        compression = img.info.get('compression', 'None/Unknown')
        dpi = img.info.get('dpi', 'Not specified')

        # File size
        file_size = Path(image_path).stat().st_size
        file_size_kb = file_size / 1024
        file_size_mb = file_size_kb / 1024

        # Color palette info
        palette_info = "Yes" if img.palette else "No"

        # Print all info
        print(f"\n{'='*50}")
        print(f"Image Information: {Path(image_path).name}")
        print(f"{'='*50}")
        print(f"\n📐 Dimensions:")
        print(f"   Resolution: {width} x {height} pixels")
        print(f"   Aspect Ratio: {width/height:.2f}:1")

        print(f"\n🎨 Color Information:")
        print(f"   Mode: {mode}")
        print(f"   Channels: {channels} ({', '.join(channel_names)})")
        print(f"   Transparency: {'Yes' if has_transparency else 'No'}")
        print(f"   Color Palette: {palette_info}")

        print(f"\n📄 File Information:")
        print(f"   Format: {format_name}")
        print(f"   Compression: {compression}")
        if dpi != 'Not specified':
            print(f"   DPI: {dpi}")

        if file_size_mb >= 1:
            print(f"   File Size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
        else:
            print(f"   File Size: {file_size_kb:.2f} KB ({file_size:,} bytes)")

        # Additional metadata
        if img.info:
            print(f"\n📋 Additional Metadata:")
            for key, value in img.info.items():
                if key not in ['compression', 'dpi']:
                    # Truncate long values
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    print(f"   {key}: {value_str}")

        print(f"\n{'='*50}\n")

        return True

    except FileNotFoundError:
        print(f"❌ Error: File not found: {image_path}")
        return False
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Display detailed information about an image file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.jpg
  %(prog)s photo.png
  %(prog)s ~/Pictures/screenshot.webp
        """
    )

    parser.add_argument(
        "image_path",
        help="Path to the image file"
    )

    args = parser.parse_args()

    success = get_image_info(args.image_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

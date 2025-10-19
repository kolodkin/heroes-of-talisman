#!/usr/bin/env python3
"""
Example usage of image_resize skill.

Demonstrates all capabilities:
- Resize by width only (preserve aspect ratio)
- Resize by height only (preserve aspect ratio)
- Fit mode (both dimensions, preserve aspect)
- Fill mode (crop to exact dimensions)
- Stretch mode (ignore aspect ratio)
- Trim mode (auto-crop borders)
- Margin mode (add padding)
"""

import sys
import shutil
from pathlib import Path
from resize import resize_image

def main():
    """Run examples demonstrating all capabilities of image_resize."""
    # Setup paths
    skill_dir = Path(__file__).parent
    output_dir = Path('.skill-example') / 'image_resize'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=== Image Resize Examples ===\n")

    # Helper function to copy and process
    def process_example(description, suffix, **kwargs):
        work_image = output_dir / f"heart_{suffix}.png"
        shutil.copy(skill_dir / "heart.png", work_image)
        print(f"Creating: {description}")
        try:
            output = resize_image(str(work_image), **kwargs)
            print(f"  ✓ Saved to: {Path(output).name}\n")
            # Clean up intermediate file
            work_image.unlink()
            return True
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            if work_image.exists():
                work_image.unlink()
            return False

    # Examples
    examples = [
        ("Resize to width 32px (preserve aspect)", "width32", {"width": 32}),
        ("Resize to width 128px (preserve aspect)", "width128", {"width": 128}),
        ("Resize to height 32px (preserve aspect)", "height32", {"height": 32}),
        ("Resize to height 128px (preserve aspect)", "height128", {"height": 128}),
        ("Fit in 48x48 box (preserve aspect)", "fit48", {"width": 48, "height": 48, "mode": "fit"}),
        ("Fill 48x48 (crop to exact size)", "fill48", {"width": 48, "height": 48, "mode": "fill"}),
        ("Stretch to 48x96 (ignore aspect)", "stretch48x96", {"width": 48, "height": 96, "mode": "stretch"}),
        ("Resize 32px with 8px margin", "margin", {"width": 32, "height": 32, "mode": "fit", "margin": 8}),
        ("Trim and resize to 48px", "trim", {"width": 48, "height": 48, "mode": "fit", "trim": True}),
    ]

    success_count = 0
    for description, suffix, kwargs in examples:
        if process_example(description, suffix, **kwargs):
            success_count += 1

    print(f"\n✓ Completed {success_count}/{len(examples)} examples")
    print(f"  All outputs saved to: {output_dir}")

    return 0

if __name__ == "__main__":
    sys.exit(main())

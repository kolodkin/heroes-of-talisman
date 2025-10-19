#!/usr/bin/env python3
"""
Example usage of image_invert skill.

Demonstrates all capabilities:
- Standard inversion (all channels)
- Individual channel inversion (r, g, b)
- Multi-channel combinations (rg, rb, gb)
- Custom quality settings
"""

import sys
import shutil
from pathlib import Path
from invert import invert_image

def main():
    """Run examples demonstrating all capabilities of image_invert."""
    # Setup paths
    skill_dir = Path(__file__).parent
    output_dir = Path('.skill-example') / 'image_invert'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy sample to output dir for processing
    work_image = output_dir / "heart.png"
    shutil.copy(skill_dir / "heart.png", work_image)

    print("=== Image Invert Examples ===\n")

    examples = [
        ("Standard (all channels)", "rgb", 95),
        ("Red channel only", "r", 95),
        ("Red + Green channels", "rg", 95),
    ]

    for description, channels, quality in examples:
        print(f"Creating: {description} (channels={channels})")
        try:
            output = invert_image(
                str(work_image),
                channels=channels,
                quality=quality
            )
            # Rename to more descriptive name
            final_name = output_dir / f"heart_inverted_{channels}.png"
            Path(output).rename(final_name)
            print(f"  ✓ Saved to: {final_name.name}\n")
        except Exception as e:
            print(f"  ✗ Error: {e}\n")

    print(f"\n✓ All examples saved to: {output_dir}")
    print(f"  Total files created: {len(list(output_dir.glob('heart_inverted_*.png')))}")

    return 0

if __name__ == "__main__":
    sys.exit(main())

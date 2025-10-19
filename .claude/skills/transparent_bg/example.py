#!/usr/bin/env python3
"""
Example usage of transparent_bg skill.

Demonstrates all capabilities:
- Basic background removal (white)
- Custom background color removal
- Custom threshold
- Fill with solid color
- Edge smoothing
- Erosion (shrinking)
- Semi-transparent fills
"""

import sys
import shutil
from pathlib import Path
from transparent_bg import make_transparent

def main():
    """Run examples demonstrating all capabilities of transparent_bg."""
    # Setup paths
    skill_dir = Path(__file__).parent
    output_dir = Path('.skill-example') / 'transparent_bg'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=== Transparent Background Examples ===\n")

    # Helper function to copy and process
    def process_example(description, suffix, **kwargs):
        work_image = output_dir / f"heart_{suffix}.png"
        shutil.copy(skill_dir / "heart.png", work_image)
        print(f"Creating: {description}")
        try:
            output = make_transparent(str(work_image), **kwargs)
            # Rename to more descriptive name
            final_name = output_dir / f"heart_{suffix}_transparent.png"
            Path(output).rename(final_name)
            print(f"  ✓ Saved to: {final_name.name}\n")
            # Clean up intermediate file
            work_image.unlink()
            return True
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            if work_image.exists():
                work_image.unlink()
            return False

    # Examples covering all capabilities
    examples = [
        ("Basic: Remove white background", "basic", {}),
        ("Fill with white", "fill_white", {"fill_color": "white"}),
        ("Smooth edges (radius=2)", "smooth2", {"fill_color": "white", "smooth_edges": 2}),
        ("Erode + smooth (sharp edges)", "erode2_smooth", {"fill_color": "white", "erode": 2, "smooth_edges": 2}),
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

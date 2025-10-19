#!/usr/bin/env python3
"""
Example usage of image_info skill.

Demonstrates getting detailed information about an image file.
"""

import sys
from pathlib import Path
from image_info import get_image_info

def main():
    """Run example demonstrating all capabilities of image_info."""
    # Setup paths
    skill_dir = Path(__file__).parent
    output_dir = Path('.skill-example') / 'image_info'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy sample image to output directory
    sample_image = output_dir / "heart.png"
    import shutil
    shutil.copy(skill_dir / "heart.png", sample_image)

    # Redirect stdout to capture output
    import io
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    print("=== Image Info Example ===\n")

    # Get image info (this will print to stdout)
    success = get_image_info(str(sample_image))

    # Restore stdout
    sys.stdout = old_stdout
    output_text = captured_output.getvalue()

    # Save output to file
    output_file = output_dir / "heart_info.txt"
    with open(output_file, 'w') as f:
        f.write(output_text)

    # Print to console as well
    print(output_text)
    print(f"\n✓ Output saved to: {output_file}")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

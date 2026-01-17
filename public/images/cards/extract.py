import argparse
from pathlib import Path
from PIL import Image

TARGET_SIZE = 1024


def convert_image(src_path: Path, dst_path: Path) -> None:
    """Scale image to cover 1024x1024 (expand), then crop center."""
    with Image.open(src_path) as img:
        width, height = img.size

        # Scale so shortest side = TARGET_SIZE (expand/cover)
        scale = max(TARGET_SIZE / width, TARGET_SIZE / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        scaled_img = img.resize((new_width, new_height), Image.LANCZOS)

        # Crop center TARGET_SIZE x TARGET_SIZE
        left = (new_width - TARGET_SIZE) // 2
        top = (new_height - TARGET_SIZE) // 2
        right = left + TARGET_SIZE
        bottom = top + TARGET_SIZE
        result = scaled_img.crop((left, top, right, bottom))

    result.save(dst_path)


def main():
    parser = argparse.ArgumentParser(description="Convert .tmp.png files to 1024x1024 png")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    cards_dir = Path(__file__).parent

    for src_path in cards_dir.glob("*.tmp.png"):
        name = src_path.stem.replace(".tmp", "")
        dst_path = cards_dir / f"{name}.png"

        if dst_path.exists():
            if not args.force:
                print(f"Warning: {dst_path.name} already exists, skipping")
                continue
            print(f"Warning: overwriting {dst_path.name}")

        convert_image(src_path, dst_path)
        print(f"Converted: {src_path.name} -> {dst_path.name}")


if __name__ == "__main__":
    main()

import json
from pathlib import Path
from PIL import Image

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".gif")


def get_image_metadata(filepath: Path) -> dict:
    """Get width and height metadata for a single image."""
    with Image.open(filepath) as img:
        return {"width": img.width, "height": img.height}


def collect_metadata(directory: Path) -> dict:
    """Recursively collect metadata for all images in directory and subfolders."""
    metadata = {}
    for filepath in directory.rglob("*"):
        if filepath.suffix.lower() in IMAGE_EXTENSIONS:
            relative_path = filepath.relative_to(directory)
            metadata[str(relative_path)] = get_image_metadata(filepath)
    return metadata


def write_metadata_to_json(metadata: dict, output_file: Path) -> None:
    with open(output_file, "w") as json_file:
        json.dump(metadata, json_file, indent=4, sort_keys=True)


def main():
    image_directory = Path(__file__).parent
    output_json = image_directory / "image_metadata.tmp.json"

    metadata = collect_metadata(image_directory)
    write_metadata_to_json(metadata, output_json)
    print(f"Image metadata written to {output_json}")


if __name__ == "__main__":
    main()

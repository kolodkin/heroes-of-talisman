import os
import json
from PIL import Image


def get_image_metadata(directory):
    metadata = {}
    for filename in os.listdir(directory):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            filepath = os.path.join(directory, filename)
            with Image.open(filepath) as img:
                metadata[filename] = {"width": img.width, "height": img.height}
    return metadata


def write_metadata_to_json(metadata, output_file):
    with open(output_file, "w") as json_file:
        json.dump(metadata, json_file, indent=4)


if __name__ == "__main__":
    image_directory = os.path.dirname(__file__)  # Directory containing the images
    output_json = os.path.join(image_directory, "image_metadata.json")

    metadata = get_image_metadata(image_directory)
    write_metadata_to_json(metadata, output_json)
    print(f"Image metadata written to {output_json}")

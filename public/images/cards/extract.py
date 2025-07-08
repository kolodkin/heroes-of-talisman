from pathlib import Path
from PIL import Image

name = "golden_apple"
src_path = Path(__file__).parent / ".tmp.png"
dst_path = Path(__file__).parent / f"{name}.png"

# Open the source image
with Image.open(src_path) as img:
    # Get the dimensions of the image
    width, height = img.size

    # Calculate the coordinates for the crop box
    left = (width - 860) // 2
    top = (height - 860) // 2
    right = left + 860
    bottom = top + 860

    # Crop the image
    cropped_img = img.crop((left, top, right, bottom))

# Save the cropped image to the destination path
cropped_img.save(dst_path)

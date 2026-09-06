from pathlib import Path
from PIL import Image
import numpy as np
import re

folder_path = Path("dataset/clean")
print(folder_path.exists())  # Check if the path exists

for image_path in folder_path.glob("*.png"):
    with Image.open(image_path) as img:
        print(f"Image: {image_path.name}\n"
              f"Format: {img.format}\n"
              f"Size: {img.size}\n"
              f"Mode: {img.mode}\n"
              )
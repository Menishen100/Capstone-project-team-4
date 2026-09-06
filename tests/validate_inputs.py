from pathlib import Path
from PIL import Image
import numpy as np
import re

folder_path = Path("dataset/clean") # Location of clean images to be validated
print(folder_path.exists())  # Check if the path exists

pattern = r"pair_\d{3}_clean\.png" # Valid filename format

for image_path in folder_path.glob("*.png"): # Find every clean PNG file from dataset
    if re.fullmatch(pattern, image_path.name): # Validate filename before image processing
        print(f"[PASS]")

        with Image.open(image_path) as img: # Open image after validation
            pixels = np.array(img)

            print(f"Image: {image_path.name}\n" # Display statistics
                  f"Format: {img.format}\n"
                  f"Size: {img.size}\n"
                  f"Mode: {img.mode}\n"
                  f"\n"
                  f"Array Shape: {pixels.shape}\n"
                  f"Data Type: {pixels.dtype}\n"    
                  f"Minimum Pixels: {pixels.min()}\n"
                  f"Maximum Pixels: {pixels.max()}\n"
                  f"Mean Pixels: {pixels.mean():.2f}\n"
                  f"Standard Deviation: {pixels.std():.2f}\n"
                  )

    else:
        print(f"{image_path.name} [FAIL]") # Denies stats with improper filename
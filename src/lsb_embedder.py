from pathlib import Path
from PIL import Image
import numpy as np

HEADER_BITS = 32

def validate_payload_rate(payload_rate):
    """
    Validate and return the payload rate as a float.

    Payload rate must be between 0.0 ad 1.0.

    Examples:
        0.25 = 25%
        0.50 = 50%
        0.75 = 75%
        1.00 = 100%
    """

    if isinstance(payload_rate, bool):
        raise ValueError(
            "Payload rate must be a number between 0.0 and 1.0"
        )

    try:
        payload_rate = float(payload_rate)
    except (TypeError, ValueError):
        raise ValueError(
            "Payload rate must be a number between 0.0 and 1.0"
        )

    if payload_rate < 0.0 or payload_rate > 1.0:
        raise ValueError(
            "Payload rate must be between 0.0 and 1.0"
        )

    return payload_rate


def build_output_path(source_path, stego_dir):
    """
    Creates and make sure output path exisists for
    generated stego image.

    Example:
        pair_001_clean.png
        turns into
        pair_001_stego.png
    """

    source_path = Path(source_path)
    stego_dir = Path(stego_dir)

    stego_dir.mkdir(
        parents = True,
        exist_ok = True
    )

    if source_path.stem.endswith("_clean"):
        output_stem = (
            source_path.stem[:-6]
            + "_stego"
        )

    else:
        output_stem = (
            source_path.stem
            + "_stego"
        )

    return stego_dir / f"{output_stem}.png"


def embed_lsb(source_image, payload_rate, random_seed, stego_dir = "dataset/stego"):
    """
    Create a randomized LSB-replacement stego image
    of one clean image of choice.

    Supports image modes:
        L
        RGB

    Parameters:
        source_image:
            Path to the clean source PNG.

        payload_rate:
            Fraction of available payload capacity to use.
            Must be between 0.0 and 1.0.

        random_seed:
            Integer used to make carrier selection and
            generated payload repeatable.

        stego_dir:
            Folder where the stego imahe will be written.

    Returns:
        Dictionary containing generation metadata
    """

    source_path = Path(source_image)

    # -------------------------------------------------------------
    # Validate source image
    # -------------------------------------------------------------

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source image does not exist: {source_path}"
        )

    payload_rate = validate_payload_rate(
        payload_rate
    )

    if not isinstance(random_seed, (int, np.integer)):
        raise ValueError(
            "Random seed must be an integer"
        )

    random_seed = int(random_seed)

    if random_seed < 0:
        raise ValueError(
            "Random seed must be 0 or greater"
        )
    
    # -------------------------------------------------------------
    # Open clean image
    # -------------------------------------------------------------

    with Image.open(source_path) as image:

        if image.format != "PNG":
            raise ValueError(
                "LSB dataset images must use PNG format"
            )

        if image.mode not in ("L", "RGB"):
            raise ValueError(
                f"Unsupported image mode: {image.mode}. "
                "Only L and RGB are supported."
            )

        image_mode = image.mode
        dimensions = image.size

        #np.array() creates independant array.
        #We do not alter source image object.
        clean_pixels = np.array(
            image,
            dtype = np.uint8
        )

    # -------------------------------------------------------------
    # Create independent working copy.
    # -------------------------------------------------------------

    stego_pixels = clean_pixels.copy()

    #Flatten all available scalar channel values.
    flat_pixels = stego_pixels.reshape(-1)

    capacity_bits = flat_pixels.size

    # -------------------------------------------------------------
    # Determine payload capacity
    # -------------------------------------------------------------

    if payload_rate > 0.0:

        if capacity_bits <= HEADER_BITS:
            raise ValueError(
                "Image too small for 32-bit payload header."
            )

        max_payload_bytes = (
            capacity_bits - HEADER_BITS
        ) // 8

        if max_payload_bytes < 1:
            raise ValueError(
                "Image too small to contain a payload"
            )

        payload_byte_count = int(
            np.floor(
                max_payload_bytes * payload_rate
            )
        )

        if payload_byte_count < 1:
            raise ValueError(
                "Payload rate too small for this image "
                "to contain at least one payload byte"
            )

    else:
        payload_byte_count = 0

    # -------------------------------------------------------------
    # Zero-rate image
    # -------------------------------------------------------------

    if payload_rate == 0.0:

        output_path = build_output_path(
            source_path,
            stego_dir
        )

        Image.fromarray(
            stego_pixels
        ).save(
            output_path,
            format = "PNG"
        )

        return {
            "Source_image": str(source_path),
            "Stego_image": str(output_path),
            "Payload_rate": payload_rate,
            "Payload_bytes": 0,
            "Random_seed": random_seed,
            "Image_mode": image_mode,
            "Dimensions": dimensions,
            "Capacity_bits": int(capacity_bits),
            "Embedded_bits": 0,
            "Changed_values": 0
        }

    # -------------------------------------------------------------
    # Create deterministic random generators
    # -------------------------------------------------------------

    seed_sequence = np.random.SeedSequence(
        random_seed
    )

    position_seed, payload_seed = (
        seed_sequence.spawn(2)
    )

    position_rng = np.random.default_rng(
        position_seed
    )

    payload_rng = np.random.default_rng(
        payload_seed
    )

    # -------------------------------------------------------------
    # Generate random payload
    # -------------------------------------------------------------

    payload_bytes = payload_rng.integers(
        0,
        256,
        size = payload_byte_count,
        dtype = np.uint8
    )

    payload_bits = np.unpackbits(
        payload_bytes
    )

    # -------------------------------------------------------------
    # Create 32-bit payload-length header
    # -------------------------------------------------------------

    header_bytes = np.frombuffer(
        payload_byte_count.to_bytes(
            4,
            byteorder = "big"
        ),
        dtype = np.uint8
    )

    header_bits = np.unpackbits(
        header_bytes
    )

    # Header followed by payload.
    bit_stream = np.concatenate(
        (
            header_bits,
            payload_bits
        )
    )

    embedded_bits = bit_stream.size

    # -------------------------------------------------------------
    # Randomly select unique carrier positions
    # -------------------------------------------------------------

    carrier_order = position_rng.permutation(
        capacity_bits
    )

    selected_positions = carrier_order[
        :embedded_bits
    ].copy()

    # Save original values for diagnostics
    original_values = flat_pixels[
        selected_positions
    ].copy()

    # -------------------------------------------------------------
    # Perform LSB replacement
    # -------------------------------------------------------------

    flat_pixels[selected_positions] = (
        (
            flat_pixels[selected_positions]
            & 0xFE
        )
        | bit_stream
    )

    changed_values = int(
        np.count_nonzero(
            original_values != flat_pixels[selected_positions]
        )
    )

    # -------------------------------------------------------------
    # Restore original image shape
    # -------------------------------------------------------------

    stego_pixels = flat_pixels.reshape(
        clean_pixels.shape
    )

    # -------------------------------------------------------------
    # Save new image
    # -------------------------------------------------------------

    output_path = build_output_path(
        source_path,
        stego_dir
    )

    Image.fromarray(
        stego_pixels
    ).save(
        output_path,
        format = "PNG"
    )

    # -------------------------------------------------------------
    # Return dataset metadata
    # -------------------------------------------------------------

    return {
        "Source_image": str(source_path),
        "Stego_image": str(output_path),
        "Payload_rate": payload_rate,
        "Payload_bytes": int(payload_byte_count),
        "Random_seed": random_seed,
        "Image_mode": image_mode,
        "Dimensions": dimensions,
        "Capacity_bits": int(capacity_bits),
        "Embedded_bits": int(embedded_bits),
        "Changed_values": changed_values
    }


def embed_clean_folder(payload_rate, base_seed = 100, clean_dir = "dataset/clean", stego_dir = "dataset/stego"):
    """
    Creates stego counterparts for every PNG image
    inside the dataset/clean folder.
    
    Each clean image will be processed using embed_lsb().
    
    Parameters:
        clean_dir:
            Folder containing clean PNG images.
            
        stego_dir:
            Folder where stego images will be saved.
            
        payload_rate:
            Payload rate used for each image.
            
        base_seed:
            Starting seed used to create unique reproducible
            seeds for each image.
            
    Returns:
        List of metadata dictionaries, one for each
        generated stego image.
    """

    clean_dir = Path(clean_dir)
    stego_dir = Path(stego_dir)

    # Make sure clean folder exists
    if not clean_dir.exists():
        raise FileNotFoundError(
            f"Clean image folder does not exist: {clean_dir}"
        )

    if not clean_dir.is_dir():
        raise ValueError(
            f"Clean image path is not a folder: {clean_dir}"
        )

    # Make sure base seed is valid
    if not isinstance(base_seed, (int, np.integer)):
        raise ValueError(
            "Base seed must be an integer"
        )

    if base_seed < 0:
        raise ValueError(
            "Base seed must be 0 or greater"
        )

    # Find every PNG in dataset/clean
    clean_images = sorted(
        clean_dir.glob("*.png")
    )

    if not clean_images:
        raise ValueError(
            f"No PNG images found in: {clean_dir}"
        )

    # Store metadata returned for every image
    results = []

    for index, image_path in enumerate(
        clean_images
    ):

        # Give every image its own reproducible seed
        image_seed = base_seed + index

        result = embed_lsb(
            source_image = image_path,
            payload_rate = payload_rate,
            random_seed = image_seed,
            stego_dir = stego_dir
        )

        results.append(result)

    return results


# Test
if __name__ == "__main__":

    results = embed_clean_folder(
        payload_rate = 0.25
    )

    print(f"\nLSB Embedding Complete: {len(results)} image(s) processed.")

    for result in results:
        print(f"\nClean: {result['Source_image']}")
        print(f"Stego: {result['Stego_image']}")
        print(f"Payload Rate: {result['Payload_rate']}")
        print(f"Random Seed: {result['Random_seed']}")
        print(f"Image Mode: {result['Image_mode']}")
        print(f"Dimensions: {result['Dimensions']}")
        print(f"Changed Values: {result['Changed_values']}")
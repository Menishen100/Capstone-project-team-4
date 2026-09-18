import numpy as np
import pytest
from PIL import Image

from src.lsb_embedder import embed_lsb


def create_grayscale_image(path):
    """
    Create a small 16 x 16 grayscale PNG for testing.
    """

    pixels = np.arange(
        16 * 16,
        dtype=np.uint8
    ).reshape(16, 16)

    Image.fromarray(
        pixels
    ).save(
        path,
        format="PNG"
    )

    return pixels


def create_rgb_image(path):
    """
    Create a small 16 x 16 RGB PNG for testing.
    """

    values = (
        np.arange(
            16 * 16 * 3,
            dtype=np.uint16
        )
        % 256
    ).astype(np.uint8)

    pixels = values.reshape(
        16,
        16,
        3
    )

    Image.fromarray(
        pixels
    ).save(
        path,
        format="PNG"
    )

    return pixels


def test_grayscale_dimensions_are_preserved(tmp_path):
    clean_path = tmp_path / "pair_001_clean.png"
    stego_dir = tmp_path / "stego"

    create_grayscale_image(
        clean_path
    )

    result = embed_lsb(
        clean_path,
        payload_rate=0.25,
        random_seed=2026,
        stego_dir=stego_dir
    )

    with Image.open(clean_path) as clean:
        with Image.open(result["Stego_image"]) as stego:
            assert clean.size == stego.size


def test_grayscale_mode_is_preserved(tmp_path):
    clean_path = tmp_path / "pair_001_clean.png"
    stego_dir = tmp_path / "stego"

    create_grayscale_image(
        clean_path
    )

    result = embed_lsb(
        clean_path,
        payload_rate=0.25,
        random_seed=2026,
        stego_dir=stego_dir
    )

    with Image.open(result["Stego_image"]) as stego:
        assert stego.mode == "L"


def test_rgb_mode_is_preserved(tmp_path):
    clean_path = tmp_path / "pair_001_clean.png"
    stego_dir = tmp_path / "stego"

    create_rgb_image(
        clean_path
    )

    result = embed_lsb(
        clean_path,
        payload_rate=0.25,
        random_seed=2026,
        stego_dir=stego_dir
    )

    with Image.open(result["Stego_image"]) as stego:
        assert stego.mode == "RGB"


def test_same_seed_produces_same_output(tmp_path):
    clean_path = tmp_path / "pair_001_clean.png"

    output_one = tmp_path / "stego_one"
    output_two = tmp_path / "stego_two"

    create_grayscale_image(
        clean_path
    )

    result_one = embed_lsb(
        clean_path,
        payload_rate=0.50,
        random_seed=2026,
        stego_dir=output_one
    )

    result_two = embed_lsb(
        clean_path,
        payload_rate=0.50,
        random_seed=2026,
        stego_dir=output_two
    )

    with Image.open(result_one["Stego_image"]) as first:
        first_pixels = np.array(first)

    with Image.open(result_two["Stego_image"]) as second:
        second_pixels = np.array(second)

    assert np.array_equal(
        first_pixels,
        second_pixels
    )


def test_nonzero_payload_changes_image(tmp_path):
    clean_path = tmp_path / "pair_001_clean.png"
    stego_dir = tmp_path / "stego"

    clean_pixels = create_grayscale_image(
        clean_path
    )

    result = embed_lsb(
        clean_path,
        payload_rate=0.50,
        random_seed=2026,
        stego_dir=stego_dir
    )

    with Image.open(result["Stego_image"]) as stego:
        stego_pixels = np.array(stego)

    assert not np.array_equal(
        clean_pixels,
        stego_pixels
    )


def test_only_lsb_bits_change(tmp_path):
    clean_path = tmp_path / "pair_001_clean.png"
    stego_dir = tmp_path / "stego"

    clean_pixels = create_grayscale_image(
        clean_path
    )

    result = embed_lsb(
        clean_path,
        payload_rate=0.50,
        random_seed=2026,
        stego_dir=stego_dir
    )

    with Image.open(result["Stego_image"]) as stego:
        stego_pixels = np.array(stego)

    xor_difference = np.bitwise_xor(
        clean_pixels,
        stego_pixels
    )

    # A value of 0 means no bit changed.
    # A value of 1 means only the LSB changed.
    assert np.all(
        (xor_difference == 0)
        | (xor_difference == 1)
    )


@pytest.mark.parametrize(
    "payload_rate",
    [
        -0.01,
        1.01,
        2.0,
        "invalid",
        None
    ]
)
def test_invalid_payload_rates_are_rejected(
    tmp_path,
    payload_rate
):
    clean_path = tmp_path / "pair_001_clean.png"

    create_grayscale_image(
        clean_path
    )

    with pytest.raises(ValueError):
        embed_lsb(
            clean_path,
            payload_rate=payload_rate,
            random_seed=2026,
            stego_dir=tmp_path / "stego"
        )


def test_tiny_image_is_rejected(tmp_path):
    clean_path = tmp_path / "tiny_clean.png"

    pixels = np.zeros(
        (2, 2),
        dtype=np.uint8
    )

    Image.fromarray(
        pixels
    ).save(
        clean_path,
        format="PNG"
    )

    with pytest.raises(ValueError):
        embed_lsb(
            clean_path,
            payload_rate=0.50,
            random_seed=2026,
            stego_dir=tmp_path / "stego"
        )


def test_unsupported_mode_is_rejected(tmp_path):
    clean_path = tmp_path / "rgba_clean.png"

    pixels = np.zeros(
        (16, 16, 4),
        dtype=np.uint8
    )

    Image.fromarray(
        pixels
    ).save(
        clean_path,
        format="PNG"
    )

    with pytest.raises(ValueError):
        embed_lsb(
            clean_path,
            payload_rate=0.50,
            random_seed=2026,
            stego_dir=tmp_path / "stego"
        )


def test_original_image_is_not_modified(tmp_path):
    clean_path = tmp_path / "pair_001_clean.png"

    create_grayscale_image(
        clean_path
    )

    original_file_bytes = clean_path.read_bytes()

    embed_lsb(
        clean_path,
        payload_rate=0.50,
        random_seed=2026,
        stego_dir=tmp_path / "stego"
    )

    after_file_bytes = clean_path.read_bytes()

    assert (
        original_file_bytes
        == after_file_bytes
    )


def test_metadata_is_recorded(tmp_path):
    clean_path = tmp_path / "pair_001_clean.png"

    create_grayscale_image(
        clean_path
    )

    result = embed_lsb(
        clean_path,
        payload_rate=0.25,
        random_seed=2026,
        stego_dir=tmp_path / "stego"
    )

    assert result["Payload_rate"] == 0.25
    assert result["Random_seed"] == 2026
    assert result["Image_mode"] == "L"
    assert result["Dimensions"] == (16, 16)

    assert (
        result["Source_image"]
        == str(clean_path)
    )


def test_zero_payload_does_not_change_image(tmp_path):
    clean_path = tmp_path / "pair_001_clean.png"
    stego_dir = tmp_path / "stego"

    clean_pixels = create_grayscale_image(
        clean_path
    )

    result = embed_lsb(
        clean_path,
        payload_rate=0.0,
        random_seed=2026,
        stego_dir=stego_dir
    )

    with Image.open(result["Stego_image"]) as stego:
        stego_pixels = np.array(stego)

    assert np.array_equal(
        clean_pixels,
        stego_pixels
    )

    assert result["Payload_bytes"] == 0
    assert result["Embedded_bits"] == 0
    assert result["Changed_values"] == 0


def test_missing_source_image_is_rejected(tmp_path):
    missing_path = tmp_path / "missing_clean.png"

    with pytest.raises(FileNotFoundError):
        embed_lsb(
            missing_path,
            payload_rate=0.25,
            random_seed=2026,
            stego_dir=tmp_path / "stego"
        )


@pytest.mark.parametrize(
    "random_seed",
    [
        -1,
        3.14,
        "invalid",
        None
    ]
)
def test_invalid_random_seeds_are_rejected(
    tmp_path,
    random_seed
):
    clean_path = tmp_path / "pair_001_clean.png"

    create_grayscale_image(
        clean_path
    )

    with pytest.raises(ValueError):
        embed_lsb(
            clean_path,
            payload_rate=0.25,
            random_seed=random_seed,
            stego_dir=tmp_path / "stego"
        )
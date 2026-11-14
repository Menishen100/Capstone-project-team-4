"""Run the Week 12 payload-rate robustness experiment."""

from pathlib import Path
from PIL import Image
import numpy as np
import csv
from src.lsb_embedder import embed_lsb
from src.detectors.difference_histogram import analyze_difference_histogram
from src.ensemble.normalization import (
    normalize_chi_square,
    normalize_rs,
    normalize_dh,
)
from src.detectors.chi_square import ChiSquareDetector
from src.detectors.rs_analysis import RSAnalysisDetector

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CLEAN_DIR = Path("dataset/clean")
EXPERIMENT_DIR = Path("data/week12_payload_images")
RESULT_PATH = Path("data/week12_payload_robustness.csv")
OUTPUT_DIR = Path("docs/assets/week12-progress")

SOURCE_NUMBERS = range(81, 101)
DEFAULT_PAYLOAD_RATE = 0.25
PAYLOAD_RATES = [
    0.10,
    DEFAULT_PAYLOAD_RATE,
    0.50,
    0.75,
    1.00,
]

CHI_WEIGHT = 0.00
RS_WEIGHT = 0.70
DH_WEIGHT = 0.30

DECISION_THRESHOLD = 0.70


def get_week12_clean_images():
    """Return clean source images 081-100."""

    clean_images = []
    for source_number in SOURCE_NUMBERS:

        image_path = CLEAN_DIR / f"pair_{source_number:03d}_clean.png"

        if not image_path.exists():
            raise FileNotFoundError(
                f"Missing Week 12 clean image: {image_path}"
            )

        clean_images.append(image_path)

    return clean_images


def get_payload_directory(payload_rate):
    """Return the Week 12 output folder for a given payload rate."""

    payload_percent = round(payload_rate * 100)

    return EXPERIMENT_DIR / f"payload_{payload_percent:03d}"


def generate_smoke_test_image(clean_images):
    """Generate one Week 12 payload image before running the full experiment."""

    source_image = clean_images[0]

    payload_rate = PAYLOAD_RATES[0]

    random_seed = 2026

    payload_directory = get_payload_directory(payload_rate)

    result = embed_lsb(
        source_image = source_image,
        payload_rate = payload_rate,
        random_seed = random_seed,
        stego_dir = payload_directory,
    )

    return result


def generate_payload_experiment(clean_images):
    """Generate Week 12 stego images for all payload rates."""

    results = []

    for source_index, source_image in enumerate(clean_images):

        source_number = SOURCE_NUMBERS.start + source_index

        random_seed = 2026 + source_index

        for payload_rate in PAYLOAD_RATES:
            payload_directory = get_payload_directory(payload_rate)

            result = embed_lsb(
                source_image = source_image,
                payload_rate = payload_rate,
                random_seed = random_seed,
                stego_dir = payload_directory,
            )

            result["Source_number"] = source_number

            results.append(result)

    return results


def verify_payload_outputs():
    """Verify that each Week 12 payload folder contains 20 images."""

    expected_images_per_payload = len(SOURCE_NUMBERS)

    for payload_rate in PAYLOAD_RATES:

        payload_directory = get_payload_directory(payload_rate)

        generated_images = sorted(payload_directory.glob("*.png"))

        if len(generated_images) != expected_images_per_payload:
            raise ValueError(
                f"Expected {expected_images_per_payload} images "
                f"for payload {payload_rate}, "
                f"found {len(generated_images)}"
            )

        print(
            f"Payload {payload_rate}: "
            f"{len(generated_images)} images verified"
        )


def test_one_dh_image():
    """Run DH analysis on one Week 12 experimental image."""

    image_path = (
        EXPERIMENT_DIR
        / "payload_010"
        / "pair_081_stego.png"
    )

    dh_result = analyze_difference_histogram(image_path)

    raw_roughness = dh_result["raw_dh_roughness"]

    dh_score = raw_roughness / (1.0 + raw_roughness)

    normalized_dh = normalize_dh(dh_score)

    print()
    print("Week 12 single-image DH test:")

    print(f"Image: {dh_result['image']}")

    print(f"Mode: {dh_result['mode']}")

    print(f"Raw DH roughness: {raw_roughness}")

    print(f"DH score: {dh_score}")

    print(f"Normalized DH: {normalized_dh}")

    print(f"Channels analyzed: {len(dh_result['channels'])}")

    return dh_result


def score_dh_experiment(experiment_results):
    """Calculate DH scores for all Week 12 experimental images."""

    dh_results = []

    for experiment_result in experiment_results:

        stego_path = Path(experiment_result["Stego_image"])

        dh_result = analyze_difference_histogram(stego_path)

        raw_roughness = dh_result["raw_dh_roughness"]

        dh_score = raw_roughness / (1.0 + raw_roughness)

        normalized_dh = normalize_dh(dh_score)

        result = {
            "Source_number": experiment_result["Source_number"],
            "Payload_rate": experiment_result["Payload_rate"],
            "Stego_image": str(stego_path),
            "Raw_dh_roughness": raw_roughness,
            "Dh_score": dh_score,
            "Normalized_dh": normalized_dh,
        }

        dh_results.append(result)

    return dh_results


def summarize_dh_by_payload(dh_results):
    """Summarize DH scores for each Week 12 payload rate."""

    summaries = []

    for payload_rate in PAYLOAD_RATES:

        payload_results = [
            result
            for result in dh_results
            if result["Payload_rate"] == payload_rate
        ]

        normalized_values = [
            result["Normalized_dh"]
            for result in payload_results
        ]

        dh_scores = [
            result["Dh_score"]
            for result in payload_results
        ]

        raw_roughness_values = [
            result["Raw_dh_roughness"]
            for result in payload_results
        ]

        summary = {
            "Payload_rate": payload_rate,
            "Image_count": len(payload_results),
            "Mean_raw_dh_roughness": sum(raw_roughness_values) / len(raw_roughness_values),
            "Mean_dh_score": sum(dh_scores) / len(dh_scores),
            "Mean_normalized_dh": sum(normalized_values) / len(normalized_values),
        }

        summaries.append(summary)

    return summaries


def plot_payload_vs_dh_score(dh_summaries):
    """Plot mean normalized DH score across payload rates."""

    OUTPUT_DIR.mkdir(
        parents=True, 
        exist_ok=True
    )

    payload_rates = [
        summary["Payload_rate"]
        for summary in dh_summaries
    ]

    mean_dh_scores = [
        summary["Mean_normalized_dh"]
        for summary in dh_summaries
    ]

    fig, ax = plt.subplots()

    ax.plot(
        payload_rates,
        mean_dh_scores,
        marker = 'o',
    )

    ax.set_xlabel("Payload Rate")

    ax.set_ylabel("Mean Normalized DH Score")

    ax.set_title("Week 12 DH Suspiciousness by Payload Rate")

    ax.set_ylim(0.0, 1.0)

    fig.tight_layout()

    output_path = OUTPUT_DIR / "payload_vs_dh_score.png"

    fig.savefig(
        output_path,
        dpi = 150,
    )

    plt.close(fig)

    return output_path


def test_one_ensemble_image():
    """Run all three detectors on one Week 12 experimental image."""

    image_path = (
        EXPERIMENT_DIR
        / "payload_010"
        / "pair_081_stego.png"
    )

    with Image.open(image_path) as img:
        pixels = np.array(img)

    chi_detector = ChiSquareDetector()
    rs_detector = RSAnalysisDetector()

    chi_result = chi_detector.analyze(pixels)
    rs_result = rs_detector.analyze(pixels)
    dh_result = analyze_difference_histogram(image_path)

    chi_score = chi_result["score"]
    rs_score = rs_result["score"]
    raw_dh_roughness = dh_result["raw_dh_roughness"]

    dh_score = (raw_dh_roughness / (1.0 + raw_dh_roughness))

    normalized_chi = normalize_chi_square(chi_score)
    normalized_rs = normalize_rs(rs_score)
    normalized_dh = normalize_dh(dh_score)

    ensemble_score = (
        CHI_WEIGHT * normalized_chi
        + RS_WEIGHT * normalized_rs
        + DH_WEIGHT * normalized_dh
    )

    prediction = (
        "Stego"
        if ensemble_score >= DECISION_THRESHOLD
        else "Clean"
    )

    print()
    print("Week 12 single-image ensemble test:")

    print(f"Image: {image_path}")

    print(f"Chi score: {chi_score}")

    print(f"Normalized Chi: {normalized_chi}")

    print(f"RS score: {rs_score}")

    print(f"Normalized RS: {normalized_rs}")

    print(f"DH score: {dh_score}")

    print(f"Normalized DH: {normalized_dh}")

    print(f"Ensemble score: {ensemble_score}")

    print(f"Prediction: {prediction}")


def score_ensemble_experiment(experiment_results):
    """Run the locked ensemble on all Week 12 experimental images."""

    results = []

    chi_detector = ChiSquareDetector()
    rs_detector = RSAnalysisDetector()

    for experiment_result in experiment_results:

        image_path = Path(experiment_result["Stego_image"])

        with Image.open(image_path) as img:
            pixels = np.array(img)

        chi_result = chi_detector.analyze(pixels)
        rs_result = rs_detector.analyze(pixels)
        dh_result = analyze_difference_histogram(image_path)

        chi_score = chi_result["score"]
        rs_score = rs_result["score"]

        raw_dh_roughness = dh_result["raw_dh_roughness"]

        dh_score = (raw_dh_roughness / (1.0 + raw_dh_roughness))

        normalized_chi = normalize_chi_square(chi_score)
        normalized_rs = normalize_rs(rs_score)
        normalized_dh = normalize_dh(dh_score)

        ensemble_score = (
            CHI_WEIGHT * normalized_chi
            + RS_WEIGHT * normalized_rs
            + DH_WEIGHT * normalized_dh
        )

        prediction = (
            "Stego"
            if ensemble_score >= DECISION_THRESHOLD
            else "Clean"
        )

        result = {
            "Source_number": experiment_result["Source_number"],
            "Payload_rate": experiment_result["Payload_rate"],
            "Stego_image": str(image_path),
            "Chi_score": chi_score,
            "Normalized_chi": normalized_chi,
            "RS_score": rs_score,
            "Normalized_rs": normalized_rs,
            "DH_score": dh_score,
            "Normalized_dh": normalized_dh,
            "Ensemble_score": ensemble_score,
            "Prediction": prediction,
            "Expected_label": "Stego",
            "Correct": prediction == "Stego",
        }

        results.append(result)

    return results


def summarize_ensemble_by_payload(ensemble_results):
    """Summarize ensemble performance for each Week 12 payload rate."""

    summaries = []

    for payload_rate in PAYLOAD_RATES:

        payload_results = [
            result
            for result in ensemble_results
            if result["Payload_rate"] == payload_rate
        ]

        ensemble_scores = [
            result["Ensemble_score"]
            for result in payload_results
        ]

        detected_count = sum(
            1
            for result in payload_results
            if result["Prediction"] == "Stego"
        )

        image_count = len(payload_results)

        detection_rate = detected_count / image_count

        summary = {
            "Payload_rate": payload_rate,
            "Image_count": image_count,
            "Mean_ensemble_score": sum(ensemble_scores) / image_count,
            "Detected_count": detected_count,
            "Detection_rate": detection_rate,
        }

        summaries.append(summary)

    return summaries


def plot_payload_vs_ensemble_score(ensemble_summaries):
    """Plot mean ensemble score across payload rates."""

    OUTPUT_DIR.mkdir(
        parents = True, 
        exist_ok = True
    )

    payload_rates = [
        summary["Payload_rate"]
        for summary in ensemble_summaries
    ]

    mean_ensemble_scores = [
        summary["Mean_ensemble_score"]
        for summary in ensemble_summaries
    ]

    fig, ax = plt.subplots()

    ax.plot(
        payload_rates,
        mean_ensemble_scores,
        marker = 'o',
    )

    ax.axhline(
        DECISION_THRESHOLD,
        linestyle = '--',
        label = "Decision Threshold"
    )

    ax.set_xlabel("Payload Rate")

    ax.set_ylabel("Mean Ensemble Score")

    ax.set_title("Week 12 Ensemble Score by Payload Rate")

    ax.set_ylim(0.0, 1.0)

    ax.legend()

    fig.tight_layout()

    output_path = OUTPUT_DIR / "payload_vs_ensemble_score.png"

    fig.savefig(
        output_path,
        dpi = 150,
    )

    plt.close(fig)

    return output_path


def plot_payload_detection_rate(ensemble_summaries):
    """Plot stego detection rate across payload rates."""

    OUTPUT_DIR.mkdir(
        parents = True, 
        exist_ok = True
    )

    payload_rates = [
        summary["Payload_rate"]
        for summary in ensemble_summaries
    ]

    detection_rates = [
        summary["Detection_rate"]
        for summary in ensemble_summaries
    ]

    fig, ax = plt.subplots()

    ax.plot(
        payload_rates,
        detection_rates,
        marker = 'o',
    )

    ax.set_xlabel("Payload Rate")

    ax.set_ylabel("Stego Detection Rate")

    ax.set_title("Week 12 Detection Rate by Payload Rate")

    ax.set_ylim(0.0, 1.0)

    fig.tight_layout()

    output_path = OUTPUT_DIR / "payload_detection_rate.png"

    fig.savefig(
        output_path,
        dpi = 150,
    )

    plt.close(fig)

    return output_path


def save_payload_robustness_csv(ensemble_results):
    """Save Week 12 payload robustness results to CSV."""

    RESULT_PATH.parent.mkdir(
        parents = True,
        exist_ok = True
    )

    fieldnames = [
        "Source_number",
        "Payload_rate",
        "Stego_image",
        "Chi_score",
        "Normalized_chi",
        "RS_score",
        "Normalized_rs",
        "DH_score",
        "Normalized_dh",
        "Ensemble_score",
        "Prediction",
        "Expected_label",
        "Correct",
    ]

    with RESULT_PATH.open(
        "w",
        newline = "",
        encoding = "utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames = fieldnames,
        )

        writer.writeheader()

        writer.writerows(ensemble_results)

    return RESULT_PATH


def verify_payload_robustness_csv():
    """Verify the Week 12 robustness CSV contains 100 data rows."""

    with RESULT_PATH.open(
        "r",
        newline = "",
        encoding = "utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        rows = list(reader)

    if len(rows) != 100:
        raise ValueError(
            f"Expected 100 CSV rows, "
            f"found {len(rows)}"
        )

    print()
    print("Week 12 robustness CSV verified.")

    print(f"CSV rows: {len(rows)}")

    print(f"First CSV row: {rows[0]}")

    print(f"Last CSV row: {rows[-1]}")


def main():

    clean_images = get_week12_clean_images()

    print("Week 12 Payload Robustness Setup Verified")

    print(f"Clean source images: {len(clean_images)}")

    print(f"First source: {clean_images[0]}")

    print(f"Last source: {clean_images[-1]}")

    print(f"Default payload rate: {DEFAULT_PAYLOAD_RATE}")

    print(f"Experimental payload rates: {PAYLOAD_RATES}")

    print(
        f"Locked weights: "
        f"Chi = {CHI_WEIGHT}, "
        f"RS = {RS_WEIGHT}, "
        f"DH = {DH_WEIGHT}, "
    )

    print(f"Locked threshold: {DECISION_THRESHOLD}")

    # Smoke test: Prints one Week 12 payload image results (Verified)
    # test_result = generate_smoke_test_image(clean_images)

    # print()
    # print("Week 12 single-image generation test:")

    # print(f"Source image: {test_result['Source_image']}")

    # print(f"Stego image: {test_result['Stego_image']}")

    # print(f"Payload rate: {test_result['Payload_rate']}")

    # print(f"Random seed: {test_result['Random_seed']}")

    # print(f"Changed values: {test_result['Changed_values']}")

    experiment_results = generate_payload_experiment(clean_images)

    print()
    print("Week 12 payload experiment generation complete.")

    print(f"Generated experimental images: {len(experiment_results)}")

    print(f"First generated image: {experiment_results[0]['Stego_image']}")

    print(f"Last generated image: {experiment_results[-1]['Stego_image']}")

    print()
    print("Verifying payload output folders:")

    verify_payload_outputs()

    #Single-image DH smoke test (Verified)
    # test_one_dh_image()

    dh_results = score_dh_experiment(experiment_results)

    print()
    print("Week 12 DH scoring complete.")

    print(f"DH-scored images: {len(dh_results)}")

    print(f"First DH result: {dh_results[0]}")

    print(f"Last DH result: {dh_results[-1]}")

    dh_summaries = summarize_dh_by_payload(dh_results)

    print()
    print("Week 12 DH payload summaries:")

    for summary in dh_summaries:
        print(
            f"Payload {summary['Payload_rate']}: "
            f"n = {summary['Image_count']}, "
            f"Mean normalized DH = {summary['Mean_normalized_dh']:.6f}"
        )

    dh_plot_path = plot_payload_vs_dh_score(dh_summaries)

    print()
    print(f"DH payload plot created: {dh_plot_path}")

    #Single-image ensemble smoke test (Verified)
    # test_one_ensemble_image()

    ensemble_results = score_ensemble_experiment(experiment_results)

    print()
    print("Week 12 ensemble scoring complete.")

    print(f"Ensemble-scored images: {len(ensemble_results)}")

    print(f"First ensemble result: {ensemble_results[0]}")

    print(f"Last ensemble result: {ensemble_results[-1]}")

    ensemble_summaries = summarize_ensemble_by_payload(ensemble_results)

    print()
    print("Week 12 ensemble payload summaries:")

    for summary in ensemble_summaries:
        print(
            f"Payload {summary['Payload_rate']}: "
            f"n = {summary['Image_count']}, "
            f"Mean ensemble score = {summary['Mean_ensemble_score']:.6f}, "
            f"Detected = {summary['Detected_count']}/{summary['Image_count']}, "
            f"Detection rate = {summary['Detection_rate']:.6f}"
        )

    ensemble_plot_path = plot_payload_vs_ensemble_score(ensemble_summaries)

    detection_plot_path = plot_payload_detection_rate(ensemble_summaries)

    print()
    print(f"Ensemble payload plot created: {ensemble_plot_path}")

    print(f"Detection rate plot created: {detection_plot_path}")

    csv_path = save_payload_robustness_csv(ensemble_results)

    print()
    print(f"Week 12 robustness CSV created: {csv_path}")

    print(f"Rows saved: {len(ensemble_results)}")

    verify_payload_robustness_csv()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
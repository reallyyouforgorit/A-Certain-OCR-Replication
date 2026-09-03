from pathlib import Path

import json
import cv2

from ocr import MangaOCR
from text_grouping import group_text_lines
from text_classifier import classify_group
from region_analyzer import analyze_group
from text_mask import create_text_mask, save_mask
from inpaint import inpaint_image, save_image
from analysis_result import build_group_result

# ==========================================
# PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE_PATH = BASE_DIR / "input" / "tes2.png"

OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(
    exist_ok=True
)

MASK_PATH = OUTPUT_DIR / "text_mask.png"

CLEAN_IMAGE_PATH = OUTPUT_DIR / "cleaned_image.png"

ANALYSIS_PATH = OUTPUT_DIR / "analysis.json"


# ==========================================
# LOAD IMAGE
# ==========================================

image = cv2.imread(
    str(IMAGE_PATH)
)

if image is None:

    raise FileNotFoundError(
        f"Gambar tidak ditemukan: {IMAGE_PATH}"
    )


# ==========================================
# OCR
# ==========================================

print("=== OCR ===")

ocr = MangaOCR()

detections = ocr.process(
    IMAGE_PATH
)


# ==========================================
# GROUPING
# ==========================================

print("=== GROUPING ===")

groups = group_text_lines(
    detections
)


# ==========================================
# ANALYSIS
# ==========================================

print()
print("================================")
print("      REGION ANALYSIS")
print("================================")


# ==========================================
# SIMPAN SEMUA HASIL GROUP
# ==========================================

all_results = []
all_groups = []

for group_id, group in enumerate(
    groups,
    start=1
):

    print()
    print(
        f"GROUP {group_id}"
    )

    print("-" * 40)

    # -------------------------------
    # Classification
    # -------------------------------

    classified_lines = classify_group(
        group
    )

    # -------------------------------
    # Container Analysis
    # -------------------------------

    results = analyze_group(
        classified_lines
    )

    # Structured Results

    group_result = build_group_result(
        group_id,
        results
    )

    all_groups.append(
        group_result
    )

    # -------------------------------
    # Simpan results
    # -------------------------------

    all_results.extend(
        results
    )

    # -------------------------------
    # Container info
    # -------------------------------

    if results:

        container_type = results[0][
            "container_type"
        ]

        container_box = results[0][
            "container_box"
        ]

    else:

        container_type = "none"
        container_box = None

    print()
    print(
        f"CONTAINER      : "
        f"{container_type.upper()}"
    )

    print(
        f"CONTAINER BOX  : "
        f"{container_box}"
    )

    print()

    # -------------------------------
    # Lines
    # -------------------------------

    for result in results:

        print(
            f"[{result['type'].upper()}]"
        )

        print(
            result["text"]
        )

        print(
            f"TEXT BOX       : "
            f"{result['box']}"
        )

        print(
            f"ACTION         : "
            f"{result['action']}"
        )

        print()


# ==========================================
# TEXT MASK
# ==========================================

print("================================")
print("         TEXT MASK")
print("================================")


mask = create_text_mask(
    image,
    all_results,
    padding=4
)


save_mask(
    mask,
    MASK_PATH
)


print(
    f"MASK SAVED     : {MASK_PATH}"
)

# ==========================================
# INPAINTING
# ==========================================

print()
print("================================")
print("         INPAINTING")
print("================================")


clean_image = inpaint_image(
    image,
    mask,
    radius=3
)


save_image(
    clean_image,
    CLEAN_IMAGE_PATH
)


print(
    f"CLEAN IMAGE    : {CLEAN_IMAGE_PATH}"
)

# ANALYSIS RESULT

with open(
    ANALYSIS_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_groups,
        f,
        ensure_ascii=False,
        indent=2
    )

print()
print(
    f"ANALYSIS SAVED : {ANALYSIS_PATH}"
)
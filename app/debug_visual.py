from pathlib import Path

import cv2

from ocr import MangaOCR
from text_grouping import group_text_lines
from text_classifier import classify_group


# ==========================================
# PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE_PATH = BASE_DIR / "input" / "tes2.png"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "debug.jpg"


# ==========================================
# OCR
# ==========================================

print("=== MEMULAI OCR ===")

ocr = MangaOCR()

detections = ocr.process(
    IMAGE_PATH
)

print("=== OCR SELESAI ===")


# ==========================================
# GROUPING
# ==========================================

groups = group_text_lines(
    detections
)

print(
    f"=== {len(groups)} GROUP DITEMUKAN ==="
)


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
# COLORS
# ==========================================

COLORS = {

    "watermark": (
        0,
        0,
        255
    ),

    "dialogue": (
        0,
        255,
        0
    ),

    "narration": (
        255,
        0,
        0
    ),

    "sfx": (
        0,
        255,
        255
    ),

    "unknown": (
        255,
        255,
        255
    )
}


# ==========================================
# DRAW
# ==========================================

line_number = 1


for group_id, group in enumerate(
    groups,
    start=1
):

    classified_lines = classify_group(
        group
    )


    for line in classified_lines:

        text = line["text"]

        text_type = line["type"]

        color = COLORS.get(
            text_type,
            COLORS["unknown"]
        )


        # ----------------------------------
        # Ambil bounding box
        # ----------------------------------

        box = line.get("box")

        if box is None:

            print(
                f"[WARNING] "
                f"Tidak ada box untuk: {text}"
            )

            continue


        x1, y1, x2, y2 = box


        # ----------------------------------
        # Draw rectangle
        # ----------------------------------

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            color,
            4
        )


        # ----------------------------------
        # Label
        # ----------------------------------

        label = (
            f"{line_number} | "
            f"{text_type.upper()}"
        )


        cv2.putText(
            image,
            label,
            (x1, max(30, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
            cv2.LINE_AA
        )


        line_number += 1


# ==========================================
# SAVE
# ==========================================

success = cv2.imwrite(
    str(OUTPUT_PATH),
    image
)


if success:

    print()
    print("================================")
    print("     DEBUG IMAGE BERHASIL")
    print("================================")
    print()
    print(
        f"Output: {OUTPUT_PATH}"
    )

else:

    print(
        "GAGAL menyimpan debug image."
    )
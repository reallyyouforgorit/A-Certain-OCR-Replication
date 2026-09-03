# ==========================================
# TEXT MASK GENERATOR
# ==========================================

import cv2
import numpy as np


def create_text_mask(image, results, padding=4):

    height, width = image.shape[:2]

    mask = np.zeros(
        (height, width),
        dtype=np.uint8
    )

    for result in results:

        # Hanya teks yang perlu dihapus
        if result.get("action") != "remove_translate":
            continue

        box = result.get("box")

        if not box:
            continue

        x1, y1, x2, y2 = box

        # Padding
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)

        x2 = min(width, x2 + padding)
        y2 = min(height, y2 + padding)

        # Masukkan area teks ke mask
        mask[y1:y2, x1:x2] = 255

    return mask


def save_mask(mask, output_path):

    cv2.imwrite(
        str(output_path),
        mask
    )
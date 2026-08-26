from pathlib import Path

from ocr import MangaOCR
from text_grouping import group_text_lines
from text_classifier import classify_group


BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE_PATH = BASE_DIR / "input" / "tes.jpg"


ocr = MangaOCR()

detections = ocr.process(
    IMAGE_PATH
)

groups = group_text_lines(
    detections
)


print()
print("================================")
print("       TEXT REGION ANALYSIS")
print("================================")


for group_id, group in enumerate(
    groups,
    start=1
):

    classified_lines = classify_group(
        group
    )

    print()
    print(f"GROUP {group_id}")
    print("-" * 40)

    for line in classified_lines:

        print(
            f"[{line['type'].upper()}]"
        )

        print(
            line["text"]
        )

        print()
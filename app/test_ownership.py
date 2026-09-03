from pathlib import Path
import sys
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BASE_DIR / "app"))

from ocr import MangaOCR
from text_grouping import group_text_lines
from text_classifier import classify_group
from region_analyzer import analyze_group
from container_refinement import refine_containers
from analysis_result import build_group_result


IMAGE_PATH = BASE_DIR / "input" / "tes2.png"


def text_key(text):
    """
    Stable identity untuk satu OCR text.
    Text saja tidak cukup karena dua text berbeda
    bisa memiliki isi yang sama.
    """
    value = text.get("text", "").strip()

    box = text.get("box")

    if box is not None:
        box = tuple(box)

    return (value, box)


print()
print("=" * 40)
print("       TEXT OWNERSHIP TEST")
print("=" * 40)


# ============================================================
# 1. OCR
# ============================================================

ocr = MangaOCR()
detections = ocr.process(IMAGE_PATH)


# ============================================================
# 2. GROUPING
# ============================================================

groups = group_text_lines(detections)


# ============================================================
# 3. CLASSIFICATION + REGION ANALYSIS
# ============================================================

analyzed_groups = []

for group_id, group in enumerate(groups, start=1):

    classified = classify_group(group)

    analyzed = analyze_group(classified)

    if not analyzed:
        continue

    group_result = build_group_result(
        group_id,
        analyzed
    )

    group_result["container_box"] = group_result["container"]["box"]
    group_result["container_type"] = group_result["container"]["type"]

    analyzed_groups.append(group_result)


# ============================================================
# 4. REFINEMENT
# ============================================================

refined = refine_containers(analyzed_groups)


logical = [
    c for c in refined
    if not c.get("excluded_from_reading_order", False)
]

aggregate = [
    c for c in refined
    if c.get("container_role") == "aggregate"
]


# ============================================================
# 5. COLLECT SOURCE TEXTS
# ============================================================

source_texts = {}

for group in analyzed_groups:

    group_id = group["group_id"]

    for text in group.get("texts", []):

        if text.get("action") != "remove_translate":
            continue

        key = text_key(text)

        source_texts[key] = {
            "group_id": group_id,
            "text": text
        }


# ============================================================
# 6. COLLECT LOGICAL CONTAINER TEXTS
# ============================================================

logical_texts = defaultdict(list)

for container in logical:

    container_id = container.get("container_id")

    for text in container.get("texts", []):

        if text.get("action") != "remove_translate":
            continue

        key = text_key(text)

        logical_texts[key].append({
            "container_id": container_id,
            "text": text
        })


# ============================================================
# 7. COLLECT AGGREGATE TEXTS
# ============================================================

aggregate_texts = defaultdict(list)

for container in aggregate:

    container_id = container.get("container_id")

    for text in container.get("texts", []):

        if text.get("action") != "remove_translate":
            continue

        key = text_key(text)

        aggregate_texts[key].append({
            "container_id": container_id,
            "text": text
        })


# ============================================================
# 8. FIND ORPHAN TEXTS
# ============================================================

orphan_texts = []

for key, info in source_texts.items():

    if key not in logical_texts:

        orphan_texts.append(info)


# ============================================================
# 9. FIND DUPLICATE LOGICAL TEXTS
# ============================================================

duplicate_texts = []

for key, owners in logical_texts.items():

    if len(owners) > 1:

        duplicate_texts.append({
            "key": key,
            "owners": owners
        })


# ============================================================
# 10. FIND AGGREGATE-ONLY TEXTS
# ============================================================

aggregate_only = []

for key, owners in aggregate_texts.items():

    if key not in logical_texts:

        aggregate_only.append({
            "key": key,
            "owners": owners
        })


# ============================================================
# 11. PRINT STRUCTURE
# ============================================================

print()
print("=" * 40)
print("       TEXT COUNTS")
print("=" * 40)

print(f"SOURCE TRANSLATABLE : {len(source_texts)}")
print(f"LOGICAL TEXTS       : {len(logical_texts)}")
print(f"AGGREGATE TEXTS     : {len(aggregate_texts)}")


# ============================================================
# 12. ORPHAN TEXTS
# ============================================================

print()
print("=" * 40)
print("       ORPHAN TEXTS")
print("=" * 40)

if not orphan_texts:

    print("NONE")

else:

    for item in orphan_texts:

        text = item["text"]

        print(
            f"G{item['group_id']:02d} -> "
            f"{text.get('text', '')}"
        )


# ============================================================
# 13. DUPLICATE TEXTS
# ============================================================

print()
print("=" * 40)
print("       DUPLICATE LOGICAL TEXTS")
print("=" * 40)

if not duplicate_texts:

    print("NONE")

else:

    for item in duplicate_texts:

        key = item["key"]

        print()
        print(f"TEXT : {key[0]}")
        print("OWNERS :")

        for owner in item["owners"]:

            print(
                f"  C{owner['container_id']}"
            )


# ============================================================
# 14. AGGREGATE-ONLY TEXTS
# ============================================================

print()
print("=" * 40)
print("       AGGREGATE-ONLY TEXTS")
print("=" * 40)

if not aggregate_only:

    print("NONE")

else:

    for item in aggregate_only:

        key = item["key"]

        print()
        print(f"TEXT : {key[0]}")

        for owner in item["owners"]:

            print(
                f"  C{owner['container_id']}"
            )


# ============================================================
# 15. AGGREGATE DETAILS
# ============================================================

print()
print("=" * 40)
print("       AGGREGATE DETAILS")
print("=" * 40)

for container in aggregate:

    cid = container.get("container_id")

    print()
    print(f"C{cid}")
    print(f"GROUPS : {container.get('group_ids', [])}")
    print(f"TEXTS  : {len(container.get('texts', []))}")

    matched = 0
    unmatched = 0

    for text in container.get("texts", []):

        if text.get("action") != "remove_translate":
            continue

        key = text_key(text)

        if key in logical_texts:
            matched += 1
        else:
            unmatched += 1

    print(f"MATCHED TO LOGICAL : {matched}")
    print(f"AGGREGATE ONLY     : {unmatched}")


# ============================================================
# 16. FINAL VERDICT
# ============================================================

print()
print("=" * 40)
print("          FINAL VERDICT")
print("=" * 40)

print(
    f"Orphan texts       : {len(orphan_texts)}"
)

print(
    f"Duplicate texts    : {len(duplicate_texts)}"
)

print(
    f"Aggregate-only     : {len(aggregate_only)}"
)

print()

if (
    len(orphan_texts) == 0
    and len(duplicate_texts) == 0
    and len(aggregate_only) == 0
):

    print("STATUS : PASS")
    print()
    print(
        "Semua text translatable memiliki "
        "logical container yang valid."
    )
    print(
        "Aggregate dapat dikeluarkan dari "
        "reading order tanpa kehilangan text."
    )

else:

    print("STATUS : REVIEW")
    print()
    print(
        "Masih ada text yang perlu diperiksa "
        "sebelum Reading Order."
    )
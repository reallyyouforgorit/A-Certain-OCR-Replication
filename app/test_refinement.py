from pathlib import Path

from ocr import MangaOCR
from text_grouping import group_text_lines
from text_classifier import classify_group
from region_analyzer import analyze_group

from container_refinement import (
    refine_containers,
    print_refined_containers,
    get_reading_order_containers,
)


# ==========================================
# PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE_PATH = BASE_DIR / "input" / "tes2.png"


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("=" * 32)
    print("    CONTAINER REFINEMENT")
    print("=" * 32)


    # ======================================
    # OCR
    # ======================================

    print()
    print("=== OCR ===")

    ocr = MangaOCR()

    detections = ocr.process(
        IMAGE_PATH
    )


    # ======================================
    # GROUPING
    # ======================================

    print()
    print("=== GROUPING ===")

    groups = group_text_lines(
        detections
    )

    print(
        f"RAW GROUPS : {len(groups)}"
    )


    # ======================================
    # REGION ANALYSIS
    # ======================================

    print()
    print("=" * 32)
    print("      REGION ANALYSIS")
    print("=" * 32)


    analyzed_groups = []


    for group_id, group in enumerate(
        groups,
        start=1
    ):

        # ------------------------------
        # Classification
        # ------------------------------

        classified_lines = classify_group(
            group
        )


        # ------------------------------
        # Container Analysis
        # ------------------------------

        results = analyze_group(
            classified_lines
        )


        if not results:
            continue


        # --------------------------------
        # Build group-level structure
        # --------------------------------

        texts = []

        for result in results:

            if result.get("action") == "remove_translate":

                texts.append(result)


        # Kalau tidak ada teks yang
        # perlu diterjemahkan, skip
        if not texts:
            continue


        container_type = results[0].get(
            "container_type"
        )

        container_box = results[0].get(
            "container_box"
        )


        analyzed_groups.append({

            "group_id": group_id,

            "type": container_type,

            "box": container_box,

            "texts": texts,

        })


    print()
    print(
        f"ANALYZED GROUPS : "
        f"{len(analyzed_groups)}"
    )


    # ======================================
    # CONTAINER REFINEMENT
    # ======================================

    print()
    print("=" * 32)
    print("     REFINING CONTAINERS")
    print("=" * 32)


    refined = refine_containers(
        analyzed_groups
    )


    print()
    print(
        f"REFINED : {len(refined)}"
    )


    # ======================================
    # DEBUG
    # ======================================

    print_refined_containers(
        refined
    )


    # ======================================
    # READING ORDER INPUT
    # ======================================

    reading_input = (
        get_reading_order_containers(
            refined
        )
    )


    print()
    print("=" * 32)
    print("   READING ORDER INPUT")
    print("=" * 32)


    print(
        f"TOTAL : {len(reading_input)}"
    )


    for item in reading_input:

        print()

        print(
            f"C{item['container_id']}"
        )

        print(
            f"  BOX    : {item['box']}"
        )

        print(
            f"  GROUPS : "
            f"{item.get('group_ids', [])}"
        )

        print(
            f"  TEXTS  : "
            f"{len(item.get('texts', []))}"
        )


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    main()
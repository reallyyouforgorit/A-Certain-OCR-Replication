from region_analyzer import analyze_group
from container_refinement import (
    refine_containers,
    print_refined_containers,
    get_reading_order_containers,
)


IMAGE_PATH = "input/tes2.png"


def main():

    print()
    print("=" * 32)
    print("    CONTAINER REFINEMENT")
    print("=" * 32)

    # --------------------------------------------------------
    # REGION ANALYSIS
    # --------------------------------------------------------

    groups = analyze_group(IMAGE_PATH)

    print(
        f"INPUT GROUPS : {len(groups)}"
    )

    # --------------------------------------------------------
    # REFINEMENT
    # --------------------------------------------------------

    refined = refine_containers(groups)

    print(
        f"REFINED      : {len(refined)}"
    )

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    print_refined_containers(
        refined
    )

    # --------------------------------------------------------
    # READING ORDER INPUT
    # --------------------------------------------------------

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
            f"  GROUPS : {item.get('group_ids', [])}"
        )

        print(
            f"  TEXTS  : {len(item.get('texts', []))}"
        )


if __name__ == "__main__":
    main()
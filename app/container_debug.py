from pathlib import Path
import json


# ==========================================
# PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

ANALYSIS_PATH = BASE_DIR / "output" / "analysis.json"


# ==========================================
# LOAD
# ==========================================

with open(
    ANALYSIS_PATH,
    "r",
    encoding="utf-8"
) as f:
    groups = json.load(f)


# ==========================================
# HELPERS
# ==========================================

def area(box):
    x1, y1, x2, y2 = box

    return max(0, x2 - x1) * max(0, y2 - y1)


def contains(outer, inner):
    ox1, oy1, ox2, oy2 = outer
    ix1, iy1, ix2, iy2 = inner

    return (
        ox1 <= ix1
        and oy1 <= iy1
        and ox2 >= ix2
        and oy2 >= iy2
    )


def overlap_ratio(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0, ix2 - ix1)
    ih = max(0, iy2 - iy1)

    intersection = iw * ih

    if intersection == 0:
        return 0

    smaller_area = min(
        area(a),
        area(b)
    )

    if smaller_area == 0:
        return 0

    return intersection / smaller_area


# ==========================================
# BUILD
# ==========================================

items = []

for group in groups:

    container = group.get("container")

    if not container:
        continue

    box = container.get("box")

    if not box:
        continue

    texts = [
        text
        for text in group.get("texts", [])
        if text.get("action") == "remove_translate"
    ]

    if not texts:
        continue

    items.append({
        "group_id": group.get("group_id"),
        "box": box,
        "type": container.get("type"),
        "text_count": len(texts),
        "area": area(box)
    })


# ==========================================
# DEBUG
# ==========================================

print()
print("================================")
print("      CONTAINER ANALYSIS")
print("================================")

print(
    f"TOTAL CONTAINERS : {len(items)}"
)


# ==========================================
# CONTAINER INFO
# ==========================================

for item in items:

    x1, y1, x2, y2 = item["box"]

    width = x2 - x1
    height = y2 - y1

    print()
    print(
        f"G{item['group_id']}"
    )

    print(
        f"  TYPE   : {item['type']}"
    )

    print(
        f"  BOX    : {item['box']}"
    )

    print(
        f"  SIZE   : {width} x {height}"
    )

    print(
        f"  AREA   : {item['area']:,}"
    )

    print(
        f"  TEXTS  : {item['text_count']}"
    )


# ==========================================
# NESTED CONTAINERS
# ==========================================

print()
print("================================")
print("      NESTED CONTAINERS")
print("================================")


found_nested = False

for outer in items:

    children = []

    for inner in items:

        if (
            outer["group_id"]
            == inner["group_id"]
        ):
            continue

        if contains(
            outer["box"],
            inner["box"]
        ):
            children.append(
                inner["group_id"]
            )

    if children:

        found_nested = True

        print()
        print(
            f"G{outer['group_id']} "
            f"CONTAINS:"
        )

        print(
            "  "
            + ", ".join(
                f"G{x}"
                for x in children
            )
        )


if not found_nested:

    print(
        "Tidak ditemukan nested container."
    )


# ==========================================
# HEAVY OVERLAP
# ==========================================

print()
print("================================")
print("      HEAVY OVERLAP")
print("================================")


found_overlap = False

for i in range(len(items)):

    for j in range(i + 1, len(items)):

        a = items[i]
        b = items[j]

        ratio = overlap_ratio(
            a["box"],
            b["box"]
        )

        # >50% area container kecil
        # tertutup container lain
        if ratio >= 0.50:

            found_overlap = True

            print(
                f"G{a['group_id']} "
                f"<-> "
                f"G{b['group_id']} "
                f": {ratio:.2f}"
            )


if not found_overlap:

    print(
        "Tidak ditemukan overlap berat."
    )
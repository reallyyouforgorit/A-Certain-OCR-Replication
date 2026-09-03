from pathlib import Path
import json
import cv2

from reading_order import sort_reading_order


# ==========================================
# PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

ANALYSIS_PATH = BASE_DIR / "output" / "analysis.json"
IMAGE_PATH = BASE_DIR / "input" / "tes.jpg"
OUTPUT_PATH = BASE_DIR / "output" / "reading_order_debug.jpg"


# ==========================================
# LOAD ANALYSIS
# ==========================================

with open(
    ANALYSIS_PATH,
    "r",
    encoding="utf-8"
) as f:
    groups = json.load(f)


# ==========================================
# LOAD IMAGE
# ==========================================

image = cv2.imread(str(IMAGE_PATH))

if image is None:
    raise FileNotFoundError(
        f"Gambar tidak ditemukan: {IMAGE_PATH}"
    )


# ==========================================
# BUILD READING ORDER ITEMS
# ==========================================

items = []

for group in groups:

    container = group.get("container")

    if not container:
        continue

    box = container.get("box")

    if box is None:
        continue

    # Ambil hanya text yang memang
    # akan diterjemahkan.
    texts = [
        text
        for text in group.get("texts", [])
        if text.get("action") == "remove_translate"
    ]

    # Kalau group tidak punya text yang
    # perlu diterjemahkan, skip.
    if not texts:
        continue

    items.append({
        "group_id": group.get("group_id"),
        "container": container,
        "texts": texts
    })


# ==========================================
# DEBUG INPUT
# ==========================================

print()
print("================================")
print("       READING ORDER INPUT")
print("================================")

print(
    f"TOTAL GROUPS        : {len(groups)}"
)

print(
    f"TRANSLATABLE GROUPS  : {len(items)}"
)


# ==========================================
# READING ORDER
# ==========================================

ordered_items = sort_reading_order(items)


# ==========================================
# PRINT RESULT
# ==========================================

print()
print("================================")
print("       READING ORDER")
print("================================")


for order_id, item in enumerate(
    ordered_items,
    start=1
):

    box = item["container"]["box"]

    x1, y1, x2, y2 = box

    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2

    print()
    print(f"ORDER {order_id}")
    print(f"GROUP  : {item['group_id']}")
    print(f"BOX    : {box}")
    print(f"CENTER : ({cx}, {cy})")

    print("TEXTS:")

    for text in item["texts"]:
        print(
            f"  - [{text['type']}] "
            f"{text['text']}"
        )


# ==========================================
# DRAW DEBUG IMAGE
# ==========================================

for order_id, item in enumerate(
    ordered_items,
    start=1
):

    x1, y1, x2, y2 = map(
        int,
        item["container"]["box"]
    )

    # --------------------------------------
    # Container box
    # --------------------------------------

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        4
    )

    # --------------------------------------
    # Reading order number
    # --------------------------------------

    cv2.putText(
        image,
        str(order_id),
        (x1 + 10, y1 + 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.4,
        (0, 0, 255),
        4,
        cv2.LINE_AA
    )

    # --------------------------------------
    # Group ID
    # --------------------------------------

    cv2.putText(
        image,
        f"G{item['group_id']}",
        (x1 + 10, y1 + 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 0, 0),
        3,
        cv2.LINE_AA
    )


# ==========================================
# SAVE
# ==========================================

cv2.imwrite(
    str(OUTPUT_PATH),
    image
)


print()
print("================================")
print("       DEBUG OUTPUT")
print("================================")

print(
    f"IMAGE : {OUTPUT_PATH}"
)

print(
    f"TOTAL : {len(ordered_items)}"
)
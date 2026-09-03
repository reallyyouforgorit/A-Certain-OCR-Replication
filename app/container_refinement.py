from __future__ import annotations

from copy import deepcopy
from math import hypot
from statistics import median


# ============================================================
# CONFIG
# ============================================================

# Seberapa dekat dua group boleh dianggap satu container.
DISTANCE_FACTOR = 2.5

# Unknown yang terlalu besar dibanding unknown lain biasanya
# bukan satu potongan teks biasa.
MAX_UNKNOWN_AREA_FACTOR = 8.0

# Container yang mengandung banyak group lain dan sangat besar
# dibanding child-nya dianggap aggregate/structural.
AGGREGATE_CHILD_COUNT = 3
AGGREGATE_AREA_FACTOR = 4.0


# ============================================================
# BASIC HELPERS
# ============================================================

def get_box(item):
    """
    Mendapatkan bounding box.

    Prioritas:
        container_box
        box
        text_box
    """

    if "container_box" in item and item["container_box"] is not None:
        return item["container_box"]

    if "box" in item and item["box"] is not None:
        return item["box"]

    if "text_box" in item and item["text_box"] is not None:
        return item["text_box"]

    raise ValueError(f"Item tidak memiliki bounding box: {item}")


def normalize_box(box):
    x1, y1, x2, y2 = box

    return [
        min(x1, x2),
        min(y1, y2),
        max(x1, x2),
        max(y1, y2),
    ]


def box_width(box):
    x1, _, x2, _ = normalize_box(box)
    return max(1, x2 - x1)


def box_height(box):
    _, y1, _, y2 = normalize_box(box)
    return max(1, y2 - y1)


def box_area(box):
    return box_width(box) * box_height(box)


def box_center(box):
    x1, y1, x2, y2 = normalize_box(box)

    return (
        (x1 + x2) / 2,
        (y1 + y2) / 2,
    )


def center_distance(box_a, box_b):
    ax, ay = box_center(box_a)
    bx, by = box_center(box_b)

    return hypot(ax - bx, ay - by)


def horizontal_gap(box_a, box_b):
    ax1, _, ax2, _ = normalize_box(box_a)
    bx1, _, bx2, _ = normalize_box(box_b)

    if ax2 < bx1:
        return bx1 - ax2

    if bx2 < ax1:
        return ax1 - bx2

    return 0


def vertical_gap(box_a, box_b):
    _, ay1, _, ay2 = normalize_box(box_a)
    _, by1, _, by2 = normalize_box(box_b)

    if ay2 < by1:
        return by1 - ay2

    if by2 < ay1:
        return ay1 - by2

    return 0


def intersection_area(box_a, box_b):
    ax1, ay1, ax2, ay2 = normalize_box(box_a)
    bx1, by1, bx2, by2 = normalize_box(box_b)

    x1 = max(ax1, bx1)
    y1 = max(ay1, by1)
    x2 = min(ax2, bx2)
    y2 = min(ay2, by2)

    if x2 <= x1 or y2 <= y1:
        return 0

    return (x2 - x1) * (y2 - y1)


def iou(box_a, box_b):
    inter = intersection_area(box_a, box_b)

    if inter == 0:
        return 0.0

    union = box_area(box_a) + box_area(box_b) - inter

    if union <= 0:
        return 0.0

    return inter / union


# ============================================================
# TEXT / TYPE HELPERS
# ============================================================

def get_type(item):
    return str(
        item.get(
            "type",
            item.get("class", "unknown")
        )
    ).lower()


def get_text_count(item):
    texts = item.get("texts")

    if isinstance(texts, list):
        return len(texts)

    text = item.get("text")

    if text:
        return 1

    return 0


def get_text_height(item):
    """
    Estimasi tinggi karakter berdasarkan tinggi bounding box.

    Untuk vertical Japanese text, tinggi box dapat besar,
    sehingga kita gunakan ukuran sisi terkecil sebagai baseline.
    """

    box = get_box(item)

    return min(
        box_width(box),
        box_height(box)
    )


def is_unknown(item):
    return get_type(item) in {
        "unknown",
        "other",
        "",
        "none",
    }


# ============================================================
# UNION FIND
# ============================================================

class UnionFind:

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]

        return x

    def union(self, a, b):
        ra = self.find(a)
        rb = self.find(b)

        if ra == rb:
            return

        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb

        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra

        else:
            self.parent[rb] = ra
            self.rank[ra] += 1


# ============================================================
# MERGE DECISION
# ============================================================

def should_merge_unknown(a, b, median_size):
    """
    Menentukan apakah dua UNKNOWN merupakan bagian dari
    logical text container yang sama.

    Kita tidak menggunakan IoU saja.

    Pertimbangan:
        - jarak
        - horizontal / vertical alignment
        - ukuran relatif
        - overlap
    """

    box_a = get_box(a)
    box_b = get_box(b)

    wa = box_width(box_a)
    ha = box_height(box_a)

    wb = box_width(box_b)
    hb = box_height(box_b)

    # --------------------------------------------------------
    # 1. Strong overlap
    # --------------------------------------------------------

    overlap = iou(box_a, box_b)

    if overlap >= 0.20:
        return True

    # --------------------------------------------------------
    # 2. Distance threshold
    # --------------------------------------------------------

    threshold = max(
        30,
        median_size * DISTANCE_FACTOR
    )

    distance = center_distance(box_a, box_b)

    if distance > threshold:
        return False

    # --------------------------------------------------------
    # 3. Horizontal relationship
    # --------------------------------------------------------

    h_gap = horizontal_gap(box_a, box_b)

    vertical_center_difference = abs(
        box_center(box_a)[1] -
        box_center(box_b)[1]
    )

    vertical_reference = max(
        ha,
        hb,
        median_size
    )

    horizontal_candidate = (
        h_gap <= threshold
        and
        vertical_center_difference
        <= vertical_reference * 1.5
    )

    if horizontal_candidate:
        return True

    # --------------------------------------------------------
    # 4. Vertical relationship
    # --------------------------------------------------------

    v_gap = vertical_gap(box_a, box_b)

    horizontal_center_difference = abs(
        box_center(box_a)[0] -
        box_center(box_b)[0]
    )

    horizontal_reference = max(
        wa,
        wb,
        median_size
    )

    vertical_candidate = (
        v_gap <= threshold
        and
        horizontal_center_difference
        <= horizontal_reference * 1.5
    )

    if vertical_candidate:
        return True

    return False


# ============================================================
# MERGE GROUPS
# ============================================================

def merge_group_items(items, group_indices):
    """
    Menggabungkan beberapa OCR groups menjadi satu container.
    """

    selected = [
        items[i]
        for i in group_indices
    ]

    boxes = [
        normalize_box(get_box(item))
        for item in selected
    ]

    x1 = min(box[0] for box in boxes)
    y1 = min(box[1] for box in boxes)
    x2 = max(box[2] for box in boxes)
    y2 = max(box[3] for box in boxes)

    merged_texts = []

    for item in selected:

        texts = item.get("texts")

        if isinstance(texts, list):
            merged_texts.extend(
                deepcopy(texts)
            )

        elif item.get("text"):
            merged_texts.append(
                deepcopy(item["text"])
            )

    # Group IDs
    group_ids = []

    for item in selected:

        gid = item.get(
            "group_id",
            item.get("id")
        )

        if gid is not None:
            group_ids.append(gid)

    merged = {
        "type": "textbox",
        "box": [x1, y1, x2, y2],
        "group_ids": group_ids,
        "texts": merged_texts,

        # useful debug information
        "refined": True,
        "source_count": len(selected),
    }

    return merged


# ============================================================
# AGGREGATE DETECTION
# ============================================================

def find_contained_indices(items, parent_index):
    """
    Cari item yang berada di dalam parent.

    Ini hanya digunakan untuk mendeteksi aggregate region,
    bukan langsung menentukan logical container.
    """

    parent_box = get_box(items[parent_index])

    children = []

    for i, item in enumerate(items):

        if i == parent_index:
            continue

        child_box = get_box(item)

        inter = intersection_area(
            parent_box,
            child_box
        )

        if inter <= 0:
            continue

        child_area = box_area(child_box)

        if child_area <= 0:
            continue

        coverage = inter / child_area

        if coverage >= 0.95:
            children.append(i)

    return children


def detect_aggregate_regions(items):
    """
    Mendeteksi bounding box besar yang sebenarnya merupakan
    parent geometris, bukan logical textbox.

    Contoh target:
        G4
        G31
    """

    aggregates = set()

    for i, item in enumerate(items):

        children = find_contained_indices(
            items,
            i
        )

        if len(children) < AGGREGATE_CHILD_COUNT:
            continue

        parent_area = box_area(
            get_box(item)
        )

        child_areas = [
            box_area(get_box(items[c]))
            for c in children
            if box_area(get_box(items[c])) > 0
        ]

        if not child_areas:
            continue

        child_median = median(child_areas)

        # Parent sangat besar dibanding child
        if (
            parent_area
            >= child_median * AGGREGATE_AREA_FACTOR
        ):
            aggregates.add(i)

    return aggregates


# ============================================================
# MAIN REFINEMENT
# ============================================================

def refine_containers(groups):
    """
    Main API.

    Input:
        list of GROUP dictionaries dari region_analyzer.py

    Output:
        list of refined logical containers.
    """

    if not groups:
        return []

    items = deepcopy(groups)

    # --------------------------------------------------------
    # STEP 1
    # Detect aggregate regions
    # --------------------------------------------------------

    aggregate_indices = detect_aggregate_regions(items)

    # --------------------------------------------------------
    # STEP 2
    # Separate normal groups and aggregate groups
    # --------------------------------------------------------

    normal_indices = [
        i
        for i in range(len(items))
        if i not in aggregate_indices
    ]

    # --------------------------------------------------------
    # STEP 3
    # Estimate text scale
    # --------------------------------------------------------

    sizes = [
        get_text_height(items[i])
        for i in normal_indices
        if get_text_height(items[i]) > 0
    ]

    if sizes:
        median_size = median(sizes)
    else:
        median_size = 50

    # --------------------------------------------------------
    # STEP 4
    # Merge unknown groups
    # --------------------------------------------------------

    unknown_indices = [
        i
        for i in normal_indices
        if is_unknown(items[i])
    ]

    uf = UnionFind(len(items))

    for pos_a in range(len(unknown_indices)):

        i = unknown_indices[pos_a]

        for pos_b in range(
            pos_a + 1,
            len(unknown_indices)
        ):

            j = unknown_indices[pos_b]

            if should_merge_unknown(
                items[i],
                items[j],
                median_size
            ):
                uf.union(i, j)

    # --------------------------------------------------------
    # STEP 5
    # Build merge groups
    # --------------------------------------------------------

    merged_groups = {}

    for i in unknown_indices:

        root = uf.find(i)

        merged_groups.setdefault(
            root,
            []
        ).append(i)

    # --------------------------------------------------------
    # STEP 6
    # Generate refined containers
    # --------------------------------------------------------

    refined = []

    consumed = set()

    # First: existing proper textbox containers
    for i in normal_indices:

        item = items[i]

        if not is_unknown(item):

            result = deepcopy(item)

            result["refined"] = True
            result["group_ids"] = [
                item.get(
                    "group_id",
                    item.get("id", i + 1)
                )
            ]

            refined.append(result)
            consumed.add(i)

    # Then: merged unknown containers
    for root, indices in merged_groups.items():

        for i in indices:
            consumed.add(i)

        merged = merge_group_items(
            items,
            indices
        )

        refined.append(merged)

    # --------------------------------------------------------
    # STEP 7
    # Aggregate regions are NOT emitted as normal containers
    # --------------------------------------------------------

    # Keep them separately for debugging.
    for i in aggregate_indices:

        aggregate = deepcopy(items[i])

        aggregate["refined"] = True
        aggregate["container_role"] = "aggregate"
        aggregate["excluded_from_reading_order"] = True

        refined.append(aggregate)

    # --------------------------------------------------------
    # STEP 8
    # Sort spatially for stable output
    # --------------------------------------------------------

    refined.sort(
        key=lambda item: (
            box_center(get_box(item))[1],
            box_center(get_box(item))[0],
        )
    )

    # --------------------------------------------------------
    # STEP 9
    # Assign container IDs
    # --------------------------------------------------------

    for index, item in enumerate(refined, start=1):

        item["container_id"] = index

    return refined


# ============================================================
# FILTER FOR READING ORDER
# ============================================================

def get_reading_order_containers(refined):
    """
    Hanya mengembalikan logical containers yang boleh
    masuk ke reading_order.py.
    """

    return [
        item
        for item in refined
        if not item.get(
            "excluded_from_reading_order",
            False
        )
    ]


# ============================================================
# DEBUG
# ============================================================

def print_refined_containers(refined):
    print()
    print("=" * 32)
    print("     REFINED CONTAINERS")
    print("=" * 32)

    for item in refined:

        cid = item.get(
            "container_id",
            "?"
        )

        role = item.get(
            "container_role",
            "logical"
        )

        ctype = item.get(
            "type",
            "unknown"
        )

        box = get_box(item)

        group_ids = item.get(
            "group_ids",
            []
        )

        texts = item.get(
            "texts",
            []
        )

        print()
        print(f"C{cid}")
        print(f"  ROLE   : {role}")
        print(f"  TYPE   : {ctype}")
        print(f"  BOX    : {box}")
        print(f"  GROUPS : {group_ids}")
        print(f"  TEXTS  : {len(texts)}")

        for text in texts:

            if isinstance(text, dict):

                label = text.get(
                    "type",
                    "text"
                )

                value = text.get(
                    "text",
                    ""
                )

                print(
                    f"    - [{label}] {value}"
                )

            else:

                print(
                    f"    - {text}"
                )
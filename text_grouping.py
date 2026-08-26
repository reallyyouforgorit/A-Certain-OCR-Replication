def get_box_info(box):
    x1, y1, x2, y2 = box

    return {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "width": x2 - x1,
        "height": y2 - y1,
        "center_x": (x1 + x2) / 2,
        "center_y": (y1 + y2) / 2,
    }


def vertical_overlap(a, b):
    top = max(a["y1"], b["y1"])
    bottom = min(a["y2"], b["y2"])

    overlap = max(0, bottom - top)

    min_height = min(
        a["height"],
        b["height"]
    )

    if min_height == 0:
        return 0

    return overlap / min_height


def horizontal_overlap(a, b):
    left = max(a["x1"], b["x1"])
    right = min(a["x2"], b["x2"])

    overlap = max(0, right - left)

    min_width = min(
        a["width"],
        b["width"]
    )

    if min_width == 0:
        return 0

    return overlap / min_width


def should_group(a, b):

    # Jarak antar baris
    vertical_gap = max(
        0,
        max(a["y1"], b["y1"])
        - min(a["y2"], b["y2"])
    )

    # Jika box memiliki overlap horizontal yang cukup
    x_overlap = horizontal_overlap(a, b)

    # Untuk baris teks horizontal
    if x_overlap > 0.3 and vertical_gap < max(
        a["height"],
        b["height"]
    ) * 1.5:

        return True

    return False


def group_text_lines(detections):

    if not detections:
        return []

    items = []

    for detection in detections:

        info = get_box_info(
            detection["box"]
        )

        item = {
            **detection,
            **info
        }

        items.append(item)

    # Urutkan dari atas ke bawah
    items.sort(
        key=lambda item: item["y1"]
    )

    groups = []

    for item in items:

        added = False

        for group in groups:

            last = group[-1]

            if should_group(last, item):

                group.append(item)
                added = True
                break

        if not added:
            groups.append([item])

    return groups
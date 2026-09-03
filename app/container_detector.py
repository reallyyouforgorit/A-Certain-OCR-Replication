# ==========================================
# CONTAINER DETECTOR
# ==========================================


def get_group_box(lines, padding=20):
    """
    Menghasilkan bounding box gabungan dari
    seluruh OCR line dalam satu group.
    """

    if not lines:
        return None

    x1 = min(line["box"][0] for line in lines)
    y1 = min(line["box"][1] for line in lines)

    x2 = max(line["box"][2] for line in lines)
    y2 = max(line["box"][3] for line in lines)

    return [
        max(0, x1 - padding),
        max(0, y1 - padding),
        x2 + padding,
        y2 + padding
    ]


def detect_container(lines):

    if not lines:
        return {
            "type": "none",
            "box": None
        }

    group_box = get_group_box(
        lines,
        padding=20
    )

    types = [
        line.get("type")
        for line in lines
    ]

    # Watermark
    if all(
        text_type == "watermark"
        for text_type in types
    ):
        return {
            "type": "none",
            "box": None
        }

    # Multi-line group
    if len(lines) >= 2:

        return {
            "type": "textbox",
            "box": group_box
        }

    # Single line
    return {
        "type": "unknown",
        "box": group_box
    }
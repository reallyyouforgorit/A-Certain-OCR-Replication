import cv2


def detect_bubble(image, text_box):

    x1, y1, x2, y2 = text_box

    height, width = image.shape[:2]

    # Area diperbesar dari bounding box OCR
    padding = 80

    rx1 = max(0, x1 - padding)
    ry1 = max(0, y1 - padding)

    rx2 = min(width, x2 + padding)
    ry2 = min(height, y2 + padding)

    roi = image[ry1:ry2, rx1:rx2]

    gray = cv2.cvtColor(
        roi,
        cv2.COLOR_BGR2GRAY
    )

    _, threshold = cv2.threshold(
        gray,
        200,
        255,
        cv2.THRESH_BINARY
    )

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    best = None
    best_area = 0

    for contour in contours:

        bx, by, bw, bh = cv2.boundingRect(contour)

        area = bw * bh

        if area <= best_area:
            continue

        # Pastikan contour mengandung teks
        if (
            bx <= (x1 - rx1)
            and by <= (y1 - ry1)
            and
            bx + bw >= (x2 - rx1)
            and
            by + bh >= (y2 - ry1)
        ):

            best = (
                rx1 + bx,
                ry1 + by,
                rx1 + bx + bw,
                ry1 + by + bh
            )

            best_area = area

    return best
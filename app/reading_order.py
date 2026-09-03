# ==========================================
# READING ORDER
# ==========================================


def get_box(item):
    """
    Mengambil bounding box dari sebuah unit.

    Prioritas:
    1. container box
    2. text box pertama
    """

    container = item.get("container")

    if container:
        box = container.get("box")

        if box is not None:
            return box

    texts = item.get("texts", [])

    if texts:
        box = texts[0].get("box")

        if box is not None:
            return box

    return None


def get_center(box):
    """
    Menghitung center dari bounding box.
    """

    x1, y1, x2, y2 = box

    return (
        (x1 + x2) / 2,
        (y1 + y2) / 2
    )


def sort_reading_order(items):
    """
    Sorting awal untuk manga Jepang.

    Prinsip:
        - region yang lebih atas dibaca lebih dahulu
        - region pada baris/area yang sama:
          kanan -> kiri

    CATATAN:
    Ini masih baseline.
    Kita akan validasi dengan debug image
    sebelum digunakan ke translation pipeline.
    """

    valid_items = []

    for item in items:

        box = get_box(item)

        if box is None:
            continue

        valid_items.append(
            (
                item,
                box,
                get_center(box)
            )
        )

    # ======================================
    # Baseline sorting
    # ======================================

    # Untuk sementara kita menggunakan
    # center Y sebagai primary key dan
    # center X descending sebagai secondary key.
    #
    # Ini sengaja masih sederhana karena
    # kita belum mengetahui seluruh struktur
    # panel dari gambar baru.
    #
    # Nanti akan diganti dengan grouping
    # berdasarkan row/panel.

    valid_items.sort(
        key=lambda data: (
            data[2][1],
            -data[2][0]
        )
    )

    return [
        item
        for item, box, center in valid_items
    ]
# ==========================================
# TRANSLATION CONTEXT
# ==========================================


def build_context(
    units,
    index,
    context_size=1
):
    """
    Membuat context berdasarkan urutan
    translation unit, bukan group_id.

    GROUP digunakan untuk hubungan spatial,
    sedangkan context digunakan untuk hubungan
    naratif / reading order.

    Parameters
    ----------
    units : list
        Semua translation units dalam reading order.

    index : int
        Index unit yang sedang diterjemahkan.

    context_size : int
        Jumlah unit sebelum dan sesudah
        current unit yang digunakan sebagai context.
    """

    if not units:
        return {
            "current": None,
            "previous": [],
            "following": []
        }

    if index < 0 or index >= len(units):
        raise IndexError(
            f"Index unit tidak valid: {index}"
        )

    current = units[index]

    # ======================================
    # Previous
    # ======================================

    previous = []

    start = max(
        0,
        index - context_size
    )

    for i in range(
        start,
        index
    ):

        unit = units[i]

        if not unit.get("text"):
            continue

        previous.append({
            "unit_id": unit.get("unit_id"),
            "group_id": unit.get("group_id"),
            "type": unit.get("type"),
            "text": unit.get("text")
        })

    # ======================================
    # Following
    # ======================================

    following = []

    end = min(
        len(units),
        index + context_size + 1
    )

    for i in range(
        index + 1,
        end
    ):

        unit = units[i]

        if not unit.get("text"):
            continue

        following.append({
            "unit_id": unit.get("unit_id"),
            "group_id": unit.get("group_id"),
            "type": unit.get("type"),
            "text": unit.get("text")
        })

    # ======================================
    # Current
    # ======================================

    current_data = {
        "unit_id": current.get("unit_id"),
        "group_id": current.get("group_id"),
        "type": current.get("type"),
        "text": current.get("text")
    }

    # ======================================
    # Result
    # ======================================

    return {
        "current": current_data,
        "previous": previous,
        "following": following
    }
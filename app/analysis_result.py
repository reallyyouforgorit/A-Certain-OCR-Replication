# ==========================================
# ANALYSIS RESULT
# ==========================================

def build_group_result(
    group_id,
    results
):
    """
    Mengubah hasil region analysis menjadi
    struktur data yang lebih terorganisir.
    """

    if not results:

        return {
            "group_id": group_id,
            "container": {
                "type": "none",
                "box": None
            },
            "texts": []
        }

    container = {
        "type": results[0].get(
            "container_type",
            "none"
        ),
        "box": results[0].get(
            "container_box"
        )
    }

    texts = []

    for result in results:

        texts.append({
            "type": result.get(
                "type"
            ),

            "text": result.get(
                "text",
                ""
            ),

            "box": result.get(
                "box"
            ),

            "action": result.get(
                "action"
            ),

            "translation": None
        })

    return {
        "group_id": group_id,
        "container": container,
        "texts": texts
    }
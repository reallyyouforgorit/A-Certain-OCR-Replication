# ==========================================
# TRANSLATION UNIT MANAGER
# ==========================================

from copy import deepcopy


# ==========================================
# CONFIGURATION
# ==========================================

TRANSLATABLE_TYPES = {
    "dialogue",
    "narration"
}


# ==========================================
# CREATE TRANSLATION UNITS
# ==========================================

def create_translation_units(
    analysis_data
):
    """
    Mengubah analysis.json menjadi
    translation units.

    Dialogue:
        1 OCR line = 1 translation unit

    Narration:
        Beberapa OCR line yang berurutan
        dalam container yang sama digabung
        menjadi 1 translation unit.
    """

    units = []

    for group in analysis_data:

        group_id = group.get(
            "group_id"
        )

        container = group.get(
            "container",
            {}
        )

        texts = group.get(
            "texts",
            []
        )

        current_narration = []

        # ----------------------------------
        # Flush narration
        # ----------------------------------

        def flush_narration():

            nonlocal current_narration

            if not current_narration:
                return

            source_lines = [
                item["text"]
                for item in current_narration
            ]

            source_text = "".join(
                source_lines
            )

            units.append({

                "unit_id": len(units) + 1,

                "group_id": group_id,

                "container": deepcopy(
                    container
                ),

                "type": "narration",

                "text": source_text,

                "source_lines": deepcopy(
                    current_narration
                ),

                "translation": None

            })

            current_narration = []

        # ----------------------------------
        # Process lines
        # ----------------------------------

        for text_item in texts:

            text_type = text_item.get(
                "type"
            )

            # ------------------------------
            # Non-translatable
            # ------------------------------

            if text_type not in (
                TRANSLATABLE_TYPES
            ):

                flush_narration()

                continue

            # ------------------------------
            # Dialogue
            # ------------------------------

            if text_type == "dialogue":

                flush_narration()

                units.append({

                    "unit_id": len(units) + 1,

                    "group_id": group_id,

                    "container": deepcopy(
                        container
                    ),

                    "type": "dialogue",

                    "text": text_item.get(
                        "text",
                        ""
                    ),

                    "source_lines": [
                        deepcopy(text_item)
                    ],

                    "translation": None

                })

            # ------------------------------
            # Narration
            # ------------------------------

            elif text_type == "narration":

                current_narration.append(
                    deepcopy(text_item)
                )

        # ----------------------------------
        # Flush remaining narration
        # ----------------------------------

        flush_narration()

    return units
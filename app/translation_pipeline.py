# ==========================================
# TRANSLATION PIPELINE
# ==========================================

import json
from pathlib import Path

from translation_unit import (
    create_translation_units
)

from translation_context import (
    build_context
)

from translator import (
    LocalTranslator
)


# ==========================================
# TRANSLATION PIPELINE
# ==========================================

class TranslationPipeline:

    def __init__(
        self,
        translator=None,
        context_size=1
    ):

        # ----------------------------------
        # Translator
        # ----------------------------------

        if translator is None:

            translator = LocalTranslator()

        self.translator = translator

        # ----------------------------------
        # Context configuration
        # ----------------------------------

        self.context_size = context_size


    # ======================================
    # TRANSLATE
    # ======================================

    def translate_units(
        self,
        units
    ):

        translated_units = []

        total = len(units)

        print()
        print("================================")
        print("       TRANSLATION")
        print("================================")

        print(
            f"TOTAL UNITS : {total}"
        )

        for index, unit in enumerate(
            units
        ):

            print()
            print(
                f"[{index + 1}/{total}] "
                f"UNIT {unit['unit_id']}"
            )

            print(
                f"TYPE   : {unit['type']}"
            )

            print(
                f"SOURCE : {unit['text']}"
            )

            # ------------------------------
            # Build context
            # ------------------------------

            context = build_context(
                units,
                index,
                context_size=self.context_size
            )

            # ------------------------------
            # Translate CURRENT only
            # ------------------------------

            translated = (
                self.translator.translate(
                    unit["text"]
                )
            )

            # ------------------------------
            # Copy unit
            # ------------------------------

            result = dict(unit)

            result["translation"] = (
                translated
            )

            # ------------------------------
            # Store context metadata
            # ------------------------------

            result["context"] = context

            translated_units.append(
                result
            )

            print(
                f"TARGET : {translated}"
            )

        return translated_units


    # ======================================
    # PROCESS JSON
    # ======================================

    def process(
        self,
        analysis_path,
        output_path
    ):

        analysis_path = Path(
            analysis_path
        )

        output_path = Path(
            output_path
        )

        # ----------------------------------
        # Load analysis
        # ----------------------------------

        with open(
            analysis_path,
            "r",
            encoding="utf-8"
        ) as f:

            analysis_data = json.load(f)

        # ----------------------------------
        # Create translation units
        # ----------------------------------

        units = create_translation_units(
            analysis_data
        )

        print()
        print(
            f"TRANSLATION UNITS : "
            f"{len(units)}"
        )

        # ----------------------------------
        # Translate
        # ----------------------------------

        translated_units = (
            self.translate_units(
                units
            )
        )

        # ----------------------------------
        # Save
        # ----------------------------------

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                translated_units,
                f,
                ensure_ascii=False,
                indent=2
            )

        print()
        print(
            "================================"
        )

        print(
            f"TRANSLATED JSON : "
            f"{output_path}"
        )

        return translated_units
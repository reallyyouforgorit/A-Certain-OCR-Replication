# ==========================================
# TEST TRANSLATION CONTEXT
# ==========================================

import json

from translation_unit import (
    create_translation_units
)

from translation_context import (
    build_context
)


# ==========================================
# LOAD ANALYSIS
# ==========================================

with open(
    "output/analysis.json",
    "r",
    encoding="utf-8"
) as f:

    analysis_data = json.load(f)


# ==========================================
# CREATE UNITS
# ==========================================

units = create_translation_units(
    analysis_data
)


# ==========================================
# TEST
# ==========================================

print()
print("================================")
print("       TRANSLATION CONTEXT")
print("================================")


for index, unit in enumerate(units):

    context = build_context(
        units,
        index,
        context_size=1
    )

    print()
    print(
        f"UNIT {unit['unit_id']}"
    )

    print("-" * 40)

    print()
    print("PREVIOUS:")

    if context["previous"]:

        for item in context["previous"]:

            print(
                f"[{item['type']}] "
                f"{item['text']}"
            )

    else:

        print("(none)")

    print()
    print("CURRENT:")

    print(
        f"[{context['current']['type']}] "
        f"{context['current']['text']}"
    )

    print()
    print("FOLLOWING:")

    if context["following"]:

        for item in context["following"]:

            print(
                f"[{item['type']}] "
                f"{item['text']}"
            )

    else:

        print("(none)")
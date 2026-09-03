import re


WATERMARK_KEYWORDS = [
    "無断転載禁止",
    "転載禁止",
    "AI学習",
    "利用禁止",
    "著作権",
    "copyright",
    "all rights reserved",
    "AI",
    "copy",
    "rights",
    "@",
]


DIALOGUE_PAIRS = [
    ("「", "」"),
    ("『", "』"),
    ("“", "”"),
    ("(", ")"),
    ("（", "）"),
]

DIALOGUE_END = [
    "」",
    "』",
    "”",
    '"',
]


SFX_CHARACTERS = [
    "ド",
    "ゴ",
    "バ",
    "ズ",
    "ガ",
    "ドン",
    "バン",
]


def contains_watermark_keyword(text):

    text_lower = text.lower()

    for keyword in WATERMARK_KEYWORDS:

        if keyword.lower() in text_lower:
            return True

    return False


def is_dialogue(text):

    text = text.strip()

    if not text:
        return False

    # --------------------------------
    # Japanese quotation
    # --------------------------------

    for start, end in zip(
        DIALOGUE_PAIRS,
        DIALOGUE_END
    ):

        if text.startswith(start):
            return True

    return False


def looks_like_sfx(text):

    text = text.strip()

    # SFX biasanya pendek
    if len(text) > 8:
        return False

    # Beberapa pola katakana pendek
    katakana_count = 0

    for char in text:

        if "ァ" <= char <= "ヺ":
            katakana_count += 1

    if katakana_count >= 2:
        return True

    return False


def classify_line(text):

    text = text.strip()

    # 1. Watermark
    if contains_watermark_keyword(text):

        return "watermark"


    # 2. Dialogue
    if is_dialogue(text):

        return "dialogue"


    # 3. SFX
    if looks_like_sfx(text):

        return "sfx"


    # 4. Narration
    return "narration"


def classify_group(group):

    results = []

    for item in group:

        text_type = classify_line(
            item["text"]
        )

        results.append({
            **item,
            "type": text_type
        })

    return results
# ==========================================
# TEST TRANSLATION PIPELINE
# ==========================================

from pathlib import Path

from translation_pipeline import (
    TranslationPipeline
)


# ==========================================
# PATH
# ==========================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

ANALYSIS_PATH = (
    BASE_DIR
    / "output"
    / "analysis.json"
)

OUTPUT_PATH = (
    BASE_DIR
    / "output"
    / "translated_analysis.json"
)


# ==========================================
# PIPELINE
# ==========================================

pipeline = TranslationPipeline(
    context_size=1
)


# ==========================================
# PROCESS
# ==========================================

pipeline.process(
    analysis_path=ANALYSIS_PATH,
    output_path=OUTPUT_PATH
)
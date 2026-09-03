# ==========================================
# LOCAL TRANSLATOR
# Japanese -> Indonesian
# ==========================================

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)


# ==========================================
# MODEL
# ==========================================

MODEL_NAME = (
    "facebook/nllb-200-distilled-600M"
)

SOURCE_LANGUAGE = "jpn_Jpan"
TARGET_LANGUAGE = "eng_Latn"


# ==========================================
# TRANSLATOR
# ==========================================

class LocalTranslator:

    def __init__(
        self,
        model_name=MODEL_NAME
    ):

        print()
        print("================================")
        print("       LOAD TRANSLATION MODEL")
        print("================================")

        print(
            f"MODEL          : {model_name}"
        )

        print(
            "DEVICE         : CPU"
        )

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                model_name
            )
        )

        self.model = (
            AutoModelForSeq2SeqLM.from_pretrained(
                model_name
            )
        )

        self.model.eval()

        print(
            "MODEL STATUS   : READY"
        )


    # ======================================
    # TRANSLATE
    # ======================================

    def translate(
        self,
        text
    ):

        if not text:
            return ""

        # ------------------------------
        # Set source language
        # ------------------------------

        self.tokenizer.src_lang = (
            SOURCE_LANGUAGE
        )

        # ------------------------------
        # Tokenize
        # ------------------------------

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        # ------------------------------
        # Target language
        # ------------------------------

        forced_bos_token_id = (
            self.tokenizer.convert_tokens_to_ids(
                TARGET_LANGUAGE
            )
        )

        # ------------------------------
        # Generate
        # ------------------------------

        with torch.no_grad():

            output_tokens = (
                self.model.generate(
                    **inputs,
                    forced_bos_token_id=(
                        forced_bos_token_id
                    ),
                    max_length=512
                )
            )

        # ------------------------------
        # Decode
        # ------------------------------

        translated = (
            self.tokenizer.decode(
                output_tokens[0],
                skip_special_tokens=True
            )
        )

        return translated.strip()
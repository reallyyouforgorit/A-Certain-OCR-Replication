from pathlib import Path
from paddleocr import PaddleOCR

print("=== PROGRAM DIMULAI ===")

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_PATH = BASE_DIR / "input" / "tes.jpg"

print(f"Image: {IMAGE_PATH}")
print(f"Exists: {IMAGE_PATH.exists()}")

ocr = PaddleOCR(
    lang="japan",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

print("=== OCR SIAP ===")

results = ocr.predict(str(IMAGE_PATH))

print("=== HASIL OCR ===")

for result in results:
    texts = result["rec_texts"]
    scores = result["rec_scores"]
    boxes = result["rec_boxes"]

    for i, (text, score, box) in enumerate(
        zip(texts, scores, boxes), start=1
    ):
        print()
        print(f"[{i}]")
        print(f"Text       : {text}")
        print(f"Confidence : {score:.4f}")
        print(f"Box        : {box.tolist()}")

print()
print("=== SELESAI ===")
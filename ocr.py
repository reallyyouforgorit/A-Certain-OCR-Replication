from pathlib import Path
from paddleocr import PaddleOCR


class MangaOCR:

    def __init__(self):

        self.ocr = PaddleOCR(
            lang="japan",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

    def process(self, image_path):

        image_path = Path(image_path)

        results = self.ocr.predict(str(image_path))

        detections = []

        for result in results:

            texts = result["rec_texts"]
            scores = result["rec_scores"]
            boxes = result["rec_boxes"]

            for text, score, box in zip(
                texts,
                scores,
                boxes
            ):

                box = box.tolist()

                x1 = box[0]
                y1 = box[1]
                x2 = box[2]
                y2 = box[3]

                detections.append({
                    "text": text,
                    "confidence": float(score),
                    "box": [
                        int(x1),
                        int(y1),
                        int(x2),
                        int(y2)
                    ]
                })

        return detections
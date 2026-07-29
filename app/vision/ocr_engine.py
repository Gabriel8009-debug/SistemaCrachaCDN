from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from PIL import Image
from rapidocr import RapidOCR


@dataclass(frozen=True)
class OCRText:
    text: str
    score: float


class OCREngine:
    def __init__(self) -> None:
        self.engine = RapidOCR()

    @staticmethod
    def _extract_new_api(result: Any) -> list[OCRText]:
        texts = getattr(result, "txts", None)
        scores = getattr(result, "scores", None)

        if texts is None:
            return []

        scores = scores or [0.0] * len(texts)
        return [
            OCRText(str(text).strip(), float(score))
            for text, score in zip(texts, scores)
            if str(text).strip()
        ]

    @staticmethod
    def _extract_legacy_api(result: Any) -> list[OCRText]:
        # Legacy rapidocr_onnxruntime:
        # ([ [box, text, score], ... ], elapsed)
        if isinstance(result, tuple):
            result = result[0]

        if not isinstance(result, list):
            return []

        output: list[OCRText] = []

        for item in result:
            if not isinstance(item, (list, tuple)):
                continue

            if len(item) >= 3:
                text = str(item[1]).strip()
                try:
                    score = float(item[2])
                except (TypeError, ValueError):
                    score = 0.0

                if text:
                    output.append(OCRText(text, score))

        return output

    def read(self, image: Image.Image) -> list[OCRText]:
        image_array = np.asarray(image.convert("RGB"))
        result = self.engine(
            image_array,
            use_det=True,
            use_cls=False,
            use_rec=True,
        )

        output = self._extract_new_api(result)
        if output:
            return output

        return self._extract_legacy_api(result)

    def read_text(self, image: Image.Image) -> str:
        return " ".join(item.text for item in self.read(image)).strip()

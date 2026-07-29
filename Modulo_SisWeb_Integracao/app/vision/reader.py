from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image

from .capture import RegionCapture
from .ocr_engine import OCREngine
from .parsers import extract_cpf, extract_phone, extract_rg, normalize_text
from .preprocess import build_variants


@dataclass
class ReadAttempt:
    variant: str
    raw_text: str
    parsed_value: str


class SisWebVisionReader:
    def __init__(
        self,
        regions_path: str | Path,
        debug_dir: str | Path | None = None,
    ) -> None:
        self.capture = RegionCapture(regions_path)
        self.ocr = OCREngine()
        self.debug_dir = Path(debug_dir) if debug_dir else None

    def _save_debug(
        self,
        field: str,
        variant: str,
        image: Image.Image,
    ) -> None:
        if self.debug_dir is None:
            return

        self.debug_dir.mkdir(parents=True, exist_ok=True)
        image.save(self.debug_dir / f"{field}_{variant}.png")

    def _read_with_parser(
        self,
        field: str,
        region_key: str,
        parser: Callable[[str], str],
    ) -> tuple[str, list[ReadAttempt]]:
        source = self.capture.capture(region_key)
        attempts: list[ReadAttempt] = []

        for variant_name, image in build_variants(source).items():
            self._save_debug(field, variant_name, image)
            raw = normalize_text(self.ocr.read_text(image))
            parsed = parser(raw)

            attempts.append(
                ReadAttempt(
                    variant=variant_name,
                    raw_text=raw,
                    parsed_value=parsed,
                )
            )

            if parsed:
                return parsed, attempts

        return "", attempts

    def read_cpf(self) -> tuple[str, list[ReadAttempt]]:
        return self._read_with_parser(
            field="cpf",
            region_key="regiao_cpf",
            parser=extract_cpf,
        )

    def read_phone(self) -> tuple[str, list[ReadAttempt]]:
        return self._read_with_parser(
            field="telefone",
            region_key="regiao_telefone",
            parser=extract_phone,
        )

    def read_rg(self) -> tuple[str, list[ReadAttempt]]:
        return self._read_with_parser(
            field="rg",
            region_key="regiao_documentos",
            parser=extract_rg,
        )

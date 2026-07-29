from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RelativeRegion:
    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top


class RegionConfig:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Configuração de regiões não encontrada: {self.path}")

        self._data: dict[str, Any] = json.loads(
            self.path.read_text(encoding="utf-8")
        )

        if "regioes" not in self._data:
            raise ValueError("JSON inválido: chave 'regioes' ausente.")

    def get(self, key: str) -> RelativeRegion:
        try:
            item = self._data["regioes"][key]["relativo"]
        except KeyError as exc:
            raise KeyError(f"Região não encontrada: {key}") from exc

        region = RelativeRegion(
            left=float(item["left"]),
            top=float(item["top"]),
            right=float(item["right"]),
            bottom=float(item["bottom"]),
        )

        if region.width <= 0 or region.height <= 0:
            raise ValueError(f"Região inválida: {key}")

        return region

    def keys(self) -> list[str]:
        return list(self._data["regioes"].keys())

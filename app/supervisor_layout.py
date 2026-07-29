from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SupervisorLayout:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.data: dict[str, Any] = {}
        self.load()

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(
                f"Configuração do supervisor não encontrada: {self.path}"
            )
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        return self.data

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get(self, key: str) -> dict[str, Any]:
        return self.data[key]

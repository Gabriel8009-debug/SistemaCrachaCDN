from __future__ import annotations

import time
from pathlib import Path

import pyautogui
from PIL import Image
from pywinauto import Desktop

from .regions import RegionConfig


class RegionCapture:
    def __init__(
        self,
        regions_path: str | Path,
        window_title_regex: str = r"^SisWeb$",
    ) -> None:
        self.regions = RegionConfig(regions_path)
        self.window_title_regex = window_title_regex

    def _window(self):
        windows = Desktop(backend="uia").windows(
            title_re=self.window_title_regex
        )
        if not windows:
            raise RuntimeError("A janela do SisWeb não foi encontrada.")

        window = windows[0]
        window.set_focus()
        time.sleep(0.25)
        return window

    def capture(self, region_key: str) -> Image.Image:
        window = self._window()
        rect = window.rectangle()
        region = self.regions.get(region_key)

        left = round(rect.left + region.left * rect.width())
        top = round(rect.top + region.top * rect.height())
        right = round(rect.left + region.right * rect.width())
        bottom = round(rect.top + region.bottom * rect.height())

        width = max(1, right - left)
        height = max(1, bottom - top)

        return pyautogui.screenshot(region=(left, top, width, height))

    def capture_to_file(
        self,
        region_key: str,
        output_path: str | Path,
    ) -> Path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        image = self.capture(region_key)
        image.save(output)
        return output

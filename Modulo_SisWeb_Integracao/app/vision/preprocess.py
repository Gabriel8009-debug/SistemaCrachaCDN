from __future__ import annotations

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def upscale(image: Image.Image, factor: int = 4) -> Image.Image:
    factor = max(1, int(factor))
    return image.resize(
        (image.width * factor, image.height * factor),
        Image.Resampling.LANCZOS,
    )


def grayscale(image: Image.Image) -> Image.Image:
    return ImageOps.grayscale(image)


def autocontrast(image: Image.Image) -> Image.Image:
    return ImageOps.autocontrast(image, cutoff=1)


def sharpen(image: Image.Image) -> Image.Image:
    return image.filter(ImageFilter.SHARPEN)


def increase_contrast(
    image: Image.Image,
    factor: float = 2.0,
) -> Image.Image:
    return ImageEnhance.Contrast(image).enhance(factor)


def threshold(image: Image.Image, level: int = 165) -> Image.Image:
    gray = grayscale(image)
    return gray.point(lambda pixel: 255 if pixel > level else 0)


def build_variants(image: Image.Image) -> dict[str, Image.Image]:
    enlarged = upscale(image, 4)
    gray = grayscale(enlarged)
    contrast = increase_contrast(autocontrast(gray), 2.2)
    sharp = sharpen(contrast)

    return {
        "original_upscaled": enlarged,
        "gray_contrast": contrast,
        "sharp": sharp,
        "binary_145": threshold(sharp, 145),
        "binary_165": threshold(sharp, 165),
        "binary_185": threshold(sharp, 185),
    }

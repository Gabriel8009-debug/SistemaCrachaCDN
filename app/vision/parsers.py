from __future__ import annotations

import re
import unicodedata


def normalize_text(value: str) -> str:
    value = value or ""
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("|", "1")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def digits_only(value: str) -> str:
    return re.sub(r"\D", "", normalize_text(value))


def format_cpf(digits: str) -> str:
    digits = digits_only(digits)
    if len(digits) != 11:
        return ""
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def cpf_is_valid(value: str) -> bool:
    digits = digits_only(value)

    if len(digits) != 11 or len(set(digits)) == 1:
        return False

    for size in (9, 10):
        total = sum(
            int(digits[index]) * (size + 1 - index)
            for index in range(size)
        )
        digit = (total * 10) % 11
        digit = 0 if digit == 10 else digit

        if digit != int(digits[size]):
            return False

    return True


def extract_cpf(text: str) -> str:
    normalized = normalize_text(text)
    candidates = re.findall(r"(?:\d[\s.\-]*){11}", normalized)

    for candidate in candidates:
        formatted = format_cpf(candidate)
        if formatted and cpf_is_valid(formatted):
            return formatted

    digits = digits_only(normalized)
    for index in range(max(0, len(digits) - 10)):
        candidate = digits[index:index + 11]
        formatted = format_cpf(candidate)
        if formatted and cpf_is_valid(formatted):
            return formatted

    return ""


def extract_phone(text: str) -> str:
    normalized = normalize_text(text)
    candidates = re.findall(r"(?:\+?55[\s().-]*)?(?:\d[\s().-]*){10,11}", normalized)

    for candidate in candidates:
        digits = digits_only(candidate)

        if len(digits) in (12, 13) and digits.startswith("55"):
            digits = digits[2:]

        if len(digits) in (10, 11):
            return digits

    return ""


def extract_rg(text: str) -> str:
    normalized = normalize_text(text).upper()

    match = re.search(
        r"\bRG\b[^0-9A-Z]*([0-9A-Z][0-9A-Z.\-/]{4,})",
        normalized,
    )
    if match:
        return match.group(1).strip(" .-/")

    candidates = re.findall(r"[0-9][0-9.\-/]{4,}[0-9X]", normalized)
    if candidates:
        return max(candidates, key=len).strip(" .-/")

    return ""

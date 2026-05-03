from pathlib import Path


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def clean_basic(text: str) -> str:
    return text.replace("\r\n", "\n").strip()

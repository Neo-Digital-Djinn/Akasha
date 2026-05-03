from string import ascii_uppercase


def identity(text: str) -> str:
    return text


def reverse_text(text: str) -> str:
    return text[::-1]


def caesar_shift(text: str, shift: int) -> str:
    out = []
    for ch in text:
        if ch in ascii_uppercase:
            idx = ascii_uppercase.index(ch)
            out.append(ascii_uppercase[(idx + shift) % 26])
        else:
            out.append(ch)
    return "".join(out)


def columnar_chunks(text: str, width: int) -> list[str]:
    return [text[i:i+width] for i in range(0, len(text), width)]


def columnar_read(text: str, width: int) -> str:
    rows = columnar_chunks(text, width)
    max_len = max(len(r) for r in rows) if rows else 0
    out = []
    for c in range(max_len):
        for row in rows:
            if c < len(row):
                out.append(row[c])
    return "".join(out)


def apply_transform(name: str, text: str, **kwargs) -> str:
    if name == "identity":
        return identity(text)
    if name == "reverse":
        return reverse_text(text)
    if name == "caesar":
        return caesar_shift(text, int(kwargs.get("shift", 0)))
    if name == "columnar":
        return columnar_read(text, int(kwargs.get("width", 5)))
    raise ValueError(f"Unknown transform: {name}")

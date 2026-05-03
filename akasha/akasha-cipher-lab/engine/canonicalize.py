import re


def canonical_forms(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    raw = "\n".join(lines)
    no_spaces = re.sub(r"\s+", "", raw)
    upper = no_spaces.upper()

    tokens = raw.split()
    chars = list(upper)

    return {
        "raw_lines": lines,
        "raw_text": raw,
        "no_spaces": no_spaces,
        "upper_stream": upper,
        "tokens": tokens,
        "chars": chars,
    }

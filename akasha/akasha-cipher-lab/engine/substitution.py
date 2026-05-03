from collections import Counter
from string import ascii_uppercase


ENGLISH_FREQ_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQZ"


def frequency_remap_preview(text: str) -> str:
    letters = [c for c in text.upper() if c in ascii_uppercase]
    counts = Counter(letters)

    ranked = [item[0] for item in counts.most_common()]
    mapping = {}

    for idx, symbol in enumerate(ranked):
        if idx < len(ENGLISH_FREQ_ORDER):
            mapping[symbol] = ENGLISH_FREQ_ORDER[idx]

    out = []
    for ch in text.upper():
        if ch in mapping:
            out.append(mapping[ch])
        else:
            out.append(ch)

    return "".join(out)


def collapse_rare_symbols(text: str, threshold: int = 1, replacement: str = "?") -> str:
    letters = [c for c in text.upper() if c in ascii_uppercase]
    counts = Counter(letters)

    out = []
    for ch in text.upper():
        if ch in ascii_uppercase and counts[ch] <= threshold:
            out.append(replacement)
        else:
            out.append(ch)

    return "".join(out)


def symbol_pattern_signature(text: str) -> str:
    mapping = {}
    next_code = 0
    out = []

    for ch in text.upper():
        if ch not in mapping:
            mapping[ch] = str(next_code)
            next_code += 1
        out.append(mapping[ch])

    return ".".join(out)

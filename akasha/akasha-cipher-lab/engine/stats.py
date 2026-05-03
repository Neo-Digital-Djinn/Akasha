from collections import Counter
from math import log2


def char_frequency(stream: str) -> dict:
    counts = Counter(stream)
    total = sum(counts.values()) or 1
    return {k: v / total for k, v in sorted(counts.items())}


def shannon_entropy(stream: str) -> float:
    counts = Counter(stream)
    total = sum(counts.values()) or 1
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * log2(p)
    return entropy


def repeated_ngrams(stream: str, n: int = 3, min_count: int = 2) -> dict:
    grams = Counter(stream[i:i+n] for i in range(len(stream) - n + 1))
    return {g: c for g, c in grams.items() if c >= min_count}


def line_length_profile(lines: list[str]) -> list[int]:
    return [len(line.replace(" ", "")) for line in lines]


def basic_report(forms: dict) -> dict:
    stream = forms["upper_stream"]
    return {
        "length": len(stream),
        "entropy": shannon_entropy(stream),
        "char_frequency": char_frequency(stream),
        "repeated_trigrams": repeated_ngrams(stream, n=3),
        "repeated_tetragrams": repeated_ngrams(stream, n=4),
        "line_lengths": line_length_profile(forms["raw_lines"]),
        "token_count": len(forms["tokens"]),
    }

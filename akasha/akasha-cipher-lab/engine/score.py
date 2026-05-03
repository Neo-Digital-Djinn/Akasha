from collections import Counter
import re

COMMON_ENGLISH = {
    "THE", "AND", "ING", "ION", "ENT", "TH", "HE", "ER", "AN", "RE"
}


def english_ngram_hint_score(text: str) -> float:
    upper = text.upper()
    score = 0.0
    for gram in COMMON_ENGLISH:
        score += upper.count(gram)
    return score


def vowel_ratio_score(text: str) -> float:
    letters = [c for c in text.upper() if "A" <= c <= "Z"]
    if not letters:
        return 0.0
    vowels = sum(1 for c in letters if c in "AEIOUY")
    ratio = vowels / len(letters)
    # crude preference toward language-like mid-range vowel ratio
    return max(0.0, 1.0 - abs(ratio - 0.38))


def repeat_penalty(text: str) -> float:
    runs = re.findall(r"(.)\1{3,}", text.upper())
    return -0.5 * len(runs)


def overall_score(text: str) -> dict:
    ngram = english_ngram_hint_score(text)
    vowel = vowel_ratio_score(text)
    penalty = repeat_penalty(text)
    total = round(ngram + vowel + penalty, 4)
    return {
        "english_ngram_hint": ngram,
        "vowel_ratio_score": round(vowel, 4),
        "repeat_penalty": penalty,
        "total_score": total,
    }

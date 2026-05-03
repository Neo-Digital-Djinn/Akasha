from collections import Counter
from string import ascii_uppercase


def build_frequency_hint(text: str) -> dict:
    """
    Produce a frequency-ranked hint mapping.
    """
    letters = [c for c in text if c in ascii_uppercase]
    counts = Counter(letters)
    ranked = [x[0] for x in counts.most_common()]

    english = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

    hint = {}

    for i, sym in enumerate(ranked):
        if i < len(english):
            hint[sym] = english[i]

    return hint


def apply_partial_substitution(text: str, mapping: dict) -> str:
    """
    Apply a partial substitution mapping.
    Unmapped letters remain unchanged.
    """
    out = []

    for c in text:
        if c in mapping:
            out.append(mapping[c])
        else:
            out.append(c)

    return "".join(out)


def pattern_signature(word: str) -> tuple:
    """
    Pattern signature like:
    HELLO -> (0,1,2,2,3)
    """
    mapping = {}
    counter = 0
    signature = []

    for c in word:
        if c not in mapping:
            mapping[c] = counter
            counter += 1

        signature.append(mapping[c])

    return tuple(signature)


def pattern_dictionary_match(cipher_word: str, dictionary: list[str]) -> list[str]:
    """
    Return dictionary words that match the pattern signature.
    """
    sig = pattern_signature(cipher_word)
    matches = []

    for word in dictionary:

        if len(word) != len(cipher_word):
            continue

        if pattern_signature(word.upper()) == sig:
            matches.append(word.upper())

    return matches


def explore_partial_mappings(text: str, seed_map: dict, depth: int = 2) -> list[str]:
    """
    Very shallow exploration of partial mappings.
    Used only to preview possible expansions.
    """
    outputs = []

    base = apply_partial_substitution(text, seed_map)
    outputs.append(base)

    remaining = [c for c in ascii_uppercase if c not in seed_map]

    for i in range(min(depth, len(remaining))):
        sym = remaining[i]
        new_map = seed_map.copy()
        new_map[sym] = ascii_uppercase[i]

        outputs.append(apply_partial_substitution(text, new_map))

    return outputs

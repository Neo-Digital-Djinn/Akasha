from collections import defaultdict


def pattern_signature(word: str) -> str:
    """
    Converts a token into a structural pattern signature.
    Example:
        QOKEEDY -> 0.1.2.3.3.4.5
    """

    mapping = {}
    next_id = 0
    pattern = []

    for ch in word:
        if ch not in mapping:
            mapping[ch] = next_id
            next_id += 1
        pattern.append(str(mapping[ch]))

    return ".".join(pattern)


def load_wordlist(path="data/wordlists/basic_english.txt"):
    words = []

    try:
        with open(path) as f:
            for line in f:
                w = line.strip().upper()
                if w.isalpha():
                    words.append(w)
    except FileNotFoundError:
        return []

    return words


def build_pattern_index(words):
    index = defaultdict(list)

    for w in words:
        sig = pattern_signature(w)
        index[sig].append(w)

    return index


def find_pattern_candidates(token, pattern_index):
    sig = pattern_signature(token)

    if sig in pattern_index:
        return pattern_index[sig][:25]

    return []

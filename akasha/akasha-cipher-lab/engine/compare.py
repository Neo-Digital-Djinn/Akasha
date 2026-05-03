from engine.canonicalize import canonical_forms
from engine.stats import basic_report


def compare_to_baseline(candidate_text: str, baseline_text: str) -> dict:
    candidate_forms = canonical_forms(candidate_text)
    baseline_forms = canonical_forms(baseline_text)

    candidate_report = basic_report(candidate_forms)
    baseline_report = basic_report(baseline_forms)

    score_delta = None
    entropy_delta = round(
        candidate_report["entropy"] - baseline_report["entropy"],
        6
    )

    trigram_delta = (
        len(candidate_report["repeated_trigrams"])
        - len(baseline_report["repeated_trigrams"])
    )

    tetragram_delta = (
        len(candidate_report["repeated_tetragrams"])
        - len(baseline_report["repeated_tetragrams"])
    )

    length_delta = candidate_report["length"] - baseline_report["length"]

    return {
        "score_delta": score_delta,
        "entropy_delta": entropy_delta,
        "repeated_trigram_delta": trigram_delta,
        "repeated_tetragram_delta": tetragram_delta,
        "length_delta": length_delta,
    }

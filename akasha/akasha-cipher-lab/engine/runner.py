import json
from pathlib import Path

from engine.dictionary_attack import (
    load_wordlist,
    build_pattern_index,
    find_pattern_candidates,
    pattern_signature,
)

from engine.ingest import load_text, clean_basic
from engine.canonicalize import canonical_forms
from engine.stats import basic_report
from engine.transforms import apply_transform
from engine.score import overall_score
from engine.hypotheses import HypothesisBranch
from engine.compare import compare_to_baseline
from engine.sections import section_report
from engine.report import generate_markdown_report

from engine.substitution import (
    frequency_remap_preview,
    collapse_rare_symbols,
    symbol_pattern_signature,
)

from engine.constraint_search import build_frequency_hint


def run_analysis(
    input_path: str,
    transform_specs: list[dict],
    output_dir: str = "outputs",
    section_mode: str = "lines",
    fixed_section_size: int = 40,
    include_substitution_lenses: bool = False,
) -> dict:

    raw = clean_basic(load_text(input_path))
    forms = canonical_forms(raw)
    report = basic_report(forms)

    upper_stream = forms["upper_stream"]

    # -----------------------------
    # Load dictionary pattern index
    # -----------------------------
    words = load_wordlist()
    pattern_index = build_pattern_index(words)

    candidates = []

    baseline_score = overall_score(upper_stream)

    for idx, spec in enumerate(transform_specs, start=1):

        name = spec["name"]
        params = spec.get("params", {})

        transformed = apply_transform(name, upper_stream, **params)

        score = overall_score(transformed)

        comparison = compare_to_baseline(transformed, upper_stream)

        comparison["score_delta"] = round(
            score["total_score"] - baseline_score["total_score"],
            6
        )

        branch = HypothesisBranch(
            branch_id=f"branch_{idx:03d}",
            source_path=input_path,
            transform_name=name,
            transform_params=params,
            output_text=transformed,
            score=score,
        )

        branch_dict = branch.to_dict()
        branch_dict["comparison_to_identity"] = comparison

        candidates.append(branch_dict)

    candidates.sort(
        key=lambda x: x["score"]["total_score"],
        reverse=True
    )

    section_analysis = section_report(
        raw,
        mode=section_mode,
        fixed_size=fixed_section_size,
    )

    substitution_lenses = {}
    constraint_preview = {}

    if include_substitution_lenses:

        freq_hint = build_frequency_hint(upper_stream)

        substitution_lenses = {
            "frequency_remap_preview": frequency_remap_preview(upper_stream),
            "rare_symbol_collapse_preview": collapse_rare_symbols(upper_stream),
            "symbol_pattern_signature": symbol_pattern_signature(upper_stream[:80]),
        }

        constraint_preview = {
            "frequency_hint_mapping": freq_hint
        }

    # -----------------------------
    # Dictionary Pattern Attack
    # -----------------------------
    pattern_attack = {}

    tokens = upper_stream.split()

    if tokens:
        token = tokens[0][:10]

        pattern_attack = {
            "token": token,
            "pattern": pattern_signature(token),
            "dictionary_candidates": find_pattern_candidates(token, pattern_index)
        }

    payload = {
        "input_path": input_path,
        "structural_report": report,
        "section_analysis": section_analysis,
        "substitution_lenses": substitution_lenses,
        "constraint_search_preview": constraint_preview,
        "pattern_attack": pattern_attack,
        "baseline_score": baseline_score,
        "candidate_count": len(candidates),
        "top_candidates": candidates[:10],
        "all_candidates": candidates,
    }

    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    stem = Path(input_path).stem

    json_outfile = outdir / f"{stem}_analysis.json"
    json_outfile.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8"
    )

    md_outfile = outdir / f"{stem}_analysis.md"

    generate_markdown_report(
        payload,
        md_outfile
    )

    return payload

from pathlib import Path


def generate_markdown_report(payload: dict, output_path: str):
    lines = []

    lines.append("# Akasha Cipher Lab Report")
    lines.append("")
    lines.append(f"Input file: `{payload['input_path']}`")
    lines.append("")

    lines.append("## Structural Overview")
    lines.append("")
    sr = payload["structural_report"]

    lines.append(f"- Length: {sr['length']}")
    lines.append(f"- Entropy: {round(sr['entropy'], 4)}")
    lines.append(f"- Token count: {sr['token_count']}")
    lines.append(f"- Repeated trigrams: {len(sr['repeated_trigrams'])}")
    lines.append(f"- Repeated tetragrams: {len(sr['repeated_tetragrams'])}")
    lines.append("")

    lines.append("## Section Analysis")
    lines.append("")
    sa = payload["section_analysis"]

    lines.append(f"Mode: **{sa['mode']}**")
    lines.append(f"Sections analyzed: **{sa['section_count']}**")
    lines.append("")

    for s in sa["sections"]:
        r = s["report"]

        lines.append(f"### {s['section_id']}")
        lines.append("")
        lines.append(f"Preview: `{s['text_preview']}`")
        lines.append("")
        lines.append(f"- Length: {r['length']}")
        lines.append(f"- Entropy: {round(r['entropy'], 4)}")
        lines.append(f"- Tokens: {r['token_count']}")
        lines.append(f"- Repeated trigrams: {len(r['repeated_trigrams'])}")
        lines.append("")

    lines.append("## Top Candidates")
    lines.append("")

    for c in payload["top_candidates"][:10]:
        lines.append(f"### {c['branch_id']}")
        lines.append("")
        lines.append(f"Transform: `{c['transform_name']}`")
        lines.append(f"Parameters: `{c['transform_params']}`")
        lines.append(f"Score: **{c['score']['total_score']}**")
        lines.append(
            f"Score delta vs identity: {c['comparison_to_identity']['score_delta']}"
        )
        lines.append("")
        lines.append("Preview:")
        lines.append("```")
        lines.append(c["output_text"][:120])
        lines.append("```")
        lines.append("")

    if payload.get("substitution_lenses"):
        lines.append("## Substitution Lenses")
        lines.append("")
        sl = payload["substitution_lenses"]

        if "frequency_remap_preview" in sl:
            lines.append("### Frequency Remap Preview")
            lines.append("```")
            lines.append(sl["frequency_remap_preview"][:200])
            lines.append("```")
            lines.append("")

        if "rare_symbol_collapse_preview" in sl:
            lines.append("### Rare Symbol Collapse")
            lines.append("```")
            lines.append(sl["rare_symbol_collapse_preview"][:200])
            lines.append("```")
            lines.append("")

        if "symbol_pattern_signature" in sl:
            lines.append("### Pattern Signature")
            lines.append("```")
            lines.append(sl["symbol_pattern_signature"])
            lines.append("```")
            lines.append("")

    if payload.get("constraint_search_preview"):
        lines.append("## Constraint Search Preview")
        lines.append("")
        mapping = payload["constraint_search_preview"].get("frequency_hint_mapping", {})

        if mapping:
            lines.append("### Frequency Hint Mapping")
            lines.append("```")
            for k, v in mapping.items():
                lines.append(f"{k} -> {v}")
            lines.append("```")
            lines.append("")
        else:
            lines.append("No constraint search preview available.")
            lines.append("")

    if payload.get("pattern_attack"):
        pa = payload["pattern_attack"]

        lines.append("## Dictionary Pattern Attack")
        lines.append("")
        lines.append(f"Token analyzed: `{pa.get('token', '')}`")
        lines.append(f"Pattern signature: `{pa.get('pattern', '')}`")
        lines.append("")

        candidates = pa.get("dictionary_candidates", [])

        if candidates:
            lines.append("Candidate words:")
            lines.append("```")
            for word in candidates:
                lines.append(word)
            lines.append("```")
            lines.append("")
        else:
            lines.append("No matching dictionary patterns found.")
            lines.append("")

    text = "\n".join(lines)
    Path(output_path).write_text(text, encoding="utf-8")

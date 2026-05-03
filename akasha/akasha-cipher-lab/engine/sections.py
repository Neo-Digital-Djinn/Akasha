from engine.canonicalize import canonical_forms
from engine.stats import basic_report


def split_by_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def split_fixed(text: str, size: int) -> list[str]:
    cleaned = "".join(text.split())
    if size <= 0:
        return [cleaned]
    return [cleaned[i:i+size] for i in range(0, len(cleaned), size)]


def analyze_sections(sections: list[str]) -> list[dict]:
    out = []

    for idx, section in enumerate(sections, start=1):
        forms = canonical_forms(section)
        report = basic_report(forms)

        out.append(
            {
                "section_id": f"section_{idx:03d}",
                "text_preview": forms["upper_stream"][:80],
                "report": report,
            }
        )

    return out


def section_report(text: str, mode: str = "lines", fixed_size: int = 40) -> dict:
    if mode == "lines":
        sections = split_by_lines(text)
    elif mode == "fixed":
        sections = split_fixed(text, fixed_size)
    else:
        raise ValueError(f"Unknown section mode: {mode}")

    analyzed = analyze_sections(sections)

    return {
        "mode": mode,
        "section_count": len(analyzed),
        "sections": analyzed,
    }

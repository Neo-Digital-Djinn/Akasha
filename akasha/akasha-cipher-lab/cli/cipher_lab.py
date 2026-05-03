#!/usr/bin/env python3
import argparse
import sys
import os

# allow imports from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.runner import run_analysis


def build_transform_specs(args) -> list[dict]:
    specs = [{"name": "identity"}]

    if args.reverse:
        specs.append({"name": "reverse"})

    for shift in args.caesar:
        specs.append({"name": "caesar", "params": {"shift": shift}})

    for width in args.columnar:
        specs.append({"name": "columnar", "params": {"width": width}})

    return specs


def main():
    parser = argparse.ArgumentParser(
        prog="cipher_lab",
        description="Akasha multi-lens cryptanalysis engine",
    )

    parser.add_argument("input_path", help="Path to input text")
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--caesar", nargs="*", type=int, default=[])
    parser.add_argument("--columnar", nargs="*", type=int, default=[])
    parser.add_argument("--output-dir", default="outputs")

    parser.add_argument(
        "--section-mode",
        choices=["lines", "fixed"],
        default="lines",
        help="How to split text for section-aware analysis",
    )
    parser.add_argument(
        "--fixed-section-size",
        type=int,
        default=40,
        help="Section size when using fixed section mode",
    )
    parser.add_argument(
        "--substitution-lenses",
        action="store_true",
        help="Enable substitution-family preview lenses",
    )

    args = parser.parse_args()

    specs = build_transform_specs(args)

    result = run_analysis(
        args.input_path,
        specs,
        args.output_dir,
        section_mode=args.section_mode,
        fixed_section_size=args.fixed_section_size,
        include_substitution_lenses=args.substitution_lenses,
    )

    print("AKASHA CIPHER LAB")
    print("-----------------")
    print(f"Input: {result['input_path']}")
    print(f"Candidates tested: {result['candidate_count']}")
    print(f"Section mode: {result['section_analysis']['mode']}")
    print(f"Sections analyzed: {result['section_analysis']['section_count']}")

    if args.substitution_lenses:
        print("Substitution lenses: enabled")
    else:
        print("Substitution lenses: disabled")

    print("Top candidates:")

    for candidate in result["top_candidates"][:5]:
        print(
            f"  - {candidate['branch_id']} "
            f"{candidate['transform_name']} "
            f"{candidate['transform_params']} "
            f"score={candidate['score']['total_score']} "
            f"delta={candidate['comparison_to_identity']['score_delta']}"
        )


if __name__ == "__main__":
    main()

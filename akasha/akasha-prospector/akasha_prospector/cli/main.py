import argparse, json
from pathlib import Path
from akasha_prospector.analysis.directives import generate_directives

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--bursts", required=True)
    parser.add_argument("--out")

    args = parser.parse_args()

    summary = json.loads(Path(args.summary).read_text())
    bursts = json.loads(Path(args.bursts).read_text())

    result = generate_directives(summary, bursts)
    rendered = json.dumps(result, indent=2)

    if args.out:
        Path(args.out).write_text(rendered)
        print("wrote", args.out)
    else:
        print(rendered)


if __name__ == "__main__":
    main()

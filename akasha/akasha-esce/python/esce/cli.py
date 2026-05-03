#!/usr/bin/env python3
"""
esce.cli — Command-line interface for the ESCE transformation pipeline.

Usage:
    esce encode-text  <text>
    esce hash-text    <text>
    esce encode-file  <input_path> <output_path>
    esce decode-file  <input_path> <output_path>

Installed as `esce` console script via pyproject.toml.
"""

import sys
from .pipeline import Pipeline
from .config import CHUNK_SIZE


def encode_text(text: str) -> None:
    pipeline = Pipeline()
    result = pipeline.process(text.encode())
    print(result.hex())


def hash_text(text: str) -> None:
    pipeline = Pipeline(["hash"])
    result = pipeline.process(text.encode())
    print(result.hex())


def encode_file(input_path: str, output_path: str) -> None:
    pipeline = Pipeline()
    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        while chunk := fin.read(CHUNK_SIZE):
            fout.write(pipeline.process(chunk))
    print(f"Encoded: {input_path} → {output_path}")


def decode_file(input_path: str, output_path: str) -> None:
    """XOR is self-inverse — decode uses the same pipeline."""
    encode_file(input_path, output_path)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    try:
        if cmd == "encode-text" and len(sys.argv) >= 3:
            encode_text(sys.argv[2])
        elif cmd == "hash-text" and len(sys.argv) >= 3:
            hash_text(sys.argv[2])
        elif cmd == "encode-file" and len(sys.argv) >= 4:
            encode_file(sys.argv[2], sys.argv[3])
        elif cmd == "decode-file" and len(sys.argv) >= 4:
            decode_file(sys.argv[2], sys.argv[3])
        else:
            print(__doc__)
            sys.exit(1)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:
        print(f"ESCE error: {exc}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()

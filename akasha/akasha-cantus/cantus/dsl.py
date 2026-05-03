"""
Cantus DSL parser.

Parses .cantus source text into a token list for the VM.

Fixes vs original Termux version:
  - parse_cantus() alias added (repl.py called parse_cantus, dsl.py
    only exported parse — caused NameError on import)
  - MOD, ROT, OVER, JNZ added to match vm.py opcode set
  - Blank-line and comment handling tightened
"""

_NULLARY = {
    "ADD", "SUB", "MUL", "DIV", "MOD",
    "POP", "DUP", "SWAP", "OVER", "ROT",
    "STORE", "LOAD",
    "PRINT", "HALT", "POKE",
}

_LABEL_OPS = {"LABEL", "JMP", "JZ", "JNZ"}


def parse(source: str) -> list:
    """Parse Cantus source text → token list [(op, arg), ...]."""
    tokens = []
    for lineno, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        op = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else None

        if op == "PUSH":
            if arg is None:
                raise SyntaxError(f"PUSH requires an argument (line {lineno})")
            tokens.append(("PUSH", int(arg)))

        elif op in _NULLARY:
            tokens.append((op, 0))

        elif op in _LABEL_OPS:
            if arg is None:
                raise SyntaxError(f"{op} requires a label name (line {lineno})")
            tokens.append((op, arg))

        else:
            raise ValueError(f"Unknown opcode '{op}' (line {lineno})")

    return tokens


# Alias used by repl.py (was missing in original, caused ImportError)
parse_cantus = parse

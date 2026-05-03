"""
dsl.py — Cantus DSL parser
akasha-cantus

PORTING CHANGES vs original:
  - Added OVER, JNZ, MOD to recognised opcodes
  - Added parse_cantus() as an alias for parse() — repl.py and test_basic.py
    import parse_cantus; original had only parse()
  - Added NOOP as a safe no-op passthrough
"""

# Opcodes that take no argument (arg defaults to 0)
_NO_ARG = {
    "ADD", "SUB", "MUL", "DIV", "MOD",
    "POP", "DUP", "SWAP", "OVER",
    "STORE", "LOAD",
    "PRINT", "HALT", "POKE", "NOOP",
}

# Opcodes that take a string label argument
_LABEL_ARG = {"LABEL", "JMP", "JZ", "JNZ"}


def parse(source):
    """Parse Cantus source text into a token list."""
    tokens = []
    for line in source.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        op = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else None

        if op == "PUSH":
            tokens.append(("PUSH", int(arg)))
        elif op in _NO_ARG:
            tokens.append((op, 0))
        elif op in _LABEL_ARG:
            tokens.append((op, arg))
        else:
            raise ValueError(f"Unknown opcode: {op}")

    return tokens


# Alias — repl.py and tests import this name
parse_cantus = parse

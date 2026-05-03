"""
compiler.py — Cantus bytecode compiler
akasha-cantus

PORTING CHANGES vs original:
  - Added MOD (16), OVER (17), JNZ (18), NOOP (19) opcodes
  - Added decompile() — bytecode back to token list (useful for POKE inspection)
"""

OPCODES = {
    "LABEL":  0,
    "PUSH":   1,
    "POP":    2,
    "DUP":    3,
    "SWAP":   4,
    "ADD":    5,
    "SUB":    6,
    "MUL":    7,
    "DIV":    8,
    "STORE":  9,
    "LOAD":  10,
    "JMP":   11,
    "JZ":    12,
    "PRINT": 13,
    "HALT":  14,
    "POKE":  15,
    "MOD":   16,
    "OVER":  17,
    "JNZ":   18,
    "NOOP":  19,
}

# Reverse map for decompile
_REVERSE = {v: k for k, v in OPCODES.items()}


def compile(tokens):
    """Compile token list to flat bytecode list."""
    bytecode = []
    for op, arg in tokens:
        code = OPCODES.get(op, 0)
        bytecode.append(code)
        if isinstance(arg, int):
            bytecode.append(arg)
    return bytecode


def decompile(bytecode):
    """Best-effort decompile of flat bytecode back to token list."""
    tokens = []
    i = 0
    while i < len(bytecode):
        code = bytecode[i]
        op = _REVERSE.get(code, "NOOP")
        i += 1
        if op in {"PUSH"} and i < len(bytecode):
            tokens.append((op, bytecode[i]))
            i += 1
        else:
            tokens.append((op, 0))
    return tokens

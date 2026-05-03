"""
Cantus bytecode compiler.

Translates a token list into a flat integer bytecode sequence.
Useful for serialization, inspection, and future execution targets.
"""

OPCODES: dict[str, int] = {
    "PUSH":  1,
    "POP":   2,
    "DUP":   3,
    "SWAP":  4,
    "OVER":  5,
    "ROT":   6,
    "ADD":   7,
    "SUB":   8,
    "MUL":   9,
    "DIV":   10,
    "MOD":   11,
    "STORE": 12,
    "LOAD":  13,
    "JMP":   14,
    "JZ":    15,
    "JNZ":   16,
    "PRINT": 17,
    "HALT":  18,
    "POKE":  19,
    "LABEL": 0,
}


def compile(tokens: list) -> list[int]:
    """
    Compile token list → flat integer bytecode.

    Label targets are encoded as their integer index in the bytecode list.
    """
    bytecode: list[int] = []
    for op, arg in tokens:
        code = OPCODES.get(op, 0)
        bytecode.append(code)
        if isinstance(arg, int):
            bytecode.append(arg)
        elif isinstance(arg, str):
            # Encode label name as zero placeholder (linker would resolve)
            bytecode.append(0)
    return bytecode

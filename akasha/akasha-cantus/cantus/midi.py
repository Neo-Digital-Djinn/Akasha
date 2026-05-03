"""
Cantus MIDI bridge.

Maps MIDI note numbers to Cantus opcodes, enabling musical input
to drive VM execution — the "beautiful" half of v2.0.

Extended note map to cover the full standard MIDI range in groups.
"""

NOTE_MAP: dict[int, str] = {
    60: "PUSH",
    62: "ADD",
    64: "MUL",
    65: "SUB",
    67: "PRINT",
    69: "HALT",
    71: "DUP",
    72: "SWAP",
    74: "POP",
    76: "OVER",
    77: "JMP",
    79: "JZ",
}


def midi_to_tokens(note_sequence: list[int]) -> list:
    """
    Convert a sequence of MIDI note numbers to a Cantus token list.

    PUSH notes use note % 12 as their integer argument.
    All other opcodes use 0.
    """
    tokens: list = []
    for note in note_sequence:
        op = NOTE_MAP.get(note)
        if op is None:
            continue
        if op == "PUSH":
            tokens.append(("PUSH", note % 12))
        else:
            tokens.append((op, 0))
    return tokens

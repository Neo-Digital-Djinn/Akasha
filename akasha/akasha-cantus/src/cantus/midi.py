
NOTE_MAP = {
    60:"PUSH",62:"ADD",64:"MUL",65:"SUB",
    67:"PRINT",69:"HALT"
}

def midi_to_tokens(note_sequence):
    tokens=[]
    for note in note_sequence:
        op=NOTE_MAP.get(note)
        if op=="PUSH":
            tokens.append(("PUSH",note%12))
        elif op:
            tokens.append((op,0))
    return tokens


NOTE_TO_OP = {
    0: "PUSH", 1: "DUP", 2: "ADD", 3: "SWAP", 4: "SUB",
    5: "MUL", 6: "DROP", 7: "DIV", 8: "OVER", 9: "JUMP",
    10: "ROT", 11: "IF_ZERO"
}

def _fallback_tokenize():
    # Simple deterministic fallback program
    return [("PUSH", 2), ("PUSH", 3), ("MUL", 0), ("PUSH", 4), ("ADD", 0)]

def tokenize(audio_path):
    if not audio_path:
        return _fallback_tokenize()

    try:
        import librosa
        import numpy as np
    except ImportError:
        return _fallback_tokenize()

    y, sr = librosa.load(audio_path)

    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7')
    )

    tokens = []
    last_midi = None
    stable_count = 0
    DEBOUNCE = 3

    for freq in f0:
        if not np.isnan(freq):
            midi_note = int(round(librosa.hz_to_midi(freq)))

            if midi_note == last_midi:
                stable_count += 1
            else:
                if last_midi is not None and stable_count >= DEBOUNCE:
                    note_idx = last_midi % 12
                    octave = last_midi // 12
                    op = NOTE_TO_OP.get(note_idx)
                    tokens.append((op, octave))

                last_midi = midi_note
                stable_count = 1

    # Flush final note
    if last_midi is not None and stable_count >= DEBOUNCE:
        note_idx = last_midi % 12
        octave = last_midi // 12
        op = NOTE_TO_OP.get(note_idx)
        tokens.append((op, octave))

    return tokens

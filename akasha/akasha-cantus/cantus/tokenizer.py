"""
Cantus acoustic tokenizer (ATVM frontend).

Converts an audio file into a Cantus token stream via pitch detection.

Termux → Debian porting notes:
  - librosa import is now fully optional with a clear error message
  - soundfile backend preferred over audioread (better Debian support)
  - Added mono-downmix for multi-channel files (per REFERENCE_ANALYZER spec)
  - Fallback program is documented and deterministic (Axiom 5)

Acoustic state model (per ATVM spec §3):
  State S = { f_c, A, H, N, Δt }
  Only transitions between states produce instructions.

This module is the Analyzer layer. It MUST NOT modify execution state.
"""

from __future__ import annotations

NOTE_TO_OP: dict[int, str] = {
    0:  "PUSH",
    1:  "DUP",
    2:  "ADD",
    3:  "SWAP",
    4:  "SUB",
    5:  "MUL",
    6:  "POP",
    7:  "DIV",
    8:  "OVER",
    9:  "JMP",
    10: "ROT",
    11: "JZ",
}


def _fallback_tokenize() -> list:
    """
    Deterministic fallback program: computes 2 * 3 + 4 = 10.
    Used when librosa is unavailable or no audio path is given.
    """
    return [
        ("PUSH", 2),
        ("PUSH", 3),
        ("MUL",  0),
        ("PUSH", 4),
        ("ADD",  0),
    ]


def tokenize(audio_path: str | None = None) -> list:
    """
    Tokenize an audio file into a Cantus token list.

    Parameters
    ----------
    audio_path : str or None
        Path to a WAV/FLAC/OGG audio file.
        If None or if librosa is not installed, returns the fallback program.

    Returns
    -------
    list of (opcode, arg) tuples
    """
    if not audio_path:
        return _fallback_tokenize()

    try:
        import librosa          # type: ignore
        import numpy as np      # type: ignore
    except ImportError:
        print(
            "[cantus] WARNING: librosa not installed — using fallback program.\n"
            "  Install with: pip install librosa soundfile"
        )
        return _fallback_tokenize()

    # Load audio — mono downmix enforced (REFERENCE_ANALYZER §2)
    try:
        y, sr = librosa.load(audio_path, mono=True)
    except Exception as exc:
        print(f"[cantus] WARNING: could not load '{audio_path}': {exc}")
        return _fallback_tokenize()

    # Pitch detection via pyin (probabilistic YIN)
    f0, _voiced_flag, _voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
    )

    tokens: list = []
    last_midi: int | None = None
    stable_count: int = 0
    DEBOUNCE: int = 3  # frames a pitch must persist to count as an instruction

    for freq in f0:
        if np.isnan(freq):
            continue
        midi_note = int(round(librosa.hz_to_midi(freq)))

        if midi_note == last_midi:
            stable_count += 1
        else:
            if last_midi is not None and stable_count >= DEBOUNCE:
                note_idx = last_midi % 12
                octave   = last_midi // 12
                op = NOTE_TO_OP.get(note_idx)
                if op:
                    tokens.append((op, octave))
            last_midi   = midi_note
            stable_count = 1

    # Flush final note
    if last_midi is not None and stable_count >= DEBOUNCE:
        note_idx = last_midi % 12
        octave   = last_midi // 12
        op = NOTE_TO_OP.get(note_idx)
        if op:
            tokens.append((op, octave))

    return tokens if tokens else _fallback_tokenize()

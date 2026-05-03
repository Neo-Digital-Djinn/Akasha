# REFERENCE_ANALYZER.md
## Acoustic Transition Virtual Machine (ATVM)

This document defines the **reference acoustic analyzer** for ATVM.
Its role is to deterministically collapse a continuous acoustic signal into
a discrete sequence of Acoustic States.

The analyzer is NOT an executor and MUST NOT emit instructions directly.

---

## 1. Responsibilities

The analyzer MUST:

1. Segment the acoustic signal into fixed windows
2. Extract all required state components per window
3. Produce a strictly ordered state sequence
4. Remain fully deterministic

The analyzer MUST NOT:

- interpret instructions
- modify execution state
- adapt parameters during execution

---

## 2. Input Signal

Accepted inputs include:

- PCM audio files (WAV, FLAC)
- real-time audio streams
- synthesized signals

The analyzer operates on a single-channel (mono) signal.
Multi-channel input MUST be reduced deterministically to mono.

---

## 3. Windowing

- Window duration Δt is fixed for the entire execution
- Overlap MAY be used but MUST be fixed
- Window function (e.g. Hann) MUST remain constant

Typical reference values:

Δt = 10–50 ms  
Overlap = 50%  

---

## 4. State Extraction

For each window, compute:

### 4.1 Frequency Centroid (f_c)
Computed via FFT magnitude spectrum centroid.

### 4.2 Amplitude (A)
Root-mean-square (RMS) amplitude of the window.

### 4.3 Harmonicity (H)
Ratio of harmonic energy to total spectral energy.

### 4.4 Noise Ratio (N)
Ratio of non-harmonic spectral energy to total energy.

### 4.5 Duration (Δt)
Fixed analysis window duration.

All values MUST be derived from the same window.

---

## 5. Normalization

Normalization MAY be applied but MUST:

- be fixed before execution
- be applied uniformly
- not depend on future windows

Adaptive normalization is forbidden.

---

## 6. Output

The analyzer outputs an ordered sequence:

S₀, S₁, S₂, … Sₙ

No state may be skipped.
No future state may influence current computation.

---

## 7. Determinism Guarantees

Given:

- identical input signal
- identical parameters
- identical numeric precision

The analyzer MUST produce identical state sequences.

---

## 8. Reference Status

This document defines the **reference analyzer behavior**.
Implementations MAY differ internally but MUST preserve all observable behavior.

---

## 9. Version

REFERENCE_ANALYZER v0.1

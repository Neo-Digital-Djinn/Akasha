# ATVM Invariants v0.1

If any invariant is violated, execution MUST enter ERROR state and HALT.

---

## I. Temporal Invariants

1. Time MUST be monotonic.
2. Analysis window Δt MUST remain constant.

---

## II. State Invariants

1. State MUST include f_c, A, H, N, Δt.
2. Bounds:
   - f_c > 0
   - A ≥ 0
   - 0.0 ≤ H ≤ 1.0
   - 0.0 ≤ N ≤ 1.0
   - Δt > 0
3. All fields MUST derive from the same window.

---

## III. Transition Invariants

1. Instructions derive ONLY from transitions.
2. Transition computation MUST be deterministic.
3. Thresholds MUST be fixed.

---

## IV. Event Invariants

1. Event emission MUST be deterministic.
2. Event order MUST match transition order.
3. No transition may be skipped.

---

## V. Execution Invariants

1. Forward-only execution.
2. Stack underflow HALTS.
3. Division by zero HALTS.

---

## VI. Program Invariants

1. Programs MUST be finite.
2. Programs MUST explicitly terminate.

---

## VII. Analyzer Invariants

1. Analyzer and VM MUST be separate.
2. Analyzer MUST be deterministic.

---

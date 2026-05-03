# Acoustic Transition Virtual Machine (ATVM) Specification v0.1

## 1. Purpose and Scope

This document specifies the Acoustic Transition Virtual Machine (ATVM): a computational substrate in which programs are encoded as ordered acoustic state transitions rather than symbolic text.

ATVM defines:
- how sound is interpreted as computation
- the minimal execution semantics
- the invariants required for deterministic behavior

This specification is medium-agnostic: any acoustic signal (file, stream, live input) may serve as a program if it satisfies the invariants.

ATVM is not a music language or notation system. It is a transition-based virtual machine whose instruction set emerges from measurable changes in acoustic state.

---

## 2. Core Principles

1. Transition, not symbol  
2. Time as instruction pointer  
3. Deterministic collapse from continuous signal to discrete events  
4. Minimal, orthogonal semantics  
5. Analyzer / VM separation  

---

## 3. Acoustic State Model

An Acoustic State is a vector sampled over a fixed analysis window Δt.

State S = {
  f_c  : frequency centroid (Hz)
  A    : amplitude (RMS)
  H    : harmonicity ratio (0.0–1.0)
  N    : noise ratio (0.0–1.0)
  Δt   : duration (seconds)
}

All fields MUST be derived from the same signal window.

---

## 4. Transition Model

A Transition is the ordered difference between two consecutive states:

Tₙ = Sₙ₊₁ − Sₙ

Only transitions may produce executable events.

---

## 5. Event Classification

A Transition Event is produced when a transition exceeds one or more semantic thresholds.
Thresholds MUST be fixed before execution and remain constant.

---

## 6. Instruction Semantics (Minimal Set)

Δf_c > +θ_f            → PUSH  
Δf_c < −θ_f            → POP  
|Δf_c| ≤ ε_f, ΔA > θ_A → ADD  
|Δf_c| ≤ ε_f, ΔA < −θ_A→ SUB  
ΔH > θ_H               → MUL  
ΔN > θ_N               → DIV  
Silence ≥ τ            → NOOP / DELIMITER  
Motif repetition      → LOOP  
Impulse spike          → IO  
Context collapse       → HALT  

---

## 7. Execution Context

- One or more stacks
- Time-indexed instruction pointer
- Optional registers
- Execution state: RUNNING | HALTED | ERROR

Execution proceeds strictly forward in time.

---

## 8. Program Definition

A Program is a finite acoustic signal whose ordered state transitions produce a valid event stream.

Programs MUST terminate via HALT or signal exhaustion.

---

## 9. Error Conditions

Execution MUST halt on:
- stack underflow
- division by zero
- invariant violation
- invalid transition

---

## 10. Determinism

Given identical input, parameters, and thresholds, an implementation MUST produce identical results.

---

## 11. Relationship to Cantus VM

ATVM functions as a frontend event generator.
The Cantus VM remains unchanged.

---

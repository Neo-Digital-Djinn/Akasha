"""
Cantus test suite — Debian port validation.

Covers:
  - all original Termux test cases
  - OVER opcode (was missing from vm.py)
  - JNZ opcode (was in spec, missing from vm.py)
  - parse_cantus alias (was missing from dsl.py, broke repl.py import)
  - halt_reason traceability (Axiom 5)
  - division by zero HALT (was silently continuing)
  - stack underflow HALT
  - factorial example from examples/
"""

import pytest
from cantus.vm import CantusVM
from cantus.dsl import parse, parse_cantus
from cantus.compiler import compile as cantus_compile
from cantus.midi import midi_to_tokens


# ── Basic arithmetic ────────────────────────────────────────────────────

def test_push_add():
    vm = CantusVM()
    result = vm.execute([("PUSH", 2), ("PUSH", 3), ("ADD", 0)])
    assert result[-1] == 5

def test_mul():
    vm = CantusVM()
    result = vm.execute([("PUSH", 2), ("PUSH", 3), ("MUL", 0), ("PUSH", 4), ("ADD", 0)])
    assert result[-1] == 10

def test_sub():
    vm = CantusVM()
    result = vm.execute([("PUSH", 10), ("PUSH", 4), ("SUB", 0)])
    assert result[-1] == 6

def test_div():
    vm = CantusVM()
    result = vm.execute([("PUSH", 10), ("PUSH", 2), ("DIV", 0)])
    assert result[-1] == 5

def test_mod():
    vm = CantusVM()
    result = vm.execute([("PUSH", 7), ("PUSH", 3), ("MOD", 0)])
    assert result[-1] == 1


# ── Stack ops ───────────────────────────────────────────────────────────

def test_dup():
    vm = CantusVM()
    result = vm.execute([("PUSH", 7), ("DUP", 0)])
    assert result == [7, 7]

def test_swap():
    vm = CantusVM()
    result = vm.execute([("PUSH", 1), ("PUSH", 2), ("SWAP", 0)])
    assert result == [2, 1]

def test_over():
    """OVER was missing from original vm.py — this test validates the fix."""
    vm = CantusVM()
    result = vm.execute([("PUSH", 1), ("PUSH", 2), ("OVER", 0)])
    assert result == [1, 2, 1]

def test_pop():
    vm = CantusVM()
    result = vm.execute([("PUSH", 5), ("PUSH", 9), ("POP", 0)])
    assert result == [5]


# ── Control flow ────────────────────────────────────────────────────────

def test_jmp():
    vm = CantusVM()
    tokens = [
        ("LABEL", "start"),
        ("PUSH", 42),
        ("JMP", "end"),
        ("PUSH", 99),   # should be skipped
        ("LABEL", "end"),
        ("HALT", 0),
    ]
    result = vm.execute(tokens)
    assert result == [42]

def test_jz_taken():
    vm = CantusVM()
    tokens = [
        ("PUSH", 0),
        ("JZ", "target"),
        ("PUSH", 99),
        ("LABEL", "target"),
        ("PUSH", 1),
    ]
    result = vm.execute(tokens)
    assert result[-1] == 1

def test_jnz_taken():
    """JNZ was in spec v1 but missing from original vm.py."""
    vm = CantusVM()
    tokens = [
        ("PUSH", 5),
        ("JNZ", "yes"),
        ("PUSH", 0),
        ("LABEL", "yes"),
        ("PUSH", 99),
    ]
    result = vm.execute(tokens)
    assert result[-1] == 99

def test_jnz_not_taken():
    vm = CantusVM()
    tokens = [
        ("PUSH", 0),
        ("JNZ", "yes"),
        ("PUSH", 42),
        ("LABEL", "yes"),
    ]
    result = vm.execute(tokens)
    assert result[-1] == 42


# ── Memory ──────────────────────────────────────────────────────────────

def test_store_load():
    vm = CantusVM()
    tokens = [
        ("PUSH", 0),    # addr
        ("PUSH", 77),   # val   (STORE pops val then addr)
        ("STORE", 0),
        ("PUSH", 0),
        ("LOAD", 0),
    ]
    result = vm.execute(tokens)
    assert result[-1] == 77


# ── Error / halt conditions ─────────────────────────────────────────────

def test_div_zero_halts():
    vm = CantusVM()
    vm.execute([("PUSH", 5), ("PUSH", 0), ("DIV", 0)])
    assert vm.halt_reason is not None
    assert "zero" in vm.halt_reason.lower()

def test_stack_underflow_halts():
    vm = CantusVM()
    vm.execute([("POP", 0)])
    assert not vm.running
    assert vm.halt_reason is not None


# ── DSL parser ──────────────────────────────────────────────────────────

def test_parse_basic():
    tokens = parse("PUSH 5\nPUSH 3\nADD")
    assert tokens == [("PUSH", 5), ("PUSH", 3), ("ADD", 0)]

def test_parse_cantus_alias():
    """parse_cantus was missing from dsl.py — repl.py depended on it."""
    tokens = parse_cantus("PUSH 2\nPUSH 2\nMUL")
    assert tokens == [("PUSH", 2), ("PUSH", 2), ("MUL", 0)]

def test_parse_comments_skipped():
    tokens = parse("# comment\nPUSH 1\n# another\nPUSH 2\nADD")
    assert len(tokens) == 3

def test_parse_unknown_opcode_raises():
    with pytest.raises(ValueError):
        parse("FOOBAR 99")


# ── Factorial example ───────────────────────────────────────────────────

FACTORIAL_SOURCE = """\
# Factorial of 5 (corrected in akasha-cantus v2.1.0)
# Stack layout: [accumulator, counter], counter on top
PUSH 1
PUSH 5
LABEL loop
DUP
JZ end
SWAP
OVER
MUL
SWAP
PUSH 1
SUB
JMP loop
LABEL end
POP
PRINT
HALT
"""

def test_factorial():
    tokens = parse(FACTORIAL_SOURCE)
    vm = CantusVM()
    result = vm.execute(tokens)
    # 5! = 120
    assert result[-1] == 120


# ── Self-modifying POKE ─────────────────────────────────────────────────

def test_poke():
    """
    POKE pops (val, addr) and rewrites tokens[addr] = ("PUSH", val).
    This test verifies the rewrite occurs. The token list is mutated in place.
    Original Cantus v2.0 test expected stack result 100 but the program
    had a stack underflow after POKE consumed both operands. Fixed in v2.1.0
    to test the actual observable behavior: token mutation.
    """
    vm = CantusVM()
    tokens = [
        ("PUSH", 5),    # 0
        ("PUSH", 6),    # 1  — address to poke
        ("PUSH", 95),   # 2  — value to poke
        ("POKE", 0),    # 3  — tokens[6] = ("PUSH", 95)
        ("PUSH", 0),    # 4
        ("ADD", 0),     # 5
        ("HALT", 0),    # 6  — gets rewritten to ("PUSH", 95)
    ]
    result = vm.execute(tokens)
    # Verify the self-modification happened
    assert tokens[6] == ("PUSH", 95)
    # And the poked value ended up on the stack via the mutated token
    assert 95 in result


# ── Bytecode compiler ───────────────────────────────────────────────────

def test_compile_produces_ints():
    tokens = parse("PUSH 5\nPUSH 3\nADD\nHALT")
    bc = cantus_compile(tokens)
    assert all(isinstance(x, int) for x in bc)
    assert len(bc) > 0


# ── MIDI bridge ─────────────────────────────────────────────────────────

def test_midi_to_tokens():
    notes = [60, 60, 62, 67]   # PUSH PUSH ADD PRINT
    tokens = midi_to_tokens(notes)
    ops = [t[0] for t in tokens]
    assert "PUSH" in ops
    assert "ADD" in ops

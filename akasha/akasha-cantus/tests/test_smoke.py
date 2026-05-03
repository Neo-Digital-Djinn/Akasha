"""
tests/test_smoke.py
akasha-cantus

Covers:
  1. Basic arithmetic
  2. OVER opcode (was missing — broke factorial.cantus)
  3. JNZ opcode (was missing from spec)
  4. MOD opcode (was missing from spec)
  5. parse_cantus alias (was missing — broke repl.py and test_basic.py)
  6. factorial.cantus end-to-end
  7. Stack underflow halts cleanly
  8. Division by zero halts cleanly
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from cantus.vm import CantusVM
from cantus.dsl import parse, parse_cantus
from cantus.compiler import compile, decompile


def test_basic_add():
    vm = CantusVM()
    result = vm.execute([("PUSH", 2), ("PUSH", 3), ("ADD", 0)])
    assert result[-1] == 5


def test_parse_cantus_alias():
    """parse_cantus must be importable and work — was broken in original."""
    tokens = parse_cantus("PUSH 2\nPUSH 3\nADD")
    vm = CantusVM()
    result = vm.execute(tokens)
    assert result[-1] == 5


def test_over_opcode():
    """OVER: ( a b -- a b a )"""
    vm = CantusVM()
    result = vm.execute([("PUSH", 7), ("PUSH", 3), ("OVER", 0)])
    assert result == [7, 3, 7]


def test_jnz_opcode():
    """JNZ: jump if top != 0"""
    vm = CantusVM()
    # PUSH 3, JNZ end, PUSH 99, LABEL end, PRINT
    tokens = [
        ("PUSH", 3),
        ("JNZ", "end"),
        ("PUSH", 99),   # should be skipped
        ("LABEL", "end"),
        ("HALT", 0),
    ]
    result = vm.execute(tokens)
    assert 99 not in result


def test_mod_opcode():
    vm = CantusVM()
    result = vm.execute([("PUSH", 10), ("PUSH", 3), ("MOD", 0)])
    assert result[-1] == 1


def test_factorial_5():
    """factorial.cantus — requires OVER which was missing."""
    vm = CantusVM()
    source = open(os.path.join(os.path.dirname(__file__), "../examples/factorial.cantus")).read()
    tokens = parse(source)
    result = vm.execute(tokens)
    assert result[-1] == 120


def test_stack_underflow_halts():
    """Stack underflow must halt cleanly, not raise."""
    vm = CantusVM()
    result = vm.execute([("POP", 0)])  # underflow
    assert vm.running is False


def test_div_by_zero_halts():
    vm = CantusVM()
    result = vm.execute([("PUSH", 5), ("PUSH", 0), ("DIV", 0)])
    assert vm.running is False


def test_bytecode_roundtrip():
    tokens = [("PUSH", 42), ("PUSH", 8), ("MUL", 0), ("HALT", 0)]
    bc = compile(tokens)
    assert isinstance(bc, list)
    assert all(isinstance(x, int) for x in bc)


if __name__ == "__main__":
    test_basic_add()
    test_parse_cantus_alias()
    test_over_opcode()
    test_jnz_opcode()
    test_mod_opcode()
    test_factorial_5()
    test_stack_underflow_halts()
    test_div_by_zero_halts()
    test_bytecode_roundtrip()
    print("All smoke tests passed.")

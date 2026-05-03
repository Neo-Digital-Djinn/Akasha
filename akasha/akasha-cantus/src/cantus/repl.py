"""
repl.py — Cantus REPL
akasha-cantus

PORTING CHANGES vs original:
  - Fixed import: parse_cantus now exists in dsl.py (was missing — caused ImportError)
  - REPL now accumulates a persistent VM across inputs (stateful session)
"""

from cantus.vm import CantusVM
from cantus.dsl import parse_cantus


def start_repl():
    print("● CANTUS REPL v2.0")
    print("Type instructions. 'exit' or 'quit' to stop. 'reset' to clear VM.")

    vm = CantusVM()

    while True:
        try:
            line = input(">>> ").strip()
            if not line:
                continue
            if line.lower() in {"exit", "quit"}:
                break
            if line.lower() == "reset":
                vm.reset()
                print("VM reset.")
                continue
            tokens = parse_cantus(line)
            result = vm.execute(tokens)
            print("STACK:", result)
        except ValueError as e:
            print("Parse error:", e)
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    start_repl()

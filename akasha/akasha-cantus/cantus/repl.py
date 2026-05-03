"""
Cantus interactive REPL.

Termux → Debian fix: repl.py originally imported `parse_cantus` from
`cantus.dsl` but that name didn't exist in dsl.py (only `parse`).
Fixed by adding the alias in dsl.py; import unchanged here so the
original source intent is preserved.
"""

from cantus.vm import CantusVM
from cantus.dsl import parse_cantus  # alias now exists in dsl.py


def start_repl() -> None:
    print("● CANTUS REPL v2.1")
    print("Type instructions one per line. 'run' executes. 'reset' clears. 'exit' to quit.")
    print()

    vm = CantusVM()
    pending: list = []

    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        cmd = line.lower()

        if cmd in {"exit", "quit"}:
            break

        elif cmd == "reset":
            vm.reset()
            pending = []
            print("VM reset.")

        elif cmd == "run":
            if not pending:
                print("Nothing to run.")
            else:
                result = vm.execute(pending)
                print("STACK:", result)
                if vm.halt_reason:
                    print("HALT:", vm.halt_reason)
                pending = []

        elif cmd == "stack":
            print("STACK:", vm.stack)

        else:
            try:
                tokens = parse_cantus(line)
                pending.extend(tokens)
                print(f"  queued {len(tokens)} token(s) — type 'run' to execute")
            except Exception as exc:
                print("Error:", exc)

"""
Cantus CLI entrypoint.

Usage:
  python -m cantus.cli program.cantus        # run a .cantus source file
  python -m cantus.cli --audio sound.wav     # tokenize audio and run
  python -m cantus.cli --repl               # interactive REPL
  python -m cantus.cli --bytecode prog.cantus # show compiled bytecode

Termux → Debian: sys.argv handling unchanged; shebang lines not used
(Debian packaging handles entry points via pyproject.toml console_scripts).
"""

import sys
from cantus.vm import CantusVM
from cantus.dsl import parse
from cantus.compiler import compile as cantus_compile


def _run_source(path: str) -> None:
    with open(path) as f:
        source = f.read()
    tokens = parse(source)
    vm = CantusVM()
    result = vm.execute(tokens)
    print("Final Stack:", result)
    if vm.halt_reason:
        print("Halt reason:", vm.halt_reason)
    print("Bytecode:", cantus_compile(tokens))


def _run_audio(path: str) -> None:
    from cantus.tokenizer import tokenize
    tokens = tokenize(path)
    print(f"Tokenized {len(tokens)} instructions from audio.")
    vm = CantusVM()
    result = vm.execute(tokens)
    print("Final Stack:", result)
    if vm.halt_reason:
        print("Halt reason:", vm.halt_reason)


def main() -> None:
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print("Usage:")
        print("  python -m cantus.cli <program.cantus>")
        print("  python -m cantus.cli --audio <sound.wav>")
        print("  python -m cantus.cli --repl")
        print("  python -m cantus.cli --bytecode <program.cantus>")
        return

    if args[0] == "--repl":
        from cantus.repl import start_repl
        start_repl()
        return

    if args[0] == "--audio":
        if len(args) < 2:
            print("Error: --audio requires a file path")
            sys.exit(1)
        _run_audio(args[1])
        return

    if args[0] == "--bytecode":
        if len(args) < 2:
            print("Error: --bytecode requires a file path")
            sys.exit(1)
        with open(args[1]) as f:
            source = f.read()
        tokens = parse(source)
        print("Bytecode:", cantus_compile(tokens))
        return

    _run_source(args[0])


if __name__ == "__main__":
    main()

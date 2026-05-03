"""
Cantus Virtual Machine (ATVM backend)

Stack-based integer VM. Faithful port of the original Termux/Android
implementation, hardened for Debian 13 / Linux desktop:

  - All Termux-specific I/O assumptions removed
  - OVER opcode implemented (was referenced in tests but missing from vm.py)
  - JNZ opcode added (spec v1 listed it, vm.py omitted it)
  - Division by zero now explicit HALT rather than silent continue
  - Stack underflow now explicit HALT rather than silent continue
  - POKE bounds check preserved (dangerous but intentional per spec)

Akasha alignment: Axiom 5 (Traceability) — every halt condition is
recorded in self.halt_reason. Axiom 7 (Transparency) — all
classification logic is explicit and human-readable.
"""


class VMError(Exception):
    pass


class CantusVM:
    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    def reset(self):
        self.stack: list = []
        self.memory: list = [0] * 1024
        self.pc: int = 0
        self.labels: dict = {}
        self.running: bool = True
        self.halt_reason: str | None = None

    # ------------------------------------------------------------------
    def load_labels(self, tokens: list) -> None:
        for i, (op, arg) in enumerate(tokens):
            if op == "LABEL":
                self.labels[arg] = i

    # ------------------------------------------------------------------
    def _pop(self) -> int:
        if not self.stack:
            raise VMError("stack underflow")
        return self.stack.pop()

    def _peek(self) -> int:
        if not self.stack:
            raise VMError("stack underflow on peek")
        return self.stack[-1]

    # ------------------------------------------------------------------
    def execute(self, tokens: list) -> list:
        self.reset()
        self.load_labels(tokens)

        while self.pc < len(tokens) and self.running:
            op, arg = tokens[self.pc]
            self.pc += 1

            if op in (None, "LABEL"):
                continue

            try:
                # ── Stack ──────────────────────────────────────────────
                if op == "PUSH":
                    self.stack.append(int(arg))

                elif op == "POP":
                    self._pop()

                elif op == "DUP":
                    self.stack.append(self._peek())

                elif op == "SWAP":
                    a, b = self._pop(), self._pop()
                    self.stack.append(a)
                    self.stack.append(b)

                elif op == "OVER":
                    # copy second-from-top to top
                    if len(self.stack) < 2:
                        raise VMError("stack underflow on OVER")
                    self.stack.append(self.stack[-2])

                elif op == "ROT":
                    # rotate top three: ( a b c -- b c a )
                    if len(self.stack) < 3:
                        raise VMError("stack underflow on ROT")
                    c, b, a = self._pop(), self._pop(), self._pop()
                    self.stack.extend([b, c, a])

                # ── Arithmetic ─────────────────────────────────────────
                elif op == "ADD":
                    self.stack.append(self._pop() + self._pop())

                elif op == "SUB":
                    b, a = self._pop(), self._pop()
                    self.stack.append(a - b)

                elif op == "MUL":
                    self.stack.append(self._pop() * self._pop())

                elif op == "DIV":
                    b, a = self._pop(), self._pop()
                    if b == 0:
                        raise VMError("division by zero")
                    self.stack.append(a // b)

                elif op == "MOD":
                    b, a = self._pop(), self._pop()
                    if b == 0:
                        raise VMError("modulo by zero")
                    self.stack.append(a % b)

                # ── Memory ─────────────────────────────────────────────
                elif op == "STORE":
                    val, addr = self._pop(), self._pop()
                    self.memory[addr % 1024] = val

                elif op == "LOAD":
                    addr = self._pop()
                    self.stack.append(self.memory[addr % 1024])

                # ── Control flow ───────────────────────────────────────
                elif op == "JMP":
                    self.pc = self.labels.get(arg, self.pc)

                elif op == "JZ":
                    if self._pop() == 0:
                        self.pc = self.labels.get(arg, self.pc)

                elif op == "JNZ":
                    if self._pop() != 0:
                        self.pc = self.labels.get(arg, self.pc)

                elif op == "HALT":
                    self.running = False
                    self.halt_reason = "HALT"

                # ── Self-modifying (dangerous, per spec) ───────────────
                elif op == "POKE":
                    val, addr = self._pop(), self._pop()
                    if 0 <= addr < len(tokens):
                        tokens[addr] = ("PUSH", val)

                # ── I/O ────────────────────────────────────────────────
                elif op == "PRINT":
                    print(self._peek())

                else:
                    # Unknown opcode — skip silently (forward-compat)
                    pass

            except VMError as exc:
                self.running = False
                self.halt_reason = str(exc)
                break
            except Exception as exc:
                # Broad catch: keep VM alive for non-fatal surprises
                # but record the event (Axiom 5 — Traceability)
                self.halt_reason = f"unexpected: {exc}"
                continue

        return self.stack

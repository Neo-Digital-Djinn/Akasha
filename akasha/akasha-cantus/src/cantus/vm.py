"""
vm.py — Cantus Virtual Machine
akasha-cantus

PORTING CHANGES vs original:
  - Added OVER opcode (required by factorial.cantus example, listed in v1 spec)
  - Added JNZ opcode (listed in v1 spec, absent from implementation)
  - Added MOD opcode (listed in v1 spec, absent from implementation)
  - Stack underflow guard: operations on insufficient stack now halt gracefully
    rather than raising unhandled IndexError (ATVM Invariant V.2)
  - Division by zero now halts cleanly (ATVM Invariant V.3)
  - POKE guard: address must be within token list bounds
"""


class CantusVM:
    def __init__(self):
        self.reset()

    def reset(self):
        self.stack = []
        self.memory = [0] * 1024
        self.pc = 0
        self.labels = {}
        self.running = True

    def load_labels(self, tokens):
        for i, (op, arg) in enumerate(tokens):
            if op == "LABEL":
                self.labels[arg] = i

    def _pop(self):
        """Pop with underflow guard — halts on underflow (ATVM Invariant V.2)."""
        if not self.stack:
            self.running = False
            raise IndexError("stack underflow")
        return self.stack.pop()

    def execute(self, tokens):
        self.reset()
        self.load_labels(tokens)

        while self.pc < len(tokens) and self.running:
            op, arg = tokens[self.pc]
            self.pc += 1

            if op in (None, "LABEL"):
                continue

            try:
                # ── Stack ────────────────────────────────────────────────────
                if op == "PUSH":
                    self.stack.append(arg)
                elif op == "POP":
                    self._pop()
                elif op == "DUP":
                    self.stack.append(self.stack[-1])
                elif op == "SWAP":
                    b, a = self._pop(), self._pop()
                    self.stack.append(b)
                    self.stack.append(a)
                elif op == "OVER":
                    # OVER: copy second-from-top onto top  ( a b -- a b a )
                    if len(self.stack) < 2:
                        self.running = False
                        break
                    self.stack.append(self.stack[-2])

                # ── Arithmetic ───────────────────────────────────────────────
                elif op == "ADD":
                    b, a = self._pop(), self._pop()
                    self.stack.append(a + b)
                elif op == "SUB":
                    b, a = self._pop(), self._pop()
                    self.stack.append(a - b)
                elif op == "MUL":
                    b, a = self._pop(), self._pop()
                    self.stack.append(a * b)
                elif op == "DIV":
                    b, a = self._pop(), self._pop()
                    if b == 0:
                        self.running = False  # ATVM Invariant V.3
                        break
                    self.stack.append(a // b)
                elif op == "MOD":
                    b, a = self._pop(), self._pop()
                    if b == 0:
                        self.running = False
                        break
                    self.stack.append(a % b)

                # ── Memory ───────────────────────────────────────────────────
                elif op == "STORE":
                    val, addr = self._pop(), self._pop()
                    self.memory[addr % 1024] = val
                elif op == "LOAD":
                    addr = self._pop()
                    self.stack.append(self.memory[addr % 1024])

                # ── Control flow ─────────────────────────────────────────────
                elif op == "JMP":
                    self.pc = self.labels.get(arg, self.pc)
                elif op == "JZ":
                    val = self._pop()
                    if val == 0:
                        self.pc = self.labels.get(arg, self.pc)
                elif op == "JNZ":
                    val = self._pop()
                    if val != 0:
                        self.pc = self.labels.get(arg, self.pc)
                elif op == "HALT":
                    self.running = False

                # ── Self-modifying (dangerous) ───────────────────────────────
                elif op == "POKE":
                    val, addr = self._pop(), self._pop()
                    if 0 <= addr < len(tokens):
                        tokens[addr] = ("PUSH", val)

                # ── Output ───────────────────────────────────────────────────
                elif op == "PRINT":
                    if self.stack:
                        print(self.stack[-1])

            except IndexError:
                # Stack underflow already set self.running = False
                break
            except Exception:
                continue

        return self.stack

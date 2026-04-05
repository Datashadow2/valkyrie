#!/usr/bin/env python3
"""
VALKYRIE MINIMAL PRO
Lightweight but powerful
"""

import sys

# =========================
# COLORS
# =========================
COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "blue": "\033[34m",
    "yellow": "\033[33m",
    "reset": "\033[0m"
}

def out(text):
    print(f"{COLORS['green']}{text}{COLORS['reset']}")

def err(text):
    print(f"{COLORS['blue']}{text}{COLORS['reset']}")

def user_input(prompt=""):
    return input(f"{COLORS['red']}{prompt}{COLORS['reset']}")

# =========================
# BUILTINS
# =========================
def vk_str(x): return str(x)
def vk_int(x): return int(x)
def vk_len(x): return len(x)

WEAPONS = {
    "str": vk_str,
    "int": vk_int,
    "len": vk_len,
    "input": user_input
}

# =========================
# INTERPRETER
# =========================
class Valkyrie:
    def __init__(self):
        self.vars = {}
        self.funcs = {}
        self.lines = []
        self.pc = 0
        self.ret_val = None
        self.returning = False

    # ---------------------
    # EVALUATOR (SAFE-ish)
    # ---------------------
    def evaluate(self, expr):
        expr = expr.strip()

        if expr == "_result":
            return self.vars.get("_result", "")

        # Replace variables safely
        for k, v in self.vars.items():
            expr = expr.replace(k, repr(v))

        # Built-in calls like str(x)
        try:
            return eval(expr, {"__builtins__": {}}, WEAPONS)
        except:
            return expr

    # ---------------------
    # EXECUTION
    # ---------------------
    def run(self, source):
        self.lines = [l.strip() for l in source.split("\n") if l.strip() and not l.startswith("#")]
        self.pc = 0

        while self.pc < len(self.lines):
            line = self.lines[self.pc]
            self.pc += 1

            try:
                self.execute(line)
            except Exception as e:
                err(f"[Execution Error] {e}")
                break

    # ---------------------
    # LINE EXECUTION
    # ---------------------
    def execute(self, line):

        # PRINT
        if line.startswith("print "):
            val = self.evaluate(line[6:])
            out(val)
            return

        # LET
        if line.startswith("let "):
            var, val = line[4:].split("=", 1)
            self.vars[var.strip()] = self.evaluate(val)
            return

        # CALL
        if line.startswith("call "):
            parts = line.split()
            name = parts[1]
            args = [self.evaluate(a) for a in parts[2:]]

            if name in WEAPONS:
                self.vars["_result"] = WEAPONS[name](*args)
            elif name in self.funcs:
                self.vars["_result"] = self.run_func(name, args)
            return

        # IF
        if line.startswith("if "):
            cond = line[3:]
            body = []

            while self.lines[self.pc] != "endif":
                body.append(self.lines[self.pc])
                self.pc += 1
            self.pc += 1

            if self.evaluate(cond):
                for l in body:
                    self.execute(l)
            return

        # WHILE
        if line.startswith("while "):
            cond = line[6:]
            body = []
            start = self.pc

            while self.lines[self.pc] != "endwhile":
                body.append(self.lines[self.pc])
                self.pc += 1
            self.pc += 1

            while self.evaluate(cond):
                for l in body:
                    self.execute(l)
            return

        # FOR
        if line.startswith("for "):
            var, rest = line[4:].split(" in ")
            iterable = self.evaluate(rest)

            body = []
            while self.lines[self.pc] != "endfor":
                body.append(self.lines[self.pc])
                self.pc += 1
            self.pc += 1

            for val in iterable:
                self.vars[var.strip()] = val
                for l in body:
                    self.execute(l)
            return

        # FUNCTION
        if line.startswith("fn "):
            parts = line.split()
            name = parts[1]
            params = parts[2:]

            body = []
            while self.lines[self.pc] != "endfn":
                body.append(self.lines[self.pc])
                self.pc += 1
            self.pc += 1

            self.funcs[name] = (params, body)
            return

        # RETURN
        if line.startswith("return "):
            self.ret_val = self.evaluate(line[7:])
            self.returning = True
            return

        # HLT
        if line == "hlt":
            sys.exit(0)

    # ---------------------
    # FUNCTION CALL
    # ---------------------
    def run_func(self, name, args):
        params, body = self.funcs[name]
        old = self.vars.copy()

        for i, p in enumerate(params):
            self.vars[p] = args[i] if i < len(args) else None

        result = None
        for l in body:
            if l.startswith("return "):
                result = self.evaluate(l[7:])
                break
            self.execute(l)

        self.vars = old
        return result


# =========================
# MAIN
# =========================
def main():
    if len(sys.argv) < 2:
        print("Usage: ./valkyrie.py script.vk")
        return

    with open(sys.argv[1]) as f:
        code = f.read()

    vk = Valkyrie()
    vk.run(code)

if __name__ == "__main__":
    main()

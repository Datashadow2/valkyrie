#!/usr/bin/env python3
"""
VALKYRIE 5.1 - FINAL CROSS-LANGUAGE ENABLED
"""

import sys
import os
import random
import secrets
import hashlib
import subprocess
import json
import base64
import urllib.request
from datetime import datetime
import ctypes

# ============================================================
# TEXT & COLOR HELPERS
# ============================================================

def color_print(text, color="green"):
    colors = {
        "default": "\033[39m",
        "red": "\033[31m",
        "green": "\033[32m",
        "blue": "\033[34m",
        "yellow": "\033[33m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bold": "\033[1m",
        "underline": "\033[4m",
        "reverse": "\033[7m",
    }
    c = colors.get(color.lower(), colors["green"])
    reset = "\033[0m"
    print(f"{c}{text}{reset}")
    return text

def user_input(prompt="> "):
    return input(f"\033[31m{prompt}\033[0m")  # always red

def error_print(text):
    color_print(text, "blue")

# ============================================================
# CROSS-LANGUAGE HELPERS
# ============================================================

_loaded_modules = {}
_loaded_libs = {}

def call_python(module_name, func_name, *args):
    if module_name not in _loaded_modules:
        try:
            _loaded_modules[module_name] = __import__(module_name)
        except Exception as e:
            error_print(f"[Python Import Error] {e}")
            return None
    mod = _loaded_modules[module_name]
    return getattr(mod, func_name)(*args)

def call_c(lib_path, func_name, *args, restype=ctypes.c_int, argtypes=None):
    if lib_path not in _loaded_libs:
        try:
            _loaded_libs[lib_path] = ctypes.CDLL(lib_path)
        except Exception as e:
            error_print(f"[C Load Error] {e}")
            return None
    lib = _loaded_libs[lib_path]
    func = getattr(lib, func_name)
    if argtypes: func.argtypes = argtypes
    func.restype = restype
    return func(*args)

def call_go(binary, *args):
    try:
        result = subprocess.run([binary, *map(str, args)], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        error_print(f"[Go Error] {e}")
        return None

def call_java(jar, *args):
    try:
        result = subprocess.run(["java", "-jar", jar, *map(str, args)], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        error_print(f"[Java Error] {e}")
        return None

def call_lang(lang, *args):
    lang = lang.lower()
    try:
        if lang == "python":
            return call_python(*args)
        elif lang == "c":
            return call_c(*args)
        elif lang == "go":
            return call_go(*args)
        elif lang == "java":
            return call_java(*args)
        else:
            error_print(f"[call_lang] Unknown language: {lang}")
    except Exception as e:
        error_print(f"[call_lang Error] {e}")
        return None

# ============================================================
# BASIC WEAPONS
# ============================================================

def file_write(path, data):
    try:
        with open(path, 'w') as f: f.write(str(data))
        return True
    except Exception as e:
        error_print(f"[File Write Error] {e}")
        return False

def file_read(path):
    try:
        with open(path, 'r') as f: return f.read()
    except Exception as e:
        error_print(f"[File Read Error] {e}")
        return ""

def sha256(s): return hashlib.sha256(str(s).encode()).hexdigest()
def md5(s): return hashlib.md5(str(s).encode()).hexdigest()
def base64_encode(s): return base64.b64encode(str(s).encode()).decode()
def base64_decode(s): return base64.b64decode(s).decode()
def now(): return datetime.now()
def sleep(sec):
    import time; time.sleep(sec); return sec
def str_convert(x): return str(x)

# ============================================================
# WEAPONS DICTIONARY
# ============================================================

WEAPONS = {
    'file_write': file_write,
    'file_read': file_read,
    'sha256': sha256,
    'md5': md5,
    'base64_encode': base64_encode,
    'base64_decode': base64_decode,
    'sleep': sleep,
    'now': now,
    'str': str_convert,
    'color_print': color_print,
    'input': user_input,
    'call_lang': call_lang,
}

# ============================================================
# INTERPRETER
# ============================================================

class Valkyrie:
    def __init__(self):
        self.vars = {}
        self.funcs = {}
        self.labels = {}
        self.lines = []
        self.pc = 0
        self.halted = False
        self.returning = False
        self.ret_val = None

    def evaluate(self, expr):
        expr = expr.strip()
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        if expr in self.vars: return self.vars[expr]
        if expr == '_result': return self.vars.get('_result', '')
        if expr == 'true': return True
        if expr == 'false': return False
        if expr == 'None': return None
        try:
            if '.' in expr: return float(expr)
            return int(expr)
        except: pass
        for op in ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=']:
            if op in expr:
                parts = expr.split(op, 1)
                if len(parts) == 2:
                    left = self.evaluate(parts[0].strip())
                    right = self.evaluate(parts[1].strip())
                    if op == '+': return left + right
                    if op == '-': return left - right
                    if op == '*': return left * right
                    if op == '/': return left / right if right != 0 else None
                    if op == '==': return left == right
                    if op == '!=': return left != right
                    if op == '<': return left < right
                    if op == '>': return left > right
                    if op == '<=': return left <= right
                    if op == '>=': return left >= right
        if '(' in expr and expr.endswith(')'):
            name = expr[:expr.index('(')]
            args_str = expr[expr.index('(')+1:-1]
            args = [self.evaluate(a.strip()) for a in args_str.split(',')] if args_str else []
            if name in WEAPONS: return WEAPONS[name](*args)
        return expr

    def execute_line(self, line):
        if not line or line.startswith('#'): return
        if line.startswith('print '):
            val = self.evaluate(line[6:])
            color_print(val, "green")
        elif line.startswith('let '):
            var, val = line[4:].split('=', 1)
            self.vars[var.strip()] = self.evaluate(val.strip())
        elif line.startswith('call '):
            parts = line[5:].split()
            name = parts[0]
            args = [self.evaluate(a) for a in parts[1:]]
            if name in WEAPONS: self.vars['_result'] = WEAPONS[name](*args)
        elif line.startswith('hlt'): self.halted = True

    def run(self, source):
        self.lines = [l.strip() for l in source.split('\n') if l.strip() and not l.strip().startswith('#')]
        self.pc = 0
        while self.pc < len(self.lines) and not self.halted:
            line = self.lines[self.pc]
            self.pc += 1
            try: self.execute_line(line)
            except Exception as e: error_print(f"[Execution Error] {e}")

# ============================================================
# MAIN
# ============================================================

def main():
    if len(sys.argv) < 2:
        color_print("Valkyrie - Systems Language\nUsage: python valkyrie.py script.vk", "green")
        return
    with open(sys.argv[1], 'r') as f:
        source = f.read()
    vk = Valkyrie()
    vk.run(source)

if __name__ == "__main__":
    main()

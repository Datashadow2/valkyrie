#!/usr/bin/env python3
"""
VALKYRIE 5.0 - FULL ULTIMATE VERSION
All features included: lists, loops, functions, colored I/O, cross-language calls
"""

import sys, os, subprocess, json, base64, hashlib, random, secrets, ctypes
from datetime import datetime

# ============================
# COLOR PRINTING
# ============================

def color_print(text, color="default"):
    colors = {
        "default": "\033[39m",
        "red": "\033[31m",
        "green": "\033[32m",
        "blue": "\033[34m",
        "yellow": "\033[33m",
        "cyan": "\033[36m",
        "magenta": "\033[35m",
        "white": "\033[37m",
        "bold": "\033[1m",
    }
    c = colors.get(color.lower(), colors["default"])
    reset = "\033[0m"
    print(f"{c}{text}{reset}")
    return text

def user_input(prompt=""):
    return input(f"\033[31m{prompt}\033[0m")

# ============================
# WEAPONS / FUNCTIONS
# ============================

WEAPONS = {}

def file_write(path, data):
    try:
        with open(path, 'w') as f: f.write(str(data))
        return True
    except: return False

def file_read(path):
    try:
        with open(path, 'r') as f: return f.read()
    except: return ""

WEAPONS.update({
    'file_write': file_write,
    'file_read': file_read,
    'input': user_input,
    'str': str,
    'int': int,
    'float': float,
    'len': len,
    'hash_sha256': lambda s: hashlib.sha256(str(s).encode()).hexdigest(),
    'hash_md5': lambda s: hashlib.md5(str(s).encode()).hexdigest(),
    'base64_encode': lambda s: base64.b64encode(str(s).encode()).decode(),
    'base64_decode': lambda s: base64.b64decode(str(s).encode()).decode(),
})

# ============================
# CROSS-LANGUAGE CALL ENGINE
# ============================

def call_lang(lang, *args):
    lang = lang.lower()
    try:
        if lang == 'python':
            module_name, func_name, *fargs = args
            module = __import__(module_name)
            func = getattr(module, func_name)
            return func(*fargs)
        elif lang == 'c':
            lib_path, func_name, *fargs = args
            lib = ctypes.CDLL(lib_path)
            func = getattr(lib, func_name)
            return func(*fargs)
        elif lang == 'rust':
            # Rust compiled as PyO3 module
            mod_name, func_name, *fargs = args
            mod = __import__(mod_name)
            return getattr(mod, func_name)(*fargs)
        elif lang == 'go':
            binary, *bargs = args
            cmd = [binary] + [str(a) for a in bargs]
            return subprocess.check_output(cmd).decode()
        elif lang == 'java':
            jar, *jargs = args
            cmd = ['java', '-jar', jar] + [str(a) for a in jargs]
            return subprocess.check_output(cmd).decode()
        else:
            return f"[call_lang Error] Unsupported language {lang}"
    except Exception as e:
        return f"[call_lang Error] {e}"

WEAPONS['call_lang'] = call_lang

# ============================
# VALKYRIE INTERPRETER
# ============================

class Valkyrie:
    def __init__(self):
        self.vars = {}
        self.funcs = {}
        self.labels = {}
        self.lines = []
        self.pc = 0
        self.halted = False
        self.stack = []
        self.ret_val = None
        self.returning = False

    def evaluate(self, expr):
        expr = expr.strip()
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        if expr == '_result': return self.vars.get('_result', '')
        if expr in self.vars: return self.vars[expr]
        if expr == 'true': return True
        if expr == 'false': return False
        if expr == 'None': return None

        # Binary ops
        for op in ['+', '-', '*', '/', '==', '!=', '<=', '>=', '<', '>']:
            if op in expr:
                left, right = expr.split(op,1)
                left = self.evaluate(left.strip())
                right = self.evaluate(right.strip())
                return eval(f'left {op} right')

        # Function call
        if '(' in expr and expr.endswith(')'):
            name = expr[:expr.index('(')]
            args_str = expr[expr.index('(')+1:-1]
            args = [self.evaluate(a.strip()) for a in args_str.split(',')] if args_str else []
            if name in WEAPONS: return WEAPONS[name](*args)
            if name in self.funcs:
                func = self.funcs[name]
                old_vars = self.vars.copy()
                for i,p in enumerate(func['params']):
                    self.vars[p] = args[i] if i < len(args) else None
                self.returning=False
                for line in func['body']:
                    if self.halted or self.returning: break
                    self.execute_line(line)
                res = self.ret_val if self.returning else None
                self.vars = old_vars
                self.returning=False
                return res

        try:
            if '.' in expr: return float(expr)
            return int(expr)
        except: return expr

    def execute_line(self, line):
        if not line or line.startswith('#'): return
        if line.startswith('print '):
            color_print(str(self.evaluate(line[6:])), 'green')
        elif line.startswith('let '):
            var,val = line[4:].split('=',1)
            self.vars[var.strip()] = self.evaluate(val.strip())
        elif line.startswith('add '):
            var,val = line[4:].split(None,1)
            self.vars[var]=self.vars.get(var,0)+self.evaluate(val)
        elif line.startswith('sub '):
            var,val = line[4:].split(None,1)
            self.vars[var]=self.vars.get(var,0)-self.evaluate(val)
        elif line.startswith('mul '):
            var,val = line[4:].split(None,1)
            self.vars[var]=self.vars.get(var,0)*self.evaluate(val)
        elif line.startswith('div '):
            var,val = line[4:].split(None,1)
            self.vars[var]=self.vars.get(var,0)/self.evaluate(val)
        elif line.startswith('if '):
            cond=line[3:].strip()
            if self.evaluate(cond): pass
        elif line.startswith('while '):
            cond=line[6:].strip()
            start=self.pc-1
            while self.evaluate(cond):
                self.pc=start+1
                while self.pc<len(self.lines) and not self.halted:
                    self.execute_line(self.lines[self.pc])
                    self.pc+=1
        elif line.startswith('call '):
            parts=line[5:].split(); name=parts[0]; args=[self.evaluate(p) for p in parts[1:]]
            if name in WEAPONS: self.vars['_result']=WEAPONS[name](*args)
        elif line.startswith('return '):
            self.ret_val=self.evaluate(line[7:]); self.returning=True
        elif line.startswith('push '):
            self.stack.append(self.evaluate(line[5:]))
        elif line.startswith('pop '):
            var=line[4:].strip(); self.vars[var]=self.stack.pop() if self.stack else None
        elif line.startswith('hlt'):
            self.halted=True

    def run(self, source):
        self.lines=[]
        self.labels={}
        in_func=False; current_func=None; func_lines=[]
        for raw in source.split('\n'):
            line=raw.strip()
            if not line or line.startswith('#'): continue
            if in_func:
                if line=='endfn': self.funcs[current_func]['body']=func_lines.copy(); in_func=False; current_func=None; func_lines=[]; continue
                func_lines.append(line); continue
            if line.endswith(':'): self.labels[line[:-1]]=len(self.lines); continue
            if line.startswith('fn '): parts=line[3:].split();
                if parts: current_func=parts[0]; params=parts[1:] if len(parts)>1 else [];
                self.funcs[current_func]={'params':params,'body':[]}; in_func=True; continue
            self.lines.append(line)
        self.pc=0
        while self.pc<len(self.lines) and not self.halted:
            line=self.lines[self.pc]; self.pc+=1
            try: self.execute_line(line)
            except Exception as e: color_print(f"[Execution Error] {e}",'blue')

# ============================
# MAIN
# ============================

def main():
    if len(sys.argv)<2:
        color_print("Usage: python valkyrie.py script.vk",'yellow')
        return
    with open(sys.argv[1],'r') as f: source=f.read()
    vk=Valkyrie()
    vk.run(source)

if __name__=='__main__':
    main()

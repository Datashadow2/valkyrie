#!/usr/bin/env python3
"""
VALKYRIE 4.0 - FINAL WORKING VERSION WITH COLORS
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

# ============================================================
# WEAPONS
# ============================================================

def file_write(path, data):
    try:
        with open(path, 'w') as f:
            f.write(str(data))
        return True
    except:
        return False

def file_read(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return ""

def file_exists(path):
    return os.path.exists(path)

def file_listdir(path):
    try:
        return os.listdir(path)
    except:
        return []

def sha256(s):
    return hashlib.sha256(str(s).encode()).hexdigest()

def md5(s):
    return hashlib.md5(str(s).encode()).hexdigest()

def base64_encode(s):
    return base64.b64encode(str(s).encode()).decode()

def base64_decode(s):
    return base64.b64decode(s).decode()

def sleep(sec):
    import time
    time.sleep(sec)
    return sec

def now():
    return datetime.now()

def http_get(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.read().decode()
    except:
        return ""

def json_parse(s):
    try:
        if isinstance(s, str):
            s = s.strip()
            if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
                s = s[1:-1]
        return json.loads(s)
    except:
        return {}

def json_stringify(obj):
    try:
        return json.dumps(obj)
    except:
        return ""

def inject(pid, shellcode):
    print(f"[Injection] PID: {pid}, Size: {len(shellcode)}")
    return True

def beacon(url):
    class B:
        def __init__(self, u): self.u = u
        def send(self, d):
            try:
                req = urllib.request.Request(self.u, data=json.dumps(d).encode())
                with urllib.request.urlopen(req, timeout=5) as r:
                    return r.read().decode()
            except:
                return None
    return B(url)

def persist(path):
    try:
        with open('/tmp/cron', 'w') as f:
            f.write(f"@reboot {path}\n")
        subprocess.run(['crontab', '/tmp/cron'])
        return True
    except:
        return False

def anti_debug():
    import time
    start = time.perf_counter()
    time.sleep(0.001)
    if time.perf_counter() - start > 0.1:
        sys.exit(1)
    return True

def evolve(code, n=3):
    for _ in range(n):
        code += "\n# Evolved\n"
    return code

def polymorphic_mutate(code):
    lines = code.split('\n')
    lines.insert(random.randint(0, len(lines)), "# Gen " + secrets.token_hex(4))
    return '\n'.join(lines)

# ============================================================
# TEXT EFFECTS & COLOR
# ============================================================

def color_print(text, color="default"):
    colors = {
        "default": "\033[39m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bold": "\033[1m",
        "underline": "\033[4m",
        "reverse": "\033[7m",
    }
    c = colors.get(color.lower(), colors["default"])
    reset = "\033[0m"
    print(f"{c}{text}{reset}")
    return text

def rainbow_text(text):
    rainbow = ["\033[31m", "\033[33m", "\033[32m", "\033[36m", "\033[34m", "\033[35m"]
    reset = "\033[0m"
    result = ""
    for i, ch in enumerate(text):
        result += rainbow[i % len(rainbow)] + ch
    print(result + reset)
    return text

# ============================================================
# WEAPONS DICTIONARY
# ============================================================

WEAPONS = {
    'file_write': file_write,
    'file_read': file_read,
    'file_exists': file_exists,
    'file_listdir': file_listdir,
    'sha256': sha256,
    'md5': md5,
    'base64_encode': base64_encode,
    'base64_decode': base64_decode,
    'sleep': sleep,
    'now': now,
    'http_get': http_get,
    'json_parse': json_parse,
    'json_stringify': json_stringify,
    'inject': inject,
    'beacon': beacon,
    'persist': persist,
    'anti_debug': anti_debug,
    'evolve': evolve,
    'polymorphic_mutate': polymorphic_mutate,
    'color_print': color_print,
    'rainbow_text': rainbow_text,
}

# ============================================================
# INTERPRETER
# ============================================================

class Valkyrie:
    def __init__(self):
        self.vars = {}
        self.funcs = {}
        self.labels = {}
        self.stack = []
        self.lines = []
        self.pc = 0
        self.halted = False
        self.returning = False
        self.ret_val = None
    
    def evaluate(self, expr):
        expr = expr.strip()
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except:
            pass
        if expr in self.vars:
            return self.vars[expr]
        if expr == 'true': return True
        if expr == 'false': return False
        if expr == 'None': return None
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
            if name in self.funcs:
                func = self.funcs[name]
                old_vars = self.vars.copy()
                for i, p in enumerate(func['params']):
                    self.vars[p] = args[i]
                self.returning = False
                for line in func['body']:
                    if self.halted or self.returning: break
                    self.execute_line(line)
                result = self.ret_val if self.returning else None
                self.vars = old_vars
                self.returning = False
                return result
        return expr
    
    def execute_line(self, line):
        if not line or line.startswith('#'): return
        if line.startswith('print '):
            print(self.evaluate(line[6:]))
        elif line.startswith('let '):
            var, val = line[4:].split('=', 1)
            self.vars[var.strip()] = self.evaluate(val.strip())
        elif line.startswith('if ') and ' then ' in line:
            cond, then = line[3:].split(' then ', 1)
            if self.evaluate(cond.strip()): self.execute_line(then.strip())
        elif line.startswith('goto '):
            label = line[5:].strip()
            if label in self.labels: self.pc = self.labels[label]
        elif line.startswith('return '):
            self.ret_val = self.evaluate(line[7:])
            self.returning = True
        elif line.startswith('add '):
            var, val = line[4:].split(None,1)
            self.vars[var] = self.vars.get(var,0)+self.evaluate(val)
        elif line.startswith('sub '):
            var, val = line[4:].split(None,1)
            self.vars[var] = self.vars.get(var,0)-self.evaluate(val)
        elif line.startswith('mul '):
            var, val = line[4:].split(None,1)
            self.vars[var] = self.vars.get(var,0)*self.evaluate(val)
        elif line.startswith('div '):
            var, val = line[4:].split(None,1)
            v = self.evaluate(val)
            if v != 0: self.vars[var] = self.vars.get(var,0)/v
        elif line.startswith('push '): self.stack.append(self.evaluate(line[5:]))
        elif line.startswith('pop '):
            var = line[4:].strip()
            if self.stack: self.vars[var] = self.stack.pop()
        elif line.startswith('call '):
            parts = line[5:].split()
            if not parts: return
            name, args = parts[0], []
            i = 1
            while i < len(parts):
                arg = parts[i]
                if arg.startswith('"') and not arg.endswith('"'):
                    full_arg = arg
                    i += 1
                    while i < len(parts) and not full_arg.endswith('"'):
                        full_arg += ' ' + parts[i]
                        i += 1
                    args.append(self.evaluate(full_arg))
                else:
                    args.append(self.evaluate(arg))
                    i += 1
            if name in WEAPONS: self.vars['_result'] = WEAPONS[name](*args)
            elif name in self.funcs:
                func = self.funcs[name]
                old_vars = self.vars.copy()
                for i,p in enumerate(func['params']): self.vars[p]=args[i]
                self.returning=False
                for l in func['body']:
                    if self.halted or self.returning: break
                    self.execute_line(l)
                self.vars = old_vars
                self.vars['_result'] = self.ret_val if self.returning else None
                self.returning=False
        elif line.startswith('hlt'): self.halted = True

    def run(self, source):
        raw_lines = source.split('\n')
        self.lines, self.labels = [], {}
        in_func, current_func, func_lines = False, None, []
        for raw in raw_lines:
            line = raw.strip()
            if not line or line.startswith('#'): continue
            if in_func:
                if line=='endfn':
                    if current_func: self.funcs[current_func]['body']=func_lines.copy()
                    in_func,current_func,func_lines=False,None,[]
                    continue
                else: func_lines.append(line); continue
            if line.endswith(':'): self.labels[line[:-1].strip()]=len(self.lines); continue
            if line.startswith('fn '):
                parts = line[3:].split()
                if parts: name = parts[0]; params = parts[1:] if len(parts)>1 else []
                self.funcs[name] = {'params': params,'body':[]}
                in_func,current_func=True,name; continue
            self.lines.append(line)
        self.pc=0
        while self.pc<len(self.lines) and not self.halted:
            line=self.lines[self.pc]; self.pc+=1
            try: self.execute_line(line)
            except Exception as e: print(f"Error: {e}"); break

# ============================================================
# MAIN
# ============================================================

def main():
    if len(sys.argv)<2:
        print("Valkyrie - Systems Language\nUsage: python valkyrie.py script.vk")
        return
    with open(sys.argv[1],'r') as f: source=f.read()
    vk=Valkyrie(); vk.run(source)

if __name__=="__main__":
    main()

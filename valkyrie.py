#!/usr/bin/env python3
"""
VALKYRIE - Complete Systems Language Interpreter
Final Version
"""

import sys, os, random, secrets, hashlib, subprocess, json, base64, urllib.request, time
from datetime import datetime

# ==========================
# COLOR PRINTING
# ==========================

COLORS = {
    "default":"\033[39m","red":"\033[31m","green":"\033[32m","yellow":"\033[33m",
    "blue":"\033[34m","magenta":"\033[35m","cyan":"\033[36m","white":"\033[37m",
    "bold":"\033[1m","underline":"\033[4m","reverse":"\033[7m"
}

def cprint(text, color="default", end="\n"):
    print(f"{COLORS.get(color,'')}{text}\033[0m", end=end)

def input_red(prompt=""):
    cprint(prompt, "red", end="")
    return input()

def error_blue(text):
    cprint(text, "blue")

def output_green(text):
    cprint(text, "green")

# ==========================
# WEAPONS (Built-ins)
# ==========================

def file_write(path, data):
    try:
        with open(path,"w") as f: f.write(str(data))
        return True
    except: return False

def file_read(path):
    try: return open(path).read()
    except: return ""

def file_exists(path): return os.path.exists(path)
def file_listdir(path): return os.listdir(path) if os.path.exists(path) else []
def sha256(s): return hashlib.sha256(str(s).encode()).hexdigest()
def md5(s): return hashlib.md5(str(s).encode()).hexdigest()
def base64_encode(s): return base64.b64encode(str(s).encode()).decode()
def base64_decode(s): return base64.b64decode(str(s).encode()).decode()
def sleep(sec): time.sleep(float(sec)); return sec
def now(): return datetime.now()
def http_get(url):
    try: return urllib.request.urlopen(url, timeout=10).read().decode()
    except: return ""
def json_parse(s):
    try: return json.loads(s)
    except: return {}
def json_stringify(obj):
    try: return json.dumps(obj)
    except: return ""
def evolve(code,n=3): return code + "\n# Evolved\n"*n
def polymorphic_mutate(code):
    lines=code.split("\n")
    lines.insert(random.randint(0,len(lines)),"#Gen "+secrets.token_hex(4))
    return "\n".join(lines)
def str_convert(x): return str(x)
def user_input(prompt=""): return input_red(prompt)

# Cross-language call
def call_lang(language,module,func,*args):
    try:
        if language.lower()=="python":
            mod=__import__(module)
            f=getattr(mod,func)
            return f(*args)
        elif language.lower()=="c":
            import ctypes
            lib=ctypes.CDLL(module)
            f=getattr(lib,func)
            return f(*args)
        elif language.lower()=="rust":
            mod=__import__(module)
            f=getattr(mod,func)
            return f(*args)
        elif language.lower()=="go":
            import subprocess
            res=subprocess.run(["./"+module]+list(map(str,args)), capture_output=True)
            return res.stdout.decode()
        elif language.lower()=="java":
            import subprocess
            res=subprocess.run(["java","-jar",module]+list(map(str,args)), capture_output=True)
            return res.stdout.decode()
        else:
            return None
    except Exception as e:
        error_blue(f"[call_lang Error] {e}")
        return None

# WEAPONS dictionary
WEAPONS = {
    "file_write":file_write,"file_read":file_read,"file_exists":file_exists,"file_listdir":file_listdir,
    "sha256":sha256,"md5":md5,"base64_encode":base64_encode,"base64_decode":base64_decode,
    "sleep":sleep,"now":now,"http_get":http_get,"json_parse":json_parse,"json_stringify":json_stringify,
    "evolve":evolve,"polymorphic_mutate":polymorphic_mutate,"str":str_convert,
    "input":user_input,"call_lang":call_lang
}

# ==========================
# INTERPRETER
# ==========================

class Valkyrie:
    def __init__(self):
        self.vars={}
        self.funcs={}
        self.labels={}
        self.stack=[]
        self.lines=[]
        self.pc=0
        self.halted=False
        self.ret_val=None
        self.returning=False

    def evaluate(self,expr):
        expr=str(expr).strip()
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        if expr in self.vars: return self.vars[expr]
        if expr=="_result": return self.vars.get("_result","")
        if expr=="true": return True
        if expr=="false": return False
        if expr=="None": return None
        # Numbers
        try:
            if '.' in expr: return float(expr)
            return int(expr)
        except: pass
        # Operators (simple parser)
        for op in ['+','-','*','/','==','!=','<=','>=','<','>']:
            if op in expr:
                left,right=expr.split(op,1)
                left=self.evaluate(left.strip())
                right=self.evaluate(right.strip())
                if op=="+": return left+right
                if op=="-": return left-right
                if op=="*": return left*right
                if op=="/": return left/right if right!=0 else None
                if op=="==": return left==right
                if op=="!=": return left!=right
                if op==">=": return left>=right
                if op=="<=": return left<=right
                if op==">": return left>right
                if op=="<": return left<right
        # Function call
        if '(' in expr and expr.endswith(')'):
            name=expr[:expr.index('(')]
            args_str=expr[expr.index('(')+1:-1]
            args=[self.evaluate(a.strip()) for a in args_str.split(',')] if args_str else []
            if name in WEAPONS: return WEAPONS[name](*args)
            if name in self.funcs:
                func=self.funcs[name]
                old=self.vars.copy()
                for i,p in enumerate(func['params']):
                    self.vars[p]=args[i] if i<len(args) else None
                self.returning=False
                for l in func['body']:
                    if self.halted or self.returning: break
                    self.execute_line(l)
                res=self.ret_val if self.returning else None
                self.vars=old
                self.returning=False
                return res
        return expr

    def execute_line(self,line):
        line=line.strip()
        if not line or line.startswith("#"): return
        try:
            # PRINT
            if line.startswith("print "):
                val=self.evaluate(line[6:])
                output_green(str(val))
            # LET
            elif line.startswith("let "):
                var,val=line[4:].split("=",1)
                self.vars[var.strip()]=self.evaluate(val.strip())
            # ADD/SUB/MUL/DIV
            elif any(line.startswith(k+" " ) for k in ["add","sub","mul","div"]):
                cmd,var,val=line.split(" ",2)
                val=self.evaluate(val)
                if cmd=="add": self.vars[var]=self.vars.get(var,0)+val
                if cmd=="sub": self.vars[var]=self.vars.get(var,0)-val
                if cmd=="mul": self.vars[var]=self.vars.get(var,0)*val
                if cmd=="div": self.vars[var]=self.vars.get(var,0)/val if val!=0 else None
            # IF
            elif line.startswith("if "):
                cond=line[3:].strip()
                body=[]
                start=self.pc
                while self.pc<len(self.lines):
                    l=self.lines[self.pc]
                    self.pc+=1
                    if l.strip()=="endif": break
                    body.append(l)
                if self.evaluate(cond):
                    for l in body: self.execute_line(l)
            # WHILE
            elif line.startswith("while "):
                cond=line[6:].strip()
                start=self.pc
                body=[]
                while self.pc<len(self.lines):
                    l=self.lines[self.pc]
                    self.pc+=1
                    if l.strip()=="endwhile": break
                    body.append(l)
                while self.evaluate(cond):
                    temp_pc=self.pc
                    for l in body: self.execute_line(l)
                    self.pc=temp_pc
            # FOR var in list
            elif line.startswith("for "):
                parts=line[4:].split(" in ",1)
                var=parts[0].strip()
                lst=self.evaluate(parts[1].strip())
                body=[]
                while self.pc<len(self.lines):
                    l=self.lines[self.pc]
                    self.pc+=1
                    if l.strip()=="endfor": break
                    body.append(l)
                for x in lst:
                    self.vars[var]=x
                    for l in body: self.execute_line(l)
            # CALL
            elif line.startswith("call "):
                parts=line[5:].split()
                if not parts: return
                name=parts[0]
                args=[]
                i=1
                while i<len(parts):
                    arg=parts[i]
                    if arg.startswith('"') and not arg.endswith('"'):
                        full=arg
                        i+=1
                        while i<len(parts) and not full.endswith('"'):
                            full+=" "+parts[i]
                            i+=1
                        args.append(self.evaluate(full))
                    else:
                        args.append(self.evaluate(arg))
                        i+=1
                if name in WEAPONS: self.vars["_result"]=WEAPONS[name](*args)
                elif name in self.funcs:
                    func=self.funcs[name]
                    old=self.vars.copy()
                    for i,p in enumerate(func['params']):
                        self.vars[p]=args[i] if i<len(args) else None
                    self.returning=False
                    for l in func['body']:
                        if self.halted or self.returning: break
                        self.execute_line(l)
                    self.vars=old
                    self.vars["_result"]=self.ret_val if self.returning else None
                    self.returning=False
            # RETURN
            elif line.startswith("return "):
                self.ret_val=self.evaluate(line[7:])
                self.returning=True
            # PUSH/POP
            elif line.startswith("push "): self.stack.append(self.evaluate(line[5:]))
            elif line.startswith("pop "):
                var=line[4:].strip()
                if self.stack: self.vars[var]=self.stack.pop()
            # HLT
            elif line=="hlt": self.halted=True
        except Exception as e: error_blue(f"[Execution Error] {e}")

    def run(self,source):
        self.lines=[]
        self.labels={}
        self.funcs={}
        in_func=False
        func_name=None
        func_body=[]
        raw_lines=source.split("\n")
        for raw in raw_lines:
            line=raw.strip()
            if not line or line.startswith("#"): continue
            # FUNCTIONS
            if in_func:
                if line=="endfn":
                    self.funcs[func_name]["body"]=func_body.copy()
                    in_func=False
                    func_name=None
                    func_body=[]
                else: func_body.append(line)
                continue
            if line.startswith("fn "):
                parts=line[3:].split()
                if parts:
                    func_name=parts[0]
                    params=parts[1:] if len(parts)>1 else []
                    self.funcs[func_name]={"params":params,"body":[]}
                    in_func=True
                continue
            # LABELS
            if line.endswith(":"):
                self.labels[line[:-1].strip()]=len(self.lines)
                continue
            self.lines.append(line)
        # Execute
        self.pc=0
        while self.pc<len(self.lines) and not self.halted:
            line=self.lines[self.pc]
            self.pc+=1
            self.execute_line(line)

def main():
    if len(sys.argv)<2:
        output_green("Valkyrie - Systems Language\nUsage: python valkyrie.py script.vk")
        return
    with open(sys.argv[1],"r") as f: src=f.read()
    vk=Valkyrie()
    vk.run(src)

if __name__=="__main__":
    main()

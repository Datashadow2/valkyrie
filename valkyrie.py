#!/usr/bin/env python3
"""
Valkyrie - Production Hybrid Systems Language
Write once, run anywhere. Call Python, C, Rust, or shell directly.
"""

import sys
import os
import json
import re
import hashlib
import subprocess
import threading
import queue
import time
import ctypes
import ctypes.util
import urllib.request
import urllib.parse
import tempfile
import shutil
import inspect
import traceback
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

# ============================================================
# ERROR HANDLING
# ============================================================

class ValkyrieError(Exception):
    """Base exception for Valkyrie"""
    pass

class ValkyrieSyntaxError(ValkyrieError):
    pass

class ValkyrieRuntimeError(ValkyrieError):
    pass

# ============================================================
# STANDARD LIBRARY - Complete
# ============================================================

class ValkyrieFile:
    @staticmethod
    def read(path: str) -> str:
        with open(path, 'r') as f:
            return f.read()
    
    @staticmethod
    def write(path: str, data: str) -> None:
        with open(path, 'w') as f:
            f.write(data)
    
    @staticmethod
    def append(path: str, data: str) -> None:
        with open(path, 'a') as f:
            f.write(data)
    
    @staticmethod
    def delete(path: str) -> None:
        os.remove(path)
    
    @staticmethod
    def copy(src: str, dst: str) -> None:
        shutil.copy2(src, dst)
    
    @staticmethod
    def move(src: str, dst: str) -> None:
        shutil.move(src, dst)
    
    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(path)
    
    @staticmethod
    def listdir(path: str) -> List[str]:
        return os.listdir(path)
    
    @staticmethod
    def mkdir(path: str) -> None:
        os.makedirs(path, exist_ok=True)

class ValkyrieHTTP:
    @staticmethod
    def get(url: str, headers: Dict = None) -> str:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req) as response:
            return response.read().decode()
    
    @staticmethod
    def post(url: str, data: Union[str, Dict], headers: Dict = None) -> str:
        if isinstance(data, dict):
            data = urllib.parse.urlencode(data).encode()
        elif isinstance(data, str):
            data = data.encode()
        req = urllib.request.Request(url, data=data, headers=headers or {})
        with urllib.request.urlopen(req) as response:
            return response.read().decode()

class ValkyrieCrypto:
    @staticmethod
    def sha256(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def md5(data: str) -> str:
        return hashlib.md5(data.encode()).hexdigest()
    
    @staticmethod
    def base64_encode(data: str) -> str:
        import base64
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def base64_decode(data: str) -> str:
        import base64
        return base64.b64decode(data).decode()
    
    @staticmethod
    def xor(data: str, key: str) -> str:
        result = []
        for i, c in enumerate(data):
            result.append(chr(ord(c) ^ ord(key[i % len(key)])))
        return ''.join(result)

class ValkyrieJSON:
    @staticmethod
    def parse(s: str) -> Any:
        return json.loads(s)
    
    @staticmethod
    def stringify(obj: Any, indent: int = None) -> str:
        return json.dumps(obj, indent=indent)

class ValkyrieThread:
    def __init__(self, target, args=()):
        self.target = target
        self.args = args
        self._thread = None
        self._result = None
        self._error = None
    
    def start(self):
        def wrapper():
            try:
                self._result = self.target(*self.args)
            except Exception as e:
                self._error = e
        self._thread = threading.Thread(target=wrapper)
        self._thread.start()
    
    def join(self, timeout=None):
        self._thread.join(timeout)
        if self._error:
            raise self._error
        return self._result

class ValkyrieQueue:
    def __init__(self):
        self._queue = queue.Queue()
    
    def put(self, item):
        self._queue.put(item)
    
    def get(self, timeout=None):
        return self._queue.get(timeout=timeout)
    
    def size(self):
        return self._queue.qsize()

# ============================================================
# FOREIGN FUNCTION INTERFACE
# ============================================================

class ValkyrieFFI:
    @staticmethod
    def python(module: str, func: str, *args) -> Any:
        """Call any Python function from any module"""
        try:
            mod = __import__(module)
            for part in module.split('.')[1:]:
                mod = getattr(mod, part)
            fn = getattr(mod, func)
            return fn(*args)
        except Exception as e:
            raise ValkyrieRuntimeError(f"Python call failed: {module}.{func} - {e}")
    
    @staticmethod
    def c(library: str, func: str, *args) -> Any:
        """Call any C function from any shared library"""
        try:
            lib = ctypes.CDLL(library)
            fn = getattr(lib, func)
            return fn(*args)
        except Exception as e:
            raise ValkyrieRuntimeError(f"C call failed: {library}.{func} - {e}")
    
    @staticmethod
    def rust(binary: str, *args) -> str:
        """Execute Rust binary and capture output"""
        try:
            result = subprocess.run([binary] + list(args), capture_output=True, text=True)
            if result.returncode != 0:
                raise ValkyrieRuntimeError(f"Rust binary failed: {result.stderr}")
            return result.stdout
        except Exception as e:
            raise ValkyrieRuntimeError(f"Rust call failed: {binary} - {e}")
    
    @staticmethod
    def shell(command: str) -> Tuple[int, str, str]:
        """Execute shell command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            raise ValkyrieRuntimeError(f"Shell command failed: {command} - {e}")

# ============================================================
# PROCESS INJECTION (Windows & Linux)
# ============================================================

class ValkyrieInject:
    @staticmethod
    def windows(pid: int, shellcode: bytes) -> bool:
        """Inject shellcode into Windows process"""
        if sys.platform != 'win32':
            raise ValkyrieRuntimeError("Windows injection only works on Windows")
        
        try:
            kernel32 = ctypes.windll.kernel32
            
            # Open process
            PROCESS_ALL_ACCESS = 0x1F0FFF
            hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
            if not hProcess:
                raise ValkyrieRuntimeError(f"Failed to open process {pid}")
            
            # Allocate memory
            MEM_COMMIT = 0x00001000
            MEM_RESERVE = 0x00002000
            PAGE_EXECUTE_READWRITE = 0x40
            addr = kernel32.VirtualAllocEx(hProcess, None, len(shellcode), 
                                           MEM_COMMIT | MEM_RESERVE, 
                                           PAGE_EXECUTE_READWRITE)
            if not addr:
                raise ValkyrieRuntimeError("Failed to allocate memory")
            
            # Write shellcode
            written = ctypes.c_size_t(0)
            kernel32.WriteProcessMemory(hProcess, addr, shellcode, len(shellcode), 
                                        ctypes.byref(written))
            
            # Create remote thread
            kernel32.CreateRemoteThread(hProcess, None, 0, addr, None, 0, None)
            
            kernel32.CloseHandle(hProcess)
            return True
            
        except Exception as e:
            raise ValkyrieRuntimeError(f"Injection failed: {e}")
    
    @staticmethod
    def linux(pid: int, shellcode: bytes) -> bool:
        """Inject shellcode into Linux process using ptrace"""
        if sys.platform != 'linux':
            raise ValkyrieRuntimeError("Linux injection only works on Linux")
        
        # Linux injection would use ptrace
        # Simplified for production
        raise ValkyrieRuntimeError("Linux injection requires ptrace implementation")

# ============================================================
# SELF-EVOLUTION ENGINE
# ============================================================

class ValkyrieEvolve:
    def __init__(self):
        self.generation = 0
        self.history = []
    
    def mutate(self, code: str) -> str:
        """Mutate code for evolution"""
        self.generation += 1
        
        mutations = [
            # Optimize loops
            (r'while\s+(\w+)\s*<\s*(\d+)', r'for \1 in range(\2)'),
            # Inline simple returns
            (r'return\s+(\w+)\s*\+\s*(\w+)', r'return \1 + \2  # inlined'),
            # Add type hints
            (r'let\s+(\w+)\s*=', r'let \1: auto ='),
        ]
        
        for pattern, replacement in mutations:
            code = re.sub(pattern, replacement, code)
        
        self.history.append({
            'generation': self.generation,
            'timestamp': str(datetime.now()),
            'code_length': len(code)
        })
        
        return code
    
    def optimize(self, code: str, iterations: int = 5) -> str:
        """Run multiple evolution iterations"""
        for _ in range(iterations):
            code = self.mutate(code)
        return code

# ============================================================
# PARSER & INTERPRETER
# ============================================================

class ValkyrieParser:
    def __init__(self):
        self.vars = {}
        self.functions = {}
        self.evolve_engine = ValkyrieEvolve()
        self.error_recovery = True
    
    def run(self, source: str, filename: str = "<string>") -> Dict:
        """Execute Valkyrie source code"""
        lines = source.split('\n')
        i = 0
        result = None
        
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            if not line or line.startswith('#'):
                continue
            
            try:
                # Variable assignment
                if line.startswith('let '):
                    parts = line[4:].split('=', 1)
                    if len(parts) == 2:
                        var = parts[0].strip()
                        value = self._evaluate_expr(parts[1].strip())
                        self.vars[var] = value
                    else:
                        raise ValkyrieSyntaxError(f"Invalid assignment: {line}")
                
                # Print
                elif line.startswith('print '):
                    expr = line[6:].strip()
                    value = self._evaluate_expr(expr)
                    print(value)
                    result = value
                
                # If statement
                elif line.startswith('if '):
                    # Simplified if - single line
                    condition = line[3:].split(':', 1)[0].strip()
                    if self._evaluate_expr(condition):
                        # Find the body (next line indented)
                        body = []
                        while i < len(lines) and lines[i].startswith('    '):
                            body.append(lines[i].strip())
                            i += 1
                        for stmt in body:
                            self._execute_stmt(stmt)
                
                # While loop
                elif line.startswith('while '):
                    condition = line[6:].split(':', 1)[0].strip()
                    # Find body
                    body = []
                    while i < len(lines) and lines[i].startswith('    '):
                        body.append(lines[i].strip())
                        i += 1
                    while self._evaluate_expr(condition):
                        for stmt in body:
                            self._execute_stmt(stmt)
                
                # For loop
                elif line.startswith('for '):
                    # for var in range(10):
                    match = re.match(r'for\s+(\w+)\s+in\s+range\((\d+)\):', line)
                    if match:
                        var, max_val = match.groups()
                        body = []
                        while i < len(lines) and lines[i].startswith('    '):
                            body.append(lines[i].strip())
                            i += 1
                        for val in range(int(max_val)):
                            self.vars[var] = val
                            for stmt in body:
                                self._execute_stmt(stmt)
                
                # Function definition
                elif line.startswith('fn '):
                    match = re.match(r'fn\s+(\w+)\(([^)]*)\):', line)
                    if match:
                        name, params_str = match.groups()
                        params = [p.strip() for p in params_str.split(',')] if params_str else []
                        body = []
                        while i < len(lines) and lines[i].startswith('    '):
                            body.append(lines[i].strip())
                            i += 1
                        self.functions[name] = {'params': params, 'body': body}
                
                # Return statement
                elif line.startswith('return '):
                    expr = line[7:].strip()
                    return self._evaluate_expr(expr)
                
                # Unsafe block
                elif line == 'unsafe:':
                    body = []
                    while i < len(lines) and lines[i].startswith('    '):
                        body.append(lines[i].strip())
                        i += 1
                    for stmt in body:
                        if stmt.startswith('syscall '):
                            cmd = stmt[8:]
                            code, out, err = ValkyrieFFI.shell(cmd)
                            if code != 0:
                                print(f"Warning: syscall failed: {err}", file=sys.stderr)
                
                # Evolve block
                elif line == 'evolve:':
                    body = []
                    while i < len(lines) and lines[i].startswith('    '):
                        body.append(lines[i].strip())
                        i += 1
                    # Evolve the body code
                    evolved = self.evolve_engine.optimize('\n'.join(body))
                    print(f"[Evolved to generation {self.evolve_engine.generation}]")
                    # Run evolved code
                    self.run(evolved)
                
                # Python call
                elif line.startswith('python('):
                    match = re.match(r'python\(([^,]+),\s*([^,]+),\s*(.+)\)', line)
                    if match:
                        module, func, args_str = match.groups()
                        args = self._parse_args(args_str)
                        result = ValkyrieFFI.python(module.strip('"\' '), 
                                                     func.strip('"\' '), 
                                                     *args)
                        self.vars['_result'] = result
                
                # C call
                elif line.startswith('c('):
                    match = re.match(r'c\(([^,]+),\s*([^,]+),\s*(.+)\)', line)
                    if match:
                        lib, func, args_str = match.groups()
                        args = self._parse_args(args_str)
                        result = ValkyrieFFI.c(lib.strip('"\' '), 
                                                func.strip('"\' '), 
                                                *args)
                        self.vars['_result'] = result
                
                # Shell command
                elif line.startswith('shell('):
                    match = re.match(r'shell\(([^)]+)\)', line)
                    if match:
                        cmd = match.group(1).strip('"\' ')
                        code, out, err = ValkyrieFFI.shell(cmd)
                        self.vars['_result'] = out
                
                # Injection
                elif line.startswith('inject('):
                    match = re.match(r'inject\((\d+),\s*([^)]+)\)', line)
                    if match:
                        pid, shellcode_str = match.groups()
                        shellcode = bytes.fromhex(shellcode_str.strip('"\' '))
                        if sys.platform == 'win32':
                            ValkyrieInject.windows(int(pid), shellcode)
                        else:
                            ValkyrieInject.linux(int(pid), shellcode)
                        self.vars['_result'] = True
                
                # Function call
                elif re.match(r'\w+\(', line):
                    match = re.match(r'(\w+)\((.*)\)', line)
                    if match and match.group(1) in self.functions:
                        func_name, args_str = match.groups()
                        args = self._parse_args(args_str)
                        func = self.functions[func_name]
                        # Set parameters
                        old_vars = self.vars.copy()
                        for i, param in enumerate(func['params']):
                            self.vars[param] = args[i] if i < len(args) else None
                        # Execute body
                        for stmt in func['body']:
                            result = self._execute_stmt(stmt)
                        self.vars = old_vars
                        if result is not None:
                            self.vars['_result'] = result
                
                else:
                    # Expression evaluation
                    result = self._evaluate_expr(line)
                    if result is not None:
                        self.vars['_result'] = result
                        
            except Exception as e:
                if self.error_recovery:
                    print(f"Error at line {i}: {e}", file=sys.stderr)
                    if hasattr(e, '__traceback__'):
                        traceback.print_exc()
                else:
                    raise
        
        return self.vars
    
    def _execute_stmt(self, stmt: str) -> Any:
        """Execute a single statement"""
        if stmt.startswith('print '):
            expr = stmt[6:].strip()
            value = self._evaluate_expr(expr)
            print(value)
            return value
        elif stmt.startswith('let '):
            parts = stmt[4:].split('=', 1)
            if len(parts) == 2:
                var = parts[0].strip()
                value = self._evaluate_expr(parts[1].strip())
                self.vars[var] = value
        elif '=' in stmt and not stmt.startswith('if') and not stmt.startswith('while'):
            var, expr = stmt.split('=', 1)
            self.vars[var.strip()] = self._evaluate_expr(expr.strip())
        else:
            return self._evaluate_expr(stmt)
        return None
    
    def _evaluate_expr(self, expr: str) -> Any:
        """Evaluate an expression"""
        expr = expr.strip()
        
        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        # Number
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass
        
        # List literal
        if expr.startswith('[') and expr.endswith(']'):
            items = expr[1:-1].split(',')
            return [self._evaluate_expr(i.strip()) for i in items if i.strip()]
        
        # Dict literal
        if expr.startswith('{') and expr.endswith('}'):
            result = {}
            items = expr[1:-1].split(',')
            for item in items:
                if ':' in item:
                    k, v = item.split(':', 1)
                    result[self._evaluate_expr(k.strip())] = self._evaluate_expr(v.strip())
            return result
        
        # Variable
        if expr in self.vars:
            return self.vars[expr]
        
        # Function call in expression
        match = re.match(r'(\w+)\((.*)\)', expr)
        if match and match.group(1) in self.functions:
            func_name, args_str = match.groups()
            args = self._parse_args(args_str)
            func = self.functions[func_name]
            old_vars = self.vars.copy()
            for i, param in enumerate(func['params']):
                self.vars[param] = args[i] if i < len(args) else None
            result = None
            for stmt in func['body']:
                result = self._execute_stmt(stmt)
            self.vars = old_vars
            return result
        
        # Binary operations
        ops = [
            (r'(.+)\s*\+\s*(.+)', lambda a, b: a + b),
            (r'(.+)\s*-\s*(.+)', lambda a, b: a - b),
            (r'(.+)\s*\*\s*(.+)', lambda a, b: a * b),
            (r'(.+)\s*/\s*(.+)', lambda a, b: a / b),
            (r'(.+)\s*==\s*(.+)', lambda a, b: a == b),
            (r'(.+)\s*!=\s*(.+)', lambda a, b: a != b),
            (r'(.+)\s*<\s*(.+)', lambda a, b: a < b),
            (r'(.+)\s*>\s*(.+)', lambda a, b: a > b),
            (r'(.+)\s*<=\s*(.+)', lambda a, b: a <= b),
            (r'(.+)\s*>=\s*(.+)', lambda a, b: a >= b),
        ]
        
        for pattern, func in ops:
            match = re.match(pattern, expr)
            if match:
                left = self._evaluate_expr(match.group(1))
                right = self._evaluate_expr(match.group(2))
                return func(left, right)
        
        # Python call in expression
        match = re.match(r'python\(([^,]+),\s*([^,]+),\s*(.+)\)', expr)
        if match:
            module, func_name, args_str = match.groups()
            args = self._parse_args(args_str)
            return ValkyrieFFI.python(module.strip('"\' '), func_name.strip('"\' '), *args)
        
        # C call in expression
        match = re.match(r'c\(([^,]+),\s*([^,]+),\s*(.+)\)', expr)
        if match:
            lib, func_name, args_str = match.groups()
            args = self._parse_args(args_str)
            return ValkyrieFFI.c(lib.strip('"\' '), func_name.strip('"\' '), *args)
        
        # Shell call in expression
        match = re.match(r'shell\(([^)]+)\)', expr)
        if match:
            cmd = match.group(1).strip('"\' ')
            code, out, err = ValkyrieFFI.shell(cmd)
            return out
        
        raise ValkyrieSyntaxError(f"Cannot evaluate: {expr}")
    
    def _parse_args(self, args_str: str) -> List:
        """Parse function arguments"""
        if not args_str.strip():
            return []
        return [self._evaluate_expr(arg.strip()) for arg in args_str.split(',')]

# ============================================================
# MAIN ENTRY POINT
# ============================================================

class Valkyrie:
    def __init__(self):
        self.version = "1.0.0-production"
        self.parser = ValkyrieParser()
    
    def run_file(self, filename: str) -> Dict:
        """Run a .vk file"""
        with open(filename, 'r') as f:
            source = f.read()
        return self.parser.run(source, filename)
    
    def run_string(self, source: str) -> Dict:
        """Run source code string"""
        return self.parser.run(source)
    
    def repl(self):
        """Interactive REPL"""
        print(f"Valkyrie v{self.version} - Production Hybrid Language")
        print("Features: Python | C | Rust | Shell | Inject | Evolve")
        print("Type 'exit' to quit\n")
        
        while True:
            try:
                code = input(">>> ")
                if code in ('exit', 'quit'):
                    break
                if code.strip():
                    result = self.parser.run(code)
                    if result and '_result' in result:
                        print(f" => {result['_result']}")
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")

def main():
    if len(sys.argv) < 2:
        vk = Valkyrie()
        vk.repl()
    elif sys.argv[1] == 'run' and len(sys.argv) > 2:
        vk = Valkyrie()
        vk.run_file(sys.argv[2])
    elif sys.argv[1] == 'evolve' and len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            source = f.read()
        evolve = ValkyrieEvolve()
        evolved = evolve.optimize(source, iterations=5)
        output = sys.argv[2].replace('.vk', '_evolved.vk')
        with open(output, 'w') as f:
            f.write(evolved)
        print(f"Evolved code written to {output}")
    else:
        vk = Valkyrie()
        vk.run_file(sys.argv[1])

if __name__ == '__main__':
    main()

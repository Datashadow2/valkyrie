# valkyrie

**Write once. Run anywhere. Evolve on its own.**

Valkyrie is a multi-purpose systems programming language combining the simplicity of Python, the performance of C/Java, and the self-evolution capabilities of esoteric languages like Malbolge — designed for malware development, system design, and automation.

## Core Principles

- **Pythonic syntax** — readable, expressive, approachable
- **C/Java performance** — optional manual memory, JIT/AOT compilation, zero-cost abstractions
- **WORA (Write Once, Run Anywhere)** — portable bytecode + platform-specific VMs
- **Self-evolving code** — programs that optimize, mutate, and adapt at runtime
- **Unsafe mode** — direct syscalls, memory manipulation, process injection for exploit development

## Quick Example

```valkyrie
# High-level automation (Python style)
def deploy_servers():
    for ip in read_config("servers.txt"):
        ssh.connect(ip).run("systemctl restart nginx")

# Low-level exploit (C style, unsafe block)
unsafe:
    let shellcode = b"\x48\x31\xc0\x50..."
    let ptr = mmap(0x1000, PROT_EXEC | PROT_WRITE)
    memcpy(ptr, shellcode, len(shellcode))
    ((void(*)())ptr)()

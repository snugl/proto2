
from dataclasses import dataclass
from dataclasses import field

import subprocess

@dataclass
class Buffer:
    buffer : list[str] = field(default_factory=lambda: [
        "[bits 64]",
        "global _start",
        "section .text",
        "",
        "print:    ",
        "    mov rbp, rsp    ;frame construction",
        "",
        "    dec rsp             ;push",
        "    mov byte [rsp], 10  ;newline ",
        "",
        "    mov rdx, 1      ;length (+1 for newline)",
        "render_loop:",
        "    push rdx        ;save length",
        "",
        "    mov rdi, 10     ;divident",
        "    mov rdx, 0      ;has to be zero for some fucking reason",
        "    div rdi         ;divmod by 10",
        "    mov cl, dl      ;write mod to c register",
        "",
        "    pop rdx         ;restore length",
        "    inc rdx         ;inc length",
        "",
        "    add cl, '0'     ;compute ascii code",
        "    dec rsp         ;push",
        "    mov [rsp], cl   ;write code to stack",
        "",
        "    ;loop control",
        "    sub rax, 0      ",
        "    jnz render_loop",
        "    ",
        "    mov rax, 1      ;write to fd",
        "    mov rdi, 1      ;stdout",
        "    mov rsi, rsp    ;pointer into stack containing rendered number",
        "    syscall",
        "",
        "    mov rsp, rbp    ;frame teardown",
        "    ret",
        "",
        "_start:"
    ])

    def __call__(self, *comm):
        inst, *args_raw = comm
        args = map(str, args_raw)


        line = f"\t {inst} {', '.join(args)}"
        self.buffer.append(line)

    def render(self):
        return "\n".join(self.buffer)

    def assemble(self, path):
        with open('/tmp/output.asm', 'w') as f:
            f.write(self.render())

        subprocess.run(["nasm", "-o", "/tmp/output.o", "-f", "elf64", "/tmp/output.asm"])
        subprocess.run(["ld", "-o", path, "/tmp/output.o"])







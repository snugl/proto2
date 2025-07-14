
from dataclasses import dataclass
from dataclasses import field

import subprocess
import typing
import itertools

@dataclass
class Buffer:
    buffer : list[str] = field(default_factory=lambda: [
        "[bits 64]",
        "global _start",
        "section .data",
        "print_buffer:",
        "   times 31 db 0",
        "   db 10",
        "",
        "section .text",
		"print:",
		"       mov     rsi, 31",
		"       mov     rcx, 10",
		".L2:",
		"       test    rax, rax",
		"       je      .L5",
		"       cqo",
		"       dec     rsi",
		"       idiv    rcx",
		"       add     rdx, 48",
		"       mov     byte [print_buffer + rsi], dl",
		"       jmp     .L2",
		".L5:",
		"       mov     edx, 32",
		"       mov     edi, 1",
		"       sub     edx, esi",
		"       movsx   rsi, esi",
		"       movsx   rdx, edx",
		"       add     rsi, print_buffer",
		"		mov     rax, 1",
		"		syscall",
        "       ret",
        "",
        "_start:"
    ])

    label_generator : typing.Iterator = field(default_factory=lambda: itertools.count(0))

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

    def fresh_label(self):
        id = next(self.label_generator)
        return f't{id}'

    def def_label(self, name):
        self.buffer.append(f'{name}:')







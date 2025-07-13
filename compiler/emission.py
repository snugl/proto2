
from dataclasses import dataclass
from dataclasses import field


@dataclass
class Buffer:
    buffer : list[str] = field(default_factory=lambda: [
        "[bits 64]",
        "global _start",
        "section .text",
        "_start:"
    ])

    def __call__(self, *args):
        inst = "\t" + " ".join(args) + "\n"
        self.buffer.append(inst)



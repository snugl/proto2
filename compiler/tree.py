
from dataclasses import dataclass
from dataclasses import field
import typing
import itertools

import objs



@dataclass
class Node:
    subs   : list['Node']   = field(default_factory=lambda: [])
    locals : dict[str, int] = field(default_factory=lambda: {})

    var_allocer : typing.Iterator = field(default_factory=lambda: itertools.count())

    def alloc_var(self, name):
        if name not in self.locals:
            self.locals[name] = next(self.var_allocer)

    def infer(self):
        for sub in self.subs:
            if hasattr(sub, 'infer'):
                sub.infer(self)

    def generate(self, output):
        for sub in self.subs:
            sub.generate(output, self)


    @classmethod
    def parse(cls, stream, root=False):
        self = cls()

        if not root: stream.expect("{")

        while stream.has() and stream.peek() != "}":
            self.subs.append(objs.parse(stream))

        if not root: stream.expect("}")

        return self


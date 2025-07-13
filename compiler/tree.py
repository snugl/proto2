
from dataclasses import dataclass
from dataclasses import field

import objs



@dataclass
class Node:
    subs   : list['node']   = field(default_factory=lambda: [])
    locals : dict[str, int] = field(default_factory=lambda: {})



def parse(stream, root=False):
    self = Node()

    if root: stream.expect("{")

    while stream.has() and stream.peek() != "}":
        self.subs.append(objs.parse(stream))

    if root: stream.expect("}")


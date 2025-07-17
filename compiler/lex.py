
from dataclasses import dataclass
from dataclasses import field

import error



def get_kind(char):
    match(char):
        case x if x.isdigit():  return "numb"
        case x if x.isalpha():  return "iden"
        case ' ':               return "space"
        case '\n':              return "newline"
        case ';':               return "eos"
        case "'":               return "quote"
        case _:                 return "symb"

    

@dataclass
class Token:
    content : str
    line    : int
    path    : str
    kind    : str

    def __str__(self):
        return self.content


@dataclass
class Stream:
    token_buffer : list[Token] = field(default_factory=lambda: [])

    #in case something goes wrong, this token is responsible
    last_token : Token | None = None

    def append(self, token):
        self.token_buffer.append(token)

    def _pop(self):
        return self.token_buffer.pop(0)

    def pop(self) -> str:
        self.last_token = self._pop()
        return self.last_token.content

    def peek(self) -> str:
        return self.token_buffer[0].content

    def peek_raw(self):
        return self.token_buffer[0]

    def pop_raw(self):
        self.last_token = self._pop()
        return self.last_token

    def expect(self, content):
        token = self.pop()
        if content != token:
            error.path_line_error(
                self.last_token.path, 
                self.last_token.line, 
                f"Expected '{content}' but got '{token}'"
            )

    def has(self):
        return len(self.token_buffer) > 0

    def maybe(self, content):
        if self.peek() == content:
            self.pop()

    def __str__(self):
        return '\n'.join(list(map(str, self.token_buffer)))


def tokenize(path):
    with open(path) as f:
        source = f.read()

    stream = Stream()

    buffer = []
    line = 0
    kind_old = 'invalid'

    #modes
    string = False

    for char in source:
        kind_new = get_kind(char)

        if kind_old == 'quote': string = not string

        if char == '\n':
            line += 1

        if kind_new != kind_old and not string:
            token_content = "".join(buffer)
            buffer = []

            if kind_old not in ('invalid', 'space', 'newline'):
                stream.append(Token(
                    token_content, line, path, kind_old
                ))




        if kind_new != 'quote':
            buffer.append(char)
        kind_old = kind_new


    print(stream)
    return stream



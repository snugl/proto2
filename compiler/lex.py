
from dataclasses import dataclass
from dataclasses import field

import error



@dataclass
class token:
    content : str = ""
    line    : int = 0
    path    : str = ""
    kind    : str = ""

    def __str__(self):
        return self.content



def get_kind(char):
    match char:
        case '"':               return 'comment'
        case x if x.isdigit():  return 'numb'
        case x if x.isalpha():  return 'iden' 
        case ":"             :  return 'iden' #for scoping
        case "_"             :  return 'iden' #for naming
        case ';':               return 'eos'
        case ',':               return 'delim'
        case '\n':              return 'newline'
        case ' ':               return 'space'
        case "'":               return 'quote' #string delim
        case "(":               return 'open_paran'
        case ")":               return 'close_paran'
        case "{":               return 'open_scope'
        case "}":               return 'close_scope'
        case _:                 return 'symbol'


@dataclass
class stream:
    token_buffer : list[token]

    #in case something goes wrong, this token is responsible
    last_token : token = field(default_factory=token)

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
        token = self._pop()
        if content != str(token):
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

def tokenize(path):
    with open(path, "r") as f:
        raw = f.read()

    token_buffer = []
    buffer = []
    kind_old = None
    line = 1

    #modes
    comment  = False
    string   = False
    char_lit = False

    for char in raw:
        kind_new = get_kind(char)

        if kind_old == 'quote': string = not string

        if kind_new == 'comment': comment = True
        if kind_new == 'newline': comment = False
        if comment: continue

        if char_lit: kind_new = 'char_lit'
        if char_lit: char_lit = False
        if kind_new == 'backtick': char_lit = True


        if kind_new != kind_old and not string:
            token_content = "".join(buffer)
            buffer = []

            if kind_old not in ('space', 'newline', 'backtick', None):
                token_buffer.append(token(
                    token_content, line, path, kind_old
                ))

        if kind_new != 'quote':
            buffer.append(char)
        kind_old = kind_new
        if char == '\n': line += 1

    return stream(token_buffer)


#!/usr/bin/python3
import sys

import lex
import tree
import emission


def compile(path):
    stream = lex.tokenize(path)
    root = tree.Node.parse(stream, root=True)

    output = emission.Buffer()
    root.infer()

    print(root.locals)

    print(output.buffer)







def main():
    compile(sys.argv[1])

if __name__ == "__main__":
    main()

#!/usr/bin/python3
import sys

import lex
import tree
import emission


def compile(path):
    stream = lex.tokenize(path)
    ctx = tree.ctx.parse(stream)
    ctx.compile()

    print(ctx.render())








def main():
    compile(sys.argv[1])

if __name__ == "__main__":
    main()

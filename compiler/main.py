#!/usr/bin/python3
import sys

import lex
import tree


def compile(path):
    stream = lex.tokenize(path)
    root = tree.parse(stream)

    print(stream)







def main():
    compile(sys.argv[1])

if __name__ == "__main__":
    main()

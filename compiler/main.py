#!/usr/bin/python3
import sys

import lex


def compile(path):
    stream = lex.tokenize(path)
    print(stream)







def main():
    compile(sys.argv[1])

if __name__ == "__main__":
    main()

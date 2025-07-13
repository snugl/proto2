

run: build
	./main

build:
	./compiler/main.py prg/test.snug

push:
	git push
	git push local

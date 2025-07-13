

run: build
	./main

build:
	./compiler/main.py prg/main.snug

push:
	git push
	git push local

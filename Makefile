default: all

all: \
	$(patsubst %.g,%Lexer.py,$(wildcard *.g)) \
	$(patsubst %.g,%Parser.py,$(wildcard *.g))

%Lexer.py %Parser.py: %.g
	runantlr $<
	@touch $*Lexer.py $*Parser.py

test-aterm: atermLexer.py atermParser.py
	python test_aterm.py -v

test-asm: asmLexer.py asmParser.py
	$(foreach FILE, $(wildcard examples/ex*.s), \
		python asmLexer.py < examples/ex01.s; \
		python asmParser.py < examples/ex01.s; \
	)
test: \
	test-aterm \
	test-asm

doc:
	epydoc --css blue aterm.py

.PHONY: default all test doc

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
	$(foreach FILE, $(wildcard examples/*.s), \
		python asmLexer.py < $(FILE); \
		python asmParser.py < $(FILE); \
	)

test-ssl: sslLexer.py sslParser.py
	$(foreach FILE, $(wildcard examples/*.ssl), \
		python sslLexer.py < $(FILE); \
		python sslParser.py < $(FILE); \
	)
	
test: \
	test-aterm \
	test-asm

doc:
	epydoc --css blue aterm.py

.PHONY: default all test doc

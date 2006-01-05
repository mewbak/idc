
test: \
	test_aterm \
	test_asm

all: \
	$(patsubst %.g,%Lexer.py,$(wildcard *.g)) \
	$(patsubst %.g,%Parser.py,$(wildcard *.g))

%Lexer.py %Parser.py: %.g
	runantlr $<
	@touch $*Lexer.py $*Parser.py

test_asm: all
	python asmLexer.py < examples/ex01.s
	python asmParser.py < examples/ex01.s
	
test_aterm: all
	python $@.py -v

.PHONY: test
	

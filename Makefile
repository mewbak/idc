JAVA = java
ARCH = $(shell uname -m)

ANTLR_JAR = /usr/share/java/antlr.jar
#ANTLR = $(JAVA) -cp $(ANTLR_JAR) antlr.Tool
#ANTLR = runantlr
ANTLR = ./antlr.$(ARCH)

default: all

all:

test: \
	test-aterm \
	test-asm \
	test-ssl \
	test-tc

test-aterm: test_aterm.py atermLexer.py atermParser.py
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
	
test-tc: test_tc.py transformation.py
	python test_tc.py -v

doc:
	epydoc --css blue aterm.py

antlr: antlr.$(ARCH)

antlr.$(ARCH): $(ANTLR_JAR)
	gcj -O2 -o $@ --main=antlr.Tool $<

.PHONY: default all test doc antlr


%.py: %.t tc transformationLexer.py transformationParser.py transformationWalker.py
	python tc -o $@ $<


dependencies.mak: Makefile $(wildcard *.g)
	@for FILE in *.g; \
	do \
		sed -n -e "s/.*\bclass \(\w\+\) extends \w\+;.*/all: \1.py\n\1.py: $$FILE\n\t\$$(ANTLR) \$$<\n\t@touch \$$@\n/p" < $$FILE; \
	done > $@

include dependencies.mak

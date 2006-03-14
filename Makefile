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
		python asmLexer.py < $(FILE) > /dev/null; \
		python asmParser.py < $(FILE); \
	)

test-ssl: sslLexer.py sslParser.py
	$(foreach FILE, $(wildcard examples/*.ssl), \
		python sslLexer.py < $(FILE) > /dev/null; \
		python sslParser.py < $(FILE) > /dev/null; \
	)
	
test-wgen: test_wgen.py aterm.py walker.py
	python $< -v

test-box: test_box.py box.py aterm.py walker.py
	python $< -v

doc:
	epydoc \
		--css blue \
		aterm.py \
		walker.py \
		transformation.py

antlr: antlr.$(ARCH)

antlr.$(ARCH): $(ANTLR_JAR)
	gcj -O2 -o $@ --main=antlr.Tool $<

.PHONY: default all test doc antlr


%.py: %.w wgen wgenLexer.py wgenParser.py wgenWalker.py
	python wgen -o $@ $<


dependencies.mak: Makefile $(wildcard *.g)
	@for FILE in *.g; \
	do \
		sed -n -e "s/.*\bclass \(\w\+\) extends \w\+;.*/all: \1.py\n\1.py: $$FILE\n\t\$$(ANTLR) \$$<\n\t@touch \$$@\n/p" < $$FILE; \
	done > $@

include dependencies.mak

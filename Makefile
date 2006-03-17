# Makefile


# Configuration variables

PYTHON = python
JAVA = java
ANTLR_JAR = /usr/share/java/antlr.jar

# Use native code gcj-compiled ANTLR if possible, as it is much faster than
# Java byte code.
ARCH = $(shell uname -m)
ifneq ($(wildcard bin/antlr.$(ARCH)),)
ANTLR = bin/antlr.$(ARCH)
else
ANTLR = $(JAVA) -cp $(ANTLR_JAR) antlr.Tool
endif


# Main targets

default: all

all:

.PHONY: default all


# ANTLR parser generation

%Lexer.py %Parser.py %Walker.py: %.g
	$(ANTLR) $<
	@touch $@


# Compile ANTLR into native-code using gcj

bin:
	mkdir $@

antlr: bin/antlr.$(ARCH)

bin/antlr.$(ARCH): $(ANTLR_JAR) bin
	gcj -O2 -o $@ --main=antlr.Tool $<

.PHONY: antlr


# Aterm walker generation

all: $(patsubst %.w,%.py,$(wildcard *.w))
	
%.py: %.w wgen.py wgenLexer.py wgenParser.py wgenWalker.py
	$(PYTHON) wgen.py -o $@ $<


# Unit, component, and integration testing

test: \
	test_aterm \
	test_asm \
	test_ssl \
	test_wgen

test_aterm: test_aterm.py atermLexer.py atermParser.py

examples:
	$(MAKE) -C $@

.PHONY: examples
	
test_asm: test_asm.sh asmLexer.py asmParser.py examples

test_ssl: test_ssl.sh sslLexer.py sslParser.py sslPreprocessor.py
	
test_wgen: test_wgen.py aterm.py walker.py

test_box: test_box.py box.py aterm.py walker.py

test_%: test_%.py
	$(PYTHON) $< -v

test_%: test_%.sh
	$(SHELL) $<

.PHONY: test


# Generate reference documentation

doc: box.py
	rm -rf html
	epydoc \
		--css blue \
		aterm.py \
		walker.py \
		box.py \
		#transformation.py

.PHONY: doc


# Automated dependency generation

deps: .deps.mak

.deps.mak: Makefile $(wildcard *.g)
	@for FILE in *.g; \
	do \
		sed -n -e "s/.*\bclass \(\w\+\) extends \w\+;.*/all: \1.py\n\1.py: $$FILE\n\t\$$(ANTLR) \$$<\n\t@touch \$$@\n/p" < $$FILE; \
	done > $@

.PHONY: deps


# Make a tarball

dist: all doc
	tar -cjf ../idc.tar.bz2 \
		--exclude './bin' \
		--exclude '.*.sw?' \
		--exclude '.svn' \
		--exclude '*.pyc' \
		--exclude '*TokenTypes.txt' \
		.

.PHONY: dist


# Clean the generated files

clean:
	rm -f .deps.mak
	# FIXME: 

.PHONY: clean


# Include generated dependencies makefile

include .deps.mak

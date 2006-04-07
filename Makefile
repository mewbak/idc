# Makefile


# Configuration variables

PYTHON = python
export PYTHONPATH = .

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


VPATH=.:ssl

# Main targets

default: all

all:

.PHONY: default all


# ANTLR parser generation



# Compile ANTLR into native-code using gcj

bin:
	mkdir $@

antlr: bin/antlr.$(ARCH)

bin/antlr.$(ARCH): $(ANTLR_JAR) bin
	gcj -O2 -o $@ --main=antlr.Tool $<

.PHONY: antlr


# Aterm walker generation

all: $(patsubst %.w,%.py,$(shell find -iname '*.w'))
	
%.py: %.w util/wc/wc.py util/wc/lexer.py util/wc/parser.py util/wc/compiler.py
	$(PYTHON) util/wc/wc.py -o $@ $<


%.py: %.ssl util/sslc/sslc.py util/sslc/lexer.py util/sslc/parser.py util/sslc/preprocessor.py util/sslc/compiler.py
	$(PYTHON) util/sslc/sslc.py -o $@ $<


# Unit, component, and integration testing

tests: \
	test_aterm \
	test_wc \
	test_box \
	test_ir

test_aterm: tests/test_aterm.py aterm/lexer.py aterm/parser.py

examples:
	$(MAKE) -C $@

.PHONY: examples
	
test_asm: tests/test_asm.sh asmLexer.py asmParser.py ir.py box.py examples
	$(SHELL) $<

test_ssl: tests/test_ssl.sh sslLexer.py sslParser.py sslPreprocessor.py
	$(SHELL) $<
	
test_wc: tests/test_wc.py
	$(PYTHON) $< -v

test_box: tests/test_box.py box.py
	$(PYTHON) $< -v

test_ir: tests/test_ir.py ir.py
	$(PYTHON) $< -v

.PHONY: tests


# Generate reference documentation

doc: box.py
	rm -rf html
	epydoc \
		--css blue \
		aterm \
		walker.py \
		box.py

.PHONY: doc


# Automated dependency generation

deps: .deps.mak

.deps.mak: Makefile util/makedeps.pl $(shell find -iname '*.g')
	find -iname '*.g' | xargs perl util/makedeps.pl > $@

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
	@$(RM) .deps.mak $(patsubst %.w,%.py,$(shell find -iname '*.w'))

.PHONY: clean


# Include generated dependencies makefile

include .deps.mak

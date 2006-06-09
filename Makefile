# Makefile


# Configuration variables

PYTHON = python
export PYTHONPATH = .


# Use the native-compiled version of ANTLR if possible, as it is much faster than
# Java byte code.
ifneq ($(shell which cantlr),)
ANTLR = cantlr
else
ifneq ($(shell which runantlr),)
ANTLR = runantlr
else
JAVA = java
ANTLR_JAR = /usr/share/java/antlr.jar
ANTLR = $(JAVA) -cp $(ANTLR_JAR) antlr.Tool
endif
endif


# Main targets

default: all

all:

.PHONY: default all


# Aterm walker generation

all: $(patsubst %.w,%.py,$(shell find -iname '*.w'))
	
%.py: %.w util/wc/wc.py util/wc/lexer.py util/wc/parser.py util/wc/compiler.py
	$(PYTHON) util/wc/wc.py -o $@ $<

tests/test_wc.py: tests/test_wc.w


# SSL compilation

all: ssl/pentium.py

%.py: %.ssl util/sslc/sslc.py util/sslc/lexer.py util/sslc/parser.py util/sslc/preprocessor.py util/sslc/compiler.py
	$(PYTHON) util/sslc/sslc.py -o $@ $<


# Unit, component, and integration testing

TESTOPTS = -v

tests: \
	test-aterm \
	test-transf \
	test-path \
	test-walker \
	test-wc \
	test-box \
	test-ir \
	test-refactoring

test-%: all
	$(PYTHON) tests/test_$*.py $(TESTOPTS)

test-%: all
	$(PYTHON) $*/_tests.py $(TESTOPTS)

.PHONY: test-%

examples:
	$(MAKE) -C $@

.PHONY: examples
	
test-asm: tests/test_asm.sh asmLexer.py asmParser.py ir.py examples
	$(SHELL) $<
	
.PHONY: tests


# Generate reference documentation

doc: all
	rm -rf html
	epydoc \
		--css blue \
		--no-private \
		aterm \
		transf \
		path \
		walker \
		box \
		#ir \
		#ui

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

sweep:
	@$(RM) $(shell find -iname '*.py[oc]')

clean:
	@$(RM) .deps.mak $(patsubst %.w,%.py,$(shell find -iname '*.w'))

.PHONY: clean


# Include generated dependencies makefile

include .deps.mak

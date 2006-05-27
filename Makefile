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


# ANTLR parser generation



# Aterm walker generation

all: $(patsubst %.w,%.py,$(shell find -iname '*.w'))
	
%.py: %.w util/wc/wc.py util/wc/lexer.py util/wc/parser.py util/wc/compiler.py
	$(PYTHON) util/wc/wc.py -o $@ $<


%.py: %.ssl util/sslc/sslc.py util/sslc/lexer.py util/sslc/parser.py util/sslc/preprocessor.py util/sslc/compiler.py
	$(PYTHON) util/sslc/sslc.py -o $@ $<


# Unit, component, and integration testing

tests: \
	test_aterm \
	test_transformations \
	test_path \
	test_walker \
	test_wc \
	test_box \
	test_ir

test_aterm: tests/test_aterm.py aterm/lexer.py aterm/parser.py
	$(PYTHON) $< -v

test_transformations: tests/test_transformations.py
	$(PYTHON) $< -v

test_path: tests/test_path.py
	$(PYTHON) $< -v

test_walker: tests/test_walker.py
	$(PYTHON) $< -v

test_wc: tests/test_wc.py
	$(PYTHON) $< -v

test_box: tests/test_box.py box.py
	$(PYTHON) $< -v

test_ir: tests/test_ir.py all # ...
	$(PYTHON) $< -v

test_ssl: tests/test_ssl.py util/sslc/lexer.py util/sslc/parser.py util/sslc/preprocessor.py
	$(PYTHON) $< -v

test_refactoryings: $(filter-out $(wildcard refactoring/_*.py),$(wildcard refactoring/*.py))
# TODO: automate this from a python file
	$(foreach REFACTORING,$^,$(PYTHON) $(REFACTORING) -v ;)

examples:
	$(MAKE) -C $@

.PHONY: examples
	
test_asm: tests/test_asm.sh asmLexer.py asmParser.py ir.py box.py examples
	$(SHELL) $<
	
.PHONY: tests


# Generate reference documentation

doc: box.py
	rm -rf html
	epydoc \
		--css blue \
		aterm \
		transformations \
		path \
		walker \
		box \
		ir \
		ui

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

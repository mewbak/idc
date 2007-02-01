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


# SSL compilation

all: lang/ssl/spec/pentium.py

%.py: %.ssl util/sslc.py lang/ssl/lexer.py lang/ssl/parser.py lang/ssl/preprocessor.py lang/ssl/compiler.py
	$(PYTHON) util/sslc.py -o $@ $<


# Unit, component, and integration testing

TESTOPTS = -v

tests: \
	test-aterm \
	test-transf \
	test-box \
	test-ir \
	test-refactoring

test-%: all tests/test_%.py
	$(PYTHON) tests/test_$*.py $(TESTOPTS)

test-%: all %/_tests.py
	$(PYTHON) $*/_tests.py $(TESTOPTS)

test-%: all lang/%/_tests.py
	$(PYTHON) lang/$*/_tests.py $(TESTOPTS)

TestTransf.%: all
	$(PYTHON) transf/_tests.py $*


.PHONY: test-% tests


# Examples

examples:
	$(MAKE) -C $@

.PHONY: examples


# Generate reference documentation

#EPYDOC = epydoc
EPYDOC = ../utils/bin/epydoc

doc: all
	rm -rf doc/html
	$(EPYDOC) -v \
		--css blue \
		--no-private \
		--no-sourcecode \
		-o doc/html \
		aterm \
		transf \
		lang \
		ui \
		#ir

.PHONY: doc


# Run pylint

pylint:
	pylint --rcfile=pylintrc aterm transf

.PHONY: pylint


# Automated dependency generation

deps: .deps.mak

.deps.mak: Makefile util/makedeps.pl $(shell find -iname '*.g')
	find -iname '*.g' | xargs perl util/makedeps.pl > $@

.PHONY: deps


# Make a tarball

dist: zip

tarball: all
	rm -f ../idc.tar.bz2
	tar -cjf ../idc.tar.bz2 \
		--exclude '.*.sw?' \
		--exclude '.svn' \
		--exclude '*.pyc' \
		--exclude 'doc' \
		.

zip: all
	rm -f ../idc.zip
	zip -r ../idc.zip . \
		-x '.*' \
		-x '*/.svn/*' \
		-x '*.pyc' \
		-x 'doc/*'

.PHONY: dist


# Clean the generated files

sweep:
	-$(RM) $(shell find -iname '*.py[oc]' -or -iname '*.prof' -or -iname '*.log')

clean:
	-$(RM) .deps.mak

.PHONY: clean


# Include generated dependencies makefile

include .deps.mak

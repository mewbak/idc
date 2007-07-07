# Makefile


# Configuration variables

PYTHON = python
export PYTHONPATH = .


# Use the native-compiled version of ANTLR if possible, as it is much faster than
# Java byte code.
ifneq ($(shell which cantlr 2>/dev/null),)
ANTLR = cantlr
else
ifneq ($(shell which runantlr 2>/dev/null),)
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

.deps.mak: Makefile util/makedeps.py
	$(PYTHON) util/makedeps.py > $@

.PHONY: deps .deps.mak


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

clean:
	-$(RM) .deps.mak

.PHONY: clean


# Dependencies

transf/parse/antlratermTokenTypes.txt: antlratermTokenTypes.txt 
	cp -f $< $@

include .deps.mak

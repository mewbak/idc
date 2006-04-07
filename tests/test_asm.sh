#!/bin/sh

for FILE in examples/*.s
do
	echo "* File $FILE *"
	echo
	
	echo "** Tokens **"
	python asmLexer.py < $FILE
	echo 

	python asmParser.py < $FILE

	echo
done

#!/bin/sh

for FILE in ssl/pentium.ssl #ssl/*.ssl
do
	echo "* File $FILE *"
	echo
	
	echo "** Lexing **"
	if ! python sslLexer.py < $FILE > /dev/null 
	then 
		echo 
		continue
	fi
	echo 

	echo "** Parsing **"
	if ! python sslParser.py < $FILE > /dev/null
	then 
		echo 
		continue
	fi
	echo 

	echo "** Preprocessing **"
	if ! python sslPreprocessor.py < $FILE
	then 
		echo 
		continue
	fi
	echo
done

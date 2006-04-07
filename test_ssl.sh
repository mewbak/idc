#!/bin/sh

for FILE in ssl/*.ssl
do
	echo "* File $FILE *"
	echo
	
	echo "** Lexing **"
	if ! python utils/sslc/lexer.py < $FILE > /dev/null 
	then 
		echo 
		continue
	fi
	echo 

	echo "** Parsing **"
	if ! python util/sslc/parser.py < $FILE > /dev/null
	then 
		echo 
		continue
	fi
	echo 

	echo "** Preprocessing **"
	if ! python util/sslc/preprocessor.py < $FILE
	then 
		echo 
		continue
	fi
	echo
done

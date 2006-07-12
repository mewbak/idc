#!/bin/sh
# Source grepper

grep \
	--recursive \
	--color=always \
	--include '*.py' \
	--include '*.g' \
	"$@" . \
| less -R -FX

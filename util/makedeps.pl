#!/usr/bin/perl

my @all;

foreach $ARG (@ARGV) {
	open (FH, $ARG);

	my @depends;
	my @targets;

	$ARG =~ s:^\./::;

	push @depends, $ARG;
	
	($ARGDIR = $ARG) =~ s:[^/]*$::;
	
	while (<FH>) {
		if (/\bclass\s+(\w+)\s+extends\s+(\w+)\s*;/) {
			$class = $1;
			push @targets, "$ARGDIR$1.py";
		}
		if (/\bimportVocab\s*=\s*(\w+)\s*;/) {
			push @depends, "$ARGDIR$1TokenTypes.txt";
		}
		if (/\bexportVocab\s*=\s*(\w+)\s*;/) {
			$target = "$ARGDIR$1TokenTypes.txt";
			if (!grep {/$target/} @targets) {
				push @targets, $target;
			}
		}
	}

	print join(" ", @targets) . ': ' . join(" ", @depends) . "\n";
	print "\t\$(ANTLR) -o \$(\@D) \$<\n";
	print "\n";

	push @all, @targets;
}

print "all: " . join(" ", @all) . "\n\n";

print "clean: clean-antlr\n\n";

print "clean-antlr:\n";
print "\t\@\$(RM) " . join(" ", @all) . "\n\n";

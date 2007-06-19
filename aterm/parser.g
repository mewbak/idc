/*
 * Grammar for annotated terms. Based on the ATerm syntax.
 */


header {
    __doc__ = "Term parsing."

    __all__ = ["Parser"]
}


options {
	language = "Python";
}


class parser extends Parser;

options {
	defaultErrorHandler = false;
}

{
    __doc__ = "Term parser."

    def handleInt(self, value):
        raise NotImplementedError

    def handleReal(self, value):
        raise NotImplementedError

    def handleStr(self, value):
        raise NotImplementedError

    def handleNil(self):
        raise NotImplementedError

    def handleCons(self, head, tail):
        raise NotImplementedError

    def handleAppl(self, name, args, annos=None):
        raise NotImplementedError

    def handleWildcard(self):
        raise NotImplementedError

    def handleVar(self, name):
        raise NotImplementedError

    def handleApplCons(self, name, args, annos=None):
        raise NotImplementedError
}


do_term returns [res]
	: res=term EOF
	;

term returns [res]
	: ival:INT
		{ res = self.handleInt(int(ival.getText())) }
	| rval:REAL
		{ res = self.handleReal(float(rval.getText())) }
	| sval:STR
		{ res = self.handleStr(sval.getText()) }
	| LSQUARE elms=term_list RSQUARE
		{ res = elms }
	|
		( cname:CONS ( LPAREN args=term_args RPAREN | { args = [] } )
			{ name = cname.getText() }
		| LPAREN args=term_args RPAREN
			{ name = "" }
		)
		( LCURLY annos=term_list RCURLY
			{ res = self.handleAppl(name, args, annos) }
		|
			{ res = self.handleAppl(name, args) }
		)
	|
		( WILDCARD
			{ res = self.handleWildcard() }
		| vname:VAR
			{ res = self.handleVar(vname.getText()) }
		)
		( LPAREN args=term_list RPAREN
			( LCURLY annos=term_list RCURLY
				{ res = self.handleApplCons(res, args, annos) }
			|
				{ res = self.handleApplCons(res, args) }
			)
		)?
	;

term_list returns [res]
	:
		{ res = self.handleNil() }
	| head=term
		( COMMA tail=term_list
		|
			{ tail = self.handleNil() }
		)
			{ res = self.handleCons(head, tail) }
	| STAR
		(
			{ res = self.handleWildcard() }
		| vname:VAR
			{ res = self.handleVar(vname.getText()) }
		)
	;

term_args returns [res]
	:
			{ res = [] }
	| arg=term
			{ res = [arg] }
		( COMMA args=term_args
			{ res += args }
		)?
	;

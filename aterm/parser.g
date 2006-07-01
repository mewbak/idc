// Term parsing


options {
	language = "Python";
}


class parser extends Parser;

options {
	defaultErrorHandler = false;
}

{
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

    def handleAppl(self, name, args):
        raise NotImplementedError
       
    def handleAnnos(self, name, args):
        raise NotImplementedError
       
    def handleWildcard(self):
        raise NotImplementedError
       
    def handleVar(self, name):
        raise NotImplementedError
       
    def handleSeq(self, pre, post):
        raise NotImplementedError
       
    def handleApplCons(self, name, args):
        raise NotImplementedError
}


do_term returns [res]
	: res=term EOF
	;

term returns [res]
	: res=term_atom 
		( options { greedy = true; }
		: LCURLY annos=term_list RCURLY 
			{ res = self.handleAnnos(res, annos) }
		)?
	;

term_atom returns [res]
	: ival:INT
		{ res = self.handleInt(int(ival.getText())) }
	| rval:REAL
		{ res = self.handleReal(float(rval.getText())) }
	| sval:STR
		{ res = self.handleStr(sval.getText()) }
	| LSQUARE elms=term_list RSQUARE
		{ res = elms }
	| LPAREN args=term_args RPAREN
		{ res = self.handleAppl("", args) }
	| cname:CONS
			{ name = cname.getText() }
		( LPAREN args=term_args RPAREN
		| 
			{ args = [] } 
		)
			{ res = self.handleAppl(name, args) }
	| WILDCARD 
			{ res = self.handleWildcard() }
		( LPAREN args=term_list RPAREN
			{ res = self.handleApplCons(res, args) }
		)?
	| vname:VAR
			{ res = self.handleVar(vname.getText()) }
		( ASSIGN pattern=term
			{ res = self.handleSeq(pattern, res) }
		| LPAREN args=term_list RPAREN
			{ res = self.handleApplCons(res, args) }
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

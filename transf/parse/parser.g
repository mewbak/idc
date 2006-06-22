/* 
 * Grammar for generating term transformations. The syntax is inspired on 
 * the Stratego language.
 */


header {
    import antlr
    import transf


    class SemanticException(antlr.SemanticException):

        def __init__(self, node, msg):
            antlr.SemanticException.__init__(self)
            self.node = node
            self.msg = msg
           
        def __str__(self):
            line = self.node.getLine()
            col  = self.node.getColumn()
            text = self.node.getText()
            return "line %s:%s: \"%s\": %s" % (line, col, text, self.msg)

        __repr__ = __str__
}

header "translator.__init__" {
    self.globals = kwargs.get("globals", {})
    self.locals = kwargs.get("locals", {})
    self.stack = []
}


options {
	language = "Python";
}


class parser extends Parser;

options {
	k=2;
	buildAST = true;
	defaultErrorHandler = false;
}

transf_defs
	: ( transf_def )* EOF!
	;

rule_defs
	: ( rule_def )* EOF!
	;

meta_def
	: id_list COLON transf EOF!
	;

transf_def
	: id EQUAL! transf
		{ ## = #(#[TRANSF_DEF,"TRANSF_DEF"], ##) }
	| id LPAREN! id_list RPAREN! EQUAL transf	
		{ ## = #(#[TRANSF_FAC_DEF,"TRANSF_FAC_DEF"], ##) }
	;

rule_def
	: id EQUAL^ rule_set
	;

transf
	: transf_expr
	;

transf_prefix
	: QUEST^ term
	| BANG^ term
	| TILDE^ term
	| EQUAL^ (PLUS | MINUS)? LID (LPAREN! arg_list RPAREN!)?
	| CARET^ LID
	;

transf_method
	: v:VARMETHOD! ( LPAREN! arg_list RPAREN!)?
		{
            n, m = #v.getText().split('-')
            ## = #(#[VARMETHOD,"VARMETHOD"], #[ID,n], #[ID,m], ##) 
		}
	;

transf_atom
	: IDENT
	| FAIL
	| transf_prefix
	| transf_method
	| id 
		( 
			{ ## = #(#[TRANSF,"TRANSF"], ##) }
		| LPAREN! arg_list RPAREN!
			{ ## = #(#[TRANSF_FAC,"TRANSF_FAC"], ##) }
		)
	| LCURLY!
		( ( id_list COLON ) => id_list COLON transf
			{ ## = #(#[SCOPE,"SCOPE"], ##) } 
		| rule_set
		) RCURLY!
	| LPAREN!
		( ( term RARROW ) =>  rule
		| transf
		) RPAREN!
	| LANGLE! transf RANGLE! term
		{ ## = #(#[BUILD_APPLY,"BUILD_APPLY"], ##) }
	| IF^ transf THEN! transf ( ELSE! transf )? END!
	| LET^ defn_list IN transf END!
	| SWITCH^ transf 
		( CASE transf COLON! transf )* 
		( OTHERWISE COLON! transf )? 
	  END!
	| REC^ id COLON! transf_atom
	| WITH^ var_def_list IN transf END!
	;

transf_application
	: transf_atom ( RDARROW^ var )?
	;

transf_merge
	: transf_application 
		( RSLASH id_list LSLASH! ( LSLASH id_list RSLASH! )? transf_application 
			{ ## = #(#[JOIN,"JOIN"], ##) } 
		| LSLASH id_list RSLASH! ( RSLASH id_list LSLASH! )? transf_application
			{ ## = #(#[JOIN,"JOIN"], ##) } 
		)?
	;

transf_composition
	: transf_merge ( SEMI^ transf_merge )*
	;

transf_choice
	: transf_composition 
		( LANGLE^ transf_composition PLUS! transf_choice
		| PLUS^ transf_choice 
		)?
	;

transf_expr
	: transf_choice
	;

transf_list
	: ( transf ( COMMA! transf )* )?
	;

defn
	: id EQUAL! transf
	;

defn_list
	: defn ( COMMA! defn )*
	;

var_def_list
	: var_def (COMMA! var_def )*
	;

var_def
	: var constructor
	;

constructor
	: ( EQUAL! transf )?
		{ ## = #(#[TERM,"TERM"], ##) }
	| LSQUARE! RSQUARE! ( EQUAL! var )?
		{ ## = #(#[TABLE,"TABLE"], ##) }
	| LPAREN! RPAREN! ( EQUAL! transf )?
		{ ## = #(#[DYNAMIC,"DYNAMIC"], ##) }
	;

var
	: l:LID	{ #l.setType(VAR) }
	;

id
	: ID
	| l:LID { #l.setType(ID) }
	| u:UID { #u.setType(ID) }
	| w:WHERE { #w.setType(ID) }
	;

arg_list
	: ( arg ( COMMA! arg )* )?
	;

arg
	: OBJ
	| PRIME! var ( PRIME! )?
	| transf
	;
	
rule
	: term RARROW! term ( WHERE transf )?
		{ ## = #(#[RULE,"RULE"], ##) }
	;

anon_rule
	: rule
		{ ## = #(#[ANON,"ANON"], ##) }
	;

rule_set
	: anon_rule 
		( VERT! rule_set
			{ ## = #(#[PLUS,"PLUS"], ##) }
		)?
	;

/*
debug_term
	: t:term
		{
            if self.debug:
                import sys
                sys.stderr.write("*** Term ***\n")
                sys.stderr.write(#t.toStringTree())
                sys.stderr.write("\n")
		}
	;
*/

term
	: term_atom 
		( options { warnWhenFollowAmbig=false; }
		: term_anno
			{ ## = #(#[ANNOS,"ANNOS"], ##) }
		)?
//	| transf_prefix
	//	{ ## = #(#[TRANSF,"TRANSF"], ##) }
	| transf_method
		{ ## = #(#[TRANSF,"TRANSF"], ##) }
	;

term_atom
	: INT
	| REAL
	| STR
	| LSQUARE! term_list RSQUARE!
	| term_sym
	| term_tuple
	| term_appl
	| term_var
	| WILDCARD
	| LANGLE! transf RANGLE!
		{ ## = #(#[TRANSF,"TRANSF"], ##) }
	;

term_name
	: u:UID
		{ ## = #(#[STR,#u.getText()]) }
	;

term_var
	: var
	;

term_sym
	: term_name term_undefined
		{ ## = #(#[APPL,"APPL"], ##) }
	;
	
term_tuple
	: term_args
		{ ## = #(#[APPL,"APPL"], #[STR,""], ##) }
	;
	
term_appl
	: ( term_name | term_var | WILDCARD ) term_args
		{ ## = #(#[APPL,"APPL"], ##) }
	;
	
term_args
	: LPAREN! term_list RPAREN!
	;

term_undefined
	:
		{ ## = #(#[UNDEF,"UNDEF"]) }
	;

term_anno
	: LCURLY! term_list RCURLY!
	;

term_implicit_wildcard
	:
		{ ## = #(#[WILDCARD,"_"]) }
	;

term_opt_args
	: ( LPAREN ) => term_args
	| term_implicit_nil
	;
	
term_implicit_nil
	:
		{ ## = #(#[NIL,"NIL"]) }	
	;

term_list
	: term_implicit_nil
	| term ( COMMA! term_list | term_implicit_nil )
		{ ## = #(#[CONS,"CONS"], ##) }	
	| STAR! term_opt_wildcard
	;
	
term_opt_wildcard
	: term
	|
		{ ## = #(#[WILDCARD,"_"]) }	
	;

id_list
	: ( id ( COMMA! id )* )?
	;


{
class Meta:
    """A parsed transformation factory."""

    def __init__(self, globals, locals, args, ast):
        self.globals = globals
        self.locals = locals
        self.args = args
        self.ast = ast
    
    def __call__(self, *args):
        if len(args) != len(self.args):
            raise TypeError("%d arguments required (%d given)" % (len(self.args), len(args)))
        translator = Walker(
            globals = self.globals,
            locals = self.locals,
        )
        translator.stack.append(dict(zip(self.args, args)))
        return translator.transf(self.ast)
}

class translator extends TreeParser;

options {
	defaultErrorHandler = false;
}

{
    // XXX: too much python voodoo
    
    def bind_name(self, name):
        // lookup in the symbol stack
        for i in range(len(self.stack) - 1, -1, -1):
            try:
                return self.stack[i][name]
            except KeyError:
                pass
        
        // lookup in the caller namespace
        try:
            return eval(name, self.globals, self.locals)
        except NameError:
            pass
    
        // lookup in the builtins module
        from transf.parse import builtins
        try:
            return getattr(builtins, name)
        except AttributeError:
            pass

        // lookup in the transf module
        try:
            return eval(name, transf.__dict__)
        except NameError:
            pass
        except AttributeError:
            pass
        
        return None
    
    def define_name(self, name, value):
        // define transf in the local namespace
        eval(compile(name + " = _", "", "single"), {"_": value}, self.locals)
}

transf_defs
	: ( transf_def )+
	;
	
transf_def
	: #( TRANSF_DEF n=id t=transf )
		{ self.define_name(n, t) }
	| #( TRANSF_FAC_DEF n=id a=id_list EQUAL T=meta[a] )
	    { self.define_name(n, T) }
	;

meta_def returns [ret]
	: a=id_list COLON ret=meta[a]
	;
	
meta[a] returns [ret]
	: t:.
		{ 
           ret = Meta(
               self.globals,
               self.locals,
               a,
               #t,
           )
        }
	;
	
transf returns [ret]
	: IDENT
		{ ret = transf.base.ident }
	| FAIL
		{ ret = transf.base.fail }
	| #( QUEST m=match_term )
		{ ret = m }
	| #( BANG b=build_term )
		{ ret = b }
	| #( TILDE t=traverse_term )
		{ ret = t }
	| #( EQUAL n=id )
		{ ret = transf.variable.Set(n) }
	| #( CARET n=id )
		{ ret = transf.variable.Unset(n) }
	| #( SEMI l=transf r=transf )
		{ ret = transf.combine.Composition(l, r) }
	| #( PLUS l=transf r=transf )
		{ ret = transf.combine.Choice(l, r) }
	| #( LANGLE l=transf m=transf r=transf )
		{ ret = transf.combine.GuardedChoice(l, m, r) }
	| #( TRANSF n=i:id )
		{
            ret = None
            txn = self.bind_name(n)
            if txn is None:
                raise SemanticException(#i, "could not find %s" % n)
            if not isinstance(txn, transf.base.Transformation):
                raise SemanticException(#i, "%s is not a transformation" % n)
            ret = txn
        }
	| #( TRANSF_FAC n=f:id a=as:arg_list )
		{
            ret = None
            Txn = self.bind_name(n)
            if Txn is None:
                raise SemanticException(#f, "could not find %s" % n)
            if not callable(Txn):
                raise SemanticException(#f, "%s is not callable" % n)
            try:
                txn = Txn(*a)
            except TypeError, ex:
                raise SemanticException(#f, "error: %s" % ex)
            if not isinstance(txn, transf.base.Transformation):
                raise SemanticException(#f, "%s did not return a transformation" % n)
            ret = txn
        }
	| #( SCOPE vars=id_list COLON ret=transf )
		{
            if vars:
                ret = transf.scope.Local(ret, vars)
        }
	| #( RULE m=match_term b=build_term
		( WHERE w=transf 
			{ ret = transf.combine.Composition(transf.combine.Where(w), b) }
		|
			{ ret = b }
		)
			{ ret = transf.combine.Composition(m, ret) }
	  )
	| #( ANON ret=at:transf )
		{
            vars = []
            self.collect_transf_vars(#at, vars)
            if vars:
                ret = transf.scope.Local(ret, vars)
        }
	| #( RDARROW t=transf v=var )
		{ ret = transf.combine.Where(transf.combine.Composition(t, transf.variable.Set(v))) }
	| #( BUILD_APPLY t=transf b=build_term )
		{ ret = transf.combine.Composition(b, t) }
	| #( IF c=transf t=transf 
		(
			{ ret = transf.combine.IfThen(c, t) }
		| e=transf
			{ ret = transf.combine.IfThenElse(c, t, e) }
		)
	  )
	| #( SWITCH cond=transf 
			{ cases = [] }
		( CASE c=transf a=transf
			{ cases.append((c, a)) }
		)*
		( OTHERWISE o=transf
		|
			{ o=None }
		)
			{ ret = transf.combine.Switch(cond, cases, o) }
	  )
	| #( LET 
			{ vars = {} }
		( n=id v=transf
			{ vars[n] = v }
		)* IN t=transf
	  )
	  	{ ret = transf.scope.Let(t, **vars) }
	| #( JOIN l=transf 
			{ unames = [] }
			{ inames = [] }
		( LSLASH ids=id_list 
			{ inames.extend(ids) }
		| RSLASH ids=id_list
			{ unames.extend(ids) }
		)* r=transf
	 ) 
		{ ret = transf.table.Join(l, r, unames, inames) }
	| #( REC 
			{ ret = transf.util.Proxy() }
		r=id 
			{ self.stack.append({r: ret}) }
		t=transf
			{ self.stack.pop() }
			{ ret.subject = t }
	  )
	| #( VARMETHOD v=id m=id a=arg_list )
		{ ret = transf.variable.Wrap(v, m, *a) }
	| #( WITH v=var_def_list IN t=transf )
		{ ret = transf.scope.With(v, t) }
	;

arg_list returns [ret]
	: { ret = [] } ( a=arg  { ret.append(a) } )*
	;
	
arg returns [ret]
	: o:OBJ
		{ ret = eval(#o.getText(), self.globals, self.locals) }
	| ret=var
	| ret=transf
	;

var_def_list returns [ret]
	: { ret = [] } ( v=var_def { ret.append(v) } )*
	;
	
var_def returns [ret]
	: v=var c=constructor
		{ ret = (v, c) }
	;

constructor returns [ret]
	: #( TERM 
		( t=transf 
			{ ret = transf.term.Transf(t) }
		|
			{ ret = transf.term.new }
		)
	  )
	| #( TABLE
		( v=var
			{ ret = transf.table.Copy(v) }
		|
			{ ret = transf.table.new }
		)
	 )
	;
	
match_term returns [ret]
	: i:INT 
		{ ret = transf.match.Int(int(#i.getText())) }
	| r:REAL 
		{ ret = transf.match.Real(float(#r.getText())) }
	| s:STR 
		{ ret = transf.match.Str(#s.getText()) }
	| NIL
		{ ret = transf.match.nil }
	| #( CONS h=match_term t=match_term )
		{ ret = transf.match.Cons(h, t) }
	| #( APPL n=match_term a=match_term )
		{ ret = transf.match.Appl(n, a) }
	| w:WILDCARD 
		{ ret = transf.base.ident }
	| #( v:VAR // TODO: handle sub-patterns
		{ ret = transf.match.Var(#v.getText()) }
		( p=match_term
			{ ret = transf.combine.Composition(p, ret) }
		)?
	  )
	| #( ANNOS t=match_term a=match_term )
		{ ret = transf.combine.Composition(t, transf.match.Annos(a)) }
	| UNDEF 
		{ ret = transf.base.ident }
	| #( TRANSF txn=transf )
		{ ret = txn }
	;

collect_transf_vars[vars]
	: #( RULE collect_term_vars[vars] )
	| .
	;

collect_term_vars[vars]
	: INT | REAL | STR 
	| NIL
	| #( CONS collect_term_vars[vars] collect_term_vars[vars] )
	| #( APPL collect_term_vars[vars] collect_term_vars[vars] )
	| WILDCARD 
	| #( v:VAR ( collect_term_vars[vars] )? )
		{
            name = #v.getText()
            if name not in vars:
                vars.append(name)
        }
	| #( ANNOS collect_term_vars[vars] collect_term_vars[vars] )
	| UNDEF 
	| TRANSF
	;

build_term returns [ret]
	: i:INT 
		{ ret = transf.build.Int(int(#i.getText())) }
	| r:REAL 
		{ ret = transf.build.Real(float(#r.getText())) }
	| s:STR 
		{ ret = transf.build.Str(#s.getText()) }
	| NIL
		{ ret = transf.build.nil }
	| #( CONS h=build_term t=build_term )
		{ ret = transf.build.Cons(h, t) }
	| #( APPL n=build_term a=build_term )
		{ ret = transf.build.Appl(n, a) }
	| w:WILDCARD 
		{ ret = transf.base.ident }
	| v:VAR 
		{ ret = transf.build.Var(#v.getText()) }
	| #( ANNOS t=build_term a=build_term )
		{ ret = transf.combine.Composition(t, transf.build.Annos(a)) }
	| UNDEF 
		{ ret = transf.build.nil }
	| #( TRANSF txn=transf )
		{ ret = txn }
	;

traverse_term returns [ret]
	: i:INT 
		{ ret = transf.match.Int(int(#i.getText())) }
	| r:REAL 
		{ ret = transf.match.Real(float(#r.getText())) }
	| s:STR 
		{ ret = transf.match.Str(#s.getText()) }
	| NIL
		{ ret = transf.match.nil }
	| #( CONS h=traverse_term t=traverse_term )
		{ ret = transf.congruent.Cons(h, t) }
	| #( APPL n=traverse_term a=traverse_term )
		{ ret = transf.congruent.Appl(n, a) }
	| w:WILDCARD 
		{ ret = transf.base.ident }
	| v:VAR
		{ ret = transf.congruent.Var(#v.getText()) }
	| #( ANNOS t=traverse_term a=traverse_term )
		{ ret = transf.combine.Composition(t, transf.congruent.Annos(a)) }
	| UNDEF 
		{ ret = transf.base.ident }
	| #( TRANSF txn=transf )
		{ ret = txn }
	;

id_list returns [ret]
	: { ret = [] } ( i=id  { ret.append(i) } )*
	;

id returns [ret]
	: i:ID
		{ ret = #i.getText() }
	| l:LID
		{ ret = #l.getText() }
	| u:UID
		{ ret = #u.getText() }
	;
	
var returns [ret]
	: v:VAR
		{ ret = #v.getText() }
	| l:LID
		{ ret = #l.getText() }
	;
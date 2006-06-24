/* 
 * Grammar for generating term transformations. The syntax is inspired on 
 * the Stratego language.
 */


header {
    import antlr
    import aterm.factory
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
	importVocab = parser;
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
	| #( IF 
			{ conds = [] }
		( cond=transf action=transf 
			{ conds.append((cond, action)) }
		)*
		( ELSE other=transf 
		|
			{ other = transf.base.ident }
		)
			{ ret = transf.combine.IfElifElse(conds, other) }
	  )
	| #( SWITCH cond=transf 
			{ cases = [] }
		( CASE c=static_term a=transf
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
	| #( JOIN l=transf names=merge_names r=transf ) 
		{ ret = transf.table.Join(l, r, names[0], names[1]) }
	| #( ITERATE names=merge_names r=transf ) 
		{ ret = transf.table.Iterate(r, names[0], names[1]) }
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

merge_names returns [ret]
	:
			{ unames = [] }
			{ inames = [] }
		( LSLASH ids=id_list 
			{ inames.extend(ids) }
		| RSLASH ids=id_list
			{ unames.extend(ids) }
		)*
			{ ret = unames, inames }
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
	
static_term returns [ret]
	: i:INT 
		{ ret = aterm.factory.factory.makeInt(int(#i.getText())) }
	| r:REAL 
		{ ret = aterm.factory.factory.makeReal(float(#r.getText())) }
	| s:STR 
		{ ret = aterm.factory.factory.makeStr(#s.getText()) }
	| NIL
		{ ret = aterm.factory.factory.makeNil() }
	| #( CONS h=static_term t=static_term )
		{ ret = aterm.factory.factory.makeCons(h, t) }
	| UNDEF 
		{ ret = aterm.factory.factory.makeNil() }	
	| #( APPL n=static_term a=static_term )
		{ ret = aterm.factory.factory.makeAppl(n, a) }
	| #( ANNOS t=static_term a=static_term )
		{ ret = t.setAnnotations(a) }
	| w:WILDCARD 
		{ raise SemanticException(#w, "wildcard in static term") }
	| v:VAR
		{ raise SemanticException(#v, "variable in static term") }
	| t:TRANSF
		{ raise SemanticException(#t, "transformation in static term") }
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
	| UNDEF 
		{ ret = transf.base.ident }
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
	| UNDEF 
		{ ret = transf.build.nil }
	| #( APPL n=build_term a=build_term )
		{ ret = transf.build.Appl(n, a) }
	| w:WILDCARD 
		{ ret = transf.base.ident }
	| v:VAR 
		{ ret = transf.build.Var(#v.getText()) }
	| #( ANNOS t=build_term a=build_term )
		{ ret = transf.combine.Composition(t, transf.build.Annos(a)) }
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
	| UNDEF 
		{ ret = transf.base.ident }
	| #( APPL n=traverse_term a=traverse_term )
		{ ret = transf.congruent.Appl(n, a) }
	| w:WILDCARD 
		{ ret = transf.base.ident }
	| v:VAR
		{ ret = transf.congruent.Var(#v.getText()) }
	| #( ANNOS t=traverse_term a=traverse_term )
		{ ret = transf.combine.Composition(t, transf.congruent.Annos(a)) }
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
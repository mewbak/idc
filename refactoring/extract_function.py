"""Extract a function body."""


import refactoring
import path
import transf


class ExtractFunction(refactoring.Refactoring):

	def name(self):
		return "Extract Function"
	
	def get_original_name(self, term, selection):
		start, end = selection
		if start != end:
			return False

		selected_term = path.fetch(term, start)
		args = []
		kargs = {}
		if selected_term.rmatch("Label(name)", args, kargs):
			return kargs['name']
		else:
			return None

	def applicable(self, term, selection):
		return self.get_original_name(term, selection) is not None

	def input(self, term, selection, inputter):
		factory = term.factory
		label = self.get_original_name(term, selection)
		args = factory.make("[label]", label = label)
		return args

	def apply(self, term, args):
		factory = term.factory
		name, = args
		txn = transf.Rule(
			"[Label(name),*rest]",
			"[FuncDef(Void,name,[],Block(rest))]",
		)
		txn = transf.factory.Module(ExtractBlock(txn,name))
		return txn(term)


# TODO: Handle seperate blocks


class SplitBlock(transf.Transformation):

	def __init__(self, name):
		self.name = name
		self.split_head = transf.Split(
			transf.Match("Label(name)", name=name)
		)
		self.split_tail = transf.Split(
			transf.Match("Ret(*)")
		)

	def __call__(self, term):
		head, first, rest = self.split_head(term)
		body, last, tail = self.split_tail(rest)
		
		return term.factory.makeList([
			head,
			body.append(last).insert(0, first),
			tail
		])


class ExtractBlock(transf.Transformation):
	
	def __init__(self, operand, name):
		self.split_block = SplitBlock(name)
		self.operand = operand
		
	def __call__(self, term):
		head, body, tail = self.split_block(term)
		body = self.operand(body)
		return head.extend(body.extend(tail))


class TestCase(refactoring.TestCase):

	cls = ExtractFunction
		
	applyTestCases = [
		(
			'''
			Module([
				Label("main"),
				Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
				Ret(Int(32,Signed),Sym("eax"))
			])
			''',
			'["main"]',
			'''
			Module([
				FuncDef(Void,"main",[],
					Block([
						Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
						Ret(Int(32,Signed),Sym("eax"))
					])
				)
			])
			'''
		),
		(
			'''
			Module([
				Asm("pre",[]),
				Label("main"),
				Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
				Ret(Int(32,Signed),Sym("eax")),
				Asm("post",[]),
			])
			''',
			'["main"]',
			'''
			Module([
				Asm("pre",[]),
				FuncDef(Void,"main",[],
					Block([
						Assign(Int(32,Signed),Sym("eax"),Lit(Int(32,Signed),1)),
						Ret(Int(32,Signed),Sym("eax"))
					])
				),
				Asm("post",[]),
			])
			'''
		),	]
	
	
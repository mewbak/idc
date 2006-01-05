"""Based on the aterm library"""


try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO
	

FREE = 0
APPL = 1
INT  = 2
REAL = 3
LIST = 4
PLACEHOLDER = 5
BLOB = 6


class ATerm:

	def getType(self):
		raise NotImplementedError

	def isEqual(self, other):
		raise NotImplementedError

	def writeToTextFile(self, fp):
		raise NotImplementedError

	def writeToString(self):
		fp = StringIO()
		self.writeToTextFile(fp)
		return fp.getvalue()

	def __str__(self):
		return self.writeToString()


class ATermInt(ATerm):

	def __init__(self, value):
		self.value = value

	def writeToTextFile(self, fp):
		fp.write("%d" % self.value)


class ATermReal(ATerm):

	def __init__(self, value):
		self.value = value

	def writeToTextFile(self, fp):
		fp.write("%.15e" % self.value)
	
	
class ATermAppl(ATerm):

	def __init__(self, sym, args = ()):
		self.sym = sym
		self.args = args
			
	def arity(self):
		return len(self.args)

	def writeToTextFile(self, fp):
		if self.sym:
			fp.write(self.sym)
		if self.arity():
			fp.write('(')
			self.args[0].writeToTextFile(fp)
			for arg in self.args[1:]:
				fp.write(',')
				arg.writeToTextFile(fp)
			fp.write(')')


class ATermList(ATerm):

	def __init__(self, elements):
		self.elements = elements
	
	def writeToTextFile(self, fp):
		fp.write('[')
		if len(self.elements):
			self.elements[0].writeToTextFile(fp)
			for element in self.elements[1:]:
				fp.write(',')
				element.writeToTextFile(fp)
		fp.write(']')


class ATermPlaceholder(ATerm):

	def __init__(self, type):
		self.type = type

	def writeToTextFile(self, fp):
		fp.write('<')
		self.type.writeToTextFile(fp)
		fp.write('>')


class ATermBlob(ATerm):

	pass



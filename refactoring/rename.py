"""Refactoring for renaming symbols globally."""

from walker import Walker, Failure

import refactoring
import path
import unittest


class Rename(refactoring.Refactoring):

        def name(self):
                return "Rename"

        def get_original_name(self, term, selection):
                start, end = selection
                if start != end:
                        return False

                selected_term = path.Evaluator.evaluate(term, start)
                args = []
                kargs = {}
                if term.factory.match("Sym(name)", selected_term, args, kargs):
                        return kargs['name']
                else:
                        return None

        def applicable(self, term, selection):
                return self.get_original_name(term, selection) is not None

        def input(self, term, selection):
                factory = term.factory
                orig = self.get_original_name(term, selection)
                new = factory.makeStr("XXX")
                args = factory.make("[orig,new]", orig = orig, new = new)
                return args

        def apply(self, term, args):
                src, dst = args
                walker = Renamer(term.factory)
                return walker.rename(term, src, dst)


class Renamer(Walker):
	
	def rename(self, _t, src, dst):
		_f = self.factory
		_a = {}
		_a['src'] = src
		_a['dst'] = dst
		try:
			_r = _t
			_ = []
			_k = _a.copy()
			if not _f.match('Sym(name)', _t, _, _k):
				raise Failure
			if not ( _k['name'].isEquivalent(_k['src']) ):
				raise Failure
			_r = _f.make('Sym(dst)', _t, **_k)
			return _r
		except Failure:
			pass
		try:
			_r = _t
			_ = []
			_k = _a.copy()
			if not _f.match('[]', _t, _, _k):
				raise Failure
			return _r
		except Failure:
			pass
		try:
			_r = _t
			_ = []
			_k = _a.copy()
			if not _f.match('[h,*t]', _t, _, _k):
				raise Failure
			_r = _f.makeConsList(self.rename(_k['h'],_k['src'],_k['dst']),self._map(_k['t'],self.rename,_k['src'],_k['dst']))
			return _r
		except Failure:
			pass
		try:
			_r = _t
			_ = []
			_k = _a.copy()
			if not _f.match('f(*a)', _t, _, _k):
				raise Failure
			_r = _f.makeAppl(_k['f'],self._map(_k['a'],self.rename,_k['src'],_k['dst']))
			return _r
		except Failure:
			pass
		try:
			_r = _t
			_ = []
			_k = _a.copy()
			if not _f.match('_', _t, _, _k):
				raise Failure
			return _r
		except Failure:
			pass
		
		raise Failure("failed to transform '%r' in rename", _t)

class TestCase(unittest.TestCase):

        def setUp(self):
                import aterm
                self.factory = aterm.Factory()

        renameTestCases = [
                ('Sym("a")', '["a", "b"]', 'Sym("b")'),
                ('Sym("c")', '["a", "b"]', 'Sym("c")'),
                ('[Sym("a"),Sym("c")]', '["a", "b"]', '[Sym("b"),Sym("c")]'),
                ('C(Sym("a"),Sym("c"))', '["a", "b"]', 'C(Sym("b"),Sym("c"))'),
        ]

        def testRename(self):
                for termStr, argsStr, expectedResultStr in self.renameTestCases:
                        term = self.factory.parse(termStr)
                        args = self.factory.parse(argsStr)
                        expectedResult = self.factory.parse(expectedResultStr)

                        refactoring = Rename()

                        result = refactoring.apply(term, args)

                        self.failUnlessEqual(result, expectedResult)

if __name__ == '__main__':
        unittest.main()



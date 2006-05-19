"""Refactoring for renaming symbols globally."""

from walker import Walker, Failure

import refactoring
import path


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
                walker = self.Renamer(term.factory)
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
			if not _f.match('f(*a)', _t, _, _k):
				raise Failure
			_r = _f.makeAppl(_k['f'],_f.makeConsList(self._map(_k['a'],self.rename,_k['src'],_k['dst']),_f.makeNilList()))
			return _r
		except Failure:
			pass
		
		raise Failure("failed to transform '%r' in rename", _t)
	# TODO: write unit-tests
	
	


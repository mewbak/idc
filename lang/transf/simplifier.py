from transf import parse

parse.Transfs('''
applName =
	?Rule(Appl(Str(_), Ident), _)  +
	?Anon(Rule(Appl(Str(_), Ident), _))


applNames = 
	?Choice(<Map(applName)>)
	
simplifyRule = {
	Rule(Appl(Str(name), Undef), build) ->
		SwitchCase([Str(name)], Build(build)) 
|	Anon(Rule(Appl(Str(name), Undef), build)) ->
		SwitchCase([Str(name)], Build(build)) 
}
	

simplifyChoice = {
	Choice(rules) -> 
		Switch(
			Transf("project.name"), 
			<<Filter(simplifyRule)> rules>, 
			Choice(<<Filter(Not(simplifyRule))>rules>)
		)
		#where <Some(simplifyRule)> rules
}

simplify = BottomUp(Try(simplifyChoice))
simplify = id

''', simplify=False)
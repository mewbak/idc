int factorial(int n)
{
	register int i, f;
	f = 1;
	for(i = 2; i <= n; i++)
		f *= i;
	return f;
}

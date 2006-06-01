#include <stdio.h>

/* compute fibonacci number recursively */
unsigned fib(int x)
{
	if(x > 2)
		return fib(x - 1) + fib(x - 2);
	else
		return 1;
}

/*
int main()
{
	register int i;

	for (i = 1; i <= 10; i++)
		printf("fibonacci(%d) = %u\n", i, fibonacci(i));
	
	return 0;
}
*/

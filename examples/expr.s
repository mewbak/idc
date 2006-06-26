	.text
.globl main
main:
	movl	$1, %eax
	movl	$2, %ebx
	addl	%eax, %ebx
	movl	$3, %ecx
	imull	%ecx
	movl	$2, %ecx
	andl	$1, %ecx
	idivl	%ecx
	addl	%eax, %edx
	ret

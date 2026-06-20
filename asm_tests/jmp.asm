.org 10

OUT: 	.word 0xFE

.start	main

main:
	LOADI R1, 10
	LOADI R2, 12
	LOADI R0, 1
	JMP tst

.org 100
tst:
	STORE R2, OUT
	HALT
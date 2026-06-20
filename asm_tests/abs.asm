.org 0x10

X:		.WORD -15
Y: 		.word 0
.start main

.org 0x15

main:
	LOADI R1, 0
	LOAD R2, X
	CMP R1, R2
	JG save
	NEG R2, R2
	JMP save

save: 
	STORE R2, Y
	HALT

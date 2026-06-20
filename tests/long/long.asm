
OUT:		.word	254
A1:			.word 	0x00000001 ;  A = R2:R1 
A2:			.word 	0xFFFFFFFF 
B1:			.word	0x00000001 ;  B = R4:R3 
B2:			.word 	0x00000001
C1:			.word 	0
C2:			.word   0

.start main

main:
	LOAD	R1,		A2
	LOAD	R2,		A1
	LOAD	R3,		B2,
	LOAD	R4,		B1
	LOAD	R5,		C2
	LOAD	R6,		C1
	
	; LOW PARTS
	ADD		R5,		R1,		R3
	JC		set_carry
	
sum_high:
	ADD		R6,		R2,		R4
	ADD		R6,		R6,		R7
	JMP		finish_program
	
set_carry:
	LOADI	R7,		1
	JMP sum_high

finish_program:
	STORE	R6,		OUT
	STORE 	R5,		OUT
	HALT
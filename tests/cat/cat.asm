
IN:			.word   253
OUT:		.word	254
STOP_WORD:	.word   10

.start	main

main:
	LOAD	R2,		STOP_WORD
	JMP loop

loop:
	IN 		R1
	CMP		R1, 	R2
	JZ		end_program
	
	STORE 	R1		OUT
	JMP		loop

end_program:
	HALT
	
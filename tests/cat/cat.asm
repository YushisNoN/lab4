
IN:			.word   255
OUT:		.word	254
STOP_WORD:	.word   10

.start	main

main:
	LOAD	R2,		STOP_WORD
	LOAD	R4,		[OUT]
	JMP loop

loop:
	LOAD 	R3,		[IN]
	CMP		R3, 	R2
	JZ		end_program
	
	STORE 	R3,		[OUT]
	JMP		loop

end_program:
	HALT
	
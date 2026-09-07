
OUT:		.word	254
STRING:		.str	"Hello world!"

.start main

main:
	LOADI	R4,		1
	LOADI	R1,		STRING
	LOAD	R2,		R1
	CMP		R2,		R0
	JZ		end_program

loop:
	ADD		R1,		R1,		R4
	LOAD	R3,		R1
	STORE	R3,		[OUT]
	
	SUB		R2,		R2,		R4
	CMP		R2,		R0
	JNZ		loop

end_program:
	HALT
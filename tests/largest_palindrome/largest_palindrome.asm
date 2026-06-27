.org 0x10

OUT:        .word 254
ANSWER:     .word 0
MAX:        .word 0		; TICK: 125304360 MAX: 906609
A:			.word 999
CONST_10:	.word 100

.start main

main:
	LOAD 	R1, 	A
	LOAD 	R2, 	A
	LOADI 	R14, 	1
	LOADI   R13,    100
	LOADI   R8,		10
	LOADI 	R10, 	0
	JMP 	loop_i
	
loop_i:
	CMP		R1,		R13
	JZ 		end_program
	
	MUL		R6,		R1,		R1
	LOAD	R7,		MAX
	CMP		R6,		R7
	JL		end_program
	
	LOAD	R2,		A
	JMP		loop_j
	
loop_i_end:
	SUB		R1,		R1,		R14
	JMP		loop_i
	
loop_j:
	CMP 	R2,  	R13
	JZ		loop_i_end
	
	MUL		R3,		R1,		R2
	MOV		R4, 	R3
	SUB		R2,		R2,		R14
	
	CMP 	R3,		R7
	JL		skip
	CALL	is_pal
	skip:
		JMP		loop_j

is_pal:
	make_palindom:
		CMP 	R3, 	R10
		JZ		end_function
		MUL		R12,	R12,	R8
		DIV		R11,	R3,		R8
		MUL		R11,	R11,	R8
		SUB		R11,	R3,		R11
		ADD		R12,	R12,	R11
		DIV		R3,		R3, 	R8
		JMP 	make_palindom
		
	end_function:
		CMP		R12,	R4
		JNZ		ret_function
	
		CALL 	save_max_palindrome
		
	ret_function:
		LOADI	R12, 	0
		ret
		
save_max_palindrome:
	LOAD 	R9,		MAX
	CMP		R9,		R12
	JG 		end_save_max_function
	STORE	R12,	MAX

end_save_max_function:
	ret

end_program:
	LOAD	R1,		MAX
	STORE 	R1, 	OUT
	HALT
	
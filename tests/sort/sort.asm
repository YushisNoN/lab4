
IN:			.word   253
OUT:		.word	254
LEN:		.word 	0
ARR:		.word 	0

.org 0x100
.start	main

main:
	IN		R1
	STORE	R1,		LEN
	LOADI	R2,		0
	LOADI	R4,		ARR
	JMP		in_loop

in_loop:
	CMP		R1,		R2
	JZ 		end_input
	
	IN 		R3
	STORE 	R3,		R4
	ADDI	R2,		1
	ADDI	R4,		1
	JMP		in_loop

end_input:
	LOADI	R2,		0
	LOADI	R3,		0
	LOAD	R1,		LEN
	CALL	bubble_sort
	
	LOAD	R1,		LEN
	LOADI	R2,		0
	JMP 	save

bubble_sort:
	i_loop:
		CMP		R2,		R1
		JZ		end_bubble_sort
		LOADI	R3,		0
		SUB		R4,		R1,		R2
		SUBI	R4,		1
		j_loop:
			CMP		R3,		R4
			JZ		i_loop_end
			
			LOADI	R10,		ARR
			ADD		R10,		R10,		R3
			LOAD 	R6,		[R10]
		
			LOADI	R11,		ARR
			ADD		R11,		R11,		R3
			ADDI	R11,		1
			LOAD	R7,		[R11]
			
			CMP		R6,		R7
			JL		continue
			
			MOV		R8,		R6
			STORE	R7,		R10
			STORE	R8,		R11
			
			continue:
				ADDI	R3,		1
				JMP		j_loop
				
		i_loop_end:
			ADDI	R2,		1
			JMP		i_loop
			
	end_bubble_sort:
		RET

save:
	
	CMP		R2,		R1
	JZ		finish_program
	
	LOADI	R3,		ARR
	ADD		R3,		R3,		R2
	LOAD 	R4,		[R3]
	STORE	R4,		OUT
	ADDI	R2,		1
	JMP 	save

finish_program:
	HALT
	
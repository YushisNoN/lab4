OUT:        	.word   254
IN:         	.word   255
QUESTION:   	.str    "What is your name?\n"
HELLO:      	.str    "Hello,  "
NAME:			.word	0x22			; buffer
BUFFER_START:	.word 	0x22


.org 0x100
.start main

main:
	LOADI	 R4,	1
    LOADI    R1, 	QUESTION
	LOAD 	 R2,	R1

print_question:
	loop:
		CMP		R2,		R0
		JZ		print_hello
		ADD		R1,		R1,		R4
		LOAD	R3,		R1
		STORE	R3,		[OUT]
		
		SUB		R2,		R2,		R4
		JMP		loop

print_hello:
	LOADI	R1,		HELLO
	LOAD	R2,		R1
	hello_loop:
		CMP		R2,		R0
		JZ		print_answer
		ADD		R1,		R1,		R4
		LOAD	R3,		R1
		STORE	R3,		[OUT]
		
		SUB		R2,		R2,		R4
		JMP		hello_loop

print_answer:
	LOAD	R1		[IN]
	LOADI	R4,		10
	answer_loop:
		CMP		R1,		R4
		JZ		end_program
		STORE	R1,		[OUT]
		ADDI	R1,		1
		LOAD	R1		[IN]
		JMP		answer_loop
		
end_program:
	HALT
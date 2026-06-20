OUT:        	.word   254
IN:         	.word   253
QUESTION:   	.str    "What is your name?\n"
HELLO:      	.str    "Hello,  "
NAME:			.word	0x22			; buffer
BUFFER_START:	.word 	0x22


.org 0x100
.start main

main:
    LOADI   R1, 	QUESTION
    PSTR    R1
	
	LOADI	R1,		HELLO
	PSTR 	R1
	
	
	LOAD	R2,		NAME
	LOADI   R4, 	10
	LOADI	R6,		0

read_loop:
    IN      R1
    CMP     R1, 	R4
    JZ      finish_read

    STORE   R1, 	R2
    ADDI    R2, 	R2, 	1
	ADDI 	R5,		1
	
    JMP     read_loop

finish_read:
	LOAD	R1,		BUFFER_START
	
	print_loop:
		CMP		R5,		R6
		JZ		finish_program
	
		LOAD	R2,		R1
		STORE	R2,		OUT
		
		ADDI	R1,		1
		SUBI	R5,		1
		JMP		print_loop

finish_program:
	HALT
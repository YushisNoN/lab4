; .const DEBUG 0
.const SIZE 10

.macro ZERO reg
    LOADI 	reg 	0
.endm

.ifdef DEBUG

.start main

	main:
		ZERO 	R1
		ADDI 	R1 		SIZE
		STORE	R1,		254
		HALT

	.else
		main:
			LOADI R1 999
			STORE	R1,		254
			HALT

.endif
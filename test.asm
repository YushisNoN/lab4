.org 100

var_a:		.word 150 ; Commentariy dlya testa penisov zov 
var_b: 		.word 50
var_c: 		.word 0   ; tmp variable

.org 120

.start main

main:
	LOAD R1, var_a ; R0 = 150
	LOAD R2, var_b ; R1 = 50
	SUB R2, R1, R2
	JL else_branch
	ADD R3, R1, R2
	JMP save

else_branch:
	SUB R3, R1, R2

save:
	STORE R3, var_c
	HALT

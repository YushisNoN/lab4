.org 0x10

X:		.str "Hello, World!" ; PSTR test comment
OUT:	.word 0xFE			 ; Output port
IN:		.word 255		     ; Input port
tmp:	.word 0				 ; temp var for gcd

.org 100

.start	main

main:
	LOADI R1, X
	PSTR R1
	IN R2
	IN R1
	CALL gcd
	STORE R1, OUT
	HALT
	
.org 200

gcd:
loop:
    PUSH R1
    LOAD R1, tmp
    CMP R2, R1
    POP R1
    JZ end

    PUSH R2
    LOAD R2, tmp
    CMP R1, R2
    POP R2
    JZ end

    CMP R2, R1
    JZ end
	JG a_gt_b
	SUB R1, R1, R2
	JMP loop

a_gt_b:
	SUB R2, R2, R1
	JMP loop

end:
    MOV R0, R1
    RET
	



	
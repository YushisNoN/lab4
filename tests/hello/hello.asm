
OUT:	.word	254
STRING:	.str	"Hello, world!"

.start	main

main:
	LOADI	R1,		STRING
	PSTR	R1
	HALT
	